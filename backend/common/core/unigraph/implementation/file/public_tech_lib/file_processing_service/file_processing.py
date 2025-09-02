
from abc import ABC

from app.common.unigraph.file.public_tech_lib.file_processing_service import pdf_reading_service, docx_reading_service, pptx_reading_service, \
    xlsx_reading_service, html_reading_service, md_reading_service, csv_reading_service, image_reading_service, \
    txt_reading_service


class FileReadingServer(ABC):
    def __init__(self):
        pass
    def get_reading_service(self, file_extension):


        if file_extension == "pdf":
            return pdf_reading_service
        elif file_extension == "docx":
            return docx_reading_service
        elif file_extension == "pptx":
            return pptx_reading_service
        elif file_extension == "xlsx":
            return xlsx_reading_service
        elif file_extension == "html":
            return html_reading_service
        elif file_extension == "md":
            return md_reading_service
        elif file_extension == "csv":
            return csv_reading_service
        elif file_extension == "jpg":
            return image_reading_service
        elif file_extension == "jpeg":
            return image_reading_service
        elif file_extension == "png":
            return image_reading_service
        elif file_extension == "bmp":
            return image_reading_service
        elif file_extension == "gif":
            return image_reading_service
        elif file_extension == "tiff":
            return image_reading_service
        elif file_extension == "txt":
            return txt_reading_service
        else:
            # Handle the case where the file extension is not recognized
            raise ValueError(f"Unsupported file type: {file_extension}")






