import re
import sys
from pathlib import Path


def read_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    return text.strip()


def check_header(lines) -> int:
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        if line.startswith("# "):
            pattern = r'^# Анкета №\d+ по проекту "HSE-Announce"$'
            return 0 if re.match(pattern, line.strip()) is None else i
        else:
            return 0
    return 0


def check_blocks(lines, *, skip=0):
    in_block = False
    block_has_questions = False
    block_name = None
    errors = []

    for i, line in enumerate(lines[skip:], 1 + skip):
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("## "):
            if in_block and not block_has_questions:
                errors.append(
                    f"Блок '{block_name}' (строка {i}) не содержит нумерованных вопросов."
                )
            in_block = True
            block_has_questions = False
            block_name = stripped[3:].strip()
            continue

        if re.match(r"^\d+\.\s", stripped):
            if not in_block:
                errors.append(f"Нумерованный пункт вне блока (строка {i}).")
            else:
                block_has_questions = True
            continue

        if re.match(r"^\s+\d+\.\s", line):
            continue

        if re.match(r"^\s*[-*]\s", line):
            continue

        errors.append(f"Найден неожиданный текст (строка {i}): {stripped}")

    if in_block and not block_has_questions:
        errors.append(f"Блок '{block_name}' не содержит нумерованных вопросов.")

    return errors


def main():
    if len(sys.argv) != 2:
        print("Ожидается путь к файлу для проверки")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Файл не найден: {path}")
        sys.exit(1)

    text = read_markdown(path)
    lines = text.splitlines()
    header = check_header(lines)

    if header == 0:
        print("❌ Ошибка: документ должен начинаться с заголовка вида:")
        print('# Анкета №1 по проекту "HSE-Announce"')
        sys.exit(1)

    errors = check_blocks(lines, skip=header)

    if errors:
        print("❌ Найдены ошибки в анкете:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    else:
        print("✅ Документ корректен и соответствует формату анкеты.")


if __name__ == "__main__":
    main()
