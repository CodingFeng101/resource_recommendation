from abc import ABC
from app.common.unigraph.file.public_tech_lib.file_processing_service.third_party_lib.docling import docling_server,chunker
from PIL import Image
import pytesseract
from transformers import AutoTokenizer
import pandas as pd
import os
import re
import tempfile

class ReadingService(ABC):
    def __init__(self):
        pass
    def read(self, file_path):
        pass

class ConvertingService(ABC):
    def __init__(self):
        pass
    def convert(self, file_path, converted_file_type):
        pass


class PdfFileConvertingService(ConvertingService):
    def __init__(self):
        super(PdfFileConvertingService, self).__init__()

    def convert(self, file_path, converted_file_type):
        pass


class PdfFileConvertingService_Docling(PdfFileConvertingService):
    def __init__(self):
        super(PdfFileConvertingService_Docling, self).__init__()
        self.docling_server = docling_server

    def __convert_md(self, file_path):
        text = self.docling_server.convert_to(file_path)

    def convert(self, file_path, converted_file_type):
        file_extension = os.path.splitext(file_path)[1].lower().strip('.')
        if file_extension == 'pdf':
            text = self.__convert_md(file_path)
        else:
            pass
        return text


class DocFileConvertingService(ConvertingService):
    def __init__(self):
        super(DocFileConvertingService, self).__init__()

    def convert(self, file_path, converted_file_type):
        pass

class DocxFileConvertingService_Docling(DocFileConvertingService):
    def __init__(self):
        super(DocxFileConvertingService_Docling, self).__init__()
        self.docling_server = docling_server

    def __convert_md(self, file_path):
        text = self.docling_server.convert_to(file_path)
        return text

    def convert(self, file_path, converted_file_type):
        if converted_file_type == 'md':
            text = self.__convert_md(file_path)
        else:
            pass
        return text

class PptFileConvertingService(ConvertingService):
    def __init__(self):
        super(PptFileConvertingService, self).__init__()

    def convert(self, file_path, converted_file_type):
        pass


class PptxtFileConvertingService_Docling(PptFileConvertingService):
    def __init__(self):
        super(PptxtFileConvertingService_Docling, self).__init__()
        self.docling_server = docling_server

    def __convert_md(self, file_path):
        text = self.docling_server.convert_to(file_path)
        return text

    def convert(self, file_path, converted_file_type):
        if converted_file_type == 'md':
            text = self.__convert_md(file_path)
        else:
            pass
        return text
class PdfFileReadingService(ReadingService):
    def __init__(self):
        super(PdfFileReadingService, self).__init__()

    def read(self, file_path):
        pass

class PdfFileReadingService_Docling(PdfFileReadingService):
    def __init__(self):
        super(PdfFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text


class PdfFileReadingService_PythonLib(PdfFileReadingService):
    def __init__(self):
        super(PdfFileReadingService_PythonLib, self).__init__()
    def read(self, file_path):
        pass

class DocxFileReadingService(ReadingService):
        def __init__(self):
            super(DocxFileReadingService, self).__init__()

        def read(self, file_path):
            pass


class \
        DocxFileReadingService_Docling(DocxFileReadingService):
    def __init__(self):
        super(DocxFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text
class PptxFileReadingService(ReadingService):
    def __init__(self):
        super(PptxFileReadingService, self).__init__()

    def read(self, file_path):
        pass

class PptxFileReadingService_Docling(PptxFileReadingService):
    def __init__(self):
        super(PptxFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text


class XlsxFileReadingService(ReadingService):
    def __init__(self):
        super(XlsxFileReadingService, self).__init__()

    def read(self, file_path):
        pass


class XlsxFileReadingService_Docling(XlsxFileReadingService):
    def __init__(self):
        super(XlsxFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text


class HtmlFileReadingService(ReadingService):
    def __init__(self):
        super(HtmlFileReadingService, self).__init__()

    def read(self, file_path):
        pass
class HtmlFileReadingService_Docling(HtmlFileReadingService):
    def __init__(self):
        super(HtmlFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text

class MdFileReadingService(ReadingService):
    def __init__(self):
        super(MdFileReadingService, self).__init__()

    def read(self, file_path):
        pass


class MdFileReadingService_Docling(MdFileReadingService):
    def __init__(self):
        super(MdFileReadingService_Docling, self).__init__()
        self.docling_server = docling_server

    def read(self, file_path):
        text = self.docling_server.extract_text(file_path, "txt")

        return text

class CsvFileReadingService(ReadingService):
    def __init__(self):
        super(CsvFileReadingService, self).__init__()
    def read(self, file_path):
        pass


class CsvFileReadingService_PythonLib(CsvFileReadingService):
    def __init__(self):
        super(CsvFileReadingService_PythonLib).__init__()

    def read(self, file_path):
        df = pd.read_csv(file_path)
        formatted_rows = [
            ', '.join([f'{col}:{row[col]}' for col in df.columns])
            for _, row in df.iterrows()
        ]
        csv_text = '\n'.join(formatted_rows)

        return csv_text


class ImageFileReadingService(ReadingService):
    def __init__(self):
        super(ImageFileReadingService).__init__()
    def read(self, file_path):
        pass


class ImageFileReadingService_PythonLib(ImageFileReadingService):
    def __init__(self):
        super(ImageFileReadingService, self).__init__()

    def read(self, file_path):
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

        return text


class TxtFileReadingService(ReadingService):
    def __init__(self):
        super(TxtFileReadingService, self).__init__()
    def read(self, file_path):
        pass


class TxtFileReadingService_PythonLib(TxtFileReadingService):
    def __init__(self):
        super(TxtFileReadingService, self).__init__()

    def read(self, file_path):
        with open(file_path, "r", encoding="utf-8") as txt_file:
            text = txt_file.read()

        return text


class RegexChunkingService(ABC):
    def __init__(self, patterns=None):
        if patterns is None:
            patterns = [r'\n\n']  # Default split pattern
        self.patterns = patterns
    def chunk(self,text):
        pass

class RegexChunkingService_PythonLib(RegexChunkingService):
    def __init__(self):
        super(RegexChunkingService_PythonLib, self).__init__()

    def chunk(self,text):
        paragraphs = [text]
        for pattern in self.patterns:
            new_paragraphs = []
            for paragraph in paragraphs:
                new_paragraphs.extend(re.split(pattern, paragraph))
            paragraphs = new_paragraphs
        return paragraphs


class SemanticChunkingService(ABC):
    def __init__(self,chunker):
        self.chunker = chunker
    def chunk(self,text):
        pass

class SemanticChunkingService_Docling(SemanticChunkingService):
    def __init__(self,docling_server):
        super(SemanticChunkingService_Docling, self).__init__(docling_server)


    def chunk(self,text):

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.md', encoding='utf-8') as temp_file:
            temp_file.write(text)
            temp_file_path = temp_file.name

        chunks = self.chunker.chunk_file(temp_file_path)
        os.remove(temp_file_path)

        return chunks


pdf_reading_service = PdfFileReadingService_Docling()
docx_reading_service = DocxFileReadingService_Docling()
pptx_reading_service = PptxFileReadingService_Docling()
xlsx_reading_service = XlsxFileReadingService_Docling()
html_reading_service = HtmlFileReadingService_Docling()
md_reading_service = MdFileReadingService_Docling()
csv_reading_service = CsvFileReadingService_PythonLib()
image_reading_service = ImageFileReadingService_PythonLib()
txt_reading_service =  TxtFileReadingService_PythonLib()
chunking_service = SemanticChunkingService_Docling(docling_server)

pdf_converting_service = PdfFileConvertingService_Docling()
docx_converting_service = DocxFileConvertingService_Docling()
pptx_converting_service = PptxtFileConvertingService_Docling()