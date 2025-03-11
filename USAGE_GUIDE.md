# Markdown to EPUB Converter - Usage Guide

This guide explains how to use the Markdown to EPUB converter to convert your academic papers and other Markdown files to EPUB format for reading on your e-book reader.

## Quick Start

The easiest way to convert a Markdown file to EPUB is to use the wrapper script:

```bash
./convert_md_to_epub.sh your_file.md
```

This will create an EPUB file with the same name as your Markdown file (e.g., `your_file.epub`).

## Adding Metadata

To add metadata like title and author to your EPUB:

```bash
./convert_md_to_epub.sh your_file.md -t "Your Title" -a "Your Name"
```

## Specifying Output File

To specify the output file name:

```bash
./convert_md_to_epub.sh your_file.md -o output.epub
```

## Converting Academic Papers

For your academic papers in the MusicTeaching directory:

```bash
./convert_md_to_epub.sh MusicTeaching/your_paper.md -o your_paper.epub -t "Paper Title" -a "Your Name"
```

## Combining Multiple Files

If you have a paper split across multiple Markdown files, you can combine them into a single EPUB:

```bash
./convert_md_to_epub.sh chapter1.md chapter2.md chapter3.md --combine -o combined.epub -t "Combined Paper" -a "Your Name"
```

## Adding a Cover Image

If you have a cover image for your e-book:

```bash
./convert_md_to_epub.sh your_file.md -c cover.jpg
```

## Converting Multiple Files at Once

You can convert multiple files by using shell wildcards:

```bash
# Convert all Markdown files in the current directory
./convert_md_to_epub.sh *.md --combine -o all_papers.epub

# Convert all Markdown files in the MusicTeaching directory
./convert_md_to_epub.sh MusicTeaching/*.md --combine -o all_music_papers.epub
```

## Markdown Formatting Support

The converter now has enhanced support for Markdown formatting. Your academic papers will look great on your e-book reader with proper formatting for:

- **Bold text** (using `**bold**` or `__bold__`)
- *Italic text* (using `*italic*` or `_italic_`)
- ~~Strikethrough text~~ (using `~~strikethrough~~`)
- Lists (ordered and unordered)
- Tables
- Code blocks with syntax highlighting
- Blockquotes
- And much more!

All these formatting elements will be properly converted to EPUB format with appropriate styling.

## Tips for Better Results

1. **Proper Heading Structure**: Make sure your Markdown files use proper heading levels (# for h1, ## for h2, etc.) for the best table of contents.

2. **First Heading as Title**: The first heading (# Title) in your Markdown file will be used as the title of the chapter or document if you don't specify a title with the `-t` option.

3. **Images**: If your Markdown files include images, make sure the image paths are correct. Relative paths are recommended.

4. **UTF-8 Encoding**: Save your Markdown files with UTF-8 encoding to ensure proper handling of special characters.

5. **Formatting**: Use standard Markdown formatting for the best results. The converter supports a wide range of Markdown extensions.

## Troubleshooting

If you encounter any issues:

1. Make sure the virtual environment is activated (the wrapper script handles this automatically).
2. Check that your Markdown files are properly formatted.
3. If images are not displaying, check the image paths in your Markdown files.
4. If formatting is not appearing correctly, make sure you're using standard Markdown syntax.

## Advanced Usage

For more advanced options, you can run the Python script directly:

```bash
source md2epub_venv/bin/activate
python md2epub.py --help
deactivate
```

This will show all available options for the converter. 