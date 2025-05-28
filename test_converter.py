#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для двунаправленной конвертации EPUB ⇄ Markdown
Использование: python test_converter.py path/to/your/file.epub|md|txt
"""

import sys
import os
import ebooklib
from app import epub_to_markdown, markdown_to_epub

def main():
    if len(sys.argv) != 2:
        print("Использование: python test_converter.py path/to/your/file.epub|md|txt")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if not os.path.exists(input_path):
        print(f"Ошибка: Файл {input_path} не найден")
        sys.exit(1)
    
    # Определяем тип файла и направление конвертации
    file_ext = input_path.lower().split('.')[-1]
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    try:
        if file_ext == 'epub':
            # EPUB → Markdown
            print(f"📚 → 📝 Конвертирую EPUB в Markdown: {input_path}...")
            markdown_content = epub_to_markdown(input_path)
            
            output_path = f"{base_name}.md"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ Конвертация EPUB → Markdown завершена!")
            print(f"📄 Результат сохранен в: {output_path}")
            print(f"📊 Размер файла: {len(markdown_content)} символов")
            
        elif file_ext in ['md', 'markdown', 'txt']:
            # Markdown/TXT → EPUB
            print(f"📝 → 📚 Конвертирую {file_ext.upper()} в EPUB: {input_path}...")
            book = markdown_to_epub(input_path)
            
            output_path = f"{base_name}.epub"
            ebooklib.epub.write_epub(output_path, book, {})
            
            file_size = os.path.getsize(output_path)
            print(f"✅ Конвертация {file_ext.upper()} → EPUB завершена!")
            print(f"📄 Результат сохранен в: {output_path}")
            print(f"📊 Размер файла: {file_size} байт")
            
        else:
            print(f"❌ Неподдерживаемый формат файла: .{file_ext}")
            print("Поддерживаемые форматы: .epub, .md, .markdown, .txt")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 