# EPUB ⇄ Markdown Converter

A web application for bidirectional conversion between EPUB files and Markdown format while preserving formatting and structure.

## 🚀 Features

- **Bidirectional conversion** - EPUB ↔ Markdown ↔ TXT
- **Simple web interface** with drag & drop support
- **Automatic format detection** and conversion direction
- **Preserves text formatting** (headers, italic, bold, lists)
- **Smart chapter creation** from Markdown headers
- **Automatic cleanup** of images, scripts, and styles (EPUB → Markdown)
- **Preserves book metadata** (title, author)
- **Cyrillic and Unicode support**
- **Modern interface design**

## 📋 Requirements

- Python 3.7+
- pip (Python package manager)

## 🛠 Installation

1. **Clone the repository or download files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Running the Application

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## 📖 Usage

1. **Upload a file:**
   - Drag and drop the file into the upload area
   - Or click on the area and select a file
   - Supported formats: `.epub`, `.md`, `.markdown`, `.txt`

2. **Automatic conversion detection:**
   - EPUB files → Convert to Markdown
   - Markdown files → Convert to EPUB
   - TXT files → Convert to EPUB

3. **Download the converted file**

## 🔧 Conversion Types

### 📚 EPUB → 📝 Markdown
- ✅ Preserves text structure (headers, paragraphs)
- ✅ Maintains formatting (bold, italic, underline)
- ✅ Keeps lists (numbered and bulleted)
- ✅ Preserves links
- ✅ Extracts metadata
- ❌ Removes images and media content
- ❌ Removes CSS styles and JavaScript
- ❌ Cleans specific HTML attributes

### 📝 Markdown → 📚 EPUB
- ✅ Creates chapters from headers (`#` and `##`)
- ✅ Converts Markdown formatting to HTML
- ✅ Generates table of contents
- ✅ Adds proper EPUB structure
- ✅ Includes CSS styling for readability
- ✅ Supports code blocks and quotes
- ✅ Auto-detects title and author from content

### 📄 TXT → 📚 EPUB
- ✅ Converts plain text to EPUB format
- ✅ Creates single chapter or splits by paragraphs
- ✅ Adds basic formatting and structure

## 📁 Project Structure

```
epub-to-markdown/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
├── test_book.md       # Sample Markdown file for testing
├── templates/
│   └── index.html     # Web interface
├── uploads/           # Temporary uploaded files
└── output/            # Ready converted files
```

## 🔍 Technical Details

### Used Libraries:
- **Flask** - web framework
- **ebooklib** - EPUB file handling
- **BeautifulSoup4** - HTML parsing
- **html2text** - HTML to Markdown conversion
- **markdown** - Markdown to HTML conversion
- **python-slugify** - URL-safe string generation
- **lxml** - XML/HTML parser

### Conversion Algorithms:

#### EPUB → Markdown:
1. Reading EPUB file and extracting metadata
2. Processing all HTML documents in correct order
3. Cleaning HTML from unnecessary tags and attributes
4. Converting to Markdown while preserving structure
5. Additional cleanup and formatting

#### Markdown → EPUB:
1. Parsing Markdown content and extracting metadata
2. Splitting content into chapters by headers
3. Converting Markdown to HTML with extensions
4. Creating EPUB structure with proper navigation
5. Adding CSS styles for better readability
6. Generating table of contents

## ⚙️ Configuration

In the `app.py` file you can modify:

- **Maximum file size:** `MAX_CONTENT_LENGTH = 16 * 1024 * 1024` (16MB)
- **Server port:** `port=5000`
- **Allowed file extensions:** `ALLOWED_EXTENSIONS = {'epub', 'md', 'markdown', 'txt'}`
- **Allowed HTML attributes:** `allowed_attrs = ['href', 'title']`

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### File processing error
- Make sure the file is not corrupted
- Verify the file format is supported
- Check file size (max 16MB)
- Try a different file

### Encoding issues
- The application supports UTF-8
- Make sure your files use correct encoding

## 📝 Usage Examples

### Command line (alternative method):
If you need to process files without the web interface:

```python
from app import epub_to_markdown, markdown_to_epub
import ebooklib

# EPUB to Markdown
markdown_content = epub_to_markdown('path/to/book.epub')
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

# Markdown to EPUB
book = markdown_to_epub('path/to/document.md')
ebooklib.epub.write_epub('output.epub', book, {})
```

### Testing with sample file:
```bash
# Test Markdown to EPUB conversion
python test_converter.py test_book.md
```

## 🤝 Contributing

If you want to improve the project:

1. Fork the repository
2. Make changes
3. Test functionality with both conversion directions
4. Submit a pull request

## 📄 License

This project is distributed under the MIT License. You are free to use, modify, and distribute the code.

## 🆘 Support

If you have questions or issues:

1. Check the "Troubleshooting" section
2. Make sure all dependencies are installed
3. Test with the provided sample files
4. Check console logs for detailed error information

---

**Happy converting! 📚⇄📝** 