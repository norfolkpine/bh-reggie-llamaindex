import os
import tempfile
import shutil
from pathlib import Path
import unittest

from llama_index.core.schema import Document
from llama_index.core.readers import SimpleDirectoryReader # Corrected import
from llama_index.readers.json import JSONReader

# Assuming custom_readers.py is in the parent directory or PYTHONPATH is set up
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from custom_readers import CustomXmlReader


class TestCustomReaders(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to store test files
        self.test_dir = Path(tempfile.mkdtemp())
        self.xml_file_path = self.test_dir / "sample.xml"
        with open(self.xml_file_path, "w", encoding="utf-8") as f: # Added encoding
            f.write("<root><item>Hello</item><item>XML content</item><empty></empty><tag with_attr='true'>More text</tag></root>")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_custom_xml_reader(self):
        reader = CustomXmlReader()
        documents = reader.load_data(file=self.xml_file_path)
        self.assertEqual(len(documents), 1)
        self.assertIsInstance(documents[0], Document)
        # Based on the CustomXmlReader logic: iterate all elements, get text, strip, join with space
        self.assertEqual(documents[0].text, "Hello XML content More text")


class TestSimpleDirectoryReaderExtensions(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.json_file_path = self.test_dir / "sample.json"
        self.xml_file_path = self.test_dir / "sample_for_sdr.xml"

        with open(self.json_file_path, "w", encoding="utf-8") as f: # Added encoding
            f.write('{"key": "value", "text_content": "JSON data here"}')
        with open(self.xml_file_path, "w", encoding="utf-8") as f: # Added encoding
            f.write("<doc><para>XML for SDR</para><para>Another para</para></doc>")

        self.file_extractor = {
            ".json": JSONReader(),
            ".xml": CustomXmlReader()
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_sdr_with_custom_extractors(self):
        reader = SimpleDirectoryReader(
            input_dir=self.test_dir,
            file_extractor=self.file_extractor,
            # Explicitly tell SimpleDirectoryReader to look for all files,
            # otherwise it might only pick up its default known extensions + .json, .xml
            # However, the file_extractor should make it pick them up.
            # Let's test default behavior first. If it fails, we can add required_exts.
        )
        documents = reader.load_data()

        self.assertEqual(len(documents), 2, f"Expected 2 documents, got {len(documents)}. Files in dir: {os.listdir(self.test_dir)}")

        json_doc_found = False
        xml_doc_found = False

        for doc in documents:
            if doc.metadata["file_name"] == "sample.json":
                json_doc_found = True
                # JSONReader by default loads the raw content of the JSON file.
                # For '{"key": "value", "text_content": "JSON data here"}'
                # The text will be something like '"key": "value",\n"text_content": "JSON data here"'
                self.assertIn('"key": "value"', doc.text)
                self.assertIn('"text_content": "JSON data here"', doc.text)

            elif doc.metadata["file_name"] == "sample_for_sdr.xml":
                xml_doc_found = True
                self.assertEqual(doc.text, "XML for SDR Another para")

        self.assertTrue(json_doc_found, "JSON document not found or processed")
        self.assertTrue(xml_doc_found, "XML document not found or processed")

if __name__ == '__main__':
    unittest.main()
