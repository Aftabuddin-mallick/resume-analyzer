import io
import re

from pypdf import PdfReader


class PDFError(Exception):
    pass


def extract_text(data: bytes) -> str:
    if not data.startswith(b"%PDF"):
        raise PDFError("That file is not a valid PDF.")
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise PDFError("This PDF is password protected. Remove the password and try again.")
        pages = [(page.extract_text() or "") for page in reader.pages[:10]]
    except PDFError:
        raise
    except Exception:
        raise PDFError("Could not read this PDF. Try exporting it again from Word or Google Docs.")

    text = "\n".join(pages)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 50:
        raise PDFError(
            "No readable text found. The PDF may be a scanned image; upload a text-based PDF instead."
        )
    return text
