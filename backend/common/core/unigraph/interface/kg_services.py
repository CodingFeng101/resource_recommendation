
from typing import List, Dict

from backend.common.core.unigraph.implementation.module.kg_constructor import SemanticKGConstructor


async def create_kg(
        kg_schema: List,
        schema_definition: Dict,
        text_data: str,
):
    """
    Create KG from documents in the specified directory based on the schema and schema definition provided.
    """
    api_result = list()
    constructor = SemanticKGConstructor(kg_schema, schema_definition)
    semantic_kg, triple_source = await constructor.extract_kg(
        text_data=text_data
    )
    api_result.append({"file_name": "all", "semantic_kg": semantic_kg, "triple_source": triple_source})
    return api_result
