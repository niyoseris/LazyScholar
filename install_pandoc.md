# Installing Pandoc on macOS

Pandoc is required for the Markdown to EPUB converter script to work. Here are the instructions to install it on macOS:

## Option 1: Using Homebrew (Recommended)

If you have [Homebrew](https://brew.sh/) installed, you can install pandoc with:

```bash
brew install pandoc
```

## Option 2: Using the Installer Package

1. Go to the [Pandoc releases page](https://github.com/jgm/pandoc/releases/latest)
2. Download the macOS installer package (e.g., `pandoc-X.XX-macOS.pkg`)
3. Open the downloaded file and follow the installation instructions

## Option 3: Using MacPorts

If you use MacPorts, you can install pandoc with:

```bash
sudo port install pandoc
```

## Verifying the Installation

After installation, verify that pandoc is correctly installed by running:

```bash
pandoc --version
```

This should display the version information for pandoc.

## Additional Information

For more details on installing pandoc, visit the official documentation:
[https://pandoc.org/installing.html](https://pandoc.org/installing.html) 