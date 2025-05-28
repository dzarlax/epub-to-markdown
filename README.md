# EPUB to Markdown Converter

A web application for converting EPUB files to clean Markdown format while preserving formatting and removing images and specific tags.

## 🚀 Features

- **Simple web interface** with drag & drop support
- **Preserves text formatting** (headers, italic, bold, lists)
- **Automatic cleanup** of images, scripts, and styles
- **Removes specific HTML tags** for clean text output
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

1. **Upload an EPUB file:**
   - Drag and drop the file into the upload area
   - Or click on the area and select a file

2. **Click "Convert to Markdown"**

3. **Download the ready Markdown file**

## 🔧 What the Converter Does

### ✅ Preserves:
- Text structure (headers, paragraphs)
- Formatting (bold, italic, underline)
- Lists (numbered and bulleted)
- Links (if present)
- Book metadata

### ❌ Removes:
- Images and media content
- CSS styles and JavaScript
- Specific HTML attributes
- Extra spaces and line breaks
- Advertising blocks and navigation

## 📁 Project Structure

```
epub-to-markdown/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
├── templates/
│   └── index.html     # Web interface
├── uploads/           # Temporary uploaded files
└── output/            # Ready Markdown files
```

## 🔍 Technical Details

### Used Libraries:
- **Flask** - web framework
- **ebooklib** - EPUB file handling
- **BeautifulSoup4** - HTML parsing
- **html2text** - HTML to Markdown conversion
- **lxml** - XML/HTML parser

### Conversion Algorithm:
1. Reading EPUB file and extracting metadata
2. Processing all HTML documents in correct order
3. Cleaning HTML from unnecessary tags and attributes
4. Converting to Markdown while preserving structure
5. Additional cleanup and formatting

## ⚙️ Configuration

In the `app.py` file you can modify:

- **Maximum file size:** `MAX_CONTENT_LENGTH = 16 * 1024 * 1024` (16MB)
- **Server port:** `port=5000`
- **Allowed HTML attributes:** `allowed_attrs = ['href', 'title']`

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### EPUB processing error
- Make sure the file is not corrupted
- Verify it's actually an EPUB file
- Try a different EPUB file

### Encoding issues
- The application supports UTF-8
- Make sure your EPUB file uses correct encoding

## 📝 Usage Examples

### Command line (alternative method):
If you need to process a file without the web interface, you can use functions directly:

```python
from app import epub_to_markdown

# Convert file
markdown_content = epub_to_markdown('path/to/your/book.epub')

# Save result
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)
```

## 🤝 Contributing

If you want to improve the project:

1. Fork the repository
2. Make changes
3. Test functionality
4. Submit a pull request

## 📄 License

This project is distributed under the MIT License. You are free to use, modify, and distribute the code.

## 🆘 Support

If you have questions or issues:

1. Check the "Troubleshooting" section
2. Make sure all dependencies are installed
3. Check console logs for detailed error information

---

**Happy converting! 📚→📝** 