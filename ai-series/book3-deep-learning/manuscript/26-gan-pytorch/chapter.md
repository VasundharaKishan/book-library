# Chapter 26: Building a GAN in PyTorch

## What You Will Learn

In this chapter, you will learn:

- How to build a Generator network that turns random noise into images
- How to build a Discriminator network that classifies images as real or fake
- How to write the complete alternating training loop
- How to build a full Deep Convolutional GAN (DCGAN) for MNIST
- How to visualize generated images throughout training
- How to save generated samples to track progress
- Common training issues and how to fix them

## Why This Chapter Matters

In the previous chapter, you learned the theory behind GANs: the adversarial game, the loss functions, mode collapse, and training tips. Now it is time to turn that theory into working code.

Building a GAN from scratch teaches you things that reading about GANs never can. You will see firsthand how sensitive the training process is, how the Generator's outputs evolve from random noise to recognizable digits, and how the Discriminator and Generator losses interact. This hands-on experience is essential for anyone who wants to work with generative models.

We will build a complete DCGAN (Deep Convolutional GAN) on MNIST. By the end of this chapter, you will have a network that generates handwritten digits from random noise, and you will understand every line of code that makes it work.

---

## 26.1 Setting Up the Project

Let us start by importing everything we need and preparing the data.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import os
```

**Line-by-line explanation:**
- `torch`: Core PyTorch library for tensors and computation
- `torch.nn`: Neural network building blocks (layers, activations)
- `torch.optim`: Optimizers (Adam, SGD, etc.)
- `datasets, transforms`: For loading MNIST and preprocessing images
- `DataLoader`: For batching data efficiently
- `matplotlib.pyplot`: For plotting and visualizing generated images
- `numpy`: For array operations
- `os`: For creating directories to save generated images

### Preparing the Data

```python
# Create output directory for generated images
os.makedirs('generated_images', exist_ok=True)

# Image settings
image_size = 28    # MNIST images are 28x28
channels = 1       # Grayscale (1 channel)
latent_dim = 100   # Size of the noise vector input to Generator

# Data preprocessing
# Normalize to [-1, 1] to match Tanh activation in Generator
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])  # Converts [0,1] to [-1,1]
])

# Load MNIST dataset
train_dataset = datasets.MNIST(
    root='./data',
    train=True,
    transform=transform,
    download=True
)

train_loader = DataLoader(
    train_dataset,
    batch_size=64,
    shuffle=True,
    drop_last=True   # Drop incomplete last batch
)

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
print(f"Training samples: {len(train_dataset)}")
print(f"Batches per epoch: {len(train_loader)}")
```

**Expected output:**
```
Using device: cpu
Training samples: 60000
Batches per epoch: 937
```

**Line-by-line explanation:**

- `latent_dim = 100`: The Generator takes a vector of 100 random numbers as input. This is the "creative seed" that produces different images.

- `transforms.Normalize([0.5], [0.5])`: This normalizes pixel values from [0, 1] to [-1, 1] using the formula: `output = (input - mean) / std = (input - 0.5) / 0.5`. We use [-1, 1] range because our Generator will use Tanh activation, which outputs values in [-1, 1].

- `drop_last=True`: Drops the last batch if it is smaller than `batch_size`. This prevents issues with batch normalization, which needs consistent batch sizes.

---

## 26.2 Building the Generator Network

The Generator takes a noise vector and produces an image. In a DCGAN, we use transposed convolutional layers (sometimes called "deconvolution" layers) to progressively upscale the noise into an image.

For MNIST (28x28), we will start with the noise vector and reshape it into a small feature map, then upscale it step by step.

```python
class Generator(nn.Module):
    def __init__(self, latent_dim=100):
        super(Generator, self).__init__()

        self.main = nn.Sequential(
            # Input: latent vector z of size (latent_dim)
            # Reshape to (256, 7, 7) using a linear layer
            nn.Linear(latent_dim, 256 * 7 * 7),
            nn.BatchNorm1d(256 * 7 * 7),
            nn.ReLU(True),

            # Now we need to reshape to (256, 7, 7) in forward()
            # This is handled in the forward method below
        )

        self.conv_layers = nn.Sequential(
            # Input: (256, 7, 7)
            # Upsample to (128, 14, 14)
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2,
                               padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            # Upsample to (1, 28, 28)
            nn.ConvTranspose2d(128, 1, kernel_size=4, stride=2,
                               padding=1, bias=False),
            nn.Tanh()  # Output range: [-1, 1]
        )

    def forward(self, z):
        # z shape: (batch_size, latent_dim)
        x = self.main(z)

        # Reshape from flat vector to feature maps
        x = x.view(x.size(0), 256, 7, 7)

        # Apply transposed convolutions to upscale
        x = self.conv_layers(x)

        return x
```

**Line-by-line explanation:**

- `nn.Linear(latent_dim, 256 * 7 * 7)`: Expands the 100-dimensional noise vector to a vector of 12,544 values (256 channels times 7 times 7). This will be reshaped into a 3D tensor.

- `nn.BatchNorm1d(256 * 7 * 7)`: Batch normalization on the 1D vector. Normalizes the values across the batch, which stabilizes training.

- `nn.ReLU(True)`: ReLU activation. The `True` means it operates in-place (modifies the tensor directly) to save memory.

- `x.view(x.size(0), 256, 7, 7)`: Reshapes the flat vector into a 3D tensor with 256 channels, each of size 7x7. This is the starting point for our upscaling layers.

- `nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1)`: A transposed convolution (sometimes called "deconvolution"). It increases spatial dimensions. With `stride=2`, it roughly doubles the height and width: 7x7 becomes 14x14. It also reduces channels from 256 to 128.

- `nn.BatchNorm2d(128)`: Batch normalization for 2D feature maps. Normalizes across the batch for each channel.

- `nn.ConvTranspose2d(128, 1, kernel_size=4, stride=2, padding=1)`: The final upscaling layer. Doubles size from 14x14 to 28x28 and reduces to 1 channel (grayscale).

- `nn.Tanh()`: Squashes output values to the range [-1, 1], matching our normalized input data.

```
ASCII Diagram: Generator Architecture

    Input: z (batch_size, 100)
         |
    Linear(100, 12544) + BatchNorm + ReLU
         |
    Reshape to (batch_size, 256, 7, 7)
         |
    ConvTranspose2d(256->128, 4x4, stride=2) + BatchNorm + ReLU
         |                                         7x7 -> 14x14
    ConvTranspose2d(128->1, 4x4, stride=2) + Tanh
         |                                        14x14 -> 28x28
    Output: Fake Image (batch_size, 1, 28, 28)

    Summary:
    Noise (100) -> 256x7x7 -> 128x14x14 -> 1x28x28 (image!)
```

---

## 26.3 Building the Discriminator Network

The Discriminator takes an image and outputs a single number: the probability that the image is real (close to 1) or fake (close to 0).

```python
class Discriminator(nn.Module):
    def __init__(self):
        super(Discriminator, self).__init__()

        self.conv_layers = nn.Sequential(
            # Input: (1, 28, 28)
            # Downsample to (64, 14, 14)
            nn.Conv2d(1, 64, kernel_size=4, stride=2, padding=1,
                      bias=False),
            nn.LeakyReLU(0.2, inplace=True),

            # Downsample to (128, 7, 7)
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1,
                      bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
        )

        self.classifier = nn.Sequential(
            # Flatten and classify
            nn.Linear(128 * 7 * 7, 1),
            nn.Sigmoid()  # Output probability [0, 1]
        )

    def forward(self, img):
        # img shape: (batch_size, 1, 28, 28)
        features = self.conv_layers(img)

        # Flatten: (batch_size, 128, 7, 7) -> (batch_size, 128*7*7)
        features = features.view(features.size(0), -1)

        # Classify as real or fake
        validity = self.classifier(features)

        return validity
```

**Line-by-line explanation:**

- `nn.Conv2d(1, 64, kernel_size=4, stride=2, padding=1)`: A regular convolution that reduces spatial dimensions. With `stride=2`, it halves the height and width: 28x28 becomes 14x14. It expands from 1 channel to 64 channels (learns 64 different features).

- `nn.LeakyReLU(0.2, inplace=True)`: LeakyReLU activation with a slope of 0.2 for negative values. Unlike standard ReLU (which outputs 0 for negative inputs), LeakyReLU allows a small gradient: `f(x) = max(0.2*x, x)`. This helps the Discriminator learn better.

- No BatchNorm on the first layer: This is a DCGAN best practice. Batch normalization on the Discriminator's input layer can cause instability.

- `nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1)`: Second convolution that further reduces size from 14x14 to 7x7 and increases channels from 64 to 128.

- `nn.Linear(128 * 7 * 7, 1)`: Flattened features (6,272 values) are mapped to a single output value.

- `nn.Sigmoid()`: Squashes the output to [0, 1], interpreted as "probability of being real."

```
ASCII Diagram: Discriminator Architecture

    Input: Image (batch_size, 1, 28, 28)
         |
    Conv2d(1->64, 4x4, stride=2) + LeakyReLU(0.2)
         |                               28x28 -> 14x14
    Conv2d(64->128, 4x4, stride=2) + BatchNorm + LeakyReLU(0.2)
         |                              14x14 -> 7x7
    Flatten to (batch_size, 6272)
         |
    Linear(6272, 1) + Sigmoid
         |
    Output: Probability (batch_size, 1)
            0.0 = fake, 1.0 = real
```

---

## 26.4 Weight Initialization

Proper weight initialization is important for GAN training stability. The DCGAN paper recommends initializing weights from a normal distribution with mean 0 and standard deviation 0.02.

```python
def weights_init(m):
    """
    Initialize weights for Conv and BatchNorm layers.
    Called with model.apply(weights_init).
    """
    classname = m.__class__.__name__

    if classname.find('Conv') != -1:
        # Initialize convolutional layer weights
        nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm') != -1:
        # Initialize batch norm weights
        nn.init.normal_(m.weight.data, 1.0, 0.02)
        nn.init.constant_(m.bias.data, 0)
    elif classname.find('Linear') != -1:
        # Initialize linear layer weights
        nn.init.normal_(m.weight.data, 0.0, 0.02)
        if m.bias is not None:
            nn.init.constant_(m.bias.data, 0)
```

**Line-by-line explanation:**

- `m.__class__.__name__`: Gets the name of the layer type (e.g., "Conv2d", "BatchNorm2d", "Linear").

- `nn.init.normal_(m.weight.data, 0.0, 0.02)`: Fills the weight tensor with values drawn from a normal distribution with mean 0.0 and standard deviation 0.02.

- `nn.init.constant_(m.bias.data, 0)`: Sets all bias values to zero.

---

## 26.5 Setting Up Training

```python
# Create models
generator = Generator(latent_dim=latent_dim).to(device)
discriminator = Discriminator().to(device)

# Apply weight initialization
generator.apply(weights_init)
discriminator.apply(weights_init)

# Loss function: Binary Cross-Entropy
criterion = nn.BCELoss()

# Optimizers (DCGAN-recommended settings)
optimizer_G = optim.Adam(
    generator.parameters(),
    lr=0.0002,
    betas=(0.5, 0.999)
)
optimizer_D = optim.Adam(
    discriminator.parameters(),
    lr=0.0002,
    betas=(0.5, 0.999)
)

# Fixed noise for visualization (same noise used throughout training)
fixed_noise = torch.randn(64, latent_dim, device=device)

# Print model summaries
print("Generator:")
total_g = sum(p.numel() for p in generator.parameters())
print(f"  Total parameters: {total_g:,}")

print("\nDiscriminator:")
total_d = sum(p.numel() for p in discriminator.parameters())
print(f"  Total parameters: {total_d:,}")
```

**Expected output:**
```
Generator:
  Total parameters: 3,435,649

Discriminator:
  Total parameters: 842,433
```

**Line-by-line explanation:**

- `generator.apply(weights_init)`: Applies the `weights_init` function to every layer in the Generator. This sets up proper initial weights.

- `criterion = nn.BCELoss()`: Binary Cross-Entropy loss. Used for both the Discriminator (real vs fake) and the Generator (fool the Discriminator).

- `lr=0.0002, betas=(0.5, 0.999)`: The DCGAN paper's recommended Adam settings. The lower `beta1=0.5` (instead of the default 0.9) provides more stable GAN training.

- `fixed_noise = torch.randn(64, latent_dim, device=device)`: A fixed set of 64 noise vectors that we will use to generate images throughout training. By using the same noise, we can see how the Generator's outputs improve over time.

---

## 26.6 The Training Loop

This is the heart of the GAN. We alternate between training the Discriminator and the Generator.

```python
def train_gan(generator, discriminator, train_loader, criterion,
              optimizer_G, optimizer_D, device, num_epochs=50,
              latent_dim=100, fixed_noise=None):
    """
    Train the GAN with alternating Generator/Discriminator updates.
    """
    g_losses = []
    d_losses = []
    d_real_acc = []  # Discriminator accuracy on real images
    d_fake_acc = []  # Discriminator accuracy on fake images

    for epoch in range(num_epochs):
        epoch_g_loss = 0
        epoch_d_loss = 0
        epoch_d_real = 0
        epoch_d_fake = 0
        num_batches = 0

        for batch_idx, (real_images, _) in enumerate(train_loader):
            batch_size = real_images.size(0)
            real_images = real_images.to(device)

            # Labels for real and fake images
            real_labels = torch.ones(batch_size, 1, device=device)
            fake_labels = torch.zeros(batch_size, 1, device=device)

            # Apply label smoothing for real labels
            real_labels_smooth = real_labels * 0.9

            # ========================================
            # PHASE 1: Train the Discriminator
            # ========================================
            optimizer_D.zero_grad()

            # 1a. Train on REAL images
            output_real = discriminator(real_images)
            d_loss_real = criterion(output_real, real_labels_smooth)

            # 1b. Train on FAKE images
            noise = torch.randn(batch_size, latent_dim, device=device)
            fake_images = generator(noise)
            # IMPORTANT: detach() stops gradients from flowing to Generator
            output_fake = discriminator(fake_images.detach())
            d_loss_fake = criterion(output_fake, fake_labels)

            # Total Discriminator loss
            d_loss = d_loss_real + d_loss_fake
            d_loss.backward()
            optimizer_D.step()

            # ========================================
            # PHASE 2: Train the Generator
            # ========================================
            optimizer_G.zero_grad()

            # Generate fake images (or reuse the ones from above)
            # We need fresh forward pass through D without detach
            output_fake_for_G = discriminator(fake_images)

            # Generator wants Discriminator to think fakes are real
            g_loss = criterion(output_fake_for_G, real_labels)
            g_loss.backward()
            optimizer_G.step()

            # Track metrics
            epoch_g_loss += g_loss.item()
            epoch_d_loss += d_loss.item()
            epoch_d_real += output_real.mean().item()
            epoch_d_fake += output_fake.mean().item()
            num_batches += 1

        # Average metrics for the epoch
        avg_g_loss = epoch_g_loss / num_batches
        avg_d_loss = epoch_d_loss / num_batches
        avg_d_real = epoch_d_real / num_batches
        avg_d_fake = epoch_d_fake / num_batches

        g_losses.append(avg_g_loss)
        d_losses.append(avg_d_loss)
        d_real_acc.append(avg_d_real)
        d_fake_acc.append(avg_d_fake)

        # Print progress
        if (epoch + 1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}] "
                  f"D_loss: {avg_d_loss:.4f} | "
                  f"G_loss: {avg_g_loss:.4f} | "
                  f"D(real): {avg_d_real:.3f} | "
                  f"D(fake): {avg_d_fake:.3f}")

        # Save generated images from fixed noise
        if (epoch + 1) % 10 == 0 and fixed_noise is not None:
            save_generated_images(generator, fixed_noise, epoch + 1)

    return g_losses, d_losses, d_real_acc, d_fake_acc
```

**Line-by-line explanation of the key parts:**

**Phase 1: Training the Discriminator**

- `output_real = discriminator(real_images)`: Feed real images to the Discriminator. We expect output close to 1.0.

- `d_loss_real = criterion(output_real, real_labels_smooth)`: BCE loss comparing the Discriminator's output on real images with the smoothed label 0.9.

- `noise = torch.randn(batch_size, latent_dim, device=device)`: Generate random noise vectors. Each vector has 100 values drawn from a standard normal distribution.

- `fake_images = generator(noise)`: The Generator creates fake images from the noise.

- `output_fake = discriminator(fake_images.detach())`: Feed fake images to the Discriminator. **The `.detach()` is critical.** It disconnects the fake images from the Generator's computation graph. Without it, when we call `d_loss.backward()`, gradients would flow all the way back through the Generator, which is wrong for this phase. We only want to update the Discriminator's weights here.

- `d_loss = d_loss_real + d_loss_fake`: Total Discriminator loss is the sum of losses on real and fake images.

**Phase 2: Training the Generator**

- `output_fake_for_G = discriminator(fake_images)`: Feed the same fake images to the Discriminator, but this time WITHOUT detach. We want gradients to flow through the Discriminator back to the Generator.

- `g_loss = criterion(output_fake_for_G, real_labels)`: The Generator's loss compares the Discriminator's output on fake images with the label 1.0 (real). The Generator is rewarded when the Discriminator thinks the fakes are real.

```
ASCII Diagram: Training Loop Flow

PHASE 1 (Train Discriminator):

    Real Images --> D --> output_real --> BCE(output_real, 0.9)
                                              |
    Noise --> G --> Fake Images --detach()--> D --> output_fake --> BCE(output_fake, 0.0)
                                                                       |
                                                            d_loss = sum of both
                                                                       |
                                                            Update D weights only

PHASE 2 (Train Generator):

    Noise --> G --> Fake Images --> D --> output_fake --> BCE(output_fake, 1.0)
              ^                    ^                           |
              |                    |                        g_loss
          (gradients)          (no update)                     |
              |                                        Update G weights only
              +<------ backpropagate through D to G ------+
```

---

## 26.7 Saving and Visualizing Generated Images

```python
def save_generated_images(generator, fixed_noise, epoch, nrow=8):
    """Generate and save images from fixed noise vectors."""
    generator.eval()

    with torch.no_grad():
        fake_images = generator(fixed_noise)

    # Denormalize from [-1, 1] to [0, 1]
    fake_images = (fake_images + 1) / 2.0

    # Convert to numpy
    images = fake_images.cpu().numpy()

    # Create grid of images
    num_images = min(64, len(images))
    rows = num_images // nrow
    fig, axes = plt.subplots(rows, nrow, figsize=(12, rows * 1.5))

    for i in range(num_images):
        row = i // nrow
        col = i % nrow
        axes[row, col].imshow(images[i].squeeze(), cmap='gray')
        axes[row, col].axis('off')

    plt.suptitle(f'Generated Images - Epoch {epoch}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'generated_images/epoch_{epoch:03d}.png', dpi=100)
    plt.close()

    generator.train()
    print(f"  Saved generated images for epoch {epoch}")

def show_training_progress(g_losses, d_losses, d_real_acc, d_fake_acc):
    """Plot training metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Plot losses
    axes[0].plot(g_losses, label='Generator Loss', linewidth=2)
    axes[0].plot(d_losses, label='Discriminator Loss', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Generator and Discriminator Losses')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot Discriminator confidence
    axes[1].plot(d_real_acc, label='D(real) - should stay high',
                 linewidth=2)
    axes[1].plot(d_fake_acc, label='D(fake) - should approach 0.5',
                 linewidth=2)
    axes[1].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5,
                    label='Ideal D(fake) = 0.5')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Average Output')
    axes[1].set_title('Discriminator Confidence')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('training_progress.png', dpi=100)
    plt.show()
    print("Training progress plot saved.")
```

**Line-by-line explanation:**

- `generator.eval()`: Switches the Generator to evaluation mode. This affects batch normalization and dropout layers.

- `fake_images = (fake_images + 1) / 2.0`: Converts from [-1, 1] range back to [0, 1] for display. Remember, our data was normalized to [-1, 1] to match Tanh.

- `plt.close()`: Closes the figure to free memory. During training, we generate many figures and not closing them would cause a memory leak.

- `generator.train()`: Switches back to training mode after saving images.

---

## 26.8 Running the Training

```python
# Train the GAN
print("Starting GAN training...")
print("=" * 60)

g_losses, d_losses, d_real_acc, d_fake_acc = train_gan(
    generator=generator,
    discriminator=discriminator,
    train_loader=train_loader,
    criterion=criterion,
    optimizer_G=optimizer_G,
    optimizer_D=optimizer_D,
    device=device,
    num_epochs=50,
    latent_dim=latent_dim,
    fixed_noise=fixed_noise
)

print("=" * 60)
print("Training complete!")
```

**Expected output:**
```
Starting GAN training...
============================================================
Epoch [5/50] D_loss: 0.8234 | G_loss: 2.3456 | D(real): 0.782 | D(fake): 0.298
Epoch [10/50] D_loss: 0.9123 | G_loss: 1.8765 | D(real): 0.723 | D(fake): 0.356
  Saved generated images for epoch 10
Epoch [15/50] D_loss: 1.0234 | G_loss: 1.5432 | D(real): 0.698 | D(fake): 0.389
Epoch [20/50] D_loss: 1.1234 | G_loss: 1.3210 | D(real): 0.672 | D(fake): 0.412
  Saved generated images for epoch 20
Epoch [25/50] D_loss: 1.1876 | G_loss: 1.2345 | D(real): 0.654 | D(fake): 0.432
Epoch [30/50] D_loss: 1.2345 | G_loss: 1.1567 | D(real): 0.641 | D(fake): 0.445
  Saved generated images for epoch 30
Epoch [35/50] D_loss: 1.2678 | G_loss: 1.0987 | D(real): 0.628 | D(fake): 0.458
Epoch [40/50] D_loss: 1.2890 | G_loss: 1.0543 | D(real): 0.615 | D(fake): 0.467
  Saved generated images for epoch 40
Epoch [45/50] D_loss: 1.3012 | G_loss: 1.0123 | D(real): 0.607 | D(fake): 0.473
Epoch [50/50] D_loss: 1.3123 | G_loss: 0.9876 | D(real): 0.598 | D(fake): 0.481
  Saved generated images for epoch 50
============================================================
Training complete!
```

Now plot the training progress:

```python
show_training_progress(g_losses, d_losses, d_real_acc, d_fake_acc)
```

**Expected output:**
```
Training progress plot saved.
```

```
ASCII Diagram: What the Progress Should Look Like

Losses:                          Discriminator Confidence:
    |                                |
  3 |G                             1 |D(real)
    | G                              | . . . . . . . .
  2 |  G G                          |
    |     G G G                   0.5|- - - - - - - - -  (ideal)
  1 |          G G G G G G           |            D(fake)
    | D D D D D D D D D D D       0  |. . . . .
  0 |                                |
    +-----+-----+-----+-->          +-----+-----+-----+-->
      0    15    30    50              0    15    30    50
```

---

## 26.9 Visualizing the Evolution of Generated Images

Let us look at how the Generator's output improves across training:

```python
def show_generation_evolution(generator, device, latent_dim=100):
    """
    This function assumes you have saved images during training.
    It loads and displays them side by side.
    """
    import glob

    saved_files = sorted(glob.glob('generated_images/epoch_*.png'))

    if not saved_files:
        print("No saved images found. Run training first.")
        return

    # Show first, middle, and last
    indices = [0, len(saved_files) // 2, -1]
    fig, axes = plt.subplots(1, len(indices), figsize=(18, 6))

    for i, idx in enumerate(indices):
        img = plt.imread(saved_files[idx])
        axes[i].imshow(img)
        axes[i].axis('off')
        epoch_num = saved_files[idx].split('_')[-1].split('.')[0]
        axes[i].set_title(f'Epoch {epoch_num}', fontsize=14)

    plt.suptitle('Generator Evolution During Training', fontsize=16)
    plt.tight_layout()
    plt.savefig('evolution.png', dpi=100)
    plt.show()
    print("Evolution plot saved.")

show_generation_evolution(generator, device)
```

```
ASCII Diagram: Generated Image Quality Over Epochs

Epoch 10:           Epoch 30:           Epoch 50:
(random noise)      (blurry shapes)     (clear digits)

  ........            ..####..            ..####..
  .#.##.#.            .##..##.            .#....#.
  ..##..#.            .#....#.            .#....#.
  .#..##..            .##..##.            .######.
  .##.#.#.            ..####..            .#....#.
  ........            ........            .#....#.
                                          ........
```

---

## 26.10 Generating Final Images

After training, let us generate a batch of final images:

```python
def generate_final_samples(generator, device, latent_dim=100,
                           num_images=100):
    """Generate a grid of final images."""
    generator.eval()

    with torch.no_grad():
        noise = torch.randn(num_images, latent_dim, device=device)
        generated = generator(noise)
        generated = (generated + 1) / 2.0  # Denormalize to [0, 1]

    images = generated.cpu().numpy()

    # Create a 10x10 grid
    nrow = 10
    rows = num_images // nrow
    fig, axes = plt.subplots(rows, nrow, figsize=(15, 15))

    for i in range(num_images):
        row = i // nrow
        col = i % nrow
        axes[row, col].imshow(images[i].squeeze(), cmap='gray')
        axes[row, col].axis('off')

    plt.suptitle('100 Generated Handwritten Digits', fontsize=16)
    plt.tight_layout()
    plt.savefig('final_generated.png', dpi=150)
    plt.show()
    print("Final generated images saved.")

generate_final_samples(generator, device)
```

**Expected output:**
```
Final generated images saved.
```

---

## 26.11 Saving the Trained Models

```python
# Save both models
torch.save(generator.state_dict(), 'generator.pth')
torch.save(discriminator.state_dict(), 'discriminator.pth')
print("Models saved!")

# To load later:
# generator_loaded = Generator(latent_dim=100).to(device)
# generator_loaded.load_state_dict(torch.load('generator.pth'))
# generator_loaded.eval()
```

**Expected output:**
```
Models saved!
```

---

## 26.12 Common Training Issues and Fixes

### Issue 1: Discriminator Loss Goes to Zero

**Symptom**: `D_loss` drops to near zero, `G_loss` keeps increasing.

**Cause**: The Discriminator has become too powerful. It perfectly classifies real vs fake, so the Generator gets no useful gradient signal.

**Fixes**:
- Increase label smoothing (use 0.8 instead of 0.9 for real labels)
- Add noise to the Discriminator's input images
- Reduce the Discriminator's learning rate
- Train the Generator more steps per Discriminator step

```python
# Example: Adding noise to Discriminator input
def add_instance_noise(images, strength=0.1):
    """Add Gaussian noise to images."""
    noise = torch.randn_like(images) * strength
    return images + noise

# During training:
# output_real = discriminator(add_instance_noise(real_images))
```

### Issue 2: Generator Loss Goes to Zero (Mode Collapse)

**Symptom**: `G_loss` is very low, but all generated images look the same.

**Cause**: The Generator found one output that always fools the Discriminator.

**Fixes**:
- Use minibatch discrimination (let D compare samples within a batch)
- Add feature matching loss
- Try a different architecture (Wasserstein GAN)
- Use unrolled GAN training

```python
# Quick check for mode collapse:
def check_mode_collapse(generator, device, latent_dim=100, num_samples=20):
    """Generate multiple samples and check for diversity."""
    generator.eval()
    with torch.no_grad():
        noise = torch.randn(num_samples, latent_dim, device=device)
        images = generator(noise)

    # Compute pairwise differences
    images_flat = images.view(num_samples, -1)
    diffs = []
    for i in range(num_samples):
        for j in range(i + 1, num_samples):
            diff = (images_flat[i] - images_flat[j]).abs().mean().item()
            diffs.append(diff)

    avg_diff = np.mean(diffs)
    print(f"Average pairwise difference: {avg_diff:.4f}")
    if avg_diff < 0.01:
        print("WARNING: Very low diversity - possible mode collapse!")
    else:
        print("Diversity looks healthy.")

    generator.train()
```

### Issue 3: Loss is NaN

**Symptom**: One or both losses become NaN.

**Cause**: Numerical instability, often from taking the log of zero.

**Fixes**:
- Add a small epsilon to prevent log(0): `torch.clamp(output, 1e-7, 1-1e-7)`
- Lower the learning rate
- Use gradient clipping
- Check for zero-division in custom loss functions

```python
# Gradient clipping example
torch.nn.utils.clip_grad_norm_(generator.parameters(), max_norm=1.0)
torch.nn.utils.clip_grad_norm_(discriminator.parameters(), max_norm=1.0)
```

### Issue 4: Training Oscillates Wildly

**Symptom**: Losses go up and down dramatically, never converging.

**Cause**: Learning rate too high or architecture mismatch between G and D.

**Fixes**:
- Lower the learning rate for both networks
- Ensure G and D have similar capacity (number of parameters)
- Use spectral normalization in the Discriminator

### Diagnostic Summary

```
ASCII Diagram: GAN Training Diagnostic Guide

    +---------------------------+-------------------------+
    | Symptom                   | Likely Fix               |
    +---------------------------+-------------------------+
    | D_loss -> 0               | Label smoothing,         |
    |                           | reduce D lr, add noise   |
    +---------------------------+-------------------------+
    | G_loss -> 0, same outputs | Mode collapse: change    |
    |                           | architecture or loss     |
    +---------------------------+-------------------------+
    | Loss = NaN                | Lower lr, add epsilon,   |
    |                           | gradient clipping        |
    +---------------------------+-------------------------+
    | Wild oscillations         | Lower lr, balance G/D    |
    |                           | capacity                 |
    +---------------------------+-------------------------+
    | Blurry outputs            | More training, bigger    |
    |                           | model, or use WGAN       |
    +---------------------------+-------------------------+
    | No improvement            | Check data normalization,|
    |                           | verify architecture      |
    +---------------------------+-------------------------+
```

---

## 26.13 Complete Code Summary

Here is the complete, minimal DCGAN code in one block for easy reference:

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

# Hyperparameters
latent_dim = 100
lr = 0.0002
batch_size = 64
num_epochs = 50
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Data
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])
train_data = datasets.MNIST('./data', train=True, transform=transform,
                            download=True)
loader = DataLoader(train_data, batch_size=batch_size, shuffle=True,
                    drop_last=True)

# Generator
class G(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(latent_dim, 256*7*7), nn.BatchNorm1d(256*7*7),
            nn.ReLU(True))
        self.conv = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128), nn.ReLU(True),
            nn.ConvTranspose2d(128, 1, 4, 2, 1, bias=False), nn.Tanh())
    def forward(self, z):
        x = self.fc(z).view(-1, 256, 7, 7)
        return self.conv(x)

# Discriminator
class D(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 64, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, True),
            nn.Conv2d(64, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128), nn.LeakyReLU(0.2, True))
        self.fc = nn.Sequential(nn.Linear(128*7*7, 1), nn.Sigmoid())
    def forward(self, img):
        x = self.conv(img).view(img.size(0), -1)
        return self.fc(x)

gen = G().to(device)
disc = D().to(device)
criterion = nn.BCELoss()
opt_g = optim.Adam(gen.parameters(), lr=lr, betas=(0.5, 0.999))
opt_d = optim.Adam(disc.parameters(), lr=lr, betas=(0.5, 0.999))

# Training loop
for epoch in range(num_epochs):
    for real, _ in loader:
        bs = real.size(0)
        real = real.to(device)
        ones = torch.ones(bs, 1, device=device) * 0.9
        zeros = torch.zeros(bs, 1, device=device)

        # Train D
        noise = torch.randn(bs, latent_dim, device=device)
        fake = gen(noise)
        opt_d.zero_grad()
        (criterion(disc(real), ones) +
         criterion(disc(fake.detach()), zeros)).backward()
        opt_d.step()

        # Train G
        opt_g.zero_grad()
        criterion(disc(fake), torch.ones(bs, 1, device=device)).backward()
        opt_g.step()
```

---

## Common Mistakes

1. **Forgetting `.detach()` when training Discriminator on fakes**: Without detach, gradients flow into the Generator during the Discriminator's update, corrupting training.

2. **Not matching data normalization with Generator output**: If data is in [-1, 1], the Generator must use Tanh. If data is in [0, 1], use Sigmoid.

3. **Using the same optimizer for both networks**: Generator and Discriminator need separate optimizers. They are updated at different times with different loss functions.

4. **Not denormalizing for visualization**: Remember to convert back from [-1, 1] to [0, 1] before displaying images: `img = (img + 1) / 2`.

5. **Batch size too small with BatchNorm**: BatchNorm needs a reasonable batch size (at least 16) to compute stable statistics. Very small batches cause unstable training.

6. **Not checking for mode collapse**: Always visually inspect generated images. A low Generator loss does not guarantee diverse outputs.

---

## Best Practices

1. **Use a fixed noise vector for tracking progress**: Generate from the same noise at every checkpoint to see how outputs improve.

2. **Save models periodically**: GAN training can be unstable. Save checkpoints every few epochs so you can roll back if training degrades.

3. **Monitor both losses and visual quality**: Losses alone do not tell the full story. Visual inspection is essential.

4. **Start with a known-good architecture**: The DCGAN architecture shown here is well-tested. Modify it only after you have it working.

5. **Use appropriate batch size**: 64 or 128 works well for MNIST. Too small causes noisy gradients. Too large may slow convergence.

6. **Be patient**: GANs often need many epochs to produce good results. Do not give up too early.

---

## Quick Summary

Building a GAN in PyTorch involves creating two separate networks (Generator and Discriminator), each with its own optimizer. The Generator uses transposed convolutions to upscale noise into images, while the Discriminator uses regular convolutions to classify images as real or fake. Training alternates between two phases: training the Discriminator to better distinguish real from fake, and training the Generator to better fool the Discriminator. The `.detach()` operation is critical when training the Discriminator on fake images to prevent incorrect gradient flow. Label smoothing, proper weight initialization, and DCGAN-specific optimizer settings help stabilize training. Regular visual inspection of generated images is essential to detect mode collapse and assess quality.

---

## Key Points

- The Generator uses `nn.ConvTranspose2d` to upscale noise into images
- The Discriminator uses `nn.Conv2d` to downsample images into a probability
- `.detach()` must be used on fake images when training the Discriminator
- Label smoothing (0.9 for real labels) helps prevent Discriminator dominance
- DCGAN uses Adam with lr=0.0002 and betas=(0.5, 0.999)
- Weight initialization with std=0.02 helps stable training
- Tanh output in Generator with data normalized to [-1, 1]
- LeakyReLU(0.2) in Discriminator, ReLU in Generator
- A fixed noise vector helps track Generator improvement over time
- Visual inspection is more informative than loss values alone

---

## Practice Questions

1. Why do we use `.detach()` on fake images when training the Discriminator but not when training the Generator? What would go wrong without it?

2. Explain why the Generator uses `nn.ConvTranspose2d` while the Discriminator uses `nn.Conv2d`. What does each operation do to the spatial dimensions?

3. What is label smoothing and why does it help GAN training? What value do we typically use for real labels?

4. How would you check if your GAN is experiencing mode collapse without looking at the loss values?

5. Why do we use a fixed noise vector for visualization during training instead of generating new noise each time?

---

## Exercises

### Exercise 1: Fashion MNIST GAN
Replace MNIST with Fashion-MNIST (dresses, shoes, bags, etc.) and train the same DCGAN. Fashion-MNIST is available in torchvision as `datasets.FashionMNIST`. Compare the quality and training stability with digit MNIST.

### Exercise 2: Conditional GAN
Modify the GAN to accept a digit label as input so you can control which digit to generate. Pass the label (one-hot encoded) as additional input to both the Generator and Discriminator.

**Hint**: Concatenate the one-hot label vector with the noise vector for the Generator. For the Discriminator, you can expand the label to an image-sized tensor and concatenate with the input image as an additional channel.

### Exercise 3: Wasserstein GAN
Replace the BCE loss with Wasserstein loss. In WGAN, the Discriminator (called the "Critic") outputs a raw score instead of a probability (remove the Sigmoid). The Critic loss is `D(real) - D(fake)` (maximize) and the Generator loss is `-D(fake)` (minimize). Apply weight clipping to the Critic: `for p in critic.parameters(): p.data.clamp_(-0.01, 0.01)`.

---

## What Is Next?

You have now built a complete GAN from scratch and seen it generate handwritten digits from pure noise. But once you have trained a model, you need to know how to save it, load it later, and deploy it so others can use it.

In the next chapter, we will cover **Saving, Loading, and Deploying Models**. You will learn how to save model checkpoints, export to ONNX format for cross-platform deployment, use TorchScript for production, and even serve your model through a simple web API. These skills bridge the gap between training a model and putting it to practical use.
