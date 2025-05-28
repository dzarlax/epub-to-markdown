#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для конвертации EPUB в Markdown
Использование: python test_converter.py path/to/your/book.epub
"""

import sys
import os
from app import epub_to_markdown

def main():
    if len(sys.argv) != 2:
        print("Использование: python test_converter.py path/to/your/book.epub")
        sys.exit(1)
    
    epub_path = sys.argv[1]
    
    if not os.path.exists(epub_path):
        print(f"Ошибка: Файл {epub_path} не найден")
        sys.exit(1)
    
    if not epub_path.lower().endswith('.epub'):
        print("Ошибка: Файл должен иметь расширение .epub")
        sys.exit(1)
    
    try:
        print(f"Конвертирую {epub_path}...")
        markdown_content = epub_to_markdown(epub_path)
        
        # Создаем имя выходного файла
        base_name = os.path.splitext(os.path.basename(epub_path))[0]
        output_path = f"{base_name}.md"
        
        # Сохраняем результат
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Конвертация завершена!")
        print(f"📄 Результат сохранен в: {output_path}")
        print(f"📊 Размер файла: {len(markdown_content)} символов")
        
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 