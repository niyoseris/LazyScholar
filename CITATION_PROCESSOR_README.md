# Citation Processor and Research Workflow

This set of tools helps you process academic PDFs, extract citations and key points, and build structured research papers through a systematic workflow.

## Overview

The workflow consists of the following steps:

1. **Process PDF files**: Send PDFs to a language model to extract citation information and key points
2. **Create subtopic sketches**: Collect the extracted information into JSON sketch files
3. **Generate subtopic papers**: Send the sketch files to the language model to generate research papers for each subtopic
4. **Combine into topic papers**: Combine subtopic papers into comprehensive topic papers
5. **Create final paper**: Combine topic papers into a complete research paper

## Requirements

- Python 3.7+
- Google Gemini API key (set as `GOOGLE_API_KEY` in a `.env` file)
- Required Python packages:
  - google-generativeai
  - PyPDF2
  - pdfplumber
  - python-dotenv
  - requests

## Installation

1. Clone this repository or download the scripts
2. Install required packages:
   ```
   pip install google-generativeai PyPDF2 pdfplumber python-dotenv requests
   ```
3. Create a `.env` file in the same directory as the scripts with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Using the Research Workflow Script

The `research_workflow.py` script provides a user-friendly interface to execute the research workflow. It has three main modes of operation:

#### 1. Subtopic Mode

Process PDFs for a single subtopic:

```bash
python research_workflow.py --mode subtopic --subtopic "Your Subtopic Name" --pdf_dir path/to/pdfs --output_dir research_output
```

#### 2. Topic Mode

Process multiple subtopics for a topic:

```bash
python research_workflow.py --mode topic --topic "Your Topic Name" --subtopics "Subtopic 1" "Subtopic 2" "Subtopic 3" --pdfs_base_dir path/to/pdfs_base_dir --output_dir research_output
```

For this mode, the PDFs should be organized in subdirectories named after each subtopic under the `pdfs_base_dir`.

#### 3. Paper Mode

Combine multiple topic papers into a final research paper:

```bash
python research_workflow.py --mode paper --title "Your Research Paper Title" --topics "Topic 1" "Topic 2" "Topic 3" --output_dir research_output
```

### Using the Citation Processor Directly

You can also use the `citation_processor.py` script directly for more fine-grained control:

```bash
python citation_processor.py --pdf_dir path/to/pdfs --subtopic "Your Subtopic Name" --output_dir research_output
```

Or to combine subtopic papers into a topic paper:

```bash
python citation_processor.py --output_dir research_output --topic "Your Topic Name"
```

Or to combine topic papers into a final paper:

```bash
python citation_processor.py --output_dir research_output --title "Your Research Paper Title"
```

## Directory Structure

For best results, organize your PDFs in the following structure:

```
research_project/
├── pdfs/
│   ├── Topic 1/
│   │   ├── Subtopic 1/
│   │   │   ├── paper1.pdf
│   │   │   ├── paper2.pdf
│   │   │   └── ...
│   │   ├── Subtopic 2/
│   │   │   ├── paper1.pdf
│   │   │   ├── paper2.pdf
│   │   │   └── ...
│   │   └── ...
│   ├── Topic 2/
│   │   ├── Subtopic 1/
│   │   │   ├── paper1.pdf
│   │   │   ├── paper2.pdf
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── research_output/
    └── (output files will be saved here)
```

## Output Files

The scripts generate the following types of output files:

- **Subtopic sketch files**: JSON files containing extracted information from PDFs (`subtopic_name_sketch.json`)
- **Subtopic paper files**: Markdown files containing generated research papers for each subtopic (`subtopic_name_paper.md`)
- **Topic paper files**: Markdown files containing combined research papers for each topic (`topic_name_paper.md`)
- **Final paper file**: Markdown file containing the complete research paper (`paper_title_final_paper.md`)

## Example Workflow

Here's an example of a complete workflow for a research project on "Climate Change":

1. Organize PDFs in the appropriate directory structure
2. Process each subtopic:
   ```bash
   python research_workflow.py --mode subtopic --subtopic "Sea Level Rise" --pdf_dir pdfs/Climate_Change/Sea_Level_Rise --output_dir research_output
   python research_workflow.py --mode subtopic --subtopic "Extreme Weather" --pdf_dir pdfs/Climate_Change/Extreme_Weather --output_dir research_output
   python research_workflow.py --mode subtopic --subtopic "Carbon Emissions" --pdf_dir pdfs/Climate_Change/Carbon_Emissions --output_dir research_output
   ```
3. Combine subtopics into a topic paper:
   ```bash
   python research_workflow.py --mode topic --topic "Climate Change" --subtopics "Sea Level Rise" "Extreme Weather" "Carbon Emissions" --pdfs_base_dir pdfs/Climate_Change --output_dir research_output
   ```
4. If you have multiple topics, combine them into a final paper:
   ```bash
   python research_workflow.py --mode paper --title "Environmental Challenges in the 21st Century" --topics "Climate Change" "Biodiversity Loss" "Pollution" --output_dir research_output
   ```

## Troubleshooting

- **PDF extraction issues**: If text extraction from PDFs fails, try converting the PDFs to text using other tools before processing
- **API rate limits**: If you encounter API rate limits, the scripts include retry logic with exponential backoff
- **Memory issues**: For very large PDFs, the scripts limit the amount of text sent to the language model to avoid token limits

## License

This project is licensed under the MIT License - see the LICENSE file for details. 