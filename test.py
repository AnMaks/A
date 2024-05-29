import os

file_path = 'plagiarism_results.csv'
if os.path.isfile(file_path):
    print("Файл существует и доступен для чтения")
    # Здесь ваш код для работы с файлом
else:
    print("Файл не найден")
