# Chapter 10: Data Versioning with DVC

## What You Will Learn

In this chapter, you will learn:

- Why versioning data is essential for reproducible ML
- How to install and set up DVC (Data Version Control)
- How to track datasets with DVC
- How to reproduce experiments using versioned data
- What .dvc files are and how they work
- How to use remote storage for large datasets

## Why This Chapter Matters

Imagine you are writing a book. You use git to track every change to your manuscript. You can go back to any previous version, see what changed, and undo mistakes. Life is good.

But your book includes photographs. Each photo is 5 megabytes. You have 500 photos. That is 2.5 gigabytes. Git was designed for text files, not huge binary files. If you put the photos in git, your repository becomes enormous, slow, and painful.

ML has the same problem. Your code is small (kilobytes), but your datasets are huge (megabytes to gigabytes). DVC solves this by tracking data files separately from code, but keeping them linked so you can always match your code with the exact data it used.

---

## The Data Versioning Problem

```
+--------------------------------------------------+
|  Without Data Versioning                          |
|                                                   |
|  "Which version of the data did model v1.2 use?"|
|  "Someone changed the training data. What was    |
|   it before?"                                    |
|  "The model worked yesterday. What changed?"     |
|  "I cannot reproduce last month's results."      |
|                                                   |
|  Common bad practices:                           |
|  - data_final.csv                                |
|  - data_final_v2.csv                             |
|  - data_DONT_TOUCH.csv                           |
|  - data_20240115_johns_version.csv               |
+--------------------------------------------------+
```

```
+--------------------------------------------------+
|  With Data Versioning (DVC)                       |
|                                                   |
|  git checkout v1.0   -> Code version 1.0         |
|  dvc checkout        -> Data version that matches|
|                                                   |
|  Everything is linked:                           |
|  Code v1.0 + Data v1.0 = Reproducible results   |
|  Code v2.0 + Data v2.0 = Reproducible results   |
+--------------------------------------------------+
```

---

## What Is DVC?

DVC (Data Version Control) works alongside git. Git tracks your code. DVC tracks your data. They stay in sync so you always know which data goes with which code.

```
+--------------------------------------------------+
|  Git + DVC Working Together                       |
|                                                   |
|  Git tracks:          DVC tracks:                |
|  - Python files       - Large data files         |
|  - Config files       - Model files              |
|  - Notebooks          - Any large binary file    |
|  - .dvc files         (actual data stored        |
|    (pointers to data)  in remote storage)        |
|                                                   |
|  Think of .dvc files as bookmarks.               |
|  The bookmark (small) goes in git.               |
|  The book (large) goes in DVC storage.           |
+--------------------------------------------------+
```

### Installing DVC

```bash
pip install dvc

# Optional: Install storage backends
pip install dvc[s3]     # For Amazon S3
pip install dvc[gs]     # For Google Cloud Storage
pip install dvc[azure]  # For Azure Blob Storage
```

---

## Getting Started with DVC

### Step 1: Initialize DVC

```bash
# First, make sure you are in a git repository
git init  # (if not already a git repo)

# Initialize DVC
dvc init
```

```
Output:
Initialized DVC repository.

You can now commit the changes to git.

+---------------------------------------------------------------------+
|                                                                     |
|        DVC has been initialized. Start tracking data.               |
|                                                                     |
+---------------------------------------------------------------------+
```

DVC creates a `.dvc/` directory (similar to git's `.git/` directory):

```
my-project/
├── .git/            # Git's internal files
├── .dvc/            # DVC's internal files
│   ├── config       # DVC configuration
│   └── .gitignore   # Files DVC should ignore
├── .dvcignore       # Files DVC should not track
└── your_code.py
```

### Step 2: Track a Dataset

```bash
# Add a data file to DVC tracking
dvc add data/training_data.csv
```

```
Output:
100% Add|████████████████████████████|1/1 [00:01, 1.23s/file]

To track the changes with git, run:

    git add data/training_data.csv.dvc data/.gitignore
```

This creates two things:

1. **data/training_data.csv.dvc** - A small pointer file that goes in git
2. **data/.gitignore** - Tells git to ignore the actual data file

### Understanding .dvc Files

```python
"""
understand_dvc.py - Understanding .dvc files.

A .dvc file is a small text file that contains a hash
(fingerprint) of your data. It is like a receipt that
describes what the data looks like without containing
the actual data.
"""

# Here is what a .dvc file looks like:
dvc_file_content = """
outs:
- md5: a1b2c3d4e5f6789012345678abcdef90
  size: 15234567
  hash: md5
  path: training_data.csv
"""

# Let us break it down:
print("What a .dvc file contains:")
print("=" * 50)
print()
print("  md5: a1b2c3d4e5f6...")
print("    -> A unique fingerprint of the data file")
print("    -> If even one byte changes, the md5 changes")
print("    -> Like a social security number for your data")
print()
print("  size: 15234567")
print("    -> The file size in bytes (about 15 MB)")
print()
print("  path: training_data.csv")
print("    -> The name of the data file")
print()
print("The .dvc file is tiny (a few bytes).")
print("The actual data file can be gigabytes.")
print("Git stores the .dvc file.")
print("DVC stores the actual data.")
```

```
Output:
What a .dvc file contains:
==================================================

  md5: a1b2c3d4e5f6...
    -> A unique fingerprint of the data file
    -> If even one byte changes, the md5 changes
    -> Like a social security number for your data

  size: 15234567
    -> The file size in bytes (about 15 MB)

  path: training_data.csv
    -> The name of the data file

The .dvc file is tiny (a few bytes).
The actual data file can be gigabytes.
Git stores the .dvc file.
DVC stores the actual data.
```

### Step 3: Commit to Git

```bash
# Add the .dvc file and .gitignore to git
git add data/training_data.csv.dvc data/.gitignore
git commit -m "Track training data with DVC"
```

---

## The DVC Workflow

```
+--------------------------------------------------+
|  DVC Workflow                                     |
|                                                   |
|  1. dvc add data/file.csv                        |
|     -> Creates file.csv.dvc (pointer)            |
|     -> Moves data to DVC cache (.dvc/cache)      |
|                                                   |
|  2. git add data/file.csv.dvc                    |
|     -> Commits the pointer to git                |
|                                                   |
|  3. dvc push                                     |
|     -> Uploads data to remote storage            |
|     -> (Like git push, but for data)             |
|                                                   |
|  4. (On another machine)                         |
|     git clone the-repo                           |
|     dvc pull                                     |
|     -> Downloads the data from remote            |
|     -> (Like git pull, but for data)             |
+--------------------------------------------------+
```

### Tracking Data Changes

When your data changes, DVC tracks the new version:

```bash
# You update the data file
# (add new rows, fix errors, etc.)

# Re-add to DVC
dvc add data/training_data.csv

# The .dvc file now has a new hash
git add data/training_data.csv.dvc
git commit -m "Update training data: added 500 new samples"

# Push data to remote
dvc push
```

### Going Back to Previous Data Versions

```bash
# See the history of data changes
git log data/training_data.csv.dvc

# Go back to a previous version
git checkout v1.0 -- data/training_data.csv.dvc
dvc checkout

# Now training_data.csv matches what it was in v1.0
```

---

## Reproducing Experiments

DVC can also track entire pipelines, not just individual files:

```python
"""
dvc_pipeline.py - Example of what a DVC pipeline does.

A DVC pipeline defines the steps to reproduce your
experiment: prepare data, train model, evaluate.

You define this in a file called dvc.yaml
"""

# Here is what a dvc.yaml pipeline looks like:
dvc_yaml_content = """
# dvc.yaml - Pipeline definition

stages:
  prepare:
    cmd: python src/prepare_data.py
    deps:
      - src/prepare_data.py
      - data/raw/dataset.csv
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/train.csv
    outs:
      - models/model.pkl
    params:
      - config.yaml:
          - model.n_estimators
          - model.max_depth

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/processed/test.csv
    metrics:
      - metrics.json:
          cache: false
"""

# Let us understand each part:
print("DVC Pipeline Stages")
print("=" * 55)
print()
print("Stage: prepare")
print("  cmd:  python src/prepare_data.py")
print("  deps: Files this stage needs (inputs)")
print("  outs: Files this stage creates (outputs)")
print()
print("Stage: train")
print("  cmd:    python src/train.py")
print("  deps:   Code + prepared data")
print("  outs:   Trained model file")
print("  params: Config values used (tracked for changes)")
print()
print("Stage: evaluate")
print("  cmd:     python src/evaluate.py")
print("  deps:    Code + model + test data")
print("  metrics: Results file (not cached, always readable)")
```

```
Output:
DVC Pipeline Stages
=======================================================

Stage: prepare
  cmd:  python src/prepare_data.py
  deps: Files this stage needs (inputs)
  outs: Files this stage creates (outputs)

Stage: train
  cmd:    python src/train.py
  deps:   Code + prepared data
  outs:   Trained model file
  params: Config values used (tracked for changes)

Stage: evaluate
  cmd:     python src/evaluate.py
  deps:    Code + model + test data
  metrics: Results file (not cached, always readable)
```

### Running the Pipeline

```bash
# Run the entire pipeline
dvc repro

# DVC automatically figures out which stages need to rerun
# If only the model parameters changed, it skips data preparation
```

```
Output:
Running stage 'prepare':
> python src/prepare_data.py
Generating lock file 'dvc.lock'

Running stage 'train':
> python src/train.py

Running stage 'evaluate':
> python src/evaluate.py

Use `dvc push` to send your updates to remote storage.
```

### Smart Re-execution

```
+--------------------------------------------------+
|  DVC Smart Re-execution                           |
|                                                   |
|  You change model parameters in config.yaml      |
|                                                   |
|  dvc repro checks:                               |
|  - prepare: deps unchanged -> SKIP (cached)      |
|  - train: params changed   -> RERUN              |
|  - evaluate: model changed -> RERUN              |
|                                                   |
|  Only reruns what is necessary!                  |
|  Saves time when data preparation is slow.       |
+--------------------------------------------------+
```

---

## Remote Storage

DVC remote storage is where your actual data files are stored. It is like GitHub for your data.

```
+--------------------------------------------------+
|  DVC Remote Storage Options                       |
|                                                   |
|  Amazon S3        -> dvc remote add -d myremote  |
|                      s3://my-bucket/dvc-storage  |
|                                                   |
|  Google Cloud     -> dvc remote add -d myremote  |
|                      gs://my-bucket/dvc-storage  |
|                                                   |
|  Azure Blob       -> dvc remote add -d myremote  |
|                      azure://my-container/dvc    |
|                                                   |
|  Local folder     -> dvc remote add -d myremote  |
|  (for testing)       /path/to/storage            |
|                                                   |
|  SSH server       -> dvc remote add -d myremote  |
|                      ssh://user@server/path      |
+--------------------------------------------------+
```

### Setting Up Remote Storage

```bash
# Add a remote (using local storage for this example)
dvc remote add -d myremote /tmp/dvc-storage

# Push data to remote
dvc push

# Pull data from remote (on another machine)
dvc pull
```

```
Output (dvc push):
2 files pushed

Output (dvc pull):
A       data/training_data.csv
A       models/model.pkl
2 files fetched
```

### How Remote Storage Works

```
+--------------------------------------------------+
|  DVC Remote Storage Flow                          |
|                                                   |
|  Your Machine:                                   |
|  +-------------------+   +-------------------+   |
|  | .dvc/cache/       |   | data/             |   |
|  | (local cache of   |   | training_data.csv |   |
|  |  all versions)    |   | (current version) |   |
|  +-------------------+   +-------------------+   |
|           |                                       |
|     dvc push / dvc pull                          |
|           |                                       |
|           v                                       |
|  Remote Storage (S3, GCS, etc.):                 |
|  +-------------------------------------------+   |
|  | All versions of all data files             |   |
|  | Shared across team members                 |   |
|  | Backed up and durable                      |   |
|  +-------------------------------------------+   |
+--------------------------------------------------+
```

---

## Complete DVC Workflow Example

```python
"""
complete_dvc_workflow.py - A complete DVC workflow example.

This shows the commands and Python code involved in
a typical DVC workflow.
"""

# The commands below are bash commands shown as strings
# for educational purposes.

workflow_steps = [
    {
        "step": "1. Initialize",
        "commands": [
            "git init",
            "dvc init",
            "git add .",
            'git commit -m "Initialize project with DVC"',
        ],
    },
    {
        "step": "2. Add data",
        "commands": [
            "dvc add data/training_data.csv",
            "git add data/training_data.csv.dvc data/.gitignore",
            'git commit -m "Add training data v1"',
        ],
    },
    {
        "step": "3. Set up remote",
        "commands": [
            "dvc remote add -d storage s3://my-bucket/dvc",
            "git add .dvc/config",
            'git commit -m "Configure DVC remote storage"',
            "dvc push",
        ],
    },
    {
        "step": "4. Train and track",
        "commands": [
            "python src/train.py",
            "dvc add models/model.pkl",
            "git add models/model.pkl.dvc",
            'git commit -m "Add trained model v1"',
            "git tag v1.0",
            "dvc push",
        ],
    },
    {
        "step": "5. Update data and retrain",
        "commands": [
            "# ... update training_data.csv ...",
            "dvc add data/training_data.csv",
            "python src/train.py",
            "dvc add models/model.pkl",
            "git add data/training_data.csv.dvc models/model.pkl.dvc",
            'git commit -m "Update data and retrain model v2"',
            "git tag v2.0",
            "dvc push",
        ],
    },
    {
        "step": "6. Reproduce old version",
        "commands": [
            "git checkout v1.0",
            "dvc checkout",
            "# Now data and model match v1.0!",
            "python src/evaluate.py",
        ],
    },
]

for step_info in workflow_steps:
    print(f"\n{step_info['step']}")
    print("-" * 40)
    for cmd in step_info["commands"]:
        print(f"  $ {cmd}")
```

```
Output:

1. Initialize
----------------------------------------
  $ git init
  $ dvc init
  $ git add .
  $ git commit -m "Initialize project with DVC"

2. Add data
----------------------------------------
  $ dvc add data/training_data.csv
  $ git add data/training_data.csv.dvc data/.gitignore
  $ git commit -m "Add training data v1"

3. Set up remote
----------------------------------------
  $ dvc remote add -d storage s3://my-bucket/dvc
  $ git add .dvc/config
  $ git commit -m "Configure DVC remote storage"
  $ dvc push

4. Train and track
----------------------------------------
  $ python src/train.py
  $ dvc add models/model.pkl
  $ git add models/model.pkl.dvc
  $ git commit -m "Add trained model v1"
  $ git tag v1.0
  $ dvc push

5. Update data and retrain
----------------------------------------
  $ # ... update training_data.csv ...
  $ dvc add data/training_data.csv
  $ python src/train.py
  $ dvc add models/model.pkl
  $ git add data/training_data.csv.dvc models/model.pkl.dvc
  $ git commit -m "Update data and retrain model v2"
  $ git tag v2.0
  $ dvc push

6. Reproduce old version
----------------------------------------
  $ git checkout v1.0
  $ dvc checkout
  $ # Now data and model match v1.0!
  $ python src/evaluate.py
```

---

## Common Mistakes

1. **Adding large data files to git.** Git is for code. DVC is for data. Never put large files in git.

2. **Forgetting to dvc push.** If you do not push, your data only exists on your machine. Teammates cannot access it.

3. **Not committing .dvc files.** The .dvc pointer files must be committed to git. Without them, DVC cannot find the data.

4. **Editing data without dvc add.** If you change a tracked file, you must run `dvc add` again to update the pointer.

5. **Not tagging versions.** Use git tags (v1.0, v2.0) to mark important versions so you can easily go back to them.

---

## Best Practices

1. **Always pair git commit with dvc push.** Keep code and data in sync.

2. **Use meaningful commit messages.** Describe what changed in the data, not just "update data."

3. **Tag important versions.** Use git tags for versions you might want to reproduce later.

4. **Set up remote storage early.** Do not wait until you have a problem to configure remote storage.

5. **Use DVC pipelines for reproducibility.** Define your entire workflow in dvc.yaml so anyone can reproduce it.

---

## Quick Summary

DVC (Data Version Control) extends git to handle large data files. It creates small pointer files (.dvc files) that git tracks, while the actual data is stored in a separate cache and remote storage. This lets you version data alongside code, reproduce experiments with exact data, and share datasets with your team.

---

## Key Points

- DVC tracks large data files that do not belong in git
- .dvc files are small pointers that go in git; actual data goes in DVC storage
- dvc add tracks a file; dvc push uploads it to remote storage
- dvc pull downloads data from remote storage
- git checkout + dvc checkout restores data for any version
- DVC pipelines (dvc.yaml) define reproducible workflows
- DVC supports S3, GCS, Azure, SSH, and local storage

---

## Practice Questions

1. Why is git not suitable for tracking large data files?

2. What information does a .dvc file contain?

3. Explain the difference between `dvc push` and `git push`.

4. How would you go back to a previous version of your training data?

5. What is the purpose of a DVC pipeline defined in dvc.yaml?

---

## Exercises

### Exercise 1: Basic DVC Setup

Initialize a DVC project, track a CSV file, and set up a local remote. Verify you can push and pull the data.

### Exercise 2: Data Version History

Create a dataset, track it with DVC, then make three updates. Tag each version. Practice switching between versions and verify the data matches.

### Exercise 3: Reproducible Pipeline

Create a DVC pipeline (dvc.yaml) with three stages:
1. Data preparation (clean raw data)
2. Model training (train on cleaned data)
3. Evaluation (generate metrics)

Run `dvc repro` and verify that changing only the model parameters skips the data preparation stage.

---

## What Is Next?

You can now version your data alongside your code. But where do your trained models go? In Chapter 11, we will learn about the MLflow Model Registry, a centralized place to manage model versions, track their status (staging, production, archived), and promote models through a controlled workflow.
