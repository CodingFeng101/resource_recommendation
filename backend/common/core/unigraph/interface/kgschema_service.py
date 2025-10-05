from backend.common.core.unigraph.implementation.module.schema_construction.schema_construction import \
    SchemaConstruction


async def create_schema(aim, text_data):
    construction = SchemaConstruction(
        kg_schema=[],
        definition={}
    )
    modify_info = {"add_entity": [], "add_relationship": [], "del_entity": [], "del_relationship": []}
    schema, definition = await construction.extract_from_path(
        aim=aim,
        text_data=text_data,
        directional_suggestion="",
    )
    return schema, definition

