# Chapter 21: File Upload and Download

## What You Will Learn

- How file uploads work in HTTP (multipart/form-data).
- How to use MultipartFile to receive uploaded files.
- How to configure maximum file size limits.
- How to save uploaded files to disk with unique filenames.
- How to validate file types and reject dangerous uploads.
- How to serve files back to users for download.
- How to set proper download headers (Content-Disposition).
- How to handle multiple file uploads in a single request.

## Why This Chapter Matters

Think about every web application you use daily. Profile pictures on social media. Resumes on job boards. Invoices in accounting software. Attachments in email. File upload and download is one of the most common features in web applications.

Getting file handling right is important for two reasons. First, files can be large. A poorly configured upload system can crash your server or fill your disk. Second, files can be dangerous. An attacker could upload a malicious script disguised as an image. You need to validate, limit, and handle files carefully.

In this chapter, you will build a complete file upload and download system that is safe, reliable, and production-ready.

---

## 21.1 How File Uploads Work in HTTP

When you submit a regular HTML form, the data is sent as `application/x-www-form-urlencoded`. That works for text fields. But files are binary data (images, PDFs, spreadsheets), and they need a different encoding.

The **multipart/form-data** encoding splits the request body into multiple parts. Each part can be a text field or a file:

```
+----------------------------------------------------+
|  HTTP REQUEST (multipart/form-data)                 |
+----------------------------------------------------+
|                                                     |
|  POST /api/files/upload HTTP/1.1                    |
|  Content-Type: multipart/form-data;                 |
|    boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW   |
|                                                     |
|  ------WebKitFormBoundary7MA4YWxkTrZu0gW            |
|  Content-Disposition: form-data; name="description" |
|                                                     |
|  My vacation photo                                  |
|  ------WebKitFormBoundary7MA4YWxkTrZu0gW            |
|  Content-Disposition: form-data; name="file";       |
|    filename="beach.jpg"                             |
|  Content-Type: image/jpeg                           |
|                                                     |
|  [Binary data of the image file]                    |
|  ------WebKitFormBoundary7MA4YWxkTrZu0gW--          |
|                                                     |
+----------------------------------------------------+
```

The boundary string separates each part. Spring Boot handles all of this parsing for you. You just need to use `MultipartFile`.

---

## 21.2 Configuring File Upload Limits

Before writing any code, configure the maximum file size in your application properties:

```properties
# src/main/resources/application.properties

# Maximum size of a single uploaded file (default is 1MB)
spring.servlet.multipart.max-file-size=10MB

# Maximum size of the entire request (all files combined)
spring.servlet.multipart.max-request-size=50MB

# Directory for storing uploaded files
file.upload-dir=uploads
```

**Line-by-line explanation:**

- `max-file-size=10MB` -- No single file can be larger than 10 megabytes. If someone tries to upload a 20MB file, Spring returns a 413 (Payload Too Large) error.
- `max-request-size=50MB` -- The total size of the entire request (if uploading multiple files) cannot exceed 50MB.
- `file.upload-dir=uploads` -- A custom property that tells our code where to save files. This is not a Spring property; we define it ourselves.

### Size Unit Reference

| Value | Size |
|-------|------|
| `1KB` | 1 Kilobyte |
| `1MB` | 1 Megabyte |
| `10MB` | 10 Megabytes |
| `1GB` | 1 Gigabyte |

---

## 21.3 Setting Up the File Storage Service

Let us create a service that handles saving and loading files:

```java
// src/main/java/com/example/fileupload/service/FileStorageService.java
package com.example.fileupload.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class FileStorageService {

    @Value("${file.upload-dir}")
    private String uploadDir;

    private Path uploadPath;

    @PostConstruct
    public void init() {
        uploadPath = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(uploadPath);
        } catch (IOException e) {
            throw new RuntimeException(
                "Could not create upload directory: " + uploadPath, e);
        }
    }

    public String storeFile(MultipartFile file) {
        // Get original filename
        String originalFilename = file.getOriginalFilename();

        // Generate unique filename to prevent overwriting
        String uniqueFilename = UUID.randomUUID().toString()
            + "_" + originalFilename;

        try {
            // Check for invalid path characters
            if (uniqueFilename.contains("..")) {
                throw new RuntimeException(
                    "Filename contains invalid path sequence: "
                    + uniqueFilename);
            }

            // Copy file to upload directory
            Path targetLocation = uploadPath.resolve(uniqueFilename);
            Files.copy(file.getInputStream(), targetLocation,
                StandardCopyOption.REPLACE_EXISTING);

            return uniqueFilename;

        } catch (IOException e) {
            throw new RuntimeException(
                "Could not store file " + uniqueFilename, e);
        }
    }

    public Path loadFile(String filename) {
        return uploadPath.resolve(filename).normalize();
    }
}
```

**Line-by-line explanation:**

- `@Value("${file.upload-dir}")` -- Reads the upload directory from application.properties.
- `@PostConstruct` -- This method runs after the bean is created. It creates the upload directory if it does not exist.
- `Files.createDirectories(uploadPath)` -- Creates the directory and any parent directories. Does nothing if the directory already exists.
- `UUID.randomUUID().toString()` -- Generates a unique identifier like "a1b2c3d4-e5f6-7890-abcd-ef1234567890". This prevents filename collisions when two users upload files with the same name.
- `uniqueFilename.contains("..")` -- This is a security check. The ".." sequence could be used for path traversal attacks (escaping the upload directory).
- `Files.copy(...)` -- Copies the uploaded file's input stream to the target location on disk.
- `StandardCopyOption.REPLACE_EXISTING` -- If a file with the same name exists (unlikely with UUID), replace it.

Here is the directory structure after a few uploads:

```
project/
  +-- uploads/
  |     +-- a1b2c3d4-..._beach.jpg
  |     +-- e5f6a7b8-..._resume.pdf
  |     +-- c9d0e1f2-..._report.xlsx
  +-- src/
  +-- pom.xml
```

---

## 21.4 The File Upload Controller

```java
// src/main/java/com/example/fileupload/controller/FileController.java
package com.example.fileupload.controller;

import com.example.fileupload.service.FileStorageService;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Path;
import java.util.Map;

@RestController
@RequestMapping("/api/files")
public class FileController {

    private final FileStorageService fileStorageService;

    public FileController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> uploadFile(
            @RequestParam("file") MultipartFile file) {

        // Check if file is empty
        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(
                Map.of("error", "Please select a file to upload"));
        }

        String filename = fileStorageService.storeFile(file);

        return ResponseEntity.ok(Map.of(
            "message", "File uploaded successfully",
            "filename", filename,
            "size", file.getSize() + " bytes",
            "contentType", file.getContentType()
        ));
    }
}
```

**Line-by-line explanation:**

- `@RequestParam("file") MultipartFile file` -- Spring automatically parses the multipart request and gives you a `MultipartFile` object. The parameter name "file" must match the form field name.
- `file.isEmpty()` -- Returns true if no file was selected. Always check this.
- `file.getSize()` -- Returns the file size in bytes.
- `file.getContentType()` -- Returns the MIME type (like "image/jpeg" or "application/pdf").

### What MultipartFile Offers

| Method | Returns | Example |
|--------|---------|---------|
| `getOriginalFilename()` | Original filename | `"beach.jpg"` |
| `getContentType()` | MIME type | `"image/jpeg"` |
| `getSize()` | Size in bytes | `1048576` |
| `getBytes()` | File content as byte array | `[binary data]` |
| `getInputStream()` | Stream for reading | `InputStream` |
| `isEmpty()` | True if no file | `false` |
| `transferTo(File dest)` | Save to a File object | void |

---

## 21.5 Testing File Upload with curl

```bash
# Upload a single file
curl -X POST http://localhost:8080/api/files/upload \
  -F "file=@/path/to/photo.jpg"
```

**Output:**

```json
{
    "message": "File uploaded successfully",
    "filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890_photo.jpg",
    "size": "245678 bytes",
    "contentType": "image/jpeg"
}
```

The `-F` flag tells curl to use multipart/form-data. The `@` symbol means "read the content from this file."

---

## 21.6 File Type Validation

Never trust file uploads blindly. An attacker could upload a `.exe` file renamed to `.jpg`. You need to validate both the file extension and the content type:

```java
// src/main/java/com/example/fileupload/service/FileValidationService.java
package com.example.fileupload.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.Set;

@Service
public class FileValidationService {

    private static final Set<String> ALLOWED_CONTENT_TYPES = Set.of(
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument" +
            ".spreadsheetml.sheet"  // .xlsx
    );

    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(
        "jpg", "jpeg", "png", "gif", "pdf", "txt", "xlsx"
    );

    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

    public void validate(MultipartFile file) {
        // Check file size
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new RuntimeException(
                "File size exceeds maximum limit of 10MB. " +
                "Actual size: " + file.getSize() + " bytes");
        }

        // Check content type
        String contentType = file.getContentType();
        if (contentType == null
                || !ALLOWED_CONTENT_TYPES.contains(contentType)) {
            throw new RuntimeException(
                "File type not allowed: " + contentType +
                ". Allowed types: " + ALLOWED_CONTENT_TYPES);
        }

        // Check file extension
        String filename = file.getOriginalFilename();
        if (filename != null) {
            String extension = getFileExtension(filename).toLowerCase();
            if (!ALLOWED_EXTENSIONS.contains(extension)) {
                throw new RuntimeException(
                    "File extension not allowed: ." + extension +
                    ". Allowed extensions: " + ALLOWED_EXTENSIONS);
            }
        }
    }

    private String getFileExtension(String filename) {
        int dotIndex = filename.lastIndexOf('.');
        if (dotIndex < 0) {
            return "";
        }
        return filename.substring(dotIndex + 1);
    }
}
```

**Line-by-line explanation:**

- `ALLOWED_CONTENT_TYPES` -- A whitelist of accepted MIME types. Anything not on this list is rejected.
- `ALLOWED_EXTENSIONS` -- A whitelist of accepted file extensions. We check both because content type alone can be spoofed.
- `getFileExtension()` -- Extracts the extension from the filename. "photo.jpg" returns "jpg".
- We validate three things: size, content type, and extension. This defense-in-depth approach makes it harder for attackers to bypass validation.

Now update the controller to use validation:

```java
@PostMapping("/upload")
public ResponseEntity<Map<String, String>> uploadFile(
        @RequestParam("file") MultipartFile file) {

    if (file.isEmpty()) {
        return ResponseEntity.badRequest().body(
            Map.of("error", "Please select a file to upload"));
    }

    // Validate the file before storing
    fileValidationService.validate(file);

    String filename = fileStorageService.storeFile(file);

    return ResponseEntity.ok(Map.of(
        "message", "File uploaded successfully",
        "filename", filename,
        "size", file.getSize() + " bytes",
        "contentType", file.getContentType()
    ));
}
```

```
+---------------------------------------------------+
|           FILE UPLOAD VALIDATION FLOW              |
+---------------------------------------------------+
|                                                    |
|  File received                                     |
|       |                                            |
|       v                                            |
|  [Is file empty?]                                  |
|       |                                            |
|       +--> Yes --> 400 Bad Request                 |
|       |                                            |
|       +--> No --> Continue                         |
|       |                                            |
|       v                                            |
|  [Size <= 10MB?]                                   |
|       |                                            |
|       +--> No --> "File too large"                 |
|       |                                            |
|       +--> Yes --> Continue                        |
|       |                                            |
|       v                                            |
|  [Content type allowed?]                           |
|       |                                            |
|       +--> No --> "File type not allowed"          |
|       |                                            |
|       +--> Yes --> Continue                        |
|       |                                            |
|       v                                            |
|  [Extension allowed?]                              |
|       |                                            |
|       +--> No --> "Extension not allowed"          |
|       |                                            |
|       +--> Yes --> Save file to disk               |
|                                                    |
+---------------------------------------------------+
```

---

## 21.7 File Download

Now let us add a download endpoint. The key is setting the right HTTP headers so the browser knows how to handle the file:

```java
// Add to FileController.java

@GetMapping("/download/{filename:.+}")
public ResponseEntity<Resource> downloadFile(
        @PathVariable String filename) {

    try {
        Path filePath = fileStorageService.loadFile(filename);
        Resource resource = new UrlResource(filePath.toUri());

        if (!resource.exists()) {
            return ResponseEntity.notFound().build();
        }

        // Determine content type
        String contentType = Files.probeContentType(filePath);
        if (contentType == null) {
            contentType = "application/octet-stream";
        }

        return ResponseEntity.ok()
            .contentType(MediaType.parseMediaType(contentType))
            .header(HttpHeaders.CONTENT_DISPOSITION,
                "attachment; filename=\"" +
                resource.getFilename() + "\"")
            .body(resource);

    } catch (MalformedURLException e) {
        return ResponseEntity.badRequest().build();
    } catch (IOException e) {
        return ResponseEntity.internalServerError().build();
    }
}
```

**Line-by-line explanation:**

- `@GetMapping("/download/{filename:.+}")` -- The `:.+` regex pattern tells Spring not to truncate the filename at the dot. Without it, "photo.jpg" would be interpreted as path variable "photo" with format "jpg".
- `new UrlResource(filePath.toUri())` -- Wraps the file path as a Spring Resource object that can be returned as a response body.
- `Files.probeContentType(filePath)` -- Determines the MIME type from the file extension. Returns "image/jpeg" for .jpg files, "application/pdf" for .pdf files, etc.
- `"application/octet-stream"` -- A fallback MIME type that means "unknown binary data." The browser will download it rather than trying to display it.
- `Content-Disposition: attachment` -- This header tells the browser to download the file instead of displaying it in the browser window.

### Inline vs Attachment

```java
// Force download (save dialog appears)
.header(HttpHeaders.CONTENT_DISPOSITION,
    "attachment; filename=\"photo.jpg\"")

// Display in browser (for images and PDFs)
.header(HttpHeaders.CONTENT_DISPOSITION,
    "inline; filename=\"photo.jpg\"")
```

Use `attachment` when you want the user to save the file. Use `inline` when you want the browser to display it (for images, PDFs, and text files).

### Testing Download

```bash
# Download a file
curl -O http://localhost:8080/api/files/download/a1b2c3d4_photo.jpg
```

The `-O` flag tells curl to save the file with its original name.

---

## 21.8 Multiple File Upload

Users often need to upload multiple files at once. Spring Boot supports this easily:

```java
// Add to FileController.java

@PostMapping("/upload-multiple")
public ResponseEntity<Map<String, Object>> uploadMultipleFiles(
        @RequestParam("files") MultipartFile[] files) {

    if (files.length == 0) {
        return ResponseEntity.badRequest().body(
            Map.of("error", "Please select files to upload"));
    }

    List<Map<String, String>> uploadedFiles = new ArrayList<>();

    for (MultipartFile file : files) {
        if (!file.isEmpty()) {
            fileValidationService.validate(file);
            String filename = fileStorageService.storeFile(file);

            uploadedFiles.add(Map.of(
                "originalName", file.getOriginalFilename(),
                "storedName", filename,
                "size", file.getSize() + " bytes",
                "contentType", file.getContentType()
            ));
        }
    }

    return ResponseEntity.ok(Map.of(
        "message", uploadedFiles.size() + " files uploaded successfully",
        "files", uploadedFiles
    ));
}
```

**Line-by-line explanation:**

- `MultipartFile[] files` -- Instead of a single `MultipartFile`, we accept an array. Spring parses all files from the request.
- `for (MultipartFile file : files)` -- Loop through each file and process it individually.
- Each file is validated and stored separately, and we collect the results.

### Testing Multiple Upload

```bash
# Upload multiple files
curl -X POST http://localhost:8080/api/files/upload-multiple \
  -F "files=@photo1.jpg" \
  -F "files=@photo2.jpg" \
  -F "files=@document.pdf"
```

**Output:**

```json
{
    "message": "3 files uploaded successfully",
    "files": [
        {
            "originalName": "photo1.jpg",
            "storedName": "a1b2c3d4-..._photo1.jpg",
            "size": "245678 bytes",
            "contentType": "image/jpeg"
        },
        {
            "originalName": "photo2.jpg",
            "storedName": "e5f6a7b8-..._photo2.jpg",
            "size": "189432 bytes",
            "contentType": "image/jpeg"
        },
        {
            "originalName": "document.pdf",
            "storedName": "c9d0e1f2-..._document.pdf",
            "size": "1024567 bytes",
            "contentType": "application/pdf"
        }
    ]
}
```

---

## 21.9 Uploading a File with Additional Data

Sometimes you need to upload a file along with additional form data, like a description or category:

```java
@PostMapping("/upload-with-data")
public ResponseEntity<Map<String, String>> uploadWithData(
        @RequestParam("file") MultipartFile file,
        @RequestParam("description") String description,
        @RequestParam(value = "category",
            defaultValue = "general") String category) {

    if (file.isEmpty()) {
        return ResponseEntity.badRequest().body(
            Map.of("error", "Please select a file"));
    }

    fileValidationService.validate(file);
    String filename = fileStorageService.storeFile(file);

    // In a real app, save metadata to database
    return ResponseEntity.ok(Map.of(
        "message", "File uploaded successfully",
        "filename", filename,
        "description", description,
        "category", category
    ));
}
```

### Testing with Additional Data

```bash
curl -X POST http://localhost:8080/api/files/upload-with-data \
  -F "file=@photo.jpg" \
  -F "description=My vacation photo" \
  -F "category=travel"
```

**Output:**

```json
{
    "message": "File uploaded successfully",
    "filename": "a1b2c3d4-..._photo.jpg",
    "description": "My vacation photo",
    "category": "travel"
}
```

---

## 21.10 Listing Uploaded Files

Let us add an endpoint to list all uploaded files:

```java
// Add to FileStorageService.java

public List<String> listAllFiles() {
    try {
        return Files.list(uploadPath)
            .map(path -> path.getFileName().toString())
            .toList();
    } catch (IOException e) {
        throw new RuntimeException(
            "Could not list files in " + uploadPath, e);
    }
}
```

```java
// Add to FileController.java

@GetMapping("/list")
public ResponseEntity<Map<String, Object>> listFiles() {
    List<String> files = fileStorageService.listAllFiles();

    return ResponseEntity.ok(Map.of(
        "totalFiles", files.size(),
        "files", files
    ));
}
```

```bash
curl http://localhost:8080/api/files/list
```

**Output:**

```json
{
    "totalFiles": 3,
    "files": [
        "a1b2c3d4-..._photo1.jpg",
        "e5f6a7b8-..._photo2.jpg",
        "c9d0e1f2-..._document.pdf"
    ]
}
```

---

## 21.11 Exception Handling for File Operations

Add a global exception handler for file-related errors:

```java
// src/main/java/com/example/fileupload/exception/FileExceptionHandler.java
package com.example.fileupload.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import java.util.Map;

@RestControllerAdvice
public class FileExceptionHandler {

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<Map<String, String>> handleMaxSizeException(
            MaxUploadSizeExceededException e) {

        return ResponseEntity
            .status(HttpStatus.PAYLOAD_TOO_LARGE)
            .body(Map.of(
                "error", "File too large",
                "message", "Maximum upload size exceeded. " +
                    "The limit is 10MB per file."
            ));
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<Map<String, String>> handleRuntimeException(
            RuntimeException e) {

        return ResponseEntity
            .status(HttpStatus.BAD_REQUEST)
            .body(Map.of(
                "error", "File operation failed",
                "message", e.getMessage()
            ));
    }
}
```

**Line-by-line explanation:**

- `MaxUploadSizeExceededException` -- Spring throws this when a file exceeds the configured `max-file-size` or `max-request-size`.
- `HttpStatus.PAYLOAD_TOO_LARGE` -- Returns HTTP status 413, which is the standard code for "payload too large."

Now when a user tries to upload a file that is too large:

```bash
curl -X POST http://localhost:8080/api/files/upload \
  -F "file=@large-video.mp4"
```

**Output:**

```json
{
    "error": "File too large",
    "message": "Maximum upload size exceeded. The limit is 10MB per file."
}
```

---

## 21.12 Complete File Controller

Here is the complete controller with all endpoints together:

```java
// src/main/java/com/example/fileupload/controller/FileController.java
package com.example.fileupload.controller;

import com.example.fileupload.service.FileStorageService;
import com.example.fileupload.service.FileValidationService;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/files")
public class FileController {

    private final FileStorageService fileStorageService;
    private final FileValidationService fileValidationService;

    public FileController(FileStorageService fileStorageService,
                          FileValidationService fileValidationService) {
        this.fileStorageService = fileStorageService;
        this.fileValidationService = fileValidationService;
    }

    @PostMapping("/upload")
    public ResponseEntity<Map<String, String>> uploadFile(
            @RequestParam("file") MultipartFile file) {

        if (file.isEmpty()) {
            return ResponseEntity.badRequest().body(
                Map.of("error", "Please select a file to upload"));
        }

        fileValidationService.validate(file);
        String filename = fileStorageService.storeFile(file);

        return ResponseEntity.ok(Map.of(
            "message", "File uploaded successfully",
            "filename", filename,
            "size", file.getSize() + " bytes",
            "contentType", file.getContentType()
        ));
    }

    @PostMapping("/upload-multiple")
    public ResponseEntity<Map<String, Object>> uploadMultipleFiles(
            @RequestParam("files") MultipartFile[] files) {

        List<Map<String, String>> uploadedFiles = new ArrayList<>();

        for (MultipartFile file : files) {
            if (!file.isEmpty()) {
                fileValidationService.validate(file);
                String filename = fileStorageService.storeFile(file);
                uploadedFiles.add(Map.of(
                    "originalName", file.getOriginalFilename(),
                    "storedName", filename
                ));
            }
        }

        return ResponseEntity.ok(Map.of(
            "message", uploadedFiles.size()
                + " files uploaded successfully",
            "files", uploadedFiles
        ));
    }

    @GetMapping("/download/{filename:.+}")
    public ResponseEntity<Resource> downloadFile(
            @PathVariable String filename) {

        try {
            Path filePath = fileStorageService.loadFile(filename);
            Resource resource = new UrlResource(filePath.toUri());

            if (!resource.exists()) {
                return ResponseEntity.notFound().build();
            }

            String contentType = Files.probeContentType(filePath);
            if (contentType == null) {
                contentType = "application/octet-stream";
            }

            return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .header(HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=\""
                    + resource.getFilename() + "\"")
                .body(resource);

        } catch (MalformedURLException e) {
            return ResponseEntity.badRequest().build();
        } catch (IOException e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    @GetMapping("/list")
    public ResponseEntity<Map<String, Object>> listFiles() {
        List<String> files = fileStorageService.listAllFiles();
        return ResponseEntity.ok(Map.of(
            "totalFiles", files.size(),
            "files", files
        ));
    }
}
```

---

## Common Mistakes

1. **Not setting file size limits.** The default limit is only 1MB. If you expect larger files, increase `max-file-size` and `max-request-size` in application.properties.

2. **Using the original filename directly.** Two users could upload files with the same name, overwriting each other. Always generate unique filenames using UUID or timestamps.

3. **Not validating file types.** Never trust the file extension alone. Check both the content type and the extension. Even better, read the file's magic bytes to verify the actual content.

4. **Storing files inside the application JAR.** Files should be stored outside the application directory. When you redeploy, the JAR is replaced and all files inside it are lost.

5. **Not handling the `..` path traversal.** An attacker could send a filename like `../../etc/passwd` to read or write files outside the upload directory. Always sanitize filenames and check for `..` sequences.

6. **Forgetting to create the upload directory.** If the directory does not exist, file writes will fail. Use `@PostConstruct` to create it when the application starts.

---

## Best Practices

1. **Always validate file type, size, and extension.** Use a whitelist approach: only allow specific types rather than blocking specific types.

2. **Generate unique filenames with UUID.** This prevents filename collisions and makes filenames unpredictable (attackers cannot guess them).

3. **Store files outside the application directory.** Use a configurable path from application.properties. In production, consider using cloud storage (like AWS S3).

4. **Set appropriate size limits.** Think about what your users actually need. Profile pictures do not need to be 100MB.

5. **Return file metadata after upload.** Tell the user the stored filename, size, and content type so they can reference it later.

6. **Handle errors gracefully.** Return clear error messages for oversized files, invalid types, and storage failures.

---

## Quick Summary

File upload in Spring Boot uses MultipartFile to receive files sent as multipart/form-data. You configure size limits with spring.servlet.multipart.max-file-size and max-request-size in application.properties. Files should be saved to disk with unique filenames (using UUID) to prevent collisions and path traversal attacks. Always validate files by checking the content type, file extension, and size against a whitelist of allowed values. For downloads, use Spring's Resource interface with Content-Disposition headers to control whether the browser downloads or displays the file. Multiple file upload works by accepting a MultipartFile array instead of a single MultipartFile.

---

## Key Points

- MultipartFile is Spring's abstraction for uploaded files.
- Configure max-file-size and max-request-size in application.properties.
- Always generate unique filenames with UUID to prevent overwriting.
- Validate content type and file extension using a whitelist approach.
- Check for ".." in filenames to prevent path traversal attacks.
- Use Content-Disposition: attachment for downloads, inline for display.
- The `{filename:.+}` path variable pattern preserves the file extension.
- Use @PostConstruct to create the upload directory on startup.
- Handle MaxUploadSizeExceededException for files that exceed limits.

---

## Practice Questions

1. What is the difference between `multipart/form-data` and `application/x-www-form-urlencoded`, and when do you use each?

2. Why should you generate unique filenames instead of using the original filename from the upload?

3. What is a path traversal attack, and how does checking for ".." in filenames prevent it?

4. What is the difference between `Content-Disposition: attachment` and `Content-Disposition: inline`?

5. Why should you validate both the content type and the file extension, rather than just one of them?

---

## Exercises

### Exercise 1: Image-Only Upload

Create a file upload endpoint that only accepts image files (JPEG, PNG, GIF). Return a 400 Bad Request with a clear error message if a non-image file is uploaded. Test with both valid images and invalid files like PDFs.

### Exercise 2: File Metadata Database

Extend the file upload system to save file metadata (original name, stored name, upload date, file size, content type) to an H2 database using JPA. Create an endpoint to search uploaded files by content type or date range.

### Exercise 3: Delete Endpoint

Add a DELETE endpoint at `/api/files/{filename}` that deletes both the file from disk and its metadata from the database. Handle the case where the file does not exist gracefully.

---

## What Is Next?

You can now handle file uploads and downloads in your Spring Boot application. But how do you know what is happening inside your application when something goes wrong? How do you track down a bug in production? In Chapter 22, you will learn about logging. You will use SLF4J and Logback to record what your application does, configure log levels, write logs to files, and use MDC to trace requests across multiple components.
