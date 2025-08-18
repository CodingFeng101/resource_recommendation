import json

from pydantic import model_validator

from .embedding import EmbeddingResponse
from .community import CommunityResponse
from .source import SourceResponse
from .knowledge_entity import KnowledgeEntityResponse
from .knowledge_graph import KnowledgeGraphResponse
from .knowledge_relationship import KnowledgeRelationshipResponse
from .schema_entity import SchemaEntityResponse
from .schema_graph import SchemaGraphResponse
from .schema_relationship import SchemaRelationshipResponse


class GetSchemaGraphDetail(SchemaGraphResponse):
    knowledge_graphs: list[KnowledgeGraphResponse]
    entities: list[SchemaEntityResponse]
    relationships: list[SchemaRelationshipResponse]


class GetKnowledgeEntityDetail(KnowledgeEntityResponse):
    embeddings: list[EmbeddingResponse] | list
    communities: list[CommunityResponse] | list[str]

    @model_validator(mode='after')
    def handel(self):
        embeddings = self.embeddings
        if embeddings and len(embeddings) >= 1:
            self.embeddings = json.loads(embeddings[0].vector)

        communities = self.communities
        if communities and len(communities) >= 1:
            self.communities = [entity_community.uuid for entity_community in communities]
        return self



class GetIndexDetail(KnowledgeGraphResponse):
    entities: list[GetKnowledgeEntityDetail]
    relationships: list[KnowledgeRelationshipResponse]
    communities: list[CommunityResponse]


class GetKnowledgeGraphDetail(GetIndexDetail):
    schema_graph: SchemaGraphResponse




