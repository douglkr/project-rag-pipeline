import base64
import logging
from io import BytesIO
from typing import List, Dict
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader
import os

logger = logging.getLogger(__name__)

class PDFImageConverter:
    def __init__(self, pdf_path: str, config: dict):
        self.pdf_path = pdf_path
        self.config = config
        self.pdf_title = self._extract_pdf_title(pdf_path)
        logger.info(f"Initialized PDFImageConverter with PDF: {pdf_path}")

    def convert_to_base64_images(self) -> List[Dict[str, str]]:
        """
        Convert all PDF pages to base64-encoded PNG images.
        Returns:
            List of dictionaries with keys based on config, plus base64_image.
        """
        logger.info(f"Converting PDF to images: {self.pdf_path}")
        try:
            images = convert_from_path(self.pdf_path)
            logger.info(f"Converted {len(images)} pages to PIL images.")
        except Exception:
            logger.exception("Failed to convert PDF to images.")
            raise

        try:
            # Extract property names from config
            property_names = [p["name"] for p in self.config["weaviate"]["collection"]["properties"]]

            base64_images = []
            for idx, image in enumerate(images):
                item = {}
                if "pdf_title" in property_names:
                    item["pdf_title"] = self.pdf_title
                if "page_number" in property_names:
                    item["page_number"] = idx + 1

                # Always include the base64 image
                item["base64_image"] = self._pil_to_base64(image, page_number=idx + 1)

                base64_images.append(item)

            logger.info(f"Successfully encoded {len(base64_images)} images to base64.")
            return base64_images
        except Exception:
            logger.exception("Failed to encode images to base64.")
            raise

    @staticmethod
    def _pil_to_base64(image: Image.Image, page_number: int = None) -> str:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        base64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        if page_number is not None:
            logger.debug(f"Converted page {page_number} to base64.")
        return base64_str

    @staticmethod
    def _extract_pdf_title(pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            title = reader.metadata.get("/Title", "").strip()
            if title.lower() not in {"", "untitled", "unknown"}:
                return title
        except Exception:
            logger.warning("Could not extract PDF title from metadata.")

        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        logger.info(f"Falling back to filename as title: {filename}")
        return filename
