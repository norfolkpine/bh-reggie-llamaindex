import xml.etree.ElementTree as ET
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from pathlib import Path

class CustomXmlReader(BaseReader):
    """Custom XML parser that extracts all text content from an XML file."""

    def load_data(self, file: Path, extra_info=None):
        """Parse XML file and extract text content.

        Args:
            file (Path): The path to the XML file.
            extra_info (Optional[dict]): Extra info to be associated with the Document.

        Returns:
            List[Document]: A list containing a single Document with extracted text.
        """
        text_content = []
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            for element in root.iter():
                if element.text:
                    text_content.append(element.text.strip())
        except ET.ParseError as e:
            print(f"Error parsing XML file {file}: {e}")
            # Return an empty document or raise error, depending on desired handling
            return [Document(text="", extra_info=extra_info or {})]
        except Exception as e:
            print(f"An unexpected error occurred while processing XML file {file}: {e}")
            return [Document(text="", extra_info=extra_info or {})]

        full_text = " ".join(filter(None, text_content))
        return [Document(text=full_text, extra_info=extra_info or {})]
