# Chapter 23: Autoencoders

## What You Will Learn

In this chapter, you will learn:

- What an autoencoder is and why it is useful
- How the encoder compresses data into a smaller representation
- How the decoder reconstructs data from that compressed form
- Why the bottleneck layer is the key to everything
- How to build an autoencoder in PyTorch from scratch
- How to train an autoencoder on the MNIST handwritten digits dataset
- How to visualize reconstructed images and explore the latent space
- Real-world use cases including denoising, anomaly detection, and data compression

## Why This Chapter Matters

Imagine you need to summarize a 500-page book into a single paragraph. You would keep only the most important ideas and throw away the minor details. Now imagine someone else reads only your paragraph and tries to rewrite the entire book. They would not get every word right, but they would capture the main story.

That is exactly what an autoencoder does with data.

Autoencoders are one of the most elegant ideas in deep learning. They learn to compress data into a small representation and then reconstruct it back. This simple concept leads to powerful applications. You can use autoencoders to remove noise from images, detect unusual patterns in data, compress files, and even generate new content.

Understanding autoencoders also prepares you for Variational Autoencoders (VAEs) and other generative models that we will cover in the next chapters. This chapter gives you the foundation for an entire family of neural network architectures.

---

## 23.1 What Is an Autoencoder?

An **autoencoder** is a neural network that learns to copy its input to its output. That might sound pointless at first. Why would you train a network just to copy data? The trick is in the middle.

Between the input and the output, there is a narrow layer called the **bottleneck**. This bottleneck has far fewer neurons than the input. The network is forced to squeeze all the important information through this tiny passage.

Think of it like this:

```
Analogy: The Bottleneck

Imagine pouring water through a funnel.
The wide top is your input (lots of data).
The narrow middle is the bottleneck (compressed data).
The wide bottom is your output (reconstructed data).

Not every drop gets through perfectly,
but most of the water makes it.
```

An autoencoder has two main parts:

1. **Encoder**: Takes the input and compresses it into a smaller representation
2. **Decoder**: Takes the compressed representation and reconstructs the original input

```
ASCII Diagram: Autoencoder Architecture

    INPUT (784 pixels for MNIST)
         |
    +---------+
    | ENCODER |    <-- Compresses data
    +---------+
         |
    [BOTTLENECK]   <-- Small representation (e.g., 32 values)
         |
    +---------+
    | DECODER |    <-- Reconstructs data
    +---------+
         |
    OUTPUT (784 pixels, same size as input)
```

### Key Terms

- **Encoder**: The first half of the network. It takes high-dimensional input (like a 784-pixel image) and maps it to a lower-dimensional representation (like 32 numbers).

- **Decoder**: The second half of the network. It takes the low-dimensional representation and maps it back to the original high-dimensional space.

- **Bottleneck** (also called the **latent space** or **code**): The narrow middle layer where compressed data lives. This is where the network stores its understanding of the input.

- **Latent space**: A mathematical space where each point represents a compressed version of some input. Think of it as a map where similar inputs are close together.

- **Reconstruction**: The output of the decoder. It is the network's attempt to recreate the original input from the compressed representation.

---

## 23.2 Why Does the Bottleneck Matter?

Without the bottleneck, the network would just learn to copy the input directly. Each neuron would pass its value to the next layer unchanged. The network would learn nothing useful.

The bottleneck forces the network to make choices. With only 32 neurons in the middle but 784 input values, the encoder must figure out which features are most important. It learns to keep the essential patterns and discard the noise.

```
ASCII Diagram: Why the Bottleneck Matters

Without bottleneck (boring, learns nothing):
    784 --> 784 --> 784 --> 784
    (just copies everything)

With bottleneck (interesting, learns patterns):
    784 --> 256 --> 32 --> 256 --> 784
    (must compress, then decompress)
```

Think of it like packing for a trip. If you have a huge suitcase, you throw everything in without thinking. But if you only have a small backpack, you carefully choose the most important items. The constraint forces you to prioritize.

---

## 23.3 Use Cases for Autoencoders

Autoencoders are not just academic curiosities. They have real practical applications:

### 1. Denoising

You can train an autoencoder to take noisy images as input and produce clean images as output. The bottleneck forces the network to learn the underlying pattern and ignore the noise.

```
Noisy Image --> [Autoencoder] --> Clean Image
```

### 2. Anomaly Detection

Train an autoencoder on "normal" data. When you feed it unusual data, the reconstruction will be poor. A high reconstruction error signals that something is abnormal.

```
Normal data: Low reconstruction error  --> "Everything is fine"
Unusual data: High reconstruction error --> "Something is wrong!"
```

This is used in fraud detection, manufacturing quality control, and medical imaging.

### 3. Data Compression

The bottleneck representation is a compressed version of the input. You can use autoencoders to compress data in ways that are specific to your domain.

### 4. Feature Learning

The encoder learns meaningful features of the data. These features can be used as inputs to other models, like classifiers.

### 5. Image Generation

While basic autoencoders are not great generators, their variants (like VAEs, which we cover next chapter) can generate entirely new images.

---

## 23.4 Building an Autoencoder in PyTorch

Let us build an autoencoder step by step. We will use the MNIST dataset, which contains 28x28 pixel images of handwritten digits (0-9).

### Step 1: Import Libraries

```python
import torch                          # Main PyTorch library
import torch.nn as nn                 # Neural network modules
import torch.optim as optim           # Optimizers like Adam
from torchvision import datasets      # Built-in datasets like MNIST
from torchvision import transforms    # Data transformations
from torch.utils.data import DataLoader  # Batching and loading data
import matplotlib.pyplot as plt       # For plotting images
import numpy as np                    # Numerical operations
```

**Line-by-line explanation:**
- `torch`: The core PyTorch library for tensor operations and automatic differentiation
- `torch.nn`: Contains building blocks for neural networks (layers, loss functions)
- `torch.optim`: Contains optimization algorithms that update network weights
- `datasets`: Provides easy access to common datasets like MNIST
- `transforms`: Tools to preprocess data (convert to tensors, normalize, etc.)
- `DataLoader`: Handles batching, shuffling, and loading data efficiently
- `matplotlib.pyplot`: Python's standard plotting library for visualizations
- `numpy`: Used for array operations when converting between PyTorch tensors and arrays

### Step 2: Load the MNIST Dataset

```python
# Define how to preprocess each image
transform = transforms.Compose([
    transforms.ToTensor(),  # Convert image to tensor (values 0-1)
])

# Download and load training data
train_dataset = datasets.MNIST(
    root='./data',          # Where to store the data
    train=True,             # Use training set
    transform=transform,    # Apply our preprocessing
    download=True           # Download if not already present
)

# Download and load test data
test_dataset = datasets.MNIST(
    root='./data',
    train=False,            # Use test set
    transform=transform,
    download=True
)

# Create data loaders for batching
train_loader = DataLoader(
    train_dataset,
    batch_size=128,         # Process 128 images at a time
    shuffle=True            # Randomize order each epoch
)

test_loader = DataLoader(
    test_dataset,
    batch_size=128,
    shuffle=False           # No need to shuffle test data
)

print(f"Training samples: {len(train_dataset)}")
print(f"Test samples: {len(test_dataset)}")
print(f"Image shape: {train_dataset[0][0].shape}")
```

**Expected output:**
```
Training samples: 60000
Test samples: 10000
Image shape: torch.Size([1, 28, 28])
```

**Line-by-line explanation:**
- `transforms.Compose`: Chains multiple transformations together. Here we only have one (convert to tensor), but you could add normalization, cropping, etc.
- `transforms.ToTensor()`: Converts a PIL image (values 0-255) into a PyTorch tensor (values 0.0-1.0). This also rearranges dimensions from (height, width, channels) to (channels, height, width).
- `datasets.MNIST(root='./data', ...)`: Downloads MNIST to the `./data` folder if it is not there already. `train=True` gives you the 60,000 training images. `train=False` gives you the 10,000 test images.
- `DataLoader(train_dataset, batch_size=128, ...)`: Wraps the dataset so you can iterate over it in batches of 128 images. `shuffle=True` randomizes the order each time you loop through the data, which helps training.

### Step 3: Define the Autoencoder

```python
class Autoencoder(nn.Module):
    def __init__(self, latent_dim=32):
        super(Autoencoder, self).__init__()

        # Encoder: compresses 784 -> 256 -> 128 -> latent_dim
        self.encoder = nn.Sequential(
            nn.Linear(784, 256),    # First compression: 784 to 256
            nn.ReLU(),              # Activation function
            nn.Linear(256, 128),    # Second compression: 256 to 128
            nn.ReLU(),              # Activation function
            nn.Linear(128, latent_dim)  # Final compression to bottleneck
        )

        # Decoder: expands latent_dim -> 128 -> 256 -> 784
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),   # First expansion
            nn.ReLU(),                    # Activation function
            nn.Linear(128, 256),          # Second expansion
            nn.ReLU(),                    # Activation function
            nn.Linear(256, 784),          # Final expansion back to original size
            nn.Sigmoid()                  # Squash output to range [0, 1]
        )

    def forward(self, x):
        # Flatten the image: (batch, 1, 28, 28) -> (batch, 784)
        x = x.view(x.size(0), -1)

        # Encode: compress to latent space
        latent = self.encoder(x)

        # Decode: reconstruct from latent space
        reconstructed = self.decoder(latent)

        # Reshape back to image: (batch, 784) -> (batch, 1, 28, 28)
        reconstructed = reconstructed.view(x.size(0), 1, 28, 28)

        return reconstructed, latent
```

**Line-by-line explanation:**

- `class Autoencoder(nn.Module)`: We define our autoencoder as a PyTorch module. This lets us use all PyTorch features like automatic gradient computation.

- `def __init__(self, latent_dim=32)`: The constructor takes `latent_dim` as a parameter. This controls how much compression we apply. A smaller value means more compression (and more information loss). The default is 32.

- `self.encoder = nn.Sequential(...)`: The encoder is a stack of layers that progressively reduce the data size. We go from 784 (28 times 28 pixels) down to 256, then 128, then finally to `latent_dim` (32 by default).

- `nn.Linear(784, 256)`: A fully connected layer that takes 784 inputs and produces 256 outputs. Each output is a weighted sum of all inputs plus a bias term.

- `nn.ReLU()`: The Rectified Linear Unit activation function. It replaces negative values with zero: `ReLU(x) = max(0, x)`. This adds non-linearity, letting the network learn complex patterns.

- `nn.Linear(128, latent_dim)`: The final encoder layer that produces the compressed representation. Note there is no ReLU after this layer. The latent values can be any real number.

- `self.decoder = nn.Sequential(...)`: The decoder mirrors the encoder but in reverse. It expands from `latent_dim` back up to 784.

- `nn.Sigmoid()`: The final activation function squashes outputs to the range [0, 1], matching the range of our input pixel values. Without this, the network might produce values outside the valid range.

- `x = x.view(x.size(0), -1)`: Flattens each 28x28 image into a single vector of 784 values. The `-1` tells PyTorch to calculate the correct dimension automatically. `x.size(0)` keeps the batch dimension intact.

- `return reconstructed, latent`: We return both the reconstructed image and the latent representation. The latent vector is useful for visualization and analysis.

```
ASCII Diagram: Network Dimensions

Encoder:
    Input:  [batch, 784]
       |
    Linear: 784 -> 256, then ReLU
       |
    Linear: 256 -> 128, then ReLU
       |
    Linear: 128 -> 32   (bottleneck / latent space)
       |

Decoder:
       |
    Linear: 32 -> 128, then ReLU
       |
    Linear: 128 -> 256, then ReLU
       |
    Linear: 256 -> 784, then Sigmoid
       |
    Output: [batch, 784] -> reshaped to [batch, 1, 28, 28]
```

### Step 4: Set Up Training

```python
# Set device (GPU if available, otherwise CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Create the model and move it to the device
model = Autoencoder(latent_dim=32).to(device)

# Loss function: Mean Squared Error
# Measures how different the reconstruction is from the original
criterion = nn.MSELoss()

# Optimizer: Adam with learning rate 0.001
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Print model summary
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params:,}")
```

**Expected output:**
```
Using device: cpu
Total parameters: 331,168
```

**Line-by-line explanation:**

- `device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')`: Checks if a GPU is available. GPUs can train neural networks much faster than CPUs. If no GPU is found, we fall back to CPU.

- `model = Autoencoder(latent_dim=32).to(device)`: Creates an instance of our autoencoder with a 32-dimensional latent space and moves it to the selected device (CPU or GPU).

- `criterion = nn.MSELoss()`: Mean Squared Error loss. It calculates the average of the squared differences between each pixel of the original image and the reconstructed image. A smaller MSE means a better reconstruction.

- `optimizer = optim.Adam(model.parameters(), lr=1e-3)`: The Adam optimizer adjusts the weights of our network during training. A learning rate of 0.001 (written as `1e-3`) controls how big each adjustment is. Adam is usually a good default choice.

- `sum(p.numel() for p in model.parameters())`: Counts the total number of trainable parameters. `numel()` returns the number of elements in each parameter tensor.

### Step 5: Train the Autoencoder

```python
def train_autoencoder(model, train_loader, criterion, optimizer,
                      device, num_epochs=20):
    """Train the autoencoder and return loss history."""
    model.train()  # Set model to training mode
    loss_history = []

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0

        for batch_images, _ in train_loader:  # We ignore labels (_)
            # Move images to device
            batch_images = batch_images.to(device)

            # Forward pass: encode and decode
            reconstructed, latent = model(batch_images)

            # Calculate loss: how different is the reconstruction?
            loss = criterion(reconstructed, batch_images)

            # Backward pass: compute gradients
            optimizer.zero_grad()  # Clear old gradients
            loss.backward()        # Compute new gradients
            optimizer.step()       # Update weights

            total_loss += loss.item()
            num_batches += 1

        # Calculate average loss for this epoch
        avg_loss = total_loss / num_batches
        loss_history.append(avg_loss)

        # Print progress every 5 epochs
        if (epoch + 1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.6f}")

    return loss_history

# Train the model
loss_history = train_autoencoder(
    model, train_loader, criterion, optimizer, device, num_epochs=20
)
```

**Expected output:**
```
Epoch [5/20], Loss: 0.021543
Epoch [10/20], Loss: 0.015876
Epoch [15/20], Loss: 0.013921
Epoch [20/20], Loss: 0.012854
```

**Line-by-line explanation:**

- `model.train()`: Puts the model in training mode. Some layers (like Dropout and BatchNorm) behave differently during training versus evaluation. For our simple model this does not make a big difference, but it is good practice.

- `for batch_images, _ in train_loader`: The data loader gives us tuples of (images, labels). Since autoencoders are unsupervised (they do not use labels), we ignore the labels with `_`.

- `reconstructed, latent = model(batch_images)`: Passes the batch through the autoencoder. The model flattens the images, encodes them to the latent space, and decodes them back.

- `loss = criterion(reconstructed, batch_images)`: Computes MSE between the original images and the reconstructed images. The network's goal is to minimize this value.

- `optimizer.zero_grad()`: Clears the gradients from the previous iteration. PyTorch accumulates gradients by default, so we must reset them before each new backward pass.

- `loss.backward()`: Computes the gradient of the loss with respect to every parameter in the network. This tells us which direction to adjust each weight.

- `optimizer.step()`: Updates all parameters using the computed gradients. The Adam optimizer applies smart adjustments that adapt to each parameter.

- `loss.item()`: Converts a single-element tensor to a Python number. We use this to track the loss value without keeping the entire computational graph in memory.

### Step 6: Plot Training Loss

```python
plt.figure(figsize=(10, 4))
plt.plot(loss_history, linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('MSE Loss')
plt.title('Autoencoder Training Loss')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('training_loss.png', dpi=100)
plt.show()
print("Training loss plot saved.")
```

**Expected output:**
```
Training loss plot saved.
```

You should see a curve that starts high and decreases over epochs, eventually flattening out. This means the model is learning to reconstruct images better and better.

```
ASCII Diagram: Expected Loss Curve

Loss
  |
  |*
  | *
  |  *
  |   **
  |     ***
  |        ****
  |            ********
  +-----------------------> Epoch
  0    5    10   15   20
```

---

## 23.5 Visualizing Reconstructions

The most satisfying part of training an autoencoder is seeing how well it can reconstruct images.

```python
def visualize_reconstructions(model, test_loader, device, num_images=10):
    """Show original images and their reconstructions side by side."""
    model.eval()  # Set model to evaluation mode

    # Get one batch of test images
    test_images, test_labels = next(iter(test_loader))
    test_images = test_images[:num_images].to(device)

    # Get reconstructions
    with torch.no_grad():  # No need to track gradients
        reconstructed, latent = model(test_images)

    # Move to CPU for plotting
    originals = test_images.cpu().numpy()
    reconstructions = reconstructed.cpu().numpy()

    # Create a figure with two rows
    fig, axes = plt.subplots(2, num_images, figsize=(20, 4))

    for i in range(num_images):
        # Top row: original images
        axes[0, i].imshow(originals[i].squeeze(), cmap='gray')
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Original', fontsize=12)

        # Bottom row: reconstructed images
        axes[1, i].imshow(reconstructions[i].squeeze(), cmap='gray')
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Reconstructed', fontsize=12)

    plt.suptitle('Autoencoder Reconstructions', fontsize=14)
    plt.tight_layout()
    plt.savefig('reconstructions.png', dpi=100)
    plt.show()
    print("Reconstructions saved.")

visualize_reconstructions(model, test_loader, device)
```

**Expected output:**
```
Reconstructions saved.
```

You will see two rows of images. The top row shows the original handwritten digits. The bottom row shows the autoencoder's reconstructions. They should look very similar, though perhaps slightly blurrier. The blur comes from the information lost during compression.

```
ASCII Diagram: Reconstruction Comparison

Original:     3  7  1  0  4  9  2  5  8  6
              __ __ __ __ __ __ __ __ __ __
             |  |  |  |  |  |  |  |  |  |  |
             |__|__|__|__|__|__|__|__|__|__|

Reconstructed: 3  7  1  0  4  9  2  5  8  6
              __ __ __ __ __ __ __ __ __ __
             |  |  |  |  |  |  |  |  |  |  |
             |__|__|__|__|__|__|__|__|__|__|
             (slightly blurrier but recognizable)
```

---

## 23.6 Exploring the Latent Space

The latent space is where the autoencoder stores its understanding of the data. Each image gets mapped to a point in this space. Let us visualize it.

To plot the latent space in 2D, we will train an autoencoder with `latent_dim=2`. This is a very tight bottleneck, but it lets us make a beautiful 2D scatter plot.

```python
# Train a new autoencoder with 2D latent space
model_2d = Autoencoder(latent_dim=2).to(device)
optimizer_2d = optim.Adam(model_2d.parameters(), lr=1e-3)

print("Training 2D autoencoder...")
loss_history_2d = train_autoencoder(
    model_2d, train_loader, criterion, optimizer_2d, device, num_epochs=30
)
print("Done!")
```

**Expected output:**
```
Training 2D autoencoder...
Epoch [5/30], Loss: 0.042187
Epoch [10/30], Loss: 0.036254
Epoch [15/30], Loss: 0.034102
Epoch [20/30], Loss: 0.033215
Epoch [25/30], Loss: 0.032578
Epoch [30/30], Loss: 0.032104
Done!
```

Notice the loss is higher than the 32-dimensional model. That is expected. With only 2 dimensions, the bottleneck is extremely tight and more information is lost.

Now let us visualize where different digits land in the 2D latent space:

```python
def plot_latent_space(model, test_loader, device):
    """Plot all test images in the 2D latent space, colored by digit."""
    model.eval()

    all_latents = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            _, latent = model(images)
            all_latents.append(latent.cpu().numpy())
            all_labels.append(labels.numpy())

    # Combine all batches
    all_latents = np.concatenate(all_latents, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)

    # Create scatter plot
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        all_latents[:, 0],    # First latent dimension (x-axis)
        all_latents[:, 1],    # Second latent dimension (y-axis)
        c=all_labels,         # Color by digit label
        cmap='tab10',         # Use 10-color colormap
        alpha=0.5,            # Semi-transparent dots
        s=5                   # Small dot size
    )
    plt.colorbar(scatter, label='Digit')
    plt.xlabel('Latent Dimension 1')
    plt.ylabel('Latent Dimension 2')
    plt.title('MNIST Digits in 2D Latent Space')
    plt.tight_layout()
    plt.savefig('latent_space.png', dpi=100)
    plt.show()
    print("Latent space plot saved.")

plot_latent_space(model_2d, test_loader, device)
```

**Expected output:**
```
Latent space plot saved.
```

You will see a scatter plot where each dot represents a digit and the color indicates which digit it is (0-9). You should notice that similar digits cluster together. For example, 1s might form one cluster, and 0s might form another cluster.

```
ASCII Diagram: 2D Latent Space (Simplified)

    Latent Dim 2
         |
      4  |         7 7
         |       7 7 7
      2  |  0 0       9 9
         | 0 0 0     9 9
      0  |     1 1
         |    1 1 1
     -2  |  6 6       3 3
         | 6 6 6     3 3
     -4  |
         +---+---+---+---+--> Latent Dim 1
           -4  -2   0   2   4

    (Each number represents a cluster of that digit)
```

---

## 23.7 Denoising Autoencoder

One of the most practical uses of autoencoders is removing noise from data. A **denoising autoencoder** is trained to take noisy input and produce clean output.

```python
def add_noise(images, noise_factor=0.3):
    """Add random noise to images."""
    noisy = images + noise_factor * torch.randn_like(images)
    # Clamp values to valid range [0, 1]
    noisy = torch.clamp(noisy, 0.0, 1.0)
    return noisy

def train_denoising_autoencoder(model, train_loader, criterion,
                                 optimizer, device, num_epochs=20,
                                 noise_factor=0.3):
    """Train a denoising autoencoder."""
    model.train()
    loss_history = []

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0

        for batch_images, _ in train_loader:
            batch_images = batch_images.to(device)

            # Add noise to input images
            noisy_images = add_noise(batch_images, noise_factor)

            # Forward pass: feed noisy images
            reconstructed, _ = model(noisy_images)

            # Loss: compare reconstruction with CLEAN images (not noisy!)
            loss = criterion(reconstructed, batch_images)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        loss_history.append(avg_loss)

        if (epoch + 1) % 5 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.6f}")

    return loss_history

# Create and train denoising autoencoder
denoiser = Autoencoder(latent_dim=64).to(device)
denoiser_optimizer = optim.Adam(denoiser.parameters(), lr=1e-3)

print("Training denoising autoencoder...")
denoiser_loss = train_denoising_autoencoder(
    denoiser, train_loader, criterion, denoiser_optimizer,
    device, num_epochs=20, noise_factor=0.3
)
```

**Expected output:**
```
Training denoising autoencoder...
Epoch [5/20], Loss: 0.025341
Epoch [10/20], Loss: 0.020187
Epoch [15/20], Loss: 0.018945
Epoch [20/20], Loss: 0.018102
```

**Key difference**: Notice that the loss compares the reconstruction with the **clean** images, not the noisy ones. We feed noisy data in, but we want clean data out. The network learns to identify and remove the noise.

Now let us visualize the denoising results:

```python
def visualize_denoising(model, test_loader, device, noise_factor=0.3,
                        num_images=10):
    """Show noisy images and their denoised reconstructions."""
    model.eval()

    test_images, _ = next(iter(test_loader))
    test_images = test_images[:num_images].to(device)
    noisy_images = add_noise(test_images, noise_factor)

    with torch.no_grad():
        denoised, _ = model(noisy_images)

    originals = test_images.cpu().numpy()
    noisy = noisy_images.cpu().numpy()
    cleaned = denoised.cpu().numpy()

    fig, axes = plt.subplots(3, num_images, figsize=(20, 6))

    for i in range(num_images):
        axes[0, i].imshow(originals[i].squeeze(), cmap='gray')
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Original', fontsize=11)

        axes[1, i].imshow(noisy[i].squeeze(), cmap='gray')
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Noisy', fontsize=11)

        axes[2, i].imshow(cleaned[i].squeeze(), cmap='gray')
        axes[2, i].axis('off')
        if i == 0:
            axes[2, i].set_title('Denoised', fontsize=11)

    plt.suptitle('Denoising Autoencoder Results', fontsize=14)
    plt.tight_layout()
    plt.savefig('denoising_results.png', dpi=100)
    plt.show()
    print("Denoising results saved.")

visualize_denoising(denoiser, test_loader, device)
```

**Expected output:**
```
Denoising results saved.
```

You will see three rows: the clean originals on top, the noisy versions in the middle, and the denoised reconstructions on the bottom. The denoised images should be much cleaner than the noisy ones, though they might be slightly blurrier than the originals.

---

## 23.8 Anomaly Detection with Autoencoders

Autoencoders can detect anomalies by measuring how well they reconstruct each input. If the model was trained on normal data, it will struggle to reconstruct abnormal data, producing a high reconstruction error.

```python
def compute_reconstruction_errors(model, data_loader, device):
    """Compute per-sample reconstruction error."""
    model.eval()
    errors = []
    labels_list = []

    with torch.no_grad():
        for images, labels in data_loader:
            images = images.to(device)
            reconstructed, _ = model(images)

            # Compute MSE for each image individually
            batch_errors = ((reconstructed - images) ** 2).mean(
                dim=[1, 2, 3]  # Average over channels, height, width
            )
            errors.append(batch_errors.cpu().numpy())
            labels_list.append(labels.numpy())

    errors = np.concatenate(errors)
    labels_list = np.concatenate(labels_list)
    return errors, labels_list

# Use our original model (trained on all digits)
errors, labels = compute_reconstruction_errors(model, test_loader, device)

# Show average error per digit
print("Average reconstruction error per digit:")
print("-" * 35)
for digit in range(10):
    mask = labels == digit
    avg_error = errors[mask].mean()
    print(f"  Digit {digit}: {avg_error:.6f}")

# Overall statistics
print(f"\nOverall mean error: {errors.mean():.6f}")
print(f"Overall std error:  {errors.std():.6f}")
```

**Expected output:**
```
Average reconstruction error per digit:
-----------------------------------
  Digit 0: 0.009821
  Digit 1: 0.007234
  Digit 2: 0.013456
  Digit 3: 0.012987
  Digit 4: 0.011234
  Digit 5: 0.013789
  Digit 6: 0.010567
  Digit 7: 0.010123
  Digit 8: 0.014321
  Digit 9: 0.011890

Overall mean error: 0.011542
Overall std error:  0.005678
```

In a real anomaly detection scenario, you would train the autoencoder on only "normal" data (say, just the digit 1). Then any other digit would produce a higher reconstruction error and be flagged as anomalous.

```python
# Example: Train on digit 1 only, then detect other digits as anomalies
# Filter training data to include only digit 1
digit_1_indices = [i for i, (_, label) in enumerate(train_dataset)
                   if label == 1]

digit_1_subset = torch.utils.data.Subset(train_dataset, digit_1_indices)
digit_1_loader = DataLoader(digit_1_subset, batch_size=128, shuffle=True)

print(f"Training on {len(digit_1_subset)} images of digit 1")

# Train a new model on digit 1 only
anomaly_model = Autoencoder(latent_dim=16).to(device)
anomaly_optimizer = optim.Adam(anomaly_model.parameters(), lr=1e-3)
anomaly_loss = train_autoencoder(
    anomaly_model, digit_1_loader, criterion,
    anomaly_optimizer, device, num_epochs=20
)

# Now compute errors on all test digits
errors, labels = compute_reconstruction_errors(
    anomaly_model, test_loader, device
)

print("\nReconstruction errors (trained on digit 1 only):")
print("-" * 45)
for digit in range(10):
    mask = labels == digit
    avg_error = errors[mask].mean()
    status = "NORMAL" if digit == 1 else "ANOMALY"
    print(f"  Digit {digit}: {avg_error:.6f}  [{status}]")
```

**Expected output:**
```
Training on 6742 images of digit 1
Epoch [5/20], Loss: 0.008123
Epoch [10/20], Loss: 0.005432
Epoch [15/20], Loss: 0.004567
Epoch [20/20], Loss: 0.004123

Reconstruction errors (trained on digit 1 only):
---------------------------------------------
  Digit 0: 0.032456  [ANOMALY]
  Digit 1: 0.004234  [NORMAL]
  Digit 2: 0.028765  [ANOMALY]
  Digit 3: 0.025678  [ANOMALY]
  Digit 4: 0.031234  [ANOMALY]
  Digit 5: 0.029876  [ANOMALY]
  Digit 6: 0.033456  [ANOMALY]
  Digit 7: 0.021234  [ANOMALY]
  Digit 8: 0.030987  [ANOMALY]
  Digit 9: 0.027654  [ANOMALY]
```

Notice how digit 1 has a much lower error than all other digits. You could set a threshold (say, 0.01) and flag anything above it as anomalous. This same principle is used in real-world fraud detection and quality control systems.

---

## 23.9 Effect of Bottleneck Size

The size of the latent space has a big impact on reconstruction quality. Let us compare different bottleneck sizes:

```python
bottleneck_sizes = [2, 8, 16, 32, 64, 128]
results = {}

for size in bottleneck_sizes:
    print(f"\nTraining with latent_dim={size}...")
    temp_model = Autoencoder(latent_dim=size).to(device)
    temp_optimizer = optim.Adam(temp_model.parameters(), lr=1e-3)

    history = train_autoencoder(
        temp_model, train_loader, criterion,
        temp_optimizer, device, num_epochs=15
    )
    results[size] = history[-1]  # Final loss

print("\n" + "=" * 40)
print("Bottleneck Size vs Final Loss")
print("=" * 40)
for size in bottleneck_sizes:
    bar = "#" * int(results[size] * 1000)
    print(f"  dim={size:>3d}: Loss={results[size]:.6f}  {bar}")
```

**Expected output:**
```
Training with latent_dim=2...
Epoch [5/15], Loss: 0.043210
Epoch [10/15], Loss: 0.035678
Epoch [15/15], Loss: 0.033456

Training with latent_dim=8...
Epoch [5/15], Loss: 0.025432
...

========================================
Bottleneck Size vs Final Loss
========================================
  dim=  2: Loss=0.033456  #################################
  dim=  8: Loss=0.018765  ##################
  dim= 16: Loss=0.014321  ##############
  dim= 32: Loss=0.012345  ############
  dim= 64: Loss=0.010567  ##########
  dim=128: Loss=0.009234  #########
```

```
ASCII Diagram: Bottleneck Size Trade-off

                    Loss vs Bottleneck Size
Loss (MSE)
    |
0.04|  *
    |
0.03|     *
    |
0.02|        *
    |           *
0.01|              *     *     *
    |
    +---+----+----+----+----+----> Bottleneck Size
        2    8   16   32   64  128

Key Insight:
- Too small (2): High loss, blurry reconstructions
- Too large (128): Low loss but less compression
- Sweet spot: Depends on your use case
```

The pattern is clear: larger bottlenecks give better reconstructions but less compression. Smaller bottlenecks force more compression but lose more detail. The right choice depends on your application.

---

## Common Mistakes

1. **Forgetting to flatten the input**: MNIST images are 28x28, but fully connected layers expect flat vectors of 784. Always flatten before the encoder and reshape after the decoder.

2. **Wrong output activation**: If your input data is in [0, 1], use `nn.Sigmoid()` on the output. If your data is in [-1, 1], use `nn.Tanh()`. If you use the wrong activation, the network cannot produce values in the right range.

3. **Using labels during training**: Autoencoders are unsupervised. They do not use labels. If you accidentally include labels in the loss calculation, you are doing something different (like a supervised encoder).

4. **Making the bottleneck too large**: If the bottleneck is the same size as the input, the network just learns to copy. There is no compression and no useful representation.

5. **Not using `torch.no_grad()` during evaluation**: When generating reconstructions or computing errors for analysis, always wrap your code in `with torch.no_grad()`. This saves memory and speeds things up.

6. **Comparing with noisy input in denoising**: The loss for a denoising autoencoder should compare the output with the **clean** original, not the noisy input.

---

## Best Practices

1. **Start with a simple architecture**: Begin with a few linear layers. Add complexity only if the simple model does not perform well enough.

2. **Choose your bottleneck size carefully**: Start with a moderate size (32 or 64) and experiment from there. Too small loses important information. Too large learns nothing useful.

3. **Monitor both training and test loss**: If training loss is much lower than test loss, your model is overfitting. Consider adding dropout or reducing model size.

4. **Use appropriate loss functions**: MSE loss works well for continuous data. Binary Cross-Entropy (BCE) can also work well for image data in the [0, 1] range.

5. **Normalize your data**: Always scale your input data to a consistent range (like [0, 1]) before feeding it to the autoencoder.

6. **Save your model checkpoints**: Training can take time. Save the model periodically so you do not lose progress if something goes wrong.

7. **Visualize at every stage**: Plot the loss curve, show reconstructions at different epochs, and explore the latent space. Visualization helps you understand what the model is learning.

---

## Quick Summary

An autoencoder is a neural network with two parts: an encoder that compresses data into a smaller representation and a decoder that reconstructs the original data from that compressed form. The bottleneck layer in the middle forces the network to learn which features are most important. Autoencoders are trained by minimizing the difference between the input and the reconstruction. They have practical applications in denoising (removing noise from data), anomaly detection (flagging unusual inputs), data compression, and feature learning. The size of the bottleneck controls the trade-off between compression and reconstruction quality.

---

## Key Points

- An autoencoder consists of an encoder, a bottleneck (latent space), and a decoder
- The bottleneck forces the network to learn a compressed representation of the data
- Training minimizes the reconstruction error between input and output
- Autoencoders are unsupervised: they do not need labeled data
- Smaller bottlenecks mean more compression but worse reconstruction
- Denoising autoencoders are trained on noisy input and compared against clean originals
- Anomaly detection works by measuring reconstruction error on new data
- The latent space captures meaningful features: similar inputs map to nearby points
- Use `nn.Sigmoid()` when data is in the [0, 1] range and `nn.Tanh()` for [-1, 1]
- Always use `torch.no_grad()` when evaluating or visualizing (not training)

---

## Practice Questions

1. What is the purpose of the bottleneck layer in an autoencoder? What happens if you make it too large or too small?

2. Explain how a denoising autoencoder differs from a regular autoencoder. What changes in the training process?

3. How can an autoencoder be used for anomaly detection? Describe the general approach step by step.

4. Why do we use `nn.Sigmoid()` as the final activation in the decoder when working with MNIST data? What would you use if the data was normalized to the range [-1, 1]?

5. If you plot the latent space of an autoencoder trained on MNIST with `latent_dim=2`, what patterns would you expect to see?

---

## Exercises

### Exercise 1: Experiment with Architecture
Modify the autoencoder to use a convolutional architecture instead of fully connected layers. Use `nn.Conv2d` in the encoder and `nn.ConvTranspose2d` in the decoder. Compare the reconstruction quality with the fully connected version.

**Hint**: The encoder might look like: Conv2d -> ReLU -> Conv2d -> ReLU -> Flatten -> Linear. The decoder reverses this.

### Exercise 2: Bottleneck Experiment
Train autoencoders with bottleneck sizes of 2, 4, 8, 16, 32, and 64. For each size, display the reconstructions of the same 10 test images side by side. At what bottleneck size do the reconstructions become "good enough" for you to read the digits?

### Exercise 3: Denoising Challenge
Train a denoising autoencoder and experiment with different noise levels (noise_factor = 0.1, 0.3, 0.5, 0.7). At what noise level does the denoiser start to struggle? Visualize the results for each noise level.

---

## What Is Next?

In this chapter, you learned how autoencoders compress and reconstruct data. But you might have noticed a limitation: the latent space is not organized in a way that makes it easy to generate new, realistic images. Points in the latent space do not correspond to smooth transitions between digits.

In the next chapter, we will fix this problem with **Variational Autoencoders (VAEs)**. A VAE adds a special structure to the latent space that makes it smooth and continuous. This turns the autoencoder from a compression tool into a true generative model that can create entirely new images by sampling from the latent space. Get ready to generate digits that never existed before.
