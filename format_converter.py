#!/usr/bin/env python3
"""
Format Converter - A tool to convert LazyScholar's markdown files to various formats

This script:
1. Takes a markdown file and converts it to the requested format
2. Supported formats: PDF, HTML, EPUB, DOCX
3. Uses pandoc for the conversion if available, otherwise falls back to Python libraries
"""

import os
import logging
import subprocess
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class FormatConverter:
    """Class to handle conversion of markdown files to various formats"""
    
    SUPPORTED_FORMATS = ['md', 'pdf', 'html', 'epub', 'docx', 'txt']
    
    def __init__(self):
        """Initialize the converter"""
        self.has_pandoc = self._check_pandoc()
        
    def _check_pandoc(self):
        """Check if pandoc is installed"""
        try:
            subprocess.run(['pandoc', '--version'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            logger.info("Pandoc is available for document conversion")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("Pandoc not found. Will use Python libraries for conversion when possible.")
            return False
            
    def convert_file(self, input_path, output_format):
        """
        Convert a file to the specified format
        
        Args:
            input_path (str): Path to the input file
            output_format (str): Format to convert to (pdf, html, epub, docx, txt)
            
        Returns:
            str: Path to the converted file, or None if conversion failed
        """
        input_path = Path(input_path)
        
        # If the format is already markdown and that's what was requested, just return the input path
        if input_path.suffix.lower() == '.md' and output_format == 'md':
            return str(input_path)
            
        # Create the output path with the new extension
        output_path = input_path.with_suffix(f'.{output_format}')
        
        # Ensure the output format is supported
        if output_format not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported output format: {output_format}")
            return None
            
        # Try to convert using pandoc if available
        if self.has_pandoc:
            return self._convert_with_pandoc(input_path, output_path, output_format)
        else:
            return self._convert_with_libraries(input_path, output_path, output_format)
    
    def _convert_with_pandoc(self, input_path, output_path, output_format):
        """Convert a file using pandoc"""
        try:
            cmd = ['pandoc', str(input_path), '-o', str(output_path)]
            
            # Add specific options for different formats
            if output_format == 'pdf':
                cmd.extend(['--pdf-engine=xelatex'])
            elif output_format == 'epub':
                cmd.extend(['--toc', '--epub-cover-image=cover.png'])
                
            # Run the conversion
            logger.info(f"Converting {input_path} to {output_format} using pandoc")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Verify the output file exists
            if output_path.exists():
                logger.info(f"Conversion successful: {output_path}")
                return str(output_path)
            else:
                logger.error("Pandoc did not produce an output file")
                return None
                
        except subprocess.SubprocessError as e:
            logger.error(f"Error converting with pandoc: {e}")
            return self._convert_with_libraries(input_path, output_path, output_format)
    
    def _convert_with_libraries(self, input_path, output_path, output_format):
        """Convert a file using Python libraries when pandoc is not available"""
        try:
            # Read the markdown content
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                
            if output_format == 'html':
                return self._convert_to_html(markdown_content, output_path)
            elif output_format == 'pdf':
                return self._convert_to_pdf(markdown_content, output_path)
            elif output_format == 'txt':
                return self._convert_to_txt(markdown_content, output_path)
            elif output_format == 'epub' or output_format == 'docx':
                logger.error(f"Cannot convert to {output_format} without pandoc")
                return None
            else:
                logger.error(f"Unsupported format for library conversion: {output_format}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting with libraries: {e}")
            return None
    
    def _convert_to_html(self, markdown_content, output_path):
        """Convert markdown to HTML using Python libraries"""
        try:
            # Try using markdown library if available
            import markdown
            html = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
            
            # Add basic HTML structure
            full_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Research Paper</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6; 
                        max-width: 900px; 
                        margin: 0 auto; 
                        padding: 20px; 
                    }}
                    h1, h2, h3 {{ color: #333; }}
                    code {{ 
                        background-color: #f4f4f4; 
                        padding: 2px 5px; 
                        border-radius: 3px; 
                    }}
                    pre {{ 
                        background-color: #f4f4f4; 
                        padding: 10px; 
                        border-radius: 5px; 
                        overflow-x: auto; 
                    }}
                    blockquote {{ 
                        border-left: 4px solid #ddd; 
                        padding-left: 15px; 
                        color: #666; 
                    }}
                    table {{ 
                        border-collapse: collapse; 
                        width: 100%; 
                    }}
                    table, th, td {{ 
                        border: 1px solid #ddd; 
                        padding: 8px; 
                    }}
                    tr:nth-child(even) {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            # Write the HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
                
            logger.info(f"Converted to HTML: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.error("Failed to convert to HTML: markdown library not found")
            return None
            
    def _convert_to_pdf(self, markdown_content, output_path):
        """Convert markdown to PDF using Python libraries"""
        try:
            # First convert to HTML
            html_path = output_path.with_suffix('.html')
            if self._convert_to_html(markdown_content, html_path):
                # Then try to convert HTML to PDF
                try:
                    import weasyprint
                    weasyprint.HTML(str(html_path)).write_pdf(str(output_path))
                    logger.info(f"Converted to PDF: {output_path}")
                    return str(output_path)
                except ImportError:
                    logger.error("Failed to convert to PDF: weasyprint library not found")
                    return None
            return None
        except Exception as e:
            logger.error(f"Error converting to PDF: {e}")
            return None
    
    def _convert_to_txt(self, markdown_content, output_path):
        """Convert markdown to plain text"""
        try:
            # Simple conversion - remove markdown formatting
            plain_text = markdown_content
            
            # Remove headers (#)
            import re
            plain_text = re.sub(r'^#+ ', '', plain_text, flags=re.MULTILINE)
            
            # Remove bold and italic markers
            plain_text = re.sub(r'\*\*|\*|__|\|_', '', plain_text)
            
            # Write the text file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
                
            logger.info(f"Converted to plain text: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error converting to TXT: {e}")
            return None


def convert_file(input_path, output_format):
    """Convenience function to convert a file to the specified format"""
    converter = FormatConverter()
    return converter.convert_file(input_path, output_format)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert markdown files to various formats")
    parser.add_argument("input", help="Input markdown file path")
    parser.add_argument("format", choices=FormatConverter.SUPPORTED_FORMATS, 
                       help="Output format (pdf, html, epub, docx, txt)")
    
    args = parser.parse_args()
    
    result = convert_file(args.input, args.format)
    
    if result:
        print(f"Conversion successful: {result}")
    else:
        print("Conversion failed") 