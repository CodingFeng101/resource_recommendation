import logging
import time
import datetime
import pandas as pd
from pathlib import Path
from io import BytesIO
from typing import Union, Iterable, Any, List, Dict

from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types import DoclingDocument
from docling_core.types.doc import TableItem, PictureItem, ImageRefMode, NodeItem, TextItem, DocItemLabel, \
    PictureClassificationData, PictureClassificationClass
from docling_core.types.io import DocumentStream
from transformers import AutoTokenizer

from public_tech_lib.file_processing_service.third_party_lib.docling.datamodel.base_models import InputFormat, ItemAndImageEnrichmentElement
from public_tech_lib.file_processing_service.third_party_lib.docling.datamodel.pipeline_options import PdfPipelineOptions, PipelineOptions
from public_tech_lib.file_processing_service.third_party_lib.docling.document_converter import DocumentConverter, PdfFormatOption
from public_tech_lib.file_processing_service.third_party_lib.docling.models.base_model import BaseItemAndImageEnrichmentModel, BaseEnrichmentModel
from public_tech_lib.file_processing_service.third_party_lib.docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline

pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = 2.0
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True


class ImageExtractor:
    def __init__(self):
        pass

    def extract(self, loaded_data, output_path: Path):

        path = []

        for result in loaded_data:
            doc_filename = result.input.file.stem
            for page_no, page in result.document.pages.items():
                page_image_filename = output_path / f"{doc_filename}-{page_no}.png"
                with page_image_filename.open("wb") as fp:
                    page.image.pil_image.save(fp, format="PNG")

                path.append(page_image_filename)

            picture_counter = 0
            for element, _ in result.document.iterate_items():

                if isinstance(element, PictureItem):
                    picture_counter += 1
                    element_image_filename = output_path / f"{doc_filename}-picture-{picture_counter}.png"
                    with element_image_filename.open("wb") as fp:
                        element.get_image(result.document).save(fp, "PNG")

                    path.append(element_image_filename)

        return path


class TableExtractor:
    def __init__(self):
        pass

    def extract(self, loaded_data, save_type, save_path):

        rows = []
        path = []

        for result in loaded_data:
            doc_filename = result.input.file.stem
            for table_ix, table in enumerate(result.document.tables):
                table_df: pd.DataFrame = table.export_to_dataframe()
                rows.append(table_df)

                if save_type == "csv":
                    element_csv_filename = save_path / f"{doc_filename}-table-{table_ix + 1}.csv"
                    table_df.to_csv(element_csv_filename, index=False)
                    path.append(element_csv_filename)
                elif save_type == "html":
                    element_html_filename = save_path / f"{doc_filename}-table-{table_ix + 1}.html"
                    with element_html_filename.open("w") as fp:
                        fp.write(table.export_to_html())
                    path.append(element_html_filename)
                elif save_type == "md":
                    element_md_filename = save_path / f"{doc_filename}-table-{table_ix + 1}.md"
                    table_df.to_markdown(element_md_filename)
                    path.append(element_md_filename)

        return path


class Chunker():
    def __init__(self,tokenizer,max_tokens):
        self.chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=max_tokens)
    def chunk(self,loaded_data):
        chunk_res = []

        for result in loaded_data:
            chunk_iter = self.chunker.chunk(dl_doc=result.document)

            for chunk in chunk_iter:
                chunk_res.append(chunk.text)

        return chunk_res





class DoclingServer:
    def __init__(self, doc_converter, image_extractor, table_extractor, chunker):
        # 有哪些服务这里要体现
        self.doc_converter = doc_converter
        self.image_extractor = image_extractor
        self.table_extractor = table_extractor
        # self.chunker = Chunker(embed_model_id="sentence-transformers/all-MiniLM-L6-v2", max_tokens=64)
        self.chunker = chunker
        self.output_dir = Path("test_scratch")

    def __loading_data(self, file_path):
        # docling怎么读取该文件
        if isinstance(file_path, str):
            with open(file_path, "rb") as f:
                stream = BytesIO(f.read())
            doc = DocumentStream(name=str(file_path), stream=stream)
            conv_res = self.doc_converter.convert_all(
                [doc],
                raises_on_error=False  # 允许错误情况下继续转换
            )
        else:
            doc_streams = []

            for doc in file_path:
                if isinstance(doc, (str, Path)):
                    with open(doc, "rb") as f:
                        stream = BytesIO(f.read())
                    doc_streams.append(DocumentStream(name=str(doc), stream=stream))
                else:
                    doc_streams.append(doc)

            conv_res = self.doc_converter.convert_all(
                doc_streams,
                raises_on_error=False  # 允许错误情况下继续转换
            )

        return conv_res

    def extract_text(self, file_path):
        loaded_data = self.__loading_data(file_path)

        for result in loaded_data:
            return result.document.export_to_text()



    # 根据读取的结果，docling能坐什么，5个功能
    def convert_to(
            self,
            file_path,
            convert_type,
            save_path: str = None
    ):
        # 根据上传的文件，转换为特定格式的文件，return 如果转换的类似是文件格式，那么我就保存文件并且返回文件路径，如果不是，直接返回内容
        if not isinstance(save_path, str):
            save_path = self.output_dir

        loaded_data = self.__loading_data(file_path)

        output_dir = Path(save_path)

        for result in loaded_data:
            doc_filename = result.input.file.stem

            if convert_type == "md":
                return result.document.export_to_markdown()
            else:
                pass

    def extract_images(self, file_path, save_path: str = None ) -> list:
        if not isinstance(save_path, str):
            save_path = self.output_dir

        loaded_data = self.__loading_data(file_path)

        save_path = Path(save_path)

        res_path = self.image_extractor.extract(loaded_data, save_path)
        return res_path

    def extract_tables(self, file_path, save_type, save_path: str = None) -> list:
        if not isinstance(save_path, str):
            save_path = self.output_dir

        loaded_data = self.__loading_data(file_path)

        save_path = Path(save_path)

        res_path = self.table_extractor.extract(loaded_data, save_type, save_path)

        return res_path

    def chunk_file(self, file_path) -> list:
        # 根据上传的文本，对其分块保存成一个列表 return 列表

        loaded_data = self.__loading_data(file_path)
        chunk_res = self.chunker.chunk(loaded_data)

        return chunk_res




# #
# if __name__ == "__main__":
#     pdf_file_path = "tests_docs/data/2206.01062.pdf"
#
#     doc_converter = DocumentConverter(
#         format_options={
#             InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#         }
#     )
#     image_extractor = ImageExtractor()
#     table_extractor = TableExtractor()
#     chunker = Chunker(embed_model_id="sentence-transformers/all-MiniLM-L6-v2", max_tokens=64)
#
#
#     docling_sever = DoclingSever(doc_converter, image_extractor, table_extractor, chunker)
#
#
#     # paths = docling_sever.convert_file_type("C:\\Users\\天选\\Desktop\\多元函数微分法及其应用.png", "md")
#     # image_paths = docling_sever.extract_images("C:\\Users\\天选\\Desktop\\计算机组成原理实验1 - 副本.docx")
#     # table_paths = docling_sever.extract_tables(pdf_file_path, "md")
#     # chunks = docling_sever.chunk_file("tests_docs/data/md/wiki.md")
#     text = docling_sever.read_file_type("C:\\Users\\天选\\Desktop\\c语言ppt .pptx", "md")
#     #
#     print(text)
    # print(paths)
    # print(image_paths)
    # print(table_paths)
    # for chunk in chunks:
    #     print(chunk)
