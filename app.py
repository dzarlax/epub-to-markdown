import os
import tempfile
import zipfile
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import html2text
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'epub'}

# Создаем необходимые директории
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_html_content(html_content):
    """Очищает HTML контент от ненужных тегов и элементов"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Удаляем скрипты, стили, изображения
    for tag in soup(['script', 'style', 'img', 'svg', 'figure']):
        tag.decompose()
    
    # Удаляем специфические атрибуты
    for tag in soup.find_all():
        # Сохраняем только основные атрибуты для форматирования
        allowed_attrs = ['href', 'title']
        attrs_to_remove = []
        for attr in tag.attrs:
            if attr not in allowed_attrs:
                attrs_to_remove.append(attr)
        for attr in attrs_to_remove:
            del tag[attr]
    
    return str(soup)

def epub_to_markdown(epub_path):
    """Конвертирует EPUB файл в Markdown"""
    try:
        book = epub.read_epub(epub_path)
        markdown_content = []
        
        # Получаем метаданные
        title = book.get_metadata('DC', 'title')
        author = book.get_metadata('DC', 'creator')
        
        if title:
            markdown_content.append(f"# {title[0][0]}\n")
        if author:
            markdown_content.append(f"**Автор:** {author[0][0]}\n\n")
        
        markdown_content.append("---\n\n")
        
        # Настройка html2text
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_links = False
        h.body_width = 0  # Отключаем перенос строк
        h.unicode_snob = True
        h.escape_snob = True
        
        # Обрабатываем все HTML документы в правильном порядке
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                
                # Очищаем HTML
                cleaned_content = clean_html_content(content)
                
                # Конвертируем в Markdown
                markdown_text = h.handle(cleaned_content)
                
                # Дополнительная очистка
                markdown_text = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_text)  # Убираем лишние пустые строки
                markdown_text = re.sub(r'^\s+', '', markdown_text, flags=re.MULTILINE)  # Убираем начальные пробелы
                
                if markdown_text.strip():
                    markdown_content.append(markdown_text)
                    markdown_content.append("\n\n---\n\n")
        
        return '\n'.join(markdown_content)
    
    except Exception as e:
        raise Exception(f"Ошибка при конвертации EPUB: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Файл не выбран')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            epub_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(epub_path)
            
            # Конвертируем в Markdown
            markdown_content = epub_to_markdown(epub_path)
            
            # Сохраняем результат
            output_filename = f"{os.path.splitext(filename)[0]}.md"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Удаляем загруженный файл
            os.remove(epub_path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            flash(f'Ошибка при обработке файла: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Разрешены только EPUB файлы')
        return redirect(url_for('index'))

@app.route('/convert', methods=['POST'])
def convert_file():
    """AJAX endpoint для конвертации файлов"""
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            epub_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(epub_path)
            
            # Конвертируем в Markdown
            markdown_content = epub_to_markdown(epub_path)
            
            # Сохраняем результат
            output_filename = f"{os.path.splitext(filename)[0]}.md"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # Удаляем загруженный файл
            os.remove(epub_path)
            
            return jsonify({
                'success': True,
                'filename': output_filename,
                'size': len(markdown_content)
            })
        
        except Exception as e:
            return jsonify({'error': f'Ошибка при обработке файла: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Разрешены только EPUB файлы'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    """Скачивание готового файла"""
    try:
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True, download_name=filename)
        else:
            flash('Файл не найден')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Ошибка при скачивании: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 