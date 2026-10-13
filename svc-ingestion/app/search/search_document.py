from app._db.pool import pool

class SearchDocument():
    def search(self, embedded_query: str):
        search_query = """
            SELECT 
                d1.document_id,
                d1.filename,
                d1.file_type,
                c2.chunk_index,
                c2.text_content,
                e3.embedding_id
            FROM documents d1
            INNER JOIN chunks c2 ON d1.document_id = c2.document_id
            INNER JOIN embeddings e3 ON c2.chunk_id = e3.chunk_id
            ORDER BY e3.embedding <=> %s::vector
            LIMIT 5;
        """
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    search_query,
                    (embedded_query,)
                )
                results = cur.fetchall()
                formatted_results = {
                    "document_id": results[0][0],
                    "document_name": f"{results[0][1]}.{results[0][2]}",
                    "chunk_number": results[0][3],
                    "chunk_content": results[0][4],
                    "embedding_id": results[0][5]
                }
        return formatted_results