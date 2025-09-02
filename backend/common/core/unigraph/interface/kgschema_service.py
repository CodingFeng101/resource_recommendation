from backend.common.core.unigraph.implementation.module.schema_construction.schema_construction import \
    SchemaConstruction


async def create_schema(
        file_path_list,
        aim,
        api_key,
        base_url,
        model: str,
):
    construction = SchemaConstruction(
        kg_schema=[],
        definition={}
    )
    modify_info = {"add_entity": [], "add_relationship": [], "del_entity": [], "del_relationship": []}
    schema, definition = await construction.extract_from_path(
        file_path_list=file_path_list,
        aim=aim,
        info=modify_info,
        directional_suggestion="",
        api_key=api_key,
        base_url=base_url,
        model=model
    )
    return schema, definition

