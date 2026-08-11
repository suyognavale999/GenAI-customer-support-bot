from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.core.exceptions import ApplicationException


class TextExtractionService:
    supported_extensions = {
        ".txt",
        ".md",
        ".pdf",
        ".docx",
    }

    def extract_text(
        self,
        filename: str,
        file_content: bytes,
    ) -> str:
        extension = Path(filename).suffix.lower()

        if extension not in self.supported_extensions:
            raise ApplicationException(
                message="Only TXT, MD, PDF and DOCX files are supported.",
                status_code=400,
                error_code="UNSUPPORTED_FILE_TYPE",
            )

        try:
            if extension in {".txt", ".md"}:
                text = file_content.decode("utf-8")

            elif extension == ".pdf":
                text = self._extract_pdf(file_content)

            else:
                text = self._extract_docx(file_content)

        except ApplicationException:
            raise

        except Exception as exc:
            raise ApplicationException(
                message="Unable to extract text from the document.",
                status_code=400,
                error_code="TEXT_EXTRACTION_FAILED",
            ) from exc

        cleaned_text = self._clean_text(text)

        if not cleaned_text:
            raise ApplicationException(
                message="The document does not contain readable text.",
                status_code=400,
                error_code="EMPTY_DOCUMENT",
            )

        return cleaned_text

    def _extract_pdf(self, file_content: bytes) -> str:
        reader = PdfReader(BytesIO(file_content))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    def _extract_docx(self, file_content: bytes) -> str:
        document = Document(BytesIO(file_content))

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    def _clean_text(self, text: str) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)