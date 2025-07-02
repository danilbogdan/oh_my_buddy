import os
import unittest
from unittest.mock import MagicMock, patch

from aimanager.knowledge.postgresql_vector import KnowledgeManager


class TestKnowledgeManager(unittest.TestCase):

    @patch('aimanager.knowledge.pgvector.PGVectorStore')
    @patch.dict(os.environ, {
        "PG_DBNAME": "test_db",
        "PG_HOST": "localhost",
        "PG_PORT": "5432",
        "PG_USER": "test_user",
        "PG_PASSWORD": "test_password"
    })
    def setUp(self, mock_pg_vector_store):
        self.mock_pg_vector_store = mock_pg_vector_store
        self.knowledge_manager = KnowledgeManager(collection_name="test_collection")

    def test_init(self):
        self.mock_pg_vector_store.from_params.assert_called_once_with(
            database="test_db",
            host="localhost",
            port="5432",
            user="test_user",
            password="test_password",
            table_name="test_collection",
            embed_dim=384,
        )
        self.assertIsNotNone(self.knowledge_manager.vector_store)

    @patch('os.path.isdir', return_value=False)
    @patch('aimanager.knowledge.pgvector.SimpleDirectoryReader')
    @patch('aimanager.knowledge.pgvector.StorageContext')
    @patch('aimanager.knowledge.pgvector.VectorStoreIndex')
    def test_save_with_file(self, mock_vector_store_index, mock_storage_context, mock_simple_directory_reader, mock_isdir):
        mock_document = MagicMock()
        mock_simple_directory_reader.return_value.load_data.return_value = [mock_document]

        self.knowledge_manager.save("dummy/path/to/file.pdf")

        mock_simple_directory_reader.assert_called_once_with(input_files=["dummy/path/to/file.pdf"])
        mock_storage_context.from_defaults.assert_called_once_with(vector_store=self.knowledge_manager.vector_store)
        mock_vector_store_index.from_documents.assert_called_once_with(
            [mock_document],
            storage_context=mock_storage_context.from_defaults.return_value
        )

    @patch('os.path.isdir', return_value=True)
    @patch('aimanager.knowledge.pgvector.SimpleDirectoryReader')
    @patch('aimanager.knowledge.pgvector.StorageContext')
    @patch('aimanager.knowledge.pgvector.VectorStoreIndex')
    def test_save_with_directory(self, mock_vector_store_index, mock_storage_context, mock_simple_directory_reader, mock_isdir):
        mock_document = MagicMock()
        mock_simple_directory_reader.return_value.load_data.return_value = [mock_document]

        self.knowledge_manager.save("dummy/path/to/folder")

        mock_simple_directory_reader.assert_called_once_with(input_dir="dummy/path/to/folder", required_exts=['.pdf'])
        mock_storage_context.from_defaults.assert_called_once_with(vector_store=self.knowledge_manager.vector_store)
        mock_vector_store_index.from_documents.assert_called_once_with(
            [mock_document],
            storage_context=mock_storage_context.from_defaults.return_value
        )

    @patch('aimanager.knowledge.pgvector.VectorStoreIndex')
    def test_search(self, mock_vector_store_index):
        mock_index = MagicMock()
        mock_query_engine = MagicMock()
        mock_response = MagicMock()
        mock_node = MagicMock()

        mock_node.get_content.return_value = "content"
        mock_response.source_nodes = [mock_node]
        mock_query_engine.query.return_value = mock_response
        mock_index.as_query_engine.return_value = mock_query_engine
        mock_vector_store_index.from_vector_store.return_value = mock_index

        result = self.knowledge_manager.search("test query", limit=1)

        mock_vector_store_index.from_vector_store.assert_called_once_with(self.knowledge_manager.vector_store)
        mock_index.as_query_engine.assert_called_once_with(similarity_top_k=1)
        mock_query_engine.query.assert_called_once_with("test query")
        self.assertEqual(result, ["content"])
    
    


if __name__ == '__main__':
    unittest.main()
