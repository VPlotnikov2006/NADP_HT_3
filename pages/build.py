import re
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown


def read_markdown(path: Path) -> str:
    """Читает .md файл и убирает комментарии."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip()


def parse_markdown(text: str):
    """
    Разбирает анкету на структуру:
    {
        "title": "...",
        "blocks": [
            {"name": "...", "questions": [ { "text": "...", "sub": ["..."] } ]}
        ]
    }
    """
    lines = text.splitlines()
    data = {"title": "", "blocks": []}

    current_block = None
    current_question = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Заголовок анкеты
        if stripped.startswith("# "):
            data["title"] = stripped[2:].strip()
            continue

        # Заголовок блока
        if stripped.startswith("## "):
            if current_block:
                if current_question:
                    current_block["questions"].append(current_question)
                    current_question = None
                data["blocks"].append(current_block)
            current_block = {"name": stripped[3:].strip(), "questions": []}
            continue

        # Вопрос
        match_q = re.match(r"^(\d+)\.\s+(.*)", stripped)
        if match_q:
            if current_question:
                current_block["questions"].append(current_question)  # type: ignore
            current_question = {"text": match_q.group(2).strip(), "sub": []}
            continue

        # Подвопрос
        match_sub = re.match(r"^\s*(\d+)\.\s+(.*)", line)
        if match_sub and current_question:
            current_question["sub"].append(match_sub.group(2).strip())
            continue

        # Маркированный список
        match_bullet = re.match(r"^\s*[-*]\s+(.*)", line)
        if match_bullet and current_question:
            current_question["sub"].append(match_bullet.group(1).strip())
            continue

    # Добавляем последний блок
    if current_question and current_block:
        current_block["questions"].append(current_question)
    if current_block:
        data["blocks"].append(current_block)

    return data


def render_html(data, template_dir, template_name):
    """Создает HTML с помощью Jinja2"""
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Добавим фильтр markdown
    def md(text):
        return markdown.markdown(text, extensions=["extra", "sane_lists", "nl2br"])

    env.filters["md"] = md

    template = env.get_template(template_name)
    return template.render(data=data)


def main():
    if len(sys.argv) != 3:
        print("Использование: python convert_to_html.py input.md output.html")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    html_path = Path(sys.argv[2])

    if not md_path.exists():
        print(f"Файл не найден: {md_path}")
        sys.exit(1)

    text = read_markdown(md_path)
    data = parse_markdown(text)
    html = render_html(
        data, template_dir="pages/templates", template_name="template.html"
    )

    html_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML успешно создан: {html_path}")


if __name__ == "__main__":
    main()
