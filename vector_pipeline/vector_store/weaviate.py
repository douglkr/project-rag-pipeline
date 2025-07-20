import logging
from typing import List
import weaviate
import weaviate.classes.config as wc
from weaviate.util import generate_uuid5
from weaviate.classes.config import Configure

logger = logging.getLogger(__name__)

class WeaviateCollectionManager:
    def __init__(self, config: str):
        self.client = None
        self.config = config

    def connect(self, connection_type, host: str = "http://localhost:8080", port="8080", api_key: str = None):
        try:
            if connection_type == 'local':
                self.client = weaviate.connect_to_local(host="localhost", port=port)
                logger.info("Connected to local Weaviate instance.")
            elif connection_type == 'weaviate_cloud':
                self.client = weaviate.connect_to_wcs(
                    cluster_url=host,
                    auth_credentials=weaviate.auth.AuthApiKey(api_key),
                )
                logger.info(f"Connected to remote Weaviate at {host}.")
            elif connection_type == 'ec2':
                self.client = weaviate.connect_to_custom(
                    http_host=host,
                    http_port=port,
                    grpc_host=host,
                    grpc_port=50051,
                    http_secure=False,
                    grpc_secure=False
                )
        except Exception as e:
            logger.exception("Error while connecting to Weaviate or creating collection.")
            self.close()  # Ensure the client is closed on failure
            raise

    def _create_collection_if_not_exists(self):
        collection_name = self.config["weaviate"]["collection"]["name"]
        existing_collections: List[weaviate.collections.collections.Collection] = self.client.collections.list_all()

        if collection_name.capitalize() in existing_collections.keys():  # Weaviate uses GraphQL naming conventions
            logger.info(f"Collection '{collection_name}' already exists.")
            return

        logging.info(f"Creating collection '{collection_name}'...")

        props = self.config["weaviate"]["collection"]["properties"]
        vectorizer = self.config["weaviate"]["collection"].get("vectorizer", {})

        properties = [
            wc.Property(name=prop["name"], data_type=getattr(wc.DataType, prop["type"]))
            for prop in props
        ]

        vectorizer_config = []
        if vectorizer.get("type") == "none":
            mv_enabled = vectorizer.get("multi_vector", False)
            vectorizer_config = [
                Configure.NamedVectors.none(
                    name=vectorizer["name"],
                    vector_index_config=Configure.VectorIndex.hnsw(
                        multi_vector=Configure.VectorIndex.MultiVector.multi_vector() if mv_enabled else None
                    )
                )
            ]

        self.client.collections.create(
            name=collection_name,
            properties=properties,
            vectorizer_config=vectorizer_config
        )

        logging.info(f"Collection '{collection_name}' created successfully.")

    def get_collection(self, collection_name: str = None):
        if self.client is None:
            raise RuntimeError("Client not connected")

        try:
            if collection_name is None:
                collection_name = self.config["collection"]["name"]

            collection = self.client.collections.get(collection_name)
            logger.info(f"Retrieved collection '{collection_name}'.")
            return collection
        except Exception as e:
            logger.exception(f"Failed to retrieve collection '{collection_name}'.")
            raise

    def insert_object(self, properties: dict, embedding: list = None):
        if self.client is None:
            raise RuntimeError("Client not connected")

        try:
            collection_name = self.config["weaviate"]["collection"]["name"]
            vectorizer = self.config["weaviate"]["collection"].get("vectorizer", {})
            vector_name = vectorizer.get("name") if vectorizer.get("type") == "none" else None

            collection = self.client.collections.get(collection_name)

            insert_kwargs = {
                "properties": properties,
            }

            insert_kwargs["uuid"] = generate_uuid5(properties)

            if embedding and vector_name:
                insert_kwargs["vector"] = {
                    vector_name: embedding
                }
            
            collection.data.insert(**insert_kwargs)
            logger.info(f"Inserted object with UUID {insert_kwargs['uuid']} into collection '{collection_name}'.")
        except Exception:
            logger.exception("Failed to insert object into Weaviate.")
            self.close()
            raise

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            logging.info("Weaviate connection closed.")
