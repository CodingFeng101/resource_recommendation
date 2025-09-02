
from typing import List, Dict

from backend.common.core.unigraph.implementation.module.kg_constructor import SemanticKGConstructor


async def create_kg(
        kg_schema: List,
        schema_definition: Dict,
        documents_dir_path: str,
        api_key: str,
        base_url: str,
        model: str
):
    """
    Create KG from documents in the specified directory based on the schema and schema definition provided.
    """
    api_result = list()
    constructor = SemanticKGConstructor(kg_schema, schema_definition)
    semantic_kg, structure_kg, triple_source = await constructor.extract_kg(
        dir_path=documents_dir_path,
        api_key=api_key,
        base_url=base_url,
        model=model
    )
    api_result.append({"file_name": "all", "semantic_kg": semantic_kg, "structure_kg": structure_kg, "triple_source": triple_source})
    return api_result
