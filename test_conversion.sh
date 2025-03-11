#!/bin/bash
# Test script for md_to_epub.py

# Make sure the script is executable
chmod +x md_to_epub.py

# Create a test directory
mkdir -p test_output

echo "Testing single file conversion..."
python md_to_epub.py example.md -o test_output/example.epub -t "Example Document" -a "Test Author"
echo ""

echo "Testing with custom CSS..."
python md_to_epub.py example.md -o test_output/example_custom_css.epub -t "Example with Custom CSS" -a "Test Author" --css custom_style.css
echo ""

# Create multiple test files
echo "Creating test chapter files..."
cat > chapter1.md << 'EOF'
# Chapter 1: Introduction

This is the first chapter of our test book.

## Section 1.1

This is a section in the first chapter.

## Section 1.2

This is another section in the first chapter.
EOF

cat > chapter2.md << 'EOF'
# Chapter 2: Development

This is the second chapter of our test book.

## Section 2.1

This is a section in the second chapter.

## Section 2.2

This is another section in the second chapter.
EOF

cat > chapter3.md << 'EOF'
# Chapter 3: Conclusion

This is the third chapter of our test book.

## Section 3.1

This is a section in the third chapter.

## Section 3.2

This is another section in the third chapter.
EOF

echo "Testing multiple file conversion..."
python md_to_epub.py chapter1.md chapter2.md chapter3.md -o test_output -t "Test Book" -a "Test Author"
echo ""

echo "Testing combining multiple files..."
python md_to_epub.py chapter1.md chapter2.md chapter3.md --combine -o test_output/combined_book.epub -t "Combined Test Book" -a "Test Author"
echo ""

echo "All tests completed. Check the test_output directory for results." 