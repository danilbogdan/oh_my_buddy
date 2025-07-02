import os

from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.postgres import PGVectorStore


class KnowledgeManager:
    def __init__(self, collection_name="knowledge"):
        self.collection_name = collection_name
        embed_model = GoogleGenAIEmbedding(model_name="text-embedding-004")
        Settings.embed_model = embed_model
        self.vector_store = PGVectorStore.from_params(
            database=os.getenv("POSTGRES_VECTOR_DB"),
            host=os.getenv("POSTGRES_VECTOR_HOST"),
            port=os.getenv("POSTGRES_VECTOR_PORT"),
            user=os.getenv("POSTGRES_VECTOR_USER"),
            password=os.getenv("POSTGRES_VECTOR_PASSWORD"),
            table_name=self.collection_name,
            embed_dim=768
        )

    def save(self, path: str):
        if os.path.isdir(path):
            documents = SimpleDirectoryReader(input_dir=path, required_exts=[".pdf"],).load_data()
        else:
            documents = SimpleDirectoryReader(input_files=[path]).load_data()
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        VectorStoreIndex.from_documents(
            documents, storage_context=storage_context, show_progress=True
        )

    def search(self, query: str, limit: int = 5):
        index = VectorStoreIndex.from_vector_store(self.vector_store)
        query_engine = index.as_query_engine(similarity_top_k=limit)
        response = query_engine.query(query)
        return [node.get_content() for node in response.source_nodes]

# if __name__ == "__main__":
    # knowledge_manager = KnowledgeManager()
    # knowledge_manager.save("/app/")
    # print(knowledge_manager.search("Какие книги по влиянию нужно прочитать?")[0])