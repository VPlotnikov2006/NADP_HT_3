from pathlib import Path
import sys

path: Path = Path("./content/questionnaire.md")

if not path.exists():
    print("❌ Ошибка: Файл не существует")
    sys.exit(1)

print("✅ Проверка прошла успешно")
