from app.rag_module.search_document import SearchDocument
from app.embeddings_module.embedding_generator import EmbeddingGenerator
from app.toolbox_module.models.tool_requirements import RAGQueryRequirements

class RAGTool:
    def __init__(
        self,
        limit: int = 5,
        min_similarity: float = 0.60
    ):
        self.embedding_generator = EmbeddingGenerator()
        self.search_document = SearchDocument()
        self.limit = limit
        self.min_similarity = min_similarity

    def execute(self, query: str) -> dict:
        params = RAGQueryRequirements(query=query)

        embedded_query = self.embedding_generator.generate(params.query)
        results = self.search_document.search(
            embedded_query,
            limit=self.limit,
            min_similarity=self.min_similarity
        )

        sources = [
            {
                "document_id": result["document_id"],
                "document_name": result["document_name"],
                "source": result["source"],
                "chunk_number": result["chunk_number"]
            }
            for result in results
        ]

        return {
            "query": params.query,
            "results": results,
            "sources": sources
        }
