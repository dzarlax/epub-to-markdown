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
import markdown
from slugify import slugify
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'epub', 'md', 'markdown', 'txt'}

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
                # Добавляем удаление текста в квадратных скобках, который может быть сносками
                markdown_text = re.sub(r'\[.*?\]', '', markdown_text) # Удаляем текст в квадратных скобках, например [1], [текст]
                
                if markdown_text.strip():
                    markdown_content.append(markdown_text)
                    markdown_content.append("\n\n---\n\n")
        
        return '\n'.join(markdown_content)
    
    except Exception as e:
        raise Exception(f"Ошибка при конвертации EPUB: {str(e)}")

def markdown_to_epub(markdown_path, title=None, author=None):
    """Конвертирует Markdown файл в EPUB"""
    try:
        # Читаем Markdown файл
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Извлекаем метаданные из начала файла, если они есть
        lines = markdown_content.split('\n')
        extracted_title = title
        extracted_author = author
        
        # Ищем заголовок и автора в первых строках
        for i, line in enumerate(lines[:10]):
            if line.startswith('# ') and not extracted_title:
                extracted_title = line[2:].strip()
            elif line.startswith('**Автор:**') or line.startswith('**Author:**'):
                extracted_author = line.split(':', 1)[1].strip()
        
        # Устанавливаем значения по умолчанию
        if not extracted_title:
            extracted_title = os.path.splitext(os.path.basename(markdown_path))[0]
        if not extracted_author:
            extracted_author = "Неизвестный автор"
        
        # Создаем EPUB книгу
        book = epub.EpubBook()
        
        # Устанавливаем метаданные
        book.set_identifier(f'id-{slugify(extracted_title)}-{datetime.now().strftime("%Y%m%d")}')
        book.set_title(extracted_title)
        book.set_language('ru')
        book.add_author(extracted_author)
        
        # Разбиваем контент на главы по заголовкам
        chapters = []
        current_chapter = []
        chapter_title = "Введение"
        chapter_count = 1
        
        for line in lines:
            if line.startswith('# ') and len(current_chapter) > 0:
                # Создаем главу из накопленного контента
                chapter_content = '\n'.join(current_chapter)
                if chapter_content.strip():
                    chapters.append((chapter_title, chapter_content))
                
                # Начинаем новую главу
                chapter_title = line[2:].strip()
                current_chapter = []
                chapter_count += 1
            elif line.startswith('## '):
                # Подзаголовок - тоже может быть главой
                if len(current_chapter) > 0:
                    chapter_content = '\n'.join(current_chapter)
                    if chapter_content.strip():
                        chapters.append((chapter_title, chapter_content))
                
                chapter_title = line[3:].strip()
                current_chapter = []
                chapter_count += 1
            else:
                current_chapter.append(line)
        
        # Добавляем последнюю главу
        if current_chapter:
            chapter_content = '\n'.join(current_chapter)
            if chapter_content.strip():
                chapters.append((chapter_title, chapter_content))
        
        # Если глав нет, создаем одну главу из всего контента
        if not chapters:
            chapters = [(extracted_title, markdown_content)]
        
        # Создаем главы EPUB
        epub_chapters = []
        spine = []
        
        for i, (title, content) in enumerate(chapters):
            # Конвертируем Markdown в HTML
            html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
            
            # Создаем главу
            chapter_id = f'chapter_{i+1}'
            chapter_filename = f'{chapter_id}.xhtml'
            
            chapter = epub.EpubHtml(
                title=title,
                file_name=chapter_filename,
                lang='ru'
            )
            
            # Добавляем CSS стили
            chapter.content = f'''
            <!DOCTYPE html>
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <title>{title}</title>
                <style>
                    body {{ font-family: serif; line-height: 1.6; margin: 2em; }}
                    h1, h2, h3 {{ color: #333; margin-top: 2em; }}
                    p {{ margin: 1em 0; text-align: justify; }}
                    blockquote {{ margin: 1em 2em; font-style: italic; }}
                    code {{ background: #f5f5f5; padding: 0.2em 0.4em; }}
                    pre {{ background: #f5f5f5; padding: 1em; overflow-x: auto; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            '''
            
            book.add_item(chapter)
            epub_chapters.append(chapter)
            spine.append(chapter)
        
        # Создаем оглавление
        book.toc = [(epub.Link(f'{chapter.file_name}', chapter.title, f'chapter_{i+1}'), []) 
                    for i, chapter in enumerate(epub_chapters)]
        
        # Добавляем навигационные файлы
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Устанавливаем порядок чтения
        book.spine = ['nav'] + spine
        
        return book
    
    except Exception as e:
        raise Exception(f"Ошибка при конвертации Markdown: {str(e)}")

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
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'epub':
                # EPUB в Markdown
                markdown_content = epub_to_markdown(file_path)
                output_filename = f"{os.path.splitext(filename)[0]}.md"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            elif file_ext in ['md', 'markdown', 'txt']:
                # Markdown в EPUB
                book = markdown_to_epub(file_path)
                output_filename = f"{os.path.splitext(filename)[0]}.epub"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                epub.write_epub(output_path, book, {})
            
            # Удаляем загруженный файл
            os.remove(file_path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            flash(f'Ошибка при обработке файла: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Разрешены только EPUB, MD, Markdown и TXT файлы')
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
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'epub':
                # EPUB в Markdown
                content = epub_to_markdown(file_path)
                output_filename = f"{os.path.splitext(filename)[0]}.md"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                conversion_type = "EPUB → Markdown"
            
            elif file_ext in ['md', 'markdown', 'txt']:
                # Markdown в EPUB
                book = markdown_to_epub(file_path)
                output_filename = f"{os.path.splitext(filename)[0]}.epub"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                epub.write_epub(output_path, book, {})
                
                # Получаем размер файла
                content_size = os.path.getsize(output_path)
                conversion_type = "Markdown → EPUB"
            else:
                return jsonify({'error': 'Неподдерживаемый формат файла'}), 400
            
            # Удаляем загруженный файл
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'filename': output_filename,
                'size': content_size if file_ext in ['md', 'markdown', 'txt'] else len(content),
                'conversion_type': conversion_type
            })
        
        except Exception as e:
            return jsonify({'error': f'Ошибка при обработке файла: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Разрешены только EPUB, MD, Markdown и TXT файлы'}), 400

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