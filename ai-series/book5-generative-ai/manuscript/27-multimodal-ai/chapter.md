# Chapter 27: Multimodal AI

## What You Will Learn

In this chapter, you will learn:

- What multimodal AI is and why it matters
- How vision-language models (GPT-4V, LLaVA) understand images and text together
- How text-to-image models (Stable Diffusion, DALL-E) generate images from descriptions
- How text-to-speech and speech-to-text (Whisper) models work
- How to use multimodal APIs in Python
- How different modalities (text, image, audio) are combined in modern AI systems

## Why This Chapter Matters

Think about how you experience the world. You do not just read text or just look at pictures or just listen to sounds. You take in information from multiple senses simultaneously -- you see a friend's face, hear their voice, and read the text they sent you. Your brain seamlessly combines all of this.

For years, AI models were specialists. A text model could only handle text. An image model could only handle images. A speech model could only handle audio. They were like people who could only use one sense at a time.

Multimodal AI changes this. These models can process and generate multiple types of data -- text, images, audio, and video -- just like humans experience the world. This is one of the most exciting frontiers in AI, and it is already powering features you use every day, from phone cameras that describe scenes to assistants that understand both your voice and your screenshots.

---

## 27.1 What Is Multimodal AI?

### Understanding Modalities

A **modality** is a type of data or sensory input. In AI, the main modalities are:

```
+---------------------------------------------------------------+
|              TYPES OF MODALITIES                              |
+---------------------------------------------------------------+
|                                                               |
|  TEXT      Words, sentences, documents                        |
|            "The cat sat on the mat"                            |
|                                                               |
|  IMAGE     Photos, diagrams, screenshots                      |
|            [A photo of a cat on a mat]                        |
|                                                               |
|  AUDIO     Speech, music, sounds                              |
|            [Recording of someone saying "hello"]              |
|                                                               |
|  VIDEO     Moving images with or without sound                |
|            [A clip of a cat jumping]                           |
|                                                               |
|  MULTIMODAL AI = Models that handle 2 or more modalities     |
|                                                               |
+---------------------------------------------------------------+
```

### Types of Multimodal Tasks

```python
# Overview of multimodal AI tasks

multimodal_tasks = {
    "Image Understanding": {
        "input": "Image",
        "output": "Text",
        "examples": [
            "Image captioning: Describe what you see in this photo",
            "Visual Q&A: How many people are in this image?",
            "OCR: Read the text in this document scan",
        ],
        "models": ["GPT-4V", "Claude 3", "LLaVA", "Gemini"],
    },
    "Image Generation": {
        "input": "Text",
        "output": "Image",
        "examples": [
            "Create a photo of a sunset over mountains",
            "Draw a diagram of a neural network",
            "Generate a logo for a coffee shop",
        ],
        "models": ["DALL-E 3", "Stable Diffusion", "Midjourney"],
    },
    "Speech to Text": {
        "input": "Audio",
        "output": "Text",
        "examples": [
            "Transcribe a podcast episode",
            "Convert a meeting recording to notes",
            "Generate subtitles for a video",
        ],
        "models": ["Whisper", "Google Speech-to-Text", "Azure Speech"],
    },
    "Text to Speech": {
        "input": "Text",
        "output": "Audio",
        "examples": [
            "Read an article aloud",
            "Create a voiceover for a video",
            "Generate a podcast from a script",
        ],
        "models": ["ElevenLabs", "OpenAI TTS", "Google TTS", "Bark"],
    },
    "Video Understanding": {
        "input": "Video",
        "output": "Text",
        "examples": [
            "Summarize a lecture video",
            "Describe what happens in a security clip",
            "Generate a transcript with timestamps",
        ],
        "models": ["Gemini 1.5 Pro", "GPT-4V (frame by frame)"],
    },
}

print("Multimodal AI Tasks:")
print("=" * 60)
for task_name, info in multimodal_tasks.items():
    print(f"\n  {task_name}")
    print(f"  Input: {info['input']} -> Output: {info['output']}")
    print(f"  Models: {', '.join(info['models'])}")
    print(f"  Examples:")
    for ex in info['examples']:
        print(f"    - {ex}")
```

**Expected output:**

```
Multimodal AI Tasks:
============================================================

  Image Understanding
  Input: Image -> Output: Text
  Models: GPT-4V, Claude 3, LLaVA, Gemini
  Examples:
    - Image captioning: Describe what you see in this photo
    - Visual Q&A: How many people are in this image?
    - OCR: Read the text in this document scan

  Image Generation
  Input: Text -> Output: Image
  Models: DALL-E 3, Stable Diffusion, Midjourney
  Examples:
    - Create a photo of a sunset over mountains
    - Draw a diagram of a neural network
    - Generate a logo for a coffee shop

  Speech to Text
  Input: Audio -> Output: Text
  Models: Whisper, Google Speech-to-Text, Azure Speech
  Examples:
    - Transcribe a podcast episode
    - Convert a meeting recording to notes
    - Generate subtitles for a video

  Text to Speech
  Input: Text -> Output: Audio
  Models: ElevenLabs, OpenAI TTS, Google TTS, Bark
  Examples:
    - Read an article aloud
    - Create a voiceover for a video
    - Generate a podcast from a script

  Video Understanding
  Input: Video -> Output: Text
  Models: Gemini 1.5 Pro, GPT-4V (frame by frame)
  Examples:
    - Summarize a lecture video
    - Describe what happens in a security clip
    - Generate a transcript with timestamps
```

---

## 27.2 Vision-Language Models

### How Models See Images

Vision-language models can process both images and text. But how does a model "see" an image?

```
+---------------------------------------------------------------+
|              HOW VISION-LANGUAGE MODELS WORK                  |
+---------------------------------------------------------------+
|                                                               |
|  Step 1: Image Encoding                                       |
|  The image is split into patches (small squares)              |
|  Each patch is converted to a vector (list of numbers)        |
|                                                               |
|  +---+---+---+---+                                            |
|  | P1| P2| P3| P4|   Original image split into               |
|  +---+---+---+---+   16 patches (4x4 grid)                   |
|  | P5| P6| P7| P8|                                           |
|  +---+---+---+---+   Each patch becomes a vector:             |
|  | P9|P10|P11|P12|   P1 -> [0.2, 0.5, -0.1, ...]            |
|  +---+---+---+---+   P2 -> [0.8, -0.3, 0.4, ...]            |
|  |P13|P14|P15|P16|   ...                                      |
|  +---+---+---+---+                                            |
|                                                               |
|  Step 2: Combine with text                                    |
|  Image vectors and text tokens go into the same               |
|  transformer model together                                   |
|                                                               |
|  [IMG_1][IMG_2]...[IMG_N] [Describe] [this] [image]          |
|   image tokens             text tokens                        |
|                                                               |
|  Step 3: Generate response                                    |
|  The model generates text based on both image and text        |
|                                                               |
+---------------------------------------------------------------+
```

### Using GPT-4V (Vision) with OpenAI

```python
# Using GPT-4 Vision to analyze images
# Requires: pip install openai
# Requires: OPENAI_API_KEY

import base64
import json
# from openai import OpenAI

def analyze_image_with_gpt4v(image_path, question):
    """
    Send an image to GPT-4V and ask a question about it.

    Args:
        image_path: Path to the image file
        question: What to ask about the image
    """
    # client = OpenAI()

    # Read and encode the image
    # with open(image_path, "rb") as f:
    #     image_data = base64.b64encode(f.read()).decode("utf-8")

    # Send to GPT-4V
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": question},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {
    #                         "url": f"data:image/jpeg;base64,{image_data}"
    #                     }
    #                 }
    #             ]
    #         }
    #     ],
    #     max_tokens=300,
    # )
    # return response.choices[0].message.content

    # Simulated response
    return "This is a photograph of a golden retriever sitting in a park. The dog appears happy with its tongue out. In the background, there are green trees and a blue sky with scattered clouds."


# Example usage
print("=== GPT-4V Image Analysis ===\n")
print("Image: photo_of_dog.jpg")
print("Question: Describe this image in detail.\n")
result = analyze_image_with_gpt4v("photo_of_dog.jpg", "Describe this image in detail.")
print(f"GPT-4V Response:\n{result}")
```

**Expected output:**

```
=== GPT-4V Image Analysis ===

Image: photo_of_dog.jpg
Question: Describe this image in detail.

GPT-4V Response:
This is a photograph of a golden retriever sitting in a park. The dog appears happy with its tongue out. In the background, there are green trees and a blue sky with scattered clouds.
```

**Line-by-line explanation:**

- `base64.b64encode(...)` -- Converts the image file into a text string that can be sent in an API request. Base64 encoding represents binary data (like images) as text characters
- The message contains both text and an image URL. The image URL uses a `data:` URL with the base64-encoded image data
- `model="gpt-4o"` -- GPT-4o is a multimodal model that can process both text and images
- `max_tokens=300` -- Limits the response length

### Using Images from URLs

```python
# You can also analyze images from URLs

def analyze_url_image(image_url, question):
    """Analyze an image from a URL using GPT-4V."""

    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": [
    #                 {"type": "text", "text": question},
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {"url": image_url}
    #                 }
    #             ]
    #         }
    #     ],
    # )
    # return response.choices[0].message.content

    return "Simulated analysis of the image from URL."

# Example
print("You can analyze images from URLs:")
print('  analyze_url_image("https://example.com/chart.png", "What does this chart show?")')
```

### Using LLaVA (Open-Source Vision Model)

```python
# LLaVA: Open-source vision-language model
# Can run locally without an API key

# pip install transformers torch pillow

from transformers import AutoProcessor, LlavaForConditionalGeneration
# from PIL import Image

def setup_llava():
    """Load the LLaVA model for local image understanding."""

    model_name = "llava-hf/llava-1.5-7b-hf"

    # Load processor and model
    # processor = AutoProcessor.from_pretrained(model_name)
    # model = LlavaForConditionalGeneration.from_pretrained(
    #     model_name,
    #     torch_dtype=torch.float16,
    #     device_map="auto",
    # )

    print(f"LLaVA model: {model_name}")
    print(f"  - Open source (free to use)")
    print(f"  - Runs locally on your GPU")
    print(f"  - No API key needed")
    print(f"  - Supports image + text input")
    print(f"  - Based on LLaMA + CLIP vision encoder")


def analyze_with_llava(image_path, question):
    """Analyze an image using local LLaVA model."""

    # image = Image.open(image_path)
    # prompt = f"USER: <image>\n{question}\nASSISTANT:"
    #
    # inputs = processor(text=prompt, images=image, return_tensors="pt").to(model.device)
    # outputs = model.generate(**inputs, max_new_tokens=200)
    # result = processor.decode(outputs[0], skip_special_tokens=True)
    # return result.split("ASSISTANT:")[-1].strip()

    return "Simulated LLaVA response: The image shows a bar chart comparing Python, JavaScript, and Java popularity over the past 5 years."


setup_llava()
print(f"\nExample:")
print(f"  {analyze_with_llava('chart.png', 'What does this chart show?')}")
```

**Expected output:**

```
LLaVA model: llava-hf/llava-1.5-7b-hf
  - Open source (free to use)
  - Runs locally on your GPU
  - No API key needed
  - Supports image + text input
  - Based on LLaMA + CLIP vision encoder

Example:
  Simulated LLaVA response: The image shows a bar chart comparing Python, JavaScript, and Java popularity over the past 5 years.
```

---

## 27.3 Text-to-Image Generation

### How Text-to-Image Models Work

```
+---------------------------------------------------------------+
|              TEXT-TO-IMAGE GENERATION                          |
+---------------------------------------------------------------+
|                                                               |
|  The Diffusion Process:                                       |
|                                                               |
|  Forward (Training):                                          |
|  Clean Image --> Add noise --> Add more noise --> Pure Noise   |
|  [Cat photo]     [Fuzzy cat]    [Very fuzzy]    [Static]      |
|                                                               |
|  Reverse (Generation):                                        |
|  Pure Noise --> Remove noise --> Remove more --> Clean Image   |
|  [Static]      [Blurry shape]   [Cat shape]    [Cat photo]    |
|                                                               |
|  The text prompt guides the denoising process:                |
|  "A cat sitting on a red couch"                               |
|  tells the model WHAT to create as it removes noise           |
|                                                               |
|  Think of it like sculpting:                                  |
|  - Start with a block of marble (noise)                       |
|  - The text prompt is your blueprint                          |
|  - Each step chips away to reveal the image                   |
|                                                               |
+---------------------------------------------------------------+
```

### Using DALL-E 3 with OpenAI

```python
# Generate images with DALL-E 3
# Requires: pip install openai
# Requires: OPENAI_API_KEY

# from openai import OpenAI

def generate_image_dalle(prompt, size="1024x1024", quality="standard"):
    """
    Generate an image using DALL-E 3.

    Args:
        prompt: Description of the image to generate
        size: Image dimensions (1024x1024, 1024x1792, 1792x1024)
        quality: "standard" or "hd"
    """
    # client = OpenAI()
    #
    # response = client.images.generate(
    #     model="dall-e-3",
    #     prompt=prompt,
    #     size=size,
    #     quality=quality,
    #     n=1,
    # )
    #
    # image_url = response.data[0].url
    # revised_prompt = response.data[0].revised_prompt
    # return image_url, revised_prompt

    return (
        "https://example.com/generated_image.png",
        f"A detailed, high-quality rendering of: {prompt}"
    )


# Example usage
print("=== DALL-E 3 Image Generation ===\n")

prompts = [
    "A cozy coffee shop interior with warm lighting and bookshelves",
    "A futuristic city skyline at sunset with flying cars",
    "A hand-drawn diagram explaining how neural networks work",
]

for prompt in prompts:
    url, revised = generate_image_dalle(prompt)
    print(f"Prompt: {prompt}")
    print(f"Revised prompt: {revised[:60]}...")
    print(f"Image URL: {url}\n")
```

**Expected output:**

```
=== DALL-E 3 Image Generation ===

Prompt: A cozy coffee shop interior with warm lighting and bookshelves
Revised prompt: A detailed, high-quality rendering of: A cozy coffee sho...
Image URL: https://example.com/generated_image.png

Prompt: A futuristic city skyline at sunset with flying cars
Revised prompt: A detailed, high-quality rendering of: A futuristic city...
Image URL: https://example.com/generated_image.png

Prompt: A hand-drawn diagram explaining how neural networks work
Revised prompt: A detailed, high-quality rendering of: A hand-drawn diag...
Image URL: https://example.com/generated_image.png
```

### Using Stable Diffusion Locally

```python
# Generate images with Stable Diffusion (runs locally)
# Requires: pip install diffusers torch accelerate

# from diffusers import StableDiffusionPipeline
# import torch

def generate_with_stable_diffusion(prompt, num_steps=50):
    """
    Generate an image using Stable Diffusion locally.

    Args:
        prompt: Description of the image
        num_steps: Number of denoising steps (more = higher quality)
    """
    # Load the model
    # pipe = StableDiffusionPipeline.from_pretrained(
    #     "stabilityai/stable-diffusion-2-1",
    #     torch_dtype=torch.float16,
    # )
    # pipe = pipe.to("cuda")  # Move to GPU
    #
    # # Generate the image
    # image = pipe(
    #     prompt,
    #     num_inference_steps=num_steps,
    #     guidance_scale=7.5,  # How closely to follow the prompt
    # ).images[0]
    #
    # # Save the image
    # image.save("generated_image.png")
    # return image

    print(f"  Model: Stable Diffusion 2.1")
    print(f"  Prompt: {prompt}")
    print(f"  Steps: {num_steps}")
    print(f"  Guidance scale: 7.5")
    print(f"  Output: generated_image.png")


print("=== Stable Diffusion (Local) ===\n")
generate_with_stable_diffusion(
    "A beautiful mountain landscape with a lake, photorealistic, 4k"
)

print(f"\n  Key parameters:")
print(f"  - num_inference_steps: More steps = higher quality but slower")
print(f"  - guidance_scale: Higher = follows prompt more closely")
print(f"  - negative_prompt: What to avoid (e.g., 'blurry, low quality')")
```

**Expected output:**

```
=== Stable Diffusion (Local) ===

  Model: Stable Diffusion 2.1
  Prompt: A beautiful mountain landscape with a lake, photorealistic, 4k
  Steps: 50
  Guidance scale: 7.5
  Output: generated_image.png

  Key parameters:
  - num_inference_steps: More steps = higher quality but slower
  - guidance_scale: Higher = follows prompt more closely
  - negative_prompt: What to avoid (e.g., 'blurry, low quality')
```

### Writing Good Image Prompts

```python
# Tips for writing effective image generation prompts

prompt_tips = {
    "Be Specific": {
        "bad": "A dog",
        "good": "A golden retriever puppy sitting on a green lawn, sunny day, shallow depth of field",
    },
    "Include Style": {
        "bad": "A city",
        "good": "A cyberpunk city at night, neon lights, rain-slicked streets, in the style of Blade Runner",
    },
    "Specify Quality": {
        "bad": "A portrait",
        "good": "A professional headshot portrait, studio lighting, 8k resolution, photorealistic",
    },
    "Use Negative Prompts": {
        "bad": "(no negative prompt)",
        "good": "Negative: blurry, low quality, distorted, deformed, ugly, watermark",
    },
}

print("Writing Better Image Prompts:")
print("=" * 60)
for tip, examples in prompt_tips.items():
    print(f"\n  {tip}:")
    print(f"    Bad:  {examples['bad']}")
    print(f"    Good: {examples['good']}")
```

**Expected output:**

```
Writing Better Image Prompts:
============================================================

  Be Specific:
    Bad:  A dog
    Good: A golden retriever puppy sitting on a green lawn, sunny day, shallow depth of field

  Include Style:
    Bad:  A city
    Good: A cyberpunk city at night, neon lights, rain-slicked streets, in the style of Blade Runner

  Specify Quality:
    Bad:  A portrait
    Good: A professional headshot portrait, studio lighting, 8k resolution, photorealistic

  Use Negative Prompts:
    Bad:  (no negative prompt)
    Good: Negative: blurry, low quality, distorted, deformed, ugly, watermark
```

---

## 27.4 Speech-to-Text with Whisper

### What Is Whisper?

Whisper is OpenAI's open-source speech recognition model. It can transcribe audio in 99+ languages and even translate between languages:

```
+---------------------------------------------------------------+
|              WHISPER CAPABILITIES                             |
+---------------------------------------------------------------+
|                                                               |
|  Input: Audio file (mp3, wav, m4a, etc.)                     |
|                                                               |
|  Capabilities:                                                |
|  1. Transcription -- Convert speech to text (same language)   |
|  2. Translation   -- Convert speech to English text           |
|  3. Timestamps    -- When each word/sentence was spoken       |
|  4. Language ID   -- Detect which language is being spoken     |
|                                                               |
|  Model sizes:                                                 |
|  tiny   (39M)  -- Fast, lower accuracy                       |
|  base   (74M)  -- Good balance                                |
|  small  (244M) -- Better accuracy                             |
|  medium (769M) -- High accuracy                               |
|  large  (1.5B) -- Best accuracy                               |
|                                                               |
|  Can run locally -- no API key needed!                        |
|                                                               |
+---------------------------------------------------------------+
```

### Using Whisper Locally

```python
# Transcribe audio with Whisper
# pip install openai-whisper
# or: pip install transformers torch

# Method 1: Using the whisper library directly
# import whisper

def transcribe_with_whisper_local(audio_path, model_size="base"):
    """
    Transcribe audio using local Whisper model.

    Args:
        audio_path: Path to the audio file
        model_size: Model size (tiny, base, small, medium, large)
    """
    # model = whisper.load_model(model_size)
    # result = model.transcribe(audio_path)
    #
    # return {
    #     "text": result["text"],
    #     "language": result["language"],
    #     "segments": result["segments"],
    # }

    # Simulated result
    return {
        "text": "Hello everyone. Today we are going to learn about multimodal AI. This is a very exciting topic because it combines different types of data together.",
        "language": "en",
        "segments": [
            {"start": 0.0, "end": 1.5, "text": "Hello everyone."},
            {"start": 1.5, "end": 5.2, "text": "Today we are going to learn about multimodal AI."},
            {"start": 5.2, "end": 9.8, "text": "This is a very exciting topic because it combines different types of data together."},
        ]
    }


print("=== Whisper Transcription ===\n")
result = transcribe_with_whisper_local("lecture.mp3", model_size="base")

print(f"Language detected: {result['language']}")
print(f"\nFull transcription:")
print(f"  {result['text']}")
print(f"\nTimestamped segments:")
for seg in result['segments']:
    print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
```

**Expected output:**

```
=== Whisper Transcription ===

Language detected: en

Full transcription:
  Hello everyone. Today we are going to learn about multimodal AI. This is a very exciting topic because it combines different types of data together.

Timestamped segments:
  [0.0s - 1.5s] Hello everyone.
  [1.5s - 5.2s] Today we are going to learn about multimodal AI.
  [5.2s - 9.8s] This is a very exciting topic because it combines different types of data together.
```

### Using Whisper via OpenAI API

```python
# Transcribe using OpenAI's Whisper API
# Requires: OPENAI_API_KEY

# from openai import OpenAI

def transcribe_with_api(audio_path):
    """Transcribe audio using OpenAI's Whisper API."""
    # client = OpenAI()
    #
    # with open(audio_path, "rb") as audio_file:
    #     transcript = client.audio.transcriptions.create(
    #         model="whisper-1",
    #         file=audio_file,
    #         response_format="verbose_json",  # Get timestamps
    #     )
    #
    # return transcript

    print("API transcription:")
    print("  Model: whisper-1")
    print("  Supports: mp3, mp4, mpeg, mpga, m4a, wav, webm")
    print("  Max file size: 25 MB")
    print("  Cost: $0.006 per minute of audio")


transcribe_with_api("meeting.mp3")
```

### Using Whisper with Hugging Face Transformers

```python
# Using Whisper through the Hugging Face Transformers library
# pip install transformers torch

from transformers import pipeline

def transcribe_with_transformers(audio_path):
    """Transcribe audio using Hugging Face's Whisper pipeline."""

    # Create the transcription pipeline
    # transcriber = pipeline(
    #     "automatic-speech-recognition",
    #     model="openai/whisper-base",
    #     device="cuda",  # Use GPU if available
    # )
    #
    # # Transcribe
    # result = transcriber(audio_path, return_timestamps=True)
    # return result

    print("Hugging Face Whisper Pipeline:")
    print("  model: openai/whisper-base")
    print("  task: automatic-speech-recognition")
    print("  return_timestamps: True")
    print("  Supports: Any audio format")

transcribe_with_transformers("podcast.mp3")
```

---

## 27.5 Text-to-Speech

### Generating Speech from Text

```python
# Text-to-Speech with OpenAI
# Requires: pip install openai

# from openai import OpenAI

def text_to_speech_openai(text, voice="alloy", output_file="speech.mp3"):
    """
    Convert text to speech using OpenAI's TTS API.

    Args:
        text: The text to convert to speech
        voice: Voice style (alloy, echo, fable, onyx, nova, shimmer)
        output_file: Where to save the audio file
    """
    # client = OpenAI()
    #
    # response = client.audio.speech.create(
    #     model="tts-1",         # or "tts-1-hd" for higher quality
    #     voice=voice,
    #     input=text,
    # )
    #
    # response.stream_to_file(output_file)

    print(f"Text-to-Speech Generation:")
    print(f"  Text: {text[:50]}...")
    print(f"  Voice: {voice}")
    print(f"  Output: {output_file}")
    print(f"  Model: tts-1")


# Available voices
voices = {
    "alloy": "Neutral, balanced voice",
    "echo": "Warm, conversational voice",
    "fable": "British-accented storytelling voice",
    "onyx": "Deep, authoritative voice",
    "nova": "Energetic, friendly voice",
    "shimmer": "Soft, gentle voice",
}

print("Available OpenAI TTS Voices:")
print("=" * 50)
for voice, description in voices.items():
    print(f"  {voice}: {description}")

print()
text_to_speech_openai(
    "Welcome to the world of multimodal AI. Today you will learn how machines can see, hear, and speak.",
    voice="nova"
)
```

**Expected output:**

```
Available OpenAI TTS Voices:
==================================================
  alloy: Neutral, balanced voice
  echo: Warm, conversational voice
  fable: British-accented storytelling voice
  onyx: Deep, authoritative voice
  nova: Energetic, friendly voice
  shimmer: Soft, gentle voice

Text-to-Speech Generation:
  Text: Welcome to the world of multimodal AI. Today y...
  Voice: nova
  Output: speech.mp3
  Model: tts-1
```

---

## 27.6 Combining Modalities

### Building a Multimodal Pipeline

```python
# A complete multimodal pipeline that combines vision, text, and speech

def multimodal_pipeline(image_path, question):
    """
    Process an image, answer a question, and speak the answer.

    1. Analyze image with vision model
    2. Generate text answer
    3. Convert answer to speech
    """
    print("=== MULTIMODAL PIPELINE ===\n")

    # Step 1: Image Understanding
    print("Step 1: Analyzing image...")
    # image_description = analyze_image_with_gpt4v(image_path, question)
    image_description = "The chart shows Python adoption growing from 25% to 45% between 2020 and 2024, while Java declined from 35% to 20%."
    print(f"  Vision model output: {image_description}\n")

    # Step 2: Generate detailed answer
    print("Step 2: Generating detailed answer...")
    # Use the image description to generate a more detailed response
    detailed_answer = f"Based on the chart analysis: {image_description} This indicates a clear trend toward Python in the software industry."
    print(f"  Answer: {detailed_answer}\n")

    # Step 3: Convert to speech
    print("Step 3: Converting to speech...")
    # text_to_speech_openai(detailed_answer, voice="nova", output_file="answer.mp3")
    print(f"  Audio saved to: answer.mp3\n")

    print("Pipeline complete!")
    print(f"  Input:  Image ({image_path}) + Question ({question})")
    print(f"  Output: Text answer + Audio file (answer.mp3)")

    return detailed_answer


# Run the pipeline
result = multimodal_pipeline(
    "programming_trends_chart.png",
    "What does this chart show about programming language trends?"
)
```

**Expected output:**

```
=== MULTIMODAL PIPELINE ===

Step 1: Analyzing image...
  Vision model output: The chart shows Python adoption growing from 25% to 45% between 2020 and 2024, while Java declined from 35% to 20%.

Step 2: Generating detailed answer...
  Answer: Based on the chart analysis: The chart shows Python adoption growing from 25% to 45% between 2020 and 2024, while Java declined from 35% to 20%. This indicates a clear trend toward Python in the software industry.

Step 3: Converting to speech...
  Audio saved to: answer.mp3

Pipeline complete!
  Input:  Image (programming_trends_chart.png) + Question (What does this chart show about programming language trends?)
  Output: Text answer + Audio file (answer.mp3)
```

---

## 27.7 Model Comparison

### Choosing the Right Model

```python
# Comparing multimodal models

comparison = {
    "Vision-Language Models": {
        "GPT-4V/4o": {"cost": "$$$", "quality": "Excellent", "local": "No", "best_for": "General image understanding"},
        "Claude 3": {"cost": "$$$", "quality": "Excellent", "local": "No", "best_for": "Document and chart analysis"},
        "Gemini 1.5": {"cost": "$$", "quality": "Very Good", "local": "No", "best_for": "Long context + images"},
        "LLaVA 1.5": {"cost": "Free", "quality": "Good", "local": "Yes", "best_for": "Privacy-sensitive tasks"},
    },
    "Image Generation": {
        "DALL-E 3": {"cost": "$$", "quality": "Excellent", "local": "No", "best_for": "Text following, consistency"},
        "Stable Diffusion": {"cost": "Free", "quality": "Very Good", "local": "Yes", "best_for": "Customization, fine-tuning"},
        "Midjourney": {"cost": "$$", "quality": "Excellent", "local": "No", "best_for": "Artistic, creative images"},
    },
    "Speech-to-Text": {
        "Whisper (local)": {"cost": "Free", "quality": "Excellent", "local": "Yes", "best_for": "Privacy, offline use"},
        "Whisper (API)": {"cost": "$", "quality": "Excellent", "local": "No", "best_for": "Convenience, no GPU needed"},
        "Google STT": {"cost": "$", "quality": "Very Good", "local": "No", "best_for": "Real-time transcription"},
    },
}

for category, models in comparison.items():
    print(f"\n{category}:")
    print(f"  {'Model':<20} {'Cost':<8} {'Quality':<12} {'Local':<8} {'Best For'}")
    print(f"  {'-'*75}")
    for model, info in models.items():
        print(f"  {model:<20} {info['cost']:<8} {info['quality']:<12} {info['local']:<8} {info['best_for']}")
```

**Expected output:**

```
Vision-Language Models:
  Model                Cost     Quality      Local    Best For
  ---------------------------------------------------------------------------
  GPT-4V/4o            $$$      Excellent    No       General image understanding
  Claude 3             $$$      Excellent    No       Document and chart analysis
  Gemini 1.5           $$       Very Good    No       Long context + images
  LLaVA 1.5            Free     Good         Yes      Privacy-sensitive tasks

Image Generation:
  Model                Cost     Quality      Local    Best For
  ---------------------------------------------------------------------------
  DALL-E 3             $$       Excellent    No       Text following, consistency
  Stable Diffusion     Free     Very Good    Yes      Customization, fine-tuning
  Midjourney           $$       Excellent    No       Artistic, creative images

Speech-to-Text:
  Model                Cost     Quality      Local    Best For
  ---------------------------------------------------------------------------
  Whisper (local)      Free     Excellent    Yes      Privacy, offline use
  Whisper (API)        $        Excellent    No       Convenience, no GPU needed
  Google STT           $        Very Good    No       Real-time transcription
```

---

## Common Mistakes

1. **Sending very large images** -- Large images waste tokens and money. Resize images to 1024x1024 or smaller before sending to vision APIs.

2. **Vague image generation prompts** -- "A dog" produces generic results. Be specific about breed, setting, lighting, style, and composition.

3. **Wrong audio format** -- Not all APIs support all audio formats. Check the documentation. Most accept MP3, WAV, and M4A.

4. **Ignoring model limitations** -- Vision models can miscount objects, misread text, and hallucinate details. Always verify critical information.

5. **Not using the right model size** -- Whisper "tiny" is fast but inaccurate for complex audio. Whisper "large" is accurate but slow. Choose based on your needs.

6. **Forgetting about costs** -- Multimodal API calls are more expensive than text-only calls. Image generation can cost $0.04-0.12 per image. Budget accordingly.

---

## Best Practices

1. **Resize images before sending** -- Most vision models work well with images around 512x512 to 1024x1024 pixels. Larger images waste tokens.

2. **Be specific in image prompts** -- Include subject, style, mood, lighting, composition, and quality keywords.

3. **Use Whisper locally for privacy** -- If your audio contains sensitive information, use the local Whisper model instead of sending it to an API.

4. **Combine modalities thoughtfully** -- A multimodal pipeline should add value at each step. Do not add speech output if the user only needs text.

5. **Cache results** -- Image generation and speech synthesis are expensive. Cache results to avoid regenerating the same content.

6. **Test with diverse inputs** -- Vision models may perform differently on photos, diagrams, screenshots, and handwritten text. Test with your specific use case.

---

## Quick Summary

Multimodal AI combines different types of data -- text, images, audio, and video -- in a single model or pipeline. Vision-language models (GPT-4V, LLaVA) can analyze images and answer questions about them. Text-to-image models (DALL-E 3, Stable Diffusion) generate images from text descriptions using a diffusion process. Speech-to-text models (Whisper) transcribe audio into text with high accuracy in 99+ languages. Text-to-speech models convert text back into natural-sounding speech. These capabilities can be combined into multimodal pipelines that process information across multiple modalities.

---

## Key Points

- **Multimodal AI** processes multiple data types: text, image, audio, video
- **Vision-language models** split images into patches and process them alongside text tokens
- **GPT-4V/4o** and **Claude 3** are leading commercial vision-language models
- **LLaVA** is an open-source vision-language model that runs locally
- **Diffusion models** generate images by gradually removing noise guided by text prompts
- **Stable Diffusion** runs locally for free; **DALL-E 3** offers best quality via API
- **Whisper** transcribes speech to text in 99+ languages and can run locally
- **Text-to-speech** APIs offer multiple voice styles for natural-sounding output
- Multimodal pipelines can chain vision, text, and speech processing together
- Always consider **cost, privacy, and quality** when choosing between API and local models

---

## Practice Questions

1. Explain how a vision-language model processes an image. What is the role of image patches?

2. Describe the diffusion process used in text-to-image generation. Why does the model start with noise?

3. You need to transcribe 100 hours of private medical recordings. Would you use Whisper locally or the Whisper API? Explain your reasoning.

4. Compare DALL-E 3 and Stable Diffusion. What are the advantages of each? When would you choose one over the other?

5. Design a multimodal pipeline for a real estate application that takes property photos, generates descriptions, and creates audio walkthroughs. What models would you use at each step?

---

## Exercises

### Exercise 1: Image Analysis Script

Write a Python script that takes a folder of images and uses a vision model (or simulated function) to generate a caption for each image. Save the results to a JSON file with the filename and caption.

### Exercise 2: Audio Transcription Pipeline

Build a pipeline that transcribes an audio file using Whisper (or simulated), then summarizes the transcript using an LLM, and finally converts the summary to speech.

### Exercise 3: Multimodal Chatbot

Design (in pseudocode or Python) a chatbot that can handle three types of input: text questions, image analysis requests, and audio transcription requests. Route each input type to the appropriate model and return the result.

---

## What Is Next?

In Chapter 28, you will put everything you have learned together in a comprehensive project: building a **RAG Chatbot**. You will load PDF documents, chunk and embed them, store them in a vector database, build a chat interface with Gradio, add conversation memory and source citations, and deploy a complete chatbot that can answer questions about your documents. This is the culminating project of Book 5.
