# Academic Formatting for LazyScholar

This feature enhances LazyScholar by automatically formatting the final research paper as a proper academic paper with citations and references.

## Features

- Transforms the basic research paper into a properly formatted academic paper
- Adds in-text citations in APA format
- Formats references according to academic standards
- Organizes content into proper academic sections
- Maintains all original research content while improving presentation

## Requirements

- Python 3.6+
- Google Generative AI API key (Gemini model)
- Required packages: `google-generativeai`, `python-dotenv`

## Setup

1. Install required packages:
   ```
   pip install google-generativeai python-dotenv
   ```

2. Set up your Google API key in a `.env` file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

3. Run the setup script:
   ```
   python setup_academic_format.py
   ```

## Usage

### Option 1: Format while generating a new research paper

Run LazyScholar with the `--academic-format` flag:

```
python lazy_scholar.py --problem-statement "Your research topic" --academic-format
```

This will:
1. Conduct the research as usual
2. Generate the standard final paper
3. Automatically format it as an academic paper

### Option 2: Format an existing research paper

If you've already generated a research paper and want to format it academically:

```
python lazy_scholar.py --problem-statement "Your research topic" --regenerate-final-paper --academic-format
```

This will:
1. Regenerate the final paper from existing subtopic files
2. Format it as an academic paper

### Option 3: Format a specific paper manually

You can also format any paper manually using the academic formatter directly:

```
python academic_formatter.py --input path/to/your/paper.md
```

## Output

The formatted academic paper will be saved as `final_paper_academic_format.md` in the research output directory.

## How It Works

1. The formatter extracts references from the original paper
2. It uses the Gemini AI model to reformat the paper with:
   - Proper academic sections (Abstract, Introduction, Literature Review, etc.)
   - In-text citations in APA format
   - Properly formatted references
   - Academic styling and organization

## Troubleshooting

- **API Key Issues**: Ensure your Google API key is correctly set in the `.env` file
- **Missing Packages**: Run `pip install -r requirements.txt` to install all dependencies
- **Formatting Errors**: Check the `academic_formatter.log` file for detailed error messages

## Customization

You can modify the `academic_formatter.py` script to change:
- Citation style (currently APA)
- Paper sections and organization
- Formatting preferences

## Contributing

Contributions to improve the academic formatting feature are welcome! Please submit a pull request or open an issue to suggest enhancements. 