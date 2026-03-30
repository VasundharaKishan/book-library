# Chapter 24: Variational Autoencoders (VAEs)

## What You Will Learn

In this chapter, you will learn:

- How a Variational Autoencoder (VAE) differs from a regular autoencoder
- Why the latent space of a regular autoencoder has gaps and how a VAE fixes this
- What the reparameterization trick is and why it is needed (explained simply)
- What KL divergence is and how it keeps the latent space organized
- How to build a VAE in PyTorch from scratch
- How to generate brand-new images by sampling from the latent space
- How to interpolate between images to create smooth transitions

## Why This Chapter Matters

In the previous chapter, you built an autoencoder that could compress and reconstruct images. But there was a problem. If you picked a random point in the latent space and tried to decode it, you would often get garbage. The latent space had holes and gaps where no meaningful data existed.

Imagine a city map where only a few streets have houses and everything else is empty wasteland. You could navigate between existing houses, but if you wandered off the streets, you would find nothing useful.

A Variational Autoencoder fixes this by making the latent space smooth and continuous, like a city where every block has a house. This means you can pick any point in the latent space and decode it into a realistic image. You can also walk smoothly from one point to another and watch one digit gradually transform into another.

This is a big deal. It turns the autoencoder from a compression tool into a **generative model**, a network that can create entirely new data that never existed before. VAEs are used in drug discovery, art generation, music composition, and much more.

---

## 24.1 The Problem with Regular Autoencoders

Let us revisit the latent space from Chapter 23. When we trained a regular autoencoder on MNIST with a 2D latent space, we saw that different digits formed clusters. But those clusters had empty spaces between them.

```
ASCII Diagram: Regular Autoencoder Latent Space (Problems)

         |
     4   |          7 7
         |        7 7 7
     2   |  0 0             <- GAP!
         | 0 0 0     9 9
     0   |      <- EMPTY ->
         |    1 1 1
    -2   |  6 6       3 3
         | 6 6 6     3 3
    -4   |
         +---+---+---+---+-->
           -4  -2   0   2   4

Problems:
  1. Gaps between clusters (decode here = garbage)
  2. Clusters have irregular shapes
  3. No guarantee that nearby points give similar outputs
```

If you randomly sample a point from one of those gaps and try to decode it, the decoder has never seen anything like it during training. The result is nonsensical, blurry noise.

A VAE solves this by adding two key ideas:

1. **The encoder outputs a probability distribution** instead of a single point
2. **A KL divergence loss** encourages all distributions to be close to a standard normal distribution

The result is a latent space that looks more like this:

```
ASCII Diagram: VAE Latent Space (Smooth)

         |
     3   |     5 5 0 0
         |   5 5 0 0 0
     1   |  6 6 4 4 9 9
         | 6 6 4 4 9 9
    -1   |  2 2 1 1 7 7
         | 2 2 1 1 7 7
    -3   |     8 8 3 3
         |   8 8 3 3
         +---+---+---+---+-->
           -3  -1   1   3

Benefits:
  1. No gaps - every point decodes to something
  2. Smooth transitions between digits
  3. Organized, overlapping regions
```

---

## 24.2 From Points to Distributions

In a regular autoencoder, the encoder maps each input to a single point in the latent space:

```
Regular Autoencoder:
    Image of "3" --> Encoder --> [2.5, -1.3]  (a single point)
```

In a VAE, the encoder maps each input to a **probability distribution**, described by two things:

- **Mean (mu)**: The center of the distribution
- **Standard deviation (sigma)**: How spread out the distribution is

```
VAE:
    Image of "3" --> Encoder --> mean = [2.5, -1.3]
                                 std  = [0.3,  0.2]

    Then we SAMPLE from this distribution to get a latent point.
```

Think of it this way. Instead of saying "this image belongs at point (2.5, -1.3)", the VAE says "this image belongs somewhere around (2.5, -1.3), give or take about (0.3, 0.2)." Every time you encode the same image, you get a slightly different point because of the random sampling.

```
ASCII Diagram: Point vs Distribution

Regular Autoencoder:        VAE:
                                  .  . .
    X  (single point)          . . X . .  (cloud of points)
                                  .  . .

    X = exact location         X = mean (center)
                               . = possible sampled points
```

This randomness is crucial. It forces the decoder to be robust. The decoder cannot rely on the exact position. It must learn to produce good outputs for a whole region of the latent space, not just a single point. This fills in the gaps.

---

## 24.3 The Reparameterization Trick (Simplified)

There is a technical problem with sampling. Neural networks learn through **backpropagation**, which requires computing gradients. But you cannot compute gradients through a random sampling operation. Randomness breaks the chain of computation.

The **reparameterization trick** solves this cleverly. Instead of sampling directly from the distribution, we:

1. Sample a random number `epsilon` from a standard normal distribution (mean=0, std=1)
2. Compute the latent point as: `z = mean + std * epsilon`

```
ASCII Diagram: Reparameterization Trick

BEFORE (cannot backpropagate through sampling):
    Encoder --> mean, std --> [SAMPLE] --> z --> Decoder
                                 ^
                            random! no gradient!

AFTER (reparameterization trick):
    Encoder --> mean, std --+
                            |
    Random --> epsilon ------+--> z = mean + std * epsilon --> Decoder
    (from outside)          |
                       (simple math, gradients work!)
```

The key insight is that the randomness comes from `epsilon`, which is generated outside the network. The computation `z = mean + std * epsilon` is just regular multiplication and addition, which PyTorch can backpropagate through perfectly.

Think of it like this. If someone asks you to "pick a random number between 3 and 7", you might pick 5.2. But we can rewrite this as "start at 5 (the middle), then add a random offset between -2 and 2." The result is the same, but now we have separated the "where to center" (which the network controls) from the "random jitter" (which comes from outside).

In code, the reparameterization trick looks like this:

```python
def reparameterize(mu, log_var):
    """
    Sample from the distribution using the reparameterization trick.

    Args:
        mu: Mean of the distribution (from encoder)
        log_var: Log of variance (from encoder)

    Returns:
        Sampled latent vector z
    """
    # Convert log variance to standard deviation
    # log_var = log(sigma^2), so sigma = exp(log_var / 2)
    std = torch.exp(0.5 * log_var)

    # Sample epsilon from standard normal distribution
    epsilon = torch.randn_like(std)

    # Reparameterization: z = mu + std * epsilon
    z = mu + std * epsilon

    return z
```

**Why `log_var` instead of `std`?**

The encoder outputs `log_var` (the logarithm of the variance) instead of `std` directly because:

- Standard deviation must be positive, but neural network outputs can be any real number
- The logarithm maps positive numbers to all real numbers, so the network can output any value
- We convert back with `std = exp(0.5 * log_var)`

This is a common technique to ensure numerical stability.

---

## 24.4 The KL Divergence Loss (Keeping Things Organized)

A regular autoencoder has one loss: reconstruction loss (how well the output matches the input). A VAE adds a second loss: **KL divergence**.

**KL divergence** (Kullback-Leibler divergence) measures how different two probability distributions are. In a VAE, we use it to measure how far each encoder distribution is from a standard normal distribution (mean=0, std=1).

```
ASCII Diagram: What KL Divergence Does

Without KL loss:
    Each digit's distribution can be anywhere, any shape:

    Digit 3: mean=[15, -20], std=[0.001, 0.001]  (far away, tiny)
    Digit 7: mean=[-50, 8],  std=[10, 0.01]      (far away, weird shape)
    --> Big gaps, irregular shapes

With KL loss:
    All distributions are pushed toward the center:

    Digit 3: mean=[0.5, -0.3], std=[0.9, 0.8]   (near center, round)
    Digit 7: mean=[-0.2, 0.8], std=[0.7, 0.9]   (near center, round)
    --> Overlapping, smooth, no gaps
```

The KL divergence loss gently pushes every encoder distribution toward the standard normal distribution. This has two effects:

1. **Centers everything**: All distributions are pushed toward the origin (0, 0), preventing clusters from drifting far apart
2. **Regularizes the shape**: Distributions are encouraged to be round and of moderate size, preventing them from collapsing to tiny points

The formula for KL divergence when comparing with a standard normal distribution is:

```
KL = -0.5 * sum(1 + log_var - mu^2 - exp(log_var))
```

In PyTorch code:

```python
def kl_divergence_loss(mu, log_var):
    """
    KL divergence between the encoder distribution and
    a standard normal distribution N(0, 1).
    """
    kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return kl
```

### The Total VAE Loss

The total loss is a combination of both:

```
Total Loss = Reconstruction Loss + KL Divergence Loss
```

These two losses pull in opposite directions:

- **Reconstruction loss** wants the decoder to perfectly recreate the input, which pushes the encoder to create distinct, informative latent codes
- **KL divergence loss** wants all distributions to look like a standard normal, which pushes the encoder to make everything similar

The balance between these two forces is what makes the latent space smooth and useful for generation.

```
ASCII Diagram: Balancing the Two Losses

Reconstruction Loss Only:         KL Loss Only:
(distinct but messy)              (organized but useless)

    3 3                           Everything collapsed
         7 7                     to the same point at
    0 0       9 9                the center. Cannot
         1 1                     tell digits apart.
    6 6       5 5
                                      * (everything here)

Both Together (VAE):
(organized AND distinct)

     5 0
    6 4 9
    2 1 7
     8 3
```

---

## 24.5 Building a VAE in PyTorch

Now let us build a complete VAE. The architecture is similar to the autoencoder from Chapter 23, but with key differences in the encoder and the loss function.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
```

### The VAE Model

```python
class VAE(nn.Module):
    def __init__(self, latent_dim=16):
        super(VAE, self).__init__()
        self.latent_dim = latent_dim

        # Encoder layers
        self.encoder_fc1 = nn.Linear(784, 256)
        self.encoder_fc2 = nn.Linear(256, 128)

        # Two output heads: one for mean, one for log variance
        self.fc_mu = nn.Linear(128, latent_dim)       # Mean
        self.fc_log_var = nn.Linear(128, latent_dim)   # Log variance

        # Decoder layers
        self.decoder_fc1 = nn.Linear(latent_dim, 128)
        self.decoder_fc2 = nn.Linear(128, 256)
        self.decoder_fc3 = nn.Linear(256, 784)

    def encode(self, x):
        """Encode input to mean and log variance."""
        h = F.relu(self.encoder_fc1(x))
        h = F.relu(self.encoder_fc2(h))

        mu = self.fc_mu(h)           # Mean of the distribution
        log_var = self.fc_log_var(h)  # Log variance of the distribution

        return mu, log_var

    def reparameterize(self, mu, log_var):
        """Sample from the distribution using reparameterization trick."""
        std = torch.exp(0.5 * log_var)   # Standard deviation
        epsilon = torch.randn_like(std)   # Random noise
        z = mu + std * epsilon            # Sampled latent vector
        return z

    def decode(self, z):
        """Decode latent vector back to image."""
        h = F.relu(self.decoder_fc1(z))
        h = F.relu(self.decoder_fc2(h))
        reconstruction = torch.sigmoid(self.decoder_fc3(h))
        return reconstruction

    def forward(self, x):
        # Flatten input
        x = x.view(x.size(0), -1)

        # Encode
        mu, log_var = self.encode(x)

        # Reparameterize (sample from distribution)
        z = self.reparameterize(mu, log_var)

        # Decode
        reconstruction = self.decode(z)

        # Reshape to image
        reconstruction = reconstruction.view(x.size(0), 1, 28, 28)

        return reconstruction, mu, log_var
```

**Line-by-line explanation:**

- `self.encoder_fc1` and `self.encoder_fc2`: These are shared encoder layers that both the mean and log variance heads build upon. They compress the input from 784 to 128 features.

- `self.fc_mu = nn.Linear(128, latent_dim)`: This layer produces the mean of the latent distribution. For each input image, it outputs a vector of `latent_dim` mean values.

- `self.fc_log_var = nn.Linear(128, latent_dim)`: This layer produces the log variance. Together with the mean, it defines a Gaussian distribution in the latent space.

- `encode(self, x)`: Takes a flattened image and returns two vectors: `mu` (where the distribution is centered) and `log_var` (how spread out the distribution is).

- `reparameterize(self, mu, log_var)`: Applies the reparameterization trick we discussed. Samples a random `epsilon`, then computes `z = mu + std * epsilon`. This lets gradients flow through during training.

- `decode(self, z)`: Takes a latent vector and reconstructs an image. Uses ReLU activations in hidden layers and Sigmoid in the output to produce pixel values in [0, 1].

- `forward(self, x)`: The complete forward pass. Encodes the input, samples from the distribution, and decodes the sample. Returns the reconstruction, mean, and log variance (we need all three for the loss function).

```
ASCII Diagram: VAE Architecture

    INPUT (784)
       |
    Linear(784, 256) + ReLU
       |
    Linear(256, 128) + ReLU
       |
    +-------+-------+
    |               |
  fc_mu(128,16)  fc_log_var(128,16)
    |               |
    mu           log_var
    |               |
    +---[SAMPLE]----+    <-- Reparameterization trick
           |
          z (16)         <-- Latent vector
           |
    Linear(16, 128) + ReLU
           |
    Linear(128, 256) + ReLU
           |
    Linear(256, 784) + Sigmoid
           |
    OUTPUT (784)
```

### The Loss Function

```python
def vae_loss_function(reconstruction, original, mu, log_var):
    """
    Compute the VAE loss.

    Args:
        reconstruction: Decoded output (batch_size, 1, 28, 28)
        original: Original input (batch_size, 1, 28, 28)
        mu: Mean from encoder (batch_size, latent_dim)
        log_var: Log variance from encoder (batch_size, latent_dim)

    Returns:
        Total loss, reconstruction loss, KL divergence loss
    """
    # Flatten both to (batch_size, 784) for loss computation
    recon_flat = reconstruction.view(reconstruction.size(0), -1)
    orig_flat = original.view(original.size(0), -1)

    # Reconstruction loss: Binary Cross-Entropy
    # Measures how well the reconstruction matches the original
    recon_loss = F.binary_cross_entropy(
        recon_flat, orig_flat, reduction='sum'
    )

    # KL Divergence loss
    # Measures how far the encoder distribution is from N(0,1)
    kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())

    # Total loss is the sum of both
    total_loss = recon_loss + kl_loss

    return total_loss, recon_loss, kl_loss
```

**Line-by-line explanation:**

- `F.binary_cross_entropy(recon_flat, orig_flat, reduction='sum')`: Binary Cross-Entropy (BCE) is used instead of MSE here because our pixel values are in [0, 1] and we applied Sigmoid. BCE works well when comparing two distributions over [0, 1]. The `reduction='sum'` means we sum the loss over all pixels in the batch.

- `-0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())`: This is the closed-form formula for KL divergence between a Gaussian distribution N(mu, sigma) and a standard normal N(0, 1). The terms work together to penalize distributions that are far from standard normal.

- `total_loss = recon_loss + kl_loss`: We simply add the two losses. You could also multiply `kl_loss` by a weight factor (called `beta`) to control the balance. When `beta > 1`, you get a "beta-VAE" that produces a more disentangled latent space.

---

## 24.6 Training the VAE

```python
# Data loading (same as Chapter 23)
transform = transforms.Compose([transforms.ToTensor()])

train_dataset = datasets.MNIST(
    root='./data', train=True, transform=transform, download=True
)
test_dataset = datasets.MNIST(
    root='./data', train=False, transform=transform, download=True
)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

# Set up model and optimizer
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

vae = VAE(latent_dim=16).to(device)
optimizer = optim.Adam(vae.parameters(), lr=1e-3)

total_params = sum(p.numel() for p in vae.parameters())
print(f"Total parameters: {total_params:,}")
```

**Expected output:**
```
Using device: cpu
Total parameters: 334,064
```

```python
def train_vae(model, train_loader, optimizer, device, num_epochs=30):
    """Train the VAE and return loss histories."""
    model.train()
    total_losses = []
    recon_losses = []
    kl_losses = []

    for epoch in range(num_epochs):
        epoch_total = 0
        epoch_recon = 0
        epoch_kl = 0
        num_samples = 0

        for batch_images, _ in train_loader:
            batch_images = batch_images.to(device)
            batch_size = batch_images.size(0)

            # Forward pass
            reconstruction, mu, log_var = model(batch_images)

            # Compute loss
            total_loss, recon_loss, kl_loss = vae_loss_function(
                reconstruction, batch_images, mu, log_var
            )

            # Backward pass
            optimizer.zero_grad()
            total_loss.backward()
            optimizer.step()

            epoch_total += total_loss.item()
            epoch_recon += recon_loss.item()
            epoch_kl += kl_loss.item()
            num_samples += batch_size

        # Average losses per sample
        avg_total = epoch_total / num_samples
        avg_recon = epoch_recon / num_samples
        avg_kl = epoch_kl / num_samples

        total_losses.append(avg_total)
        recon_losses.append(avg_recon)
        kl_losses.append(avg_kl)

        if (epoch + 1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}] "
                  f"Total: {avg_total:.2f} | "
                  f"Recon: {avg_recon:.2f} | "
                  f"KL: {avg_kl:.2f}")

    return total_losses, recon_losses, kl_losses

# Train the VAE
total_losses, recon_losses, kl_losses = train_vae(
    vae, train_loader, optimizer, device, num_epochs=30
)
```

**Expected output:**
```
Epoch [5/30] Total: 165.23 | Recon: 148.56 | KL: 16.67
Epoch [10/30] Total: 148.76 | Recon: 130.12 | KL: 18.64
Epoch [15/30] Total: 142.34 | Recon: 122.87 | KL: 19.47
Epoch [20/30] Total: 138.91 | Recon: 118.45 | KL: 20.46
Epoch [25/30] Total: 136.78 | Recon: 115.98 | KL: 20.80
Epoch [30/30] Total: 135.42 | Recon: 114.32 | KL: 21.10
```

Notice how the reconstruction loss decreases (the model gets better at recreating images) while the KL loss increases slightly. This is the tension between the two losses: as the model tries to organize the latent space, it sacrifices a little reconstruction quality.

### Plot Training Losses

```python
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(total_losses, linewidth=2)
axes[0].set_title('Total Loss')
axes[0].set_xlabel('Epoch')
axes[0].grid(True, alpha=0.3)

axes[1].plot(recon_losses, linewidth=2, color='blue')
axes[1].set_title('Reconstruction Loss')
axes[1].set_xlabel('Epoch')
axes[1].grid(True, alpha=0.3)

axes[2].plot(kl_losses, linewidth=2, color='orange')
axes[2].set_title('KL Divergence Loss')
axes[2].set_xlabel('Epoch')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('vae_training_losses.png', dpi=100)
plt.show()
print("Training loss plots saved.")
```

**Expected output:**
```
Training loss plots saved.
```

---

## 24.7 Visualizing VAE Reconstructions

```python
def visualize_vae_reconstructions(model, test_loader, device, num_images=10):
    """Show original images and VAE reconstructions."""
    model.eval()

    test_images, test_labels = next(iter(test_loader))
    test_images = test_images[:num_images].to(device)

    with torch.no_grad():
        reconstructed, mu, log_var = model(test_images)

    originals = test_images.cpu().numpy()
    reconstructions = reconstructed.cpu().numpy()

    fig, axes = plt.subplots(2, num_images, figsize=(20, 4))

    for i in range(num_images):
        axes[0, i].imshow(originals[i].squeeze(), cmap='gray')
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Original', fontsize=12)

        axes[1, i].imshow(reconstructions[i].squeeze(), cmap='gray')
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Reconstructed', fontsize=12)

    plt.suptitle('VAE Reconstructions', fontsize=14)
    plt.tight_layout()
    plt.savefig('vae_reconstructions.png', dpi=100)
    plt.show()
    print("VAE reconstructions saved.")

visualize_vae_reconstructions(vae, test_loader, device)
```

**Expected output:**
```
VAE reconstructions saved.
```

The reconstructions will be slightly blurrier than a regular autoencoder's because the KL loss forces the latent space to be smooth. This is the trade-off: we sacrifice some reconstruction sharpness to gain the ability to generate new images.

---

## 24.8 Generating New Images

This is the exciting part. With a trained VAE, you can generate images that never existed in the training data. All you need to do is:

1. Sample a random vector from the standard normal distribution
2. Pass it through the decoder

```python
def generate_images(model, device, num_images=20, latent_dim=16):
    """Generate new images by sampling from the latent space."""
    model.eval()

    with torch.no_grad():
        # Sample random vectors from standard normal distribution
        z = torch.randn(num_images, latent_dim).to(device)

        # Decode the random vectors into images
        generated = model.decode(z)
        generated = generated.view(num_images, 1, 28, 28)

    # Plot the generated images
    images = generated.cpu().numpy()

    fig, axes = plt.subplots(2, num_images // 2, figsize=(20, 4))
    axes = axes.flatten()

    for i in range(num_images):
        axes[i].imshow(images[i].squeeze(), cmap='gray')
        axes[i].axis('off')

    plt.suptitle('Generated Images (Sampled from Latent Space)', fontsize=14)
    plt.tight_layout()
    plt.savefig('generated_images.png', dpi=100)
    plt.show()
    print("Generated images saved.")

generate_images(vae, device, num_images=20, latent_dim=16)
```

**Expected output:**
```
Generated images saved.
```

You will see 20 images of handwritten digits that were created by the VAE. These digits never existed in the training data. Some will look very realistic, others might be ambiguous (is it a 4 or a 9?). This ambiguity happens in the transition regions of the latent space where one digit type blends into another.

```
ASCII Diagram: Generating New Images

Step 1: Sample random vector z from N(0, 1)
    z = [0.23, -1.45, 0.87, ..., 0.12]  (16 numbers)

Step 2: Pass through decoder
    z --> Decoder --> [784 pixel values]

Step 3: Reshape to image
    [784 values] --> 28x28 image

Result: A brand new handwritten digit!
```

---

## 24.9 Interpolating Between Images

One of the most beautiful properties of a VAE's latent space is that you can smoothly interpolate between any two images. This means you can watch one digit gradually transform into another.

```python
def interpolate_images(model, test_loader, device, steps=10):
    """
    Interpolate between two images in the latent space.
    Shows a smooth transition from one digit to another.
    """
    model.eval()

    # Get two different images
    test_images, test_labels = next(iter(test_loader))

    # Find images of two different digits (e.g., 3 and 7)
    img1_idx = None
    img2_idx = None
    for i, label in enumerate(test_labels):
        if label == 3 and img1_idx is None:
            img1_idx = i
        elif label == 7 and img2_idx is None:
            img2_idx = i
        if img1_idx is not None and img2_idx is not None:
            break

    img1 = test_images[img1_idx:img1_idx+1].to(device)
    img2 = test_images[img2_idx:img2_idx+1].to(device)

    with torch.no_grad():
        # Encode both images to get their latent representations
        mu1, _ = model.encode(img1.view(1, -1))
        mu2, _ = model.encode(img2.view(1, -1))

        # Create interpolation steps
        interpolations = []
        for alpha in np.linspace(0, 1, steps):
            # Linear interpolation in latent space
            z = (1 - alpha) * mu1 + alpha * mu2

            # Decode the interpolated point
            decoded = model.decode(z)
            decoded = decoded.view(1, 1, 28, 28)
            interpolations.append(decoded.cpu().numpy())

    # Plot the interpolation
    fig, axes = plt.subplots(1, steps, figsize=(20, 2))

    for i, img in enumerate(interpolations):
        axes[i].imshow(img.squeeze(), cmap='gray')
        axes[i].axis('off')
        if i == 0:
            axes[i].set_title(f'Digit 3', fontsize=10)
        elif i == steps - 1:
            axes[i].set_title(f'Digit 7', fontsize=10)

    plt.suptitle('Interpolation: 3 -> 7 in Latent Space', fontsize=14)
    plt.tight_layout()
    plt.savefig('interpolation.png', dpi=100)
    plt.show()
    print("Interpolation saved.")

interpolate_images(vae, test_loader, device, steps=10)
```

**Expected output:**
```
Interpolation saved.
```

You will see a smooth sequence of images that gradually transforms from a 3 into a 7. The intermediate images will look like plausible digits that are somewhere between the two. This is only possible because the VAE's latent space is smooth and continuous.

```
ASCII Diagram: Interpolation in Latent Space

Image:  3 --> 3/7 --> 3/7 --> 7/3 --> 7/3 --> 7

         3 3 3 3
Latent:  *----*----*----*----*----*
         |                        |
       z_start                 z_end
       (encoding               (encoding
        of "3")                 of "7")

Each point along the line decodes to a
smooth blend of the two digits.
```

### Interpolation Grid

We can also create a 2D grid of images by varying two dimensions of the latent space. For this, let us train a VAE with `latent_dim=2`:

```python
# Train a 2D VAE for grid visualization
vae_2d = VAE(latent_dim=2).to(device)
optimizer_2d = optim.Adam(vae_2d.parameters(), lr=1e-3)

print("Training 2D VAE...")
train_vae(vae_2d, train_loader, optimizer_2d, device, num_epochs=30)
print("Done!")

def plot_latent_grid(model, device, grid_size=15, value_range=3):
    """
    Generate a grid of images by systematically varying
    the two latent dimensions.
    """
    model.eval()

    # Create a grid of latent values
    values = np.linspace(-value_range, value_range, grid_size)

    # Create the image grid
    figure = np.zeros((28 * grid_size, 28 * grid_size))

    with torch.no_grad():
        for i, y_val in enumerate(values):
            for j, x_val in enumerate(values):
                z = torch.tensor([[x_val, y_val]],
                                dtype=torch.float32).to(device)
                decoded = model.decode(z)
                digit = decoded.cpu().numpy().reshape(28, 28)

                figure[i * 28:(i + 1) * 28,
                       j * 28:(j + 1) * 28] = digit

    plt.figure(figsize=(12, 12))
    plt.imshow(figure, cmap='gray')
    plt.xlabel('Latent Dimension 1')
    plt.ylabel('Latent Dimension 2')
    plt.title('VAE Latent Space Grid (2D)')
    plt.tight_layout()
    plt.savefig('latent_grid.png', dpi=100)
    plt.show()
    print("Latent grid saved.")

plot_latent_grid(vae_2d, device)
```

**Expected output:**
```
Training 2D VAE...
Epoch [5/30] Total: 182.45 | Recon: 162.34 | KL: 20.11
...
Epoch [30/30] Total: 161.23 | Recon: 144.56 | KL: 16.67
Done!
Latent grid saved.
```

The grid shows what the decoder produces for every point in a region of the 2D latent space. You should see smooth transitions between digit types. For example, 0s might gradually blend into 6s, or 1s might transition into 7s.

```
ASCII Diagram: Latent Grid (Simplified)

    +---+---+---+---+---+
    | 0 | 0 | 6 | 6 | 6 |
    +---+---+---+---+---+
    | 0 | 2 | 5 | 5 | 8 |
    +---+---+---+---+---+
    | 1 | 2 | 3 | 5 | 9 |
    +---+---+---+---+---+
    | 1 | 4 | 3 | 7 | 9 |
    +---+---+---+---+---+
    | 1 | 4 | 4 | 7 | 7 |
    +---+---+---+---+---+

    Each cell shows the decoded image for
    that point in the 2D latent space.
    Note the smooth transitions!
```

---

## 24.10 VAE Latent Space Visualization (Colored by Digit)

Let us also create the scatter plot of the 2D latent space, colored by digit label, to compare with the regular autoencoder from Chapter 23:

```python
def plot_vae_latent_space(model, test_loader, device):
    """Plot the VAE's 2D latent space colored by digit."""
    model.eval()

    all_mu = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            mu, log_var = model.encode(images.view(images.size(0), -1))
            all_mu.append(mu.cpu().numpy())
            all_labels.append(labels.numpy())

    all_mu = np.concatenate(all_mu, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        all_mu[:, 0], all_mu[:, 1],
        c=all_labels, cmap='tab10',
        alpha=0.5, s=5
    )
    plt.colorbar(scatter, label='Digit')
    plt.xlabel('Latent Dimension 1')
    plt.ylabel('Latent Dimension 2')
    plt.title('VAE Latent Space (2D)')
    plt.tight_layout()
    plt.savefig('vae_latent_space.png', dpi=100)
    plt.show()
    print("VAE latent space plot saved.")

plot_vae_latent_space(vae_2d, test_loader, device)
```

**Expected output:**
```
VAE latent space plot saved.
```

Compare this with the regular autoencoder latent space from Chapter 23. The VAE's latent space should look more organized, with digit clusters that are closer together, more rounded, and have fewer gaps between them. This is the effect of the KL divergence loss.

---

## Common Mistakes

1. **Forgetting the KL loss**: If you only use reconstruction loss, you get a regular autoencoder, not a VAE. The KL divergence is what makes the latent space smooth and enables generation.

2. **Using MSE with Sigmoid output**: If your decoder ends with Sigmoid, use Binary Cross-Entropy (BCE) for reconstruction loss, not MSE. Using MSE with Sigmoid can lead to slow training because of gradient saturation.

3. **Not returning `mu` and `log_var`**: The forward method must return the mean and log variance along with the reconstruction. These are needed to compute the KL loss.

4. **Confusing `log_var` with `std`**: The encoder outputs log variance, not standard deviation. Converting: `std = exp(0.5 * log_var)`. Mixing these up produces wrong results.

5. **KL loss collapsing to zero (KL vanishing)**: Sometimes the model ignores the latent space entirely and the KL loss drops to near zero. This means the encoder is not using the latent space. Solutions include using a KL warm-up schedule (start with low KL weight and gradually increase it).

6. **Using `reduction='mean'` for both losses**: Be consistent with loss reduction. If you use `reduction='sum'` for reconstruction, make sure you understand the scale difference with KL loss.

---

## Best Practices

1. **Use KL warm-up**: Start training with a low weight on the KL loss (e.g., 0.0) and gradually increase it to 1.0 over the first few epochs. This helps the model first learn to reconstruct well, then organize the latent space.

2. **Monitor both losses separately**: Track reconstruction loss and KL loss independently. If KL loss drops to zero, the model is not using the latent space. If reconstruction loss stays high, the model is struggling to reconstruct.

3. **Choose latent dimension wisely**: Too small (like 2) limits the model's capacity. Too large gives a better reconstruction but may produce a less organized latent space. Start with 16 or 32 for MNIST.

4. **Use the mean for evaluation**: During evaluation and interpolation, use the mean `mu` directly instead of sampling. Sampling adds noise that is useful during training but not during generation.

5. **Experiment with beta-VAE**: Multiply the KL loss by a factor `beta`. Values of `beta > 1` produce more disentangled latent representations where each dimension corresponds to a separate feature.

6. **Try different architectures**: Convolutional VAEs often produce sharper images than fully connected ones. Replace Linear layers with Conv2d and ConvTranspose2d for image data.

---

## Quick Summary

A Variational Autoencoder (VAE) extends the regular autoencoder by making the encoder output a probability distribution (described by mean and log variance) instead of a single point. The reparameterization trick allows backpropagation through the sampling step by separating the randomness from the learned parameters. The KL divergence loss keeps the latent space organized by pushing all distributions toward a standard normal distribution. The result is a smooth, continuous latent space where you can sample any point and get a realistic image, or interpolate between points to create smooth transitions. The total VAE loss is the sum of the reconstruction loss (how well the output matches the input) and the KL divergence loss (how organized the latent space is).

---

## Key Points

- A VAE encoder outputs a mean and log variance, defining a distribution, not a single point
- The reparameterization trick enables backpropagation: `z = mu + std * epsilon`
- KL divergence loss pushes all distributions toward the standard normal N(0, 1)
- Total loss = Reconstruction loss + KL divergence loss
- The two losses create a tension: reconstruction wants distinct codes, KL wants similarity
- You can generate new images by sampling z from N(0, 1) and passing through the decoder
- Interpolation in latent space produces smooth transitions between images
- The latent space of a VAE has no gaps, unlike a regular autoencoder
- `log_var` is used instead of `std` because neural network outputs can be any real number
- KL warm-up helps prevent the KL vanishing problem during early training

---

## Practice Questions

1. What are the two components of the VAE loss function? What does each one encourage the model to do?

2. Explain the reparameterization trick in your own words. Why is it necessary?

3. What happens if you train a VAE with only the reconstruction loss (no KL divergence)? How does the latent space change?

4. Why does the VAE encoder output `log_var` instead of the standard deviation directly?

5. How would you generate a new handwritten digit using a trained VAE? Describe the steps.

---

## Exercises

### Exercise 1: KL Warm-Up
Implement a KL warm-up schedule. Start with `beta=0.0` (no KL loss) and linearly increase it to `beta=1.0` over the first 10 epochs. Compare the reconstruction quality and latent space organization with and without warm-up.

**Hint**: Modify the training loop to multiply the KL loss by `beta`, where `beta = min(1.0, epoch / 10)`.

### Exercise 2: Different Latent Dimensions
Train VAEs with latent dimensions of 2, 8, 16, 32, and 64. For each, generate 20 random images and display them. At what dimension do the generated images look most realistic?

### Exercise 3: Conditional Generation
Modify the VAE to accept a digit label as additional input (concatenated with the latent vector in the decoder). This creates a Conditional VAE (CVAE) that lets you control which digit to generate. Train it and generate specific digits on demand.

**Hint**: One-hot encode the label (10 values) and concatenate it with the latent vector. The decoder input becomes `latent_dim + 10`.

---

## What Is Next?

You have now learned how VAEs create a smooth latent space for generating new images. But you might have noticed that VAE-generated images tend to be blurry. This is because the model averages over many possible outputs.

In the next chapter, we will explore a completely different approach to generation: **Generative Adversarial Networks (GANs)**. Instead of learning a compressed representation, GANs use a creative competition between two networks. A generator tries to create fake images, and a discriminator tries to catch the fakes. This adversarial game produces remarkably sharp and realistic images. Get ready for the forger-versus-detective showdown of deep learning.
