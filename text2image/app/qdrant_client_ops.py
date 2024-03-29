import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.conversions import common_types as types
from appconfig import DEFAULT_EMBEDDING_SIZE
from appconfig import RETURN_N_RESULTS


def get_client() -> QdrantClient:
    return QdrantClient("172.17.0.1", port=6333)


def qdrant_create(collection_name: str, size: int) -> None:
    client = get_client()
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=size, distance=Distance.DOT),
    )


def qdrant_upload(
    vector: List[float], image_url: str, collection_name: str
) -> types.UpdateResult:
    client = get_client()
    if not client.collection_exists(collection_name):
        qdrant_create(collection_name, DEFAULT_EMBEDDING_SIZE)
    unique_id = str(uuid.uuid4())
    operation_info = client.upsert(
        collection_name=collection_name,
        wait=True,
        points=[
            PointStruct(id=unique_id, vector=vector, payload={"url": image_url}),
        ],
    )
    return operation_info


def qdrant_query(vector: List[float], collection_name: str) -> List[types.ScoredPoint]:
    client = get_client()
    search_result = client.search(
        collection_name=collection_name, query_vector=vector, limit=RETURN_N_RESULTS
    )
    return search_result
