
import re
from io import BytesIO

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION


def clean_resume_content(content: str) -> str:
    """Clean common Markdown formatting from resume content."""

    if not isinstance(content, str):
        return ""

    content = content.strip()

    # Remove surrounding Markdown code fences if present.
    content = re.sub(
        r"^\s*```(?:markdown|md|text)?\s*",
        "",
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(r"\s*```\s*$", "", content)

    return content.strip()


def format_resume_for_display(content: str) -> str:
    """Prepare resume content for display in Streamlit."""

    return clean_resume_content(content)


def create_docx(content: str, title: str = "Resume") -> BytesIO:
    """Generate a formatted Word document in memory."""

    content = clean_resume_content(content)

    if not content:
        raise ValueError("Resume content cannot be empty.")

    document = Document()

    # Page margins.
    section = document.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    # Default font.
    normal_style = document.styles["Normal"]
    normal_style.font.name = "Arial"
    normal_style.font.size = Pt(10)

    title_added = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Main heading: # Name or # Resume Title.
        if line.startswith("# "):
            heading = line[2:].strip()

            if not title_added:
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

                run = paragraph.add_run(heading or title)
                run.bold = True
                run.font.name = "Arial"
                run.font.size = Pt(18)

                title_added = True
            else:
                document.add_heading(heading, level=1)

        # Section headings: ## Education, ## Skills, etc.
        elif line.startswith("## "):
            heading = line[3:].strip()
            document.add_heading(heading, level=2)

        elif line.startswith("### "):
            heading = line[4:].strip()
            document.add_heading(heading, level=3)

        # Bullets.
        elif line.startswith(("- ", "* ", "• ")):
            bullet_text = line[2:].strip()

            paragraph = document.add_paragraph(style="List Bullet")
            paragraph.add_run(_remove_inline_markdown(bullet_text))

        # Numbered lists.
        elif re.match(r"^\d+[\.)]\s+", line):
            numbered_text = re.sub(r"^\d+[\.)]\s+", "", line)

            paragraph = document.add_paragraph(style="List Number")
            paragraph.add_run(_remove_inline_markdown(numbered_text))

        # Normal paragraph.
        else:
            paragraph = document.add_paragraph()
            paragraph.add_run(_remove_inline_markdown(line))

    output = BytesIO()
    document.save(output)
    output.seek(0)

    return output


def _remove_inline_markdown(text: str) -> str:
    """Remove basic Markdown emphasis and inline-code markers."""

    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)

    return text.strip()
