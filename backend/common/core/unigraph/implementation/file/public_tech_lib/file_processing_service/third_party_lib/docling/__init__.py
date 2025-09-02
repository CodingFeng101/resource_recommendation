import argparse
import os

# ��ȡ��ǰ�ļ��ľ���·��������ȡ����Ŀ¼
current_dir = os.path.dirname(os.path.abspath(__file__))
from transformers import AutoTokenizer
# ���ù���Ŀ¼Ϊ��ǰ�ļ�����Ŀ¼
os.chdir(current_dir)
from public_tech_lib.file_processing_service.third_party_lib.docling.datamodel.base_models import InputFormat
from public_tech_lib.file_processing_service.third_party_lib.docling.datamodel.pipeline_options import PdfPipelineOptions
from public_tech_lib.file_processing_service.third_party_lib.docling.document_converter import DocumentConverter, PdfFormatOption
from public_tech_lib.file_processing_service.third_party_lib.docling.DoclingServer import DoclingServer,ImageExtractor,TableExtractor,Chunker
import yaml
# def parse_args():
#     parser = argparse.ArgumentParser(description="Process some integers.")
#     parser.add_argument('chunker_config_path', type=str, default='E:\PycharmProjects\sapperrag\sapperrag-main\public_tech_lib/file_processing_service/third_party_lib\docling\config\chunker_config.yaml',)
#     parser.add_argument('convert_config_path',type=str, default='E:\PycharmProjects\sapperrag\sapperrag-main\public_tech_lib/file_processing_service/third_party_lib\docling\config\converter_config.yaml')
#     return parser.parse_args()
chunker_config_path = "config/chunker_config.yaml"
convert_config_path = "config/converter_config.yaml"

def load_yaml_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


# args = parse_args()
chunker_config = load_yaml_config(chunker_config_path)
convert_config = load_yaml_config(convert_config_path)

pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = convert_config["pdf_converter_config"]['extracted_image_scale']
pipeline_options.generate_page_images = convert_config["pdf_converter_config"]['if_generate_page_image']
pipeline_options.generate_picture_images = convert_config["pdf_converter_config"]['if_generate_picture_images']
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
image_extractor = ImageExtractor()
table_extractor = TableExtractor()


chunker = Chunker(tokenizer=AutoTokenizer.from_pretrained(chunker_config["semantic_chunker_config"]["chunker_model"]),max_tokens = chunker_config["semantic_chunker_config"]["max_tokens"])


docling_server = DoclingServer(doc_converter, image_extractor, table_extractor, chunker)

