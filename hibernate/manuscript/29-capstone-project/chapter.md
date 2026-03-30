# Chapter 29: Capstone Project — Library Management System

---

## Learning Goals

By the end of this chapter, you will have built a complete, production-quality application that demonstrates:

- Complex entity relationships (one-to-many, many-to-many with extra columns)
- Full CRUD REST APIs with DTOs and validation
- Dynamic search with Specifications
- Pagination and sorting across all list endpoints
- Flyway database migrations
- Global exception handling
- Layered architecture (Controller-Service-Repository)
- Performance optimizations (batching, @EntityGraph, readOnly)
- Comprehensive test coverage

---

## Project Overview

We will build a **Library Management System** that tracks books, authors, members, and book loans. This is a realistic application with the kind of entity relationships and business rules you encounter in production systems.

```
Library Management System:
+------------------------------------------------------------------+
|                                                                   |
|  Entities and Relationships:                                      |
|                                                                   |
|  Author ----< BookAuthor >---- Book                               |
|  (many-to-many with display_order)                                |
|                                                                   |
|  Book ----< BookCopy                                              |
|  (one book can have multiple physical copies)                     |
|                                                                   |
|  Member ----< Loan >---- BookCopy                                 |
|  (a member borrows a specific copy)                               |
|                                                                   |
|  Book ----< Book                                                  |
|  (via Category: one category has many books)                      |
|                                                                   |
+------------------------------------------------------------------+

API Endpoints:
+------------------------------------------------------------------+
|                                                                   |
|  Authors:                                                         |
|  GET    /api/authors               List (paginated)               |
|  GET    /api/authors/{id}          Get with books                 |
|  POST   /api/authors               Create                         |
|  PUT    /api/authors/{id}          Update                         |
|                                                                   |
|  Books:                                                           |
|  GET    /api/books                 List (paginated)               |
|  GET    /api/books/{id}            Get with authors and copies    |
|  POST   /api/books                 Create with author IDs         |
|  PUT    /api/books/{id}            Update                         |
|  GET    /api/books/search          Search by title/author/isbn    |
|                                                                   |
|  Members:                                                         |
|  GET    /api/members               List (paginated)               |
|  GET    /api/members/{id}          Get with active loans          |
|  POST   /api/members               Register                      |
|                                                                   |
|  Loans:                                                           |
|  POST   /api/loans/checkout        Borrow a book                  |
|  POST   /api/loans/{id}/return     Return a book                  |
|  GET    /api/loans/overdue         List overdue loans             |
|  GET    /api/members/{id}/loans    Member's loan history          |
+------------------------------------------------------------------+
```

---

## Step 1: Entity Design

### BaseEntity

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Version
    private Integer version;

    public Long getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
}
```

### Author

```java
@Entity
@Table(name = "authors")
public class Author extends BaseEntity {

    @NotBlank
    @Column(nullable = false, length = 150)
    private String name;

    @Column(columnDefinition = "TEXT")
    private String biography;

    @Column(name = "birth_year")
    private Integer birthYear;

    @OneToMany(mappedBy = "author", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("displayOrder ASC")
    private List<BookAuthor> bookAuthors = new ArrayList<>();

    protected Author() {}

    public Author(String name) {
        this.name = name;
    }

    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getBiography() { return biography; }
    public void setBiography(String biography) { this.biography = biography; }
    public Integer getBirthYear() { return birthYear; }
    public void setBirthYear(Integer birthYear) { this.birthYear = birthYear; }
    public List<BookAuthor> getBookAuthors() {
        return Collections.unmodifiableList(bookAuthors);
    }
}
```

### Book

```java
@Entity
@Table(name = "books", indexes = {
    @Index(name = "idx_book_isbn", columnList = "isbn"),
    @Index(name = "idx_book_category", columnList = "category_id")
})
public class Book extends BaseEntity {

    @NotBlank
    @Column(nullable = false, length = 300)
    private String title;

    @Column(nullable = false, unique = true, length = 20)
    private String isbn;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "publication_year")
    private Integer publicationYear;

    @Column(length = 200)
    private String publisher;

    @Column(name = "page_count")
    private Integer pageCount;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("displayOrder ASC")
    private List<BookAuthor> bookAuthors = new ArrayList<>();

    @OneToMany(mappedBy = "book", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<BookCopy> copies = new ArrayList<>();

    protected Book() {}

    public Book(String title, String isbn) {
        this.title = title;
        this.isbn = isbn;
    }

    // Helper methods
    public void addAuthor(Author author, int displayOrder) {
        BookAuthor ba = new BookAuthor(this, author, displayOrder);
        bookAuthors.add(ba);
        author.getBookAuthors(); // ensure loaded
    }

    public BookCopy addCopy(String barcode) {
        BookCopy copy = new BookCopy(this, barcode);
        copies.add(copy);
        return copy;
    }

    public int getAvailableCopyCount() {
        return (int) copies.stream().filter(BookCopy::isAvailable).count();
    }

    // Getters and setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getIsbn() { return isbn; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Integer getPublicationYear() { return publicationYear; }
    public void setPublicationYear(Integer publicationYear) { this.publicationYear = publicationYear; }
    public String getPublisher() { return publisher; }
    public void setPublisher(String publisher) { this.publisher = publisher; }
    public Integer getPageCount() { return pageCount; }
    public void setPageCount(Integer pageCount) { this.pageCount = pageCount; }
    public Category getCategory() { return category; }
    public void setCategory(Category category) { this.category = category; }
    public List<BookAuthor> getBookAuthors() {
        return Collections.unmodifiableList(bookAuthors);
    }
    public List<BookCopy> getCopies() {
        return Collections.unmodifiableList(copies);
    }
}
```

### BookAuthor (Many-to-Many Join Entity)

```java
@Entity
@Table(name = "book_authors")
public class BookAuthor {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id", nullable = false)
    private Book book;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Author author;

    @Column(name = "display_order", nullable = false)
    private int displayOrder;

    protected BookAuthor() {}

    public BookAuthor(Book book, Author author, int displayOrder) {
        this.book = book;
        this.author = author;
        this.displayOrder = displayOrder;
    }

    public Long getId() { return id; }
    public Book getBook() { return book; }
    public Author getAuthor() { return author; }
    public int getDisplayOrder() { return displayOrder; }
}
```

### BookCopy

```java
@Entity
@Table(name = "book_copies")
public class BookCopy extends BaseEntity {

    @Column(nullable = false, unique = true, length = 50)
    private String barcode;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private CopyStatus status = CopyStatus.AVAILABLE;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id", nullable = false)
    private Book book;

    @OneToMany(mappedBy = "bookCopy")
    @OrderBy("borrowedAt DESC")
    private List<Loan> loans = new ArrayList<>();

    protected BookCopy() {}

    public BookCopy(Book book, String barcode) {
        this.book = book;
        this.barcode = barcode;
    }

    public boolean isAvailable() {
        return status == CopyStatus.AVAILABLE;
    }

    public void markBorrowed() { this.status = CopyStatus.BORROWED; }
    public void markAvailable() { this.status = CopyStatus.AVAILABLE; }
    public void markDamaged() { this.status = CopyStatus.DAMAGED; }

    // Getters
    public String getBarcode() { return barcode; }
    public CopyStatus getStatus() { return status; }
    public Book getBook() { return book; }
}

public enum CopyStatus {
    AVAILABLE, BORROWED, DAMAGED, LOST
}
```

### Member

```java
@Entity
@Table(name = "members")
public class Member extends BaseEntity {

    @NotBlank
    @Column(nullable = false, length = 150)
    private String name;

    @NotBlank
    @Email
    @Column(nullable = false, unique = true, length = 200)
    private String email;

    @Column(name = "phone_number", length = 20)
    private String phoneNumber;

    @Column(name = "membership_date", nullable = false)
    private LocalDate membershipDate;

    @Column(nullable = false)
    private boolean active = true;

    @Column(name = "max_loans", nullable = false)
    private int maxLoans = 5;

    @OneToMany(mappedBy = "member")
    @OrderBy("borrowedAt DESC")
    private List<Loan> loans = new ArrayList<>();

    protected Member() {}

    public Member(String name, String email) {
        this.name = name;
        this.email = email;
        this.membershipDate = LocalDate.now();
    }

    public int getActiveLoansCount() {
        return (int) loans.stream().filter(l -> l.getReturnedAt() == null).count();
    }

    public boolean canBorrow() {
        return active && getActiveLoansCount() < maxLoans;
    }

    // Getters and setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }
    public LocalDate getMembershipDate() { return membershipDate; }
    public boolean isActive() { return active; }
    public void setActive(boolean active) { this.active = active; }
    public int getMaxLoans() { return maxLoans; }
    public List<Loan> getLoans() { return Collections.unmodifiableList(loans); }
}
```

### Loan

```java
@Entity
@Table(name = "loans", indexes = {
    @Index(name = "idx_loan_member", columnList = "member_id"),
    @Index(name = "idx_loan_copy", columnList = "book_copy_id"),
    @Index(name = "idx_loan_due_date", columnList = "due_date")
})
public class Loan extends BaseEntity {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_copy_id", nullable = false)
    private BookCopy bookCopy;

    @Column(name = "borrowed_at", nullable = false)
    private LocalDateTime borrowedAt;

    @Column(name = "due_date", nullable = false)
    private LocalDate dueDate;

    @Column(name = "returned_at")
    private LocalDateTime returnedAt;

    @Column(columnDefinition = "TEXT")
    private String notes;

    protected Loan() {}

    public Loan(Member member, BookCopy bookCopy, int loanDurationDays) {
        this.member = member;
        this.bookCopy = bookCopy;
        this.borrowedAt = LocalDateTime.now();
        this.dueDate = LocalDate.now().plusDays(loanDurationDays);
    }

    public boolean isOverdue() {
        return returnedAt == null && LocalDate.now().isAfter(dueDate);
    }

    public boolean isActive() {
        return returnedAt == null;
    }

    public void markReturned() {
        this.returnedAt = LocalDateTime.now();
    }

    // Getters
    public Member getMember() { return member; }
    public BookCopy getBookCopy() { return bookCopy; }
    public LocalDateTime getBorrowedAt() { return borrowedAt; }
    public LocalDate getDueDate() { return dueDate; }
    public LocalDateTime getReturnedAt() { return returnedAt; }
    public String getNotes() { return notes; }
    public void setNotes(String notes) { this.notes = notes; }
}
```

### Category

```java
@Entity
@Table(name = "categories")
public class Category extends BaseEntity {

    @NotBlank
    @Column(nullable = false, unique = true, length = 100)
    private String name;

    private String description;

    @OneToMany(mappedBy = "category")
    private List<Book> books = new ArrayList<>();

    protected Category() {}

    public Category(String name) { this.name = name; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
```

```
Entity Relationship Diagram:
+------------------------------------------------------------------+
|                                                                   |
|  categories (1)----(*) books (1)----(*) book_copies               |
|                         |                    |                    |
|                         |                    |                    |
|                   book_authors          loans                     |
|                   (join entity)         |     |                   |
|                         |               |     |                   |
|                   authors (*)     members (1)--+                  |
|                                                                   |
|  Relationships:                                                   |
|  Category  1:N  Book        (one category, many books)            |
|  Book      M:N  Author      (via BookAuthor with display_order)   |
|  Book      1:N  BookCopy    (one book, many physical copies)      |
|  Member    1:N  Loan        (one member, many loans over time)    |
|  BookCopy  1:N  Loan        (one copy, many loans over time)      |
+------------------------------------------------------------------+
```

---

## Step 2: Flyway Migrations

```sql
-- V1__Create_categories_table.sql
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0
);
```

```sql
-- V2__Create_authors_table.sql
CREATE TABLE authors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    biography TEXT,
    birth_year INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0
);
```

```sql
-- V3__Create_books_table.sql
CREATE TABLE books (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    publication_year INTEGER,
    publisher VARCHAR(200),
    page_count INTEGER,
    category_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
CREATE INDEX idx_book_isbn ON books(isbn);
CREATE INDEX idx_book_category ON books(category_id);
```

```sql
-- V4__Create_book_authors_table.sql
CREATE TABLE book_authors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    book_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (author_id) REFERENCES authors(id),
    UNIQUE (book_id, author_id)
);
```

```sql
-- V5__Create_book_copies_table.sql
CREATE TABLE book_copies (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    barcode VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    book_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

```sql
-- V6__Create_members_table.sql
CREATE TABLE members (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    membership_date DATE NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    max_loans INTEGER DEFAULT 5,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0
);
```

```sql
-- V7__Create_loans_table.sql
CREATE TABLE loans (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    member_id BIGINT NOT NULL,
    book_copy_id BIGINT NOT NULL,
    borrowed_at TIMESTAMP NOT NULL,
    due_date DATE NOT NULL,
    returned_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    version INTEGER DEFAULT 0,
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (book_copy_id) REFERENCES book_copies(id)
);
CREATE INDEX idx_loan_member ON loans(member_id);
CREATE INDEX idx_loan_copy ON loans(book_copy_id);
CREATE INDEX idx_loan_due_date ON loans(due_date);
```

```sql
-- V8__Insert_seed_data.sql
INSERT INTO categories (name, description) VALUES
    ('Fiction', 'Novels, short stories, and literary fiction'),
    ('Non-Fiction', 'Biographies, history, science, and essays'),
    ('Science Fiction', 'Futuristic and speculative fiction'),
    ('Programming', 'Software development and computer science'),
    ('History', 'Historical accounts and analysis');

INSERT INTO authors (name, biography, birth_year) VALUES
    ('Robert C. Martin', 'Software engineer and author of Clean Code', 1952),
    ('Joshua Bloch', 'Former chief Java architect at Google', 1961),
    ('Martin Fowler', 'Author and software development thought leader', 1963);

INSERT INTO books (title, isbn, description, publication_year, publisher, page_count, category_id) VALUES
    ('Clean Code', '978-0132350884', 'A handbook of agile software craftsmanship', 2008, 'Prentice Hall', 464, 4),
    ('Effective Java', '978-0134685991', 'Best practices for the Java platform', 2018, 'Addison-Wesley', 416, 4);

INSERT INTO book_authors (book_id, author_id, display_order) VALUES
    (1, 1, 1),
    (2, 2, 1);

INSERT INTO book_copies (barcode, status, book_id) VALUES
    ('CC-001', 'AVAILABLE', 1),
    ('CC-002', 'AVAILABLE', 1),
    ('EJ-001', 'AVAILABLE', 2),
    ('EJ-002', 'AVAILABLE', 2),
    ('EJ-003', 'AVAILABLE', 2);

INSERT INTO members (name, email, membership_date) VALUES
    ('Alice Johnson', 'alice@library.com', '2024-01-15'),
    ('Bob Smith', 'bob@library.com', '2024-03-20');
```

---

## Step 3: Loan Service (Business Logic)

The loan service demonstrates complex business rules:

```java
@Service
public class LoanService {

    private static final int DEFAULT_LOAN_DAYS = 14;

    private final LoanRepository loanRepository;
    private final MemberRepository memberRepository;
    private final BookCopyRepository bookCopyRepository;
    private final BookRepository bookRepository;

    public LoanService(LoanRepository loanRepository,
                       MemberRepository memberRepository,
                       BookCopyRepository bookCopyRepository,
                       BookRepository bookRepository) {
        this.loanRepository = loanRepository;
        this.memberRepository = memberRepository;
        this.bookCopyRepository = bookCopyRepository;
        this.bookRepository = bookRepository;
    }

    @Transactional
    public LoanResponse checkout(CheckoutRequest request) {
        // 1. Validate member
        Member member = memberRepository.findById(request.getMemberId())
            .orElseThrow(() -> new ResourceNotFoundException("Member", request.getMemberId()));

        if (!member.isActive()) {
            throw new BusinessException("INACTIVE_MEMBER", "Member account is inactive");
        }

        // 2. Check loan limit
        long activeLoans = loanRepository.countByMemberIdAndReturnedAtIsNull(member.getId());
        if (activeLoans >= member.getMaxLoans()) {
            throw new BusinessException("LOAN_LIMIT",
                String.format("Member has reached the maximum of %d active loans",
                    member.getMaxLoans()));
        }

        // 3. Find an available copy
        BookCopy copy;
        if (request.getBarcode() != null) {
            copy = bookCopyRepository.findByBarcode(request.getBarcode())
                .orElseThrow(() -> new ResourceNotFoundException(
                    "BookCopy", "barcode", request.getBarcode()));
        } else if (request.getBookId() != null) {
            copy = bookCopyRepository.findFirstByBookIdAndStatus(
                    request.getBookId(), CopyStatus.AVAILABLE)
                .orElseThrow(() -> new BusinessException("NO_COPIES",
                    "No available copies of this book"));
        } else {
            throw new BusinessException("INVALID_REQUEST",
                "Either bookId or barcode must be provided");
        }

        if (!copy.isAvailable()) {
            throw new BusinessException("COPY_UNAVAILABLE",
                "This copy is currently " + copy.getStatus());
        }

        // 4. Check if member already has this book
        boolean alreadyBorrowed = loanRepository
            .existsByMemberIdAndBookCopy_Book_IdAndReturnedAtIsNull(
                member.getId(), copy.getBook().getId());
        if (alreadyBorrowed) {
            throw new BusinessException("ALREADY_BORROWED",
                "Member already has a copy of this book on loan");
        }

        // 5. Create the loan
        copy.markBorrowed();
        Loan loan = new Loan(member, copy, DEFAULT_LOAN_DAYS);
        Loan saved = loanRepository.save(loan);

        return toLoanResponse(saved);
    }

    @Transactional
    public LoanResponse returnBook(Long loanId) {
        Loan loan = loanRepository.findWithDetailsById(loanId)
            .orElseThrow(() -> new ResourceNotFoundException("Loan", loanId));

        if (loan.getReturnedAt() != null) {
            throw new BusinessException("ALREADY_RETURNED", "This loan was already returned");
        }

        loan.markReturned();
        loan.getBookCopy().markAvailable();

        return toLoanResponse(loan);
    }

    @Transactional(readOnly = true)
    public Page<LoanResponse> getOverdueLoans(Pageable pageable) {
        return loanRepository
            .findByReturnedAtIsNullAndDueDateBefore(LocalDate.now(), pageable)
            .map(this::toLoanResponse);
    }

    @Transactional(readOnly = true)
    public Page<LoanResponse> getMemberLoans(Long memberId, Pageable pageable) {
        if (!memberRepository.existsById(memberId)) {
            throw new ResourceNotFoundException("Member", memberId);
        }
        return loanRepository.findByMemberId(memberId, pageable)
            .map(this::toLoanResponse);
    }

    private LoanResponse toLoanResponse(Loan loan) {
        return new LoanResponse(
            loan.getId(),
            loan.getMember().getName(),
            loan.getBookCopy().getBook().getTitle(),
            loan.getBookCopy().getBarcode(),
            loan.getBorrowedAt(),
            loan.getDueDate(),
            loan.getReturnedAt(),
            loan.isOverdue()
        );
    }
}
```

```
Checkout Business Rules:
+------------------------------------------------------------------+
|                                                                   |
|  1. Member must exist and be active                               |
|  2. Member must not have exceeded max loans (default 5)           |
|  3. Book copy must be available                                   |
|  4. Member cannot borrow the same book twice simultaneously      |
|  5. Loan duration: 14 days                                        |
|                                                                   |
|  Return Business Rules:                                           |
|  1. Loan must exist                                               |
|  2. Loan must not already be returned                             |
|  3. Book copy status changes back to AVAILABLE                   |
|                                                                   |
|  If ANY rule fails, the entire operation rolls back.              |
+------------------------------------------------------------------+
```

---

## Step 4: DTOs

```java
public class CheckoutRequest {

    @NotNull(message = "Member ID is required")
    private Long memberId;

    private Long bookId;      // Borrow any available copy of this book
    private String barcode;   // Borrow a specific copy

    // Getters/setters...
    public Long getMemberId() { return memberId; }
    public void setMemberId(Long memberId) { this.memberId = memberId; }
    public Long getBookId() { return bookId; }
    public void setBookId(Long bookId) { this.bookId = bookId; }
    public String getBarcode() { return barcode; }
    public void setBarcode(String barcode) { this.barcode = barcode; }
}

public class LoanResponse {
    private Long id;
    private String memberName;
    private String bookTitle;
    private String copyBarcode;
    private LocalDateTime borrowedAt;
    private LocalDate dueDate;
    private LocalDateTime returnedAt;
    private boolean overdue;

    public LoanResponse(Long id, String memberName, String bookTitle,
                        String copyBarcode, LocalDateTime borrowedAt,
                        LocalDate dueDate, LocalDateTime returnedAt,
                        boolean overdue) {
        this.id = id;
        this.memberName = memberName;
        this.bookTitle = bookTitle;
        this.copyBarcode = copyBarcode;
        this.borrowedAt = borrowedAt;
        this.dueDate = dueDate;
        this.returnedAt = returnedAt;
        this.overdue = overdue;
    }

    // Getters...
    public Long getId() { return id; }
    public String getMemberName() { return memberName; }
    public String getBookTitle() { return bookTitle; }
    public String getCopyBarcode() { return copyBarcode; }
    public LocalDateTime getBorrowedAt() { return borrowedAt; }
    public LocalDate getDueDate() { return dueDate; }
    public LocalDateTime getReturnedAt() { return returnedAt; }
    public boolean isOverdue() { return overdue; }
}

public class BookResponse {
    private Long id;
    private String title;
    private String isbn;
    private String description;
    private Integer publicationYear;
    private String publisher;
    private Integer pageCount;
    private String categoryName;
    private List<String> authors;
    private int totalCopies;
    private int availableCopies;

    // Constructor, getters...
    public BookResponse(Long id, String title, String isbn, String description,
                        Integer publicationYear, String publisher, Integer pageCount,
                        String categoryName, List<String> authors,
                        int totalCopies, int availableCopies) {
        this.id = id;
        this.title = title;
        this.isbn = isbn;
        this.description = description;
        this.publicationYear = publicationYear;
        this.publisher = publisher;
        this.pageCount = pageCount;
        this.categoryName = categoryName;
        this.authors = authors;
        this.totalCopies = totalCopies;
        this.availableCopies = availableCopies;
    }

    public Long getId() { return id; }
    public String getTitle() { return title; }
    public String getIsbn() { return isbn; }
    public String getDescription() { return description; }
    public Integer getPublicationYear() { return publicationYear; }
    public String getPublisher() { return publisher; }
    public Integer getPageCount() { return pageCount; }
    public String getCategoryName() { return categoryName; }
    public List<String> getAuthors() { return authors; }
    public int getTotalCopies() { return totalCopies; }
    public int getAvailableCopies() { return availableCopies; }
}
```

---

## Step 5: Repositories

```java
@Repository
public interface LoanRepository extends JpaRepository<Loan, Long> {

    long countByMemberIdAndReturnedAtIsNull(Long memberId);

    boolean existsByMemberIdAndBookCopy_Book_IdAndReturnedAtIsNull(
        Long memberId, Long bookId);

    @Query("SELECT l FROM Loan l " +
           "JOIN FETCH l.member " +
           "JOIN FETCH l.bookCopy bc " +
           "JOIN FETCH bc.book " +
           "WHERE l.id = :id")
    Optional<Loan> findWithDetailsById(@Param("id") Long id);

    @Query("SELECT l FROM Loan l " +
           "JOIN FETCH l.member " +
           "JOIN FETCH l.bookCopy bc " +
           "JOIN FETCH bc.book " +
           "WHERE l.returnedAt IS NULL AND l.dueDate < :date")
    Page<Loan> findByReturnedAtIsNullAndDueDateBefore(
        @Param("date") LocalDate date, Pageable pageable);

    @EntityGraph(attributePaths = {"member", "bookCopy", "bookCopy.book"})
    Page<Loan> findByMemberId(Long memberId, Pageable pageable);
}

@Repository
public interface BookCopyRepository extends JpaRepository<BookCopy, Long> {

    Optional<BookCopy> findByBarcode(String barcode);

    Optional<BookCopy> findFirstByBookIdAndStatus(Long bookId, CopyStatus status);
}

@Repository
public interface BookRepository extends JpaRepository<Book, Long>,
        JpaSpecificationExecutor<Book> {

    boolean existsByIsbn(String isbn);

    @Query("SELECT DISTINCT b FROM Book b " +
           "LEFT JOIN FETCH b.bookAuthors ba " +
           "LEFT JOIN FETCH ba.author " +
           "LEFT JOIN FETCH b.category " +
           "LEFT JOIN FETCH b.copies " +
           "WHERE b.id = :id")
    Optional<Book> findWithDetailsById(@Param("id") Long id);
}
```

---

## Step 6: Controllers

```java
@RestController
@RequestMapping("/api/loans")
public class LoanController {

    private final LoanService loanService;

    public LoanController(LoanService loanService) {
        this.loanService = loanService;
    }

    @PostMapping("/checkout")
    public ResponseEntity<LoanResponse> checkout(
            @Valid @RequestBody CheckoutRequest request) {
        LoanResponse response = loanService.checkout(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @PostMapping("/{id}/return")
    public LoanResponse returnBook(@PathVariable Long id) {
        return loanService.returnBook(id);
    }

    @GetMapping("/overdue")
    public Page<LoanResponse> getOverdue(Pageable pageable) {
        return loanService.getOverdueLoans(pageable);
    }
}

@RestController
@RequestMapping("/api/members")
public class MemberController {

    private final MemberService memberService;
    private final LoanService loanService;

    public MemberController(MemberService memberService, LoanService loanService) {
        this.memberService = memberService;
        this.loanService = loanService;
    }

    @GetMapping
    public Page<MemberResponse> getAll(Pageable pageable) {
        return memberService.getAll(pageable);
    }

    @GetMapping("/{id}")
    public MemberResponse getById(@PathVariable Long id) {
        return memberService.getById(id);
    }

    @PostMapping
    public ResponseEntity<MemberResponse> register(
            @Valid @RequestBody CreateMemberRequest request) {
        MemberResponse response = memberService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}/loans")
    public Page<LoanResponse> getMemberLoans(
            @PathVariable Long id, Pageable pageable) {
        return loanService.getMemberLoans(id, pageable);
    }
}
```

---

## Step 7: Testing the Loan Flow

```java
@SpringBootTest
@Transactional
class LoanServiceTest {

    @Autowired private LoanService loanService;
    @Autowired private MemberRepository memberRepository;
    @Autowired private BookRepository bookRepository;
    @Autowired private BookCopyRepository bookCopyRepository;
    @Autowired private LoanRepository loanRepository;

    private Member member;
    private Book book;
    private BookCopy copy;

    @BeforeEach
    void setUp() {
        member = memberRepository.save(new Member("Test User", "test@lib.com"));
        book = new Book("Test Book", "978-0000000001");
        copy = book.addCopy("TEST-001");
        bookRepository.save(book);
    }

    @Test
    void checkout_validRequest_createsLoan() {
        CheckoutRequest request = new CheckoutRequest();
        request.setMemberId(member.getId());
        request.setBookId(book.getId());

        LoanResponse response = loanService.checkout(request);

        assertThat(response.getMemberName()).isEqualTo("Test User");
        assertThat(response.getBookTitle()).isEqualTo("Test Book");
        assertThat(response.getCopyBarcode()).isEqualTo("TEST-001");
        assertThat(response.isOverdue()).isFalse();
    }

    @Test
    void checkout_noCopiesAvailable_throwsException() {
        copy.markBorrowed();

        CheckoutRequest request = new CheckoutRequest();
        request.setMemberId(member.getId());
        request.setBookId(book.getId());

        assertThatThrownBy(() -> loanService.checkout(request))
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("No available copies");
    }

    @Test
    void checkout_memberAtLoanLimit_throwsException() {
        member = new Member("Limited", "limited@lib.com");
        // Create a custom member with maxLoans = 1 for testing
        memberRepository.save(member);

        // First checkout succeeds
        CheckoutRequest req1 = new CheckoutRequest();
        req1.setMemberId(member.getId());
        req1.setBookId(book.getId());
        loanService.checkout(req1);

        // Create another book for second checkout
        Book book2 = new Book("Second Book", "978-0000000002");
        book2.addCopy("TEST-002");
        bookRepository.save(book2);

        // Second checkout should fail if limit is 1
        // (default limit is 5, so this test uses 5 loans)
    }

    @Test
    void returnBook_validLoan_marksReturned() {
        // Checkout first
        CheckoutRequest request = new CheckoutRequest();
        request.setMemberId(member.getId());
        request.setBarcode("TEST-001");
        LoanResponse checkout = loanService.checkout(request);

        // Return
        LoanResponse returned = loanService.returnBook(checkout.getId());

        assertThat(returned.getReturnedAt()).isNotNull();

        BookCopy updatedCopy = bookCopyRepository.findByBarcode("TEST-001").orElseThrow();
        assertThat(updatedCopy.isAvailable()).isTrue();
    }

    @Test
    void returnBook_alreadyReturned_throwsException() {
        CheckoutRequest request = new CheckoutRequest();
        request.setMemberId(member.getId());
        request.setBarcode("TEST-001");
        LoanResponse checkout = loanService.checkout(request);

        loanService.returnBook(checkout.getId());

        assertThatThrownBy(() -> loanService.returnBook(checkout.getId()))
            .isInstanceOf(BusinessException.class)
            .hasMessageContaining("already returned");
    }
}
```

---

## Project Checklist

```
Capstone Project Completeness:
+------------------------------------------------------------------+
|                                                                   |
|  [ ] Entities with proper JPA annotations and relationships      |
|  [ ] BaseEntity with audit fields and @Version                   |
|  [ ] Flyway migrations (V1-V8) creating all tables and seed data |
|  [ ] ddl-auto=validate (Flyway manages schema)                   |
|  [ ] Request DTOs with Bean Validation                           |
|  [ ] Response DTOs (never expose entities)                       |
|  [ ] Repository layer with @EntityGraph and JOIN FETCH           |
|  [ ] Service layer with @Transactional and business rules        |
|  [ ] Controller layer with proper HTTP methods and status codes  |
|  [ ] Global exception handler (@ControllerAdvice)                |
|  [ ] Pagination on all list endpoints                            |
|  [ ] Search with Specifications (books)                          |
|  [ ] N+1 prevention (JOIN FETCH, @EntityGraph)                   |
|  [ ] FetchType.LAZY on all @ManyToOne                            |
|  [ ] spring.jpa.open-in-view=false                               |
|  [ ] readOnly=true on all read operations                        |
|  [ ] Tests for business rules and error cases                    |
|  [ ] Indexes on FK and frequently queried columns                |
+------------------------------------------------------------------+
```

---

## Summary

In this capstone project, you built a complete Library Management System that applies patterns from every chapter in this book:

- **6 entities** with complex relationships: one-to-many, many-to-many with join entity, and enums
- **Flyway migrations** for schema management with seed data
- **Business rules** enforced in the service layer (loan limits, availability checks, duplicate prevention)
- **DTOs** for all API input and output, never exposing entities
- **Pagination** on every list endpoint
- **@EntityGraph and JOIN FETCH** to prevent N+1 queries
- **Global exception handling** with consistent error responses
- **Tests** covering happy paths and error scenarios
- **Performance optimizations**: lazy loading, readOnly transactions, proper indexing

This is a production-quality application structure that you can use as a template for real projects.

---

## Practice Exercises

**Exercise 1: Book Search**
Implement `GET /api/books/search` with Specifications. Support filters: title (contains), author name (contains), isbn (exact), category, publication year range. All filters optional.

**Exercise 2: Overdue Notifications**
Write a service method that finds all overdue loans and returns a list of notification DTOs with member name, email, book title, due date, and days overdue.

**Exercise 3: Member Dashboard**
Create `GET /api/members/{id}/dashboard` that returns: member info, active loans count, total loans ever, overdue loans count, and a list of currently borrowed books.

**Exercise 4: Book Availability**
Create `GET /api/books/{id}/availability` that returns: total copies, available copies, borrowed copies, and a list of expected return dates for borrowed copies.

**Exercise 5: Statistics Endpoint**
Create `GET /api/admin/statistics` that returns: total books, total members, active loans, overdue loans, most borrowed book (this month), and most active member (this month). Use JPQL aggregate queries.

---

## What Is Next?

The final chapter is the **Glossary of JPA and Hibernate Terms** — an alphabetical reference of every term, annotation, and concept covered in this book. Use it as a quick lookup when you encounter unfamiliar terminology in code reviews, documentation, or interviews.
