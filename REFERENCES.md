# Enhanced References in LazyScholar

LazyScholar now includes an enhanced references system that automatically generates detailed academic citations in the final research paper.

## Features

- **Automatic Citation Enhancement**: The system automatically converts simple source references into properly formatted academic citations in APA style.
- **PDF Filename Integration**: The system uses available PDF filenames to infer publication details when generating citations.
- **Fallback Mechanism**: If citation enhancement fails, the system falls back to the original reference format.
- **Integrated in Final Paper Generation**: Enhanced references are automatically included when generating the final paper.

## How It Works

1. When generating the final paper, LazyScholar collects all references from subtopic files.
2. For each reference, it extracts the topic, subtopic, and source information.
3. It then uses the Gemini AI model to convert the simple source references into properly formatted academic citations.
4. The enhanced citations are included in the "References" section of the final paper.

## Example

Original reference format:
```
Multiple sources: [Source 1, Source 2, Source 3]
```

Enhanced reference format:
```
[Author, A. A.]. (2025). [Title of paper]. arXiv:2502.17400. [inferred]
[Author, A. A.]. (2019). [Title of paper]. arXiv:1911.08576. [inferred]
[Author, A. A.]. (2025). [Title of paper]. arXiv:2502.18363. [inferred]
```

## Usage

The enhanced references feature is automatically used when generating the final paper. You can regenerate the final paper with enhanced references using the following command:

```bash
python3 lazy_scholar.py --regenerate-final-paper "your research topic"
```

## Standalone Enhancement Tool

You can also use the standalone `enhance_references.py` script to enhance references in an existing final paper:

```bash
python3 enhance_references.py
```

This script will:
1. Read the existing final paper
2. Extract and enhance the references
3. Create a new file with enhanced references

## Limitations

- The system infers citation details from available information, which may not be complete.
- For arXiv preprints, the system uses the arXiv ID to infer the publication year and creates placeholder author and title information.
- Citations marked with [inferred] indicate that some details were inferred and should be verified before using in formal academic work.

## Future Improvements

- Integration with academic databases to retrieve more accurate citation information
- Support for different citation styles (MLA, Chicago, etc.)
- Ability to extract author and title information directly from PDF content
- Option to customize citation format preferences 