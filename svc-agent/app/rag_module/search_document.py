from app.rag_module.db_connection.pool import pool

class SearchDocument:
    def search(
        self,
        embedded_query: list[float],
        limit: int = 5,
        min_similarity: float = 0.60
    ) -> list[dict]:
        if not embedded_query:
            raise ValueError("Query embedding cannot be empty")

        if not 1 <= limit <= 20:
            raise ValueError("Limit must be between 1 and 20")

        if not 0 <= min_similarity <= 1:
            raise ValueError("Minimum similarity must be between 0 and 1")

        search_query = """
            SELECT
                d.document_id,
                d.filename,
                d.file_type,
                d.source,
                c.chunk_id,
                c.chunk_index,
                c.text_content,
                e.embedding_id,
                e.embedding <=> %s::vector AS distance
            FROM documents d
            INNER JOIN chunks c
                ON d.document_id = c.document_id
            INNER JOIN embeddings e
                ON c.chunk_id = e.chunk_id
            WHERE c.text_content IS NOT NULL
                AND BTRIM(c.text_content) <> ''
                AND 1 - (e.embedding <=> %s::vector) >= %s
            ORDER BY distance ASC
            LIMIT %s;
        """

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    search_query,
                    (embedded_query, embedded_query, min_similarity, limit)
                )
                rows = cur.fetchall()

        return [
            {
                "document_id": row[0],
                "document_name": row[1],
                "file_type": row[2],
                "source": row[3],
                "chunk_id": row[4],
                "chunk_number": row[5],
                "chunk_content": row[6],
                "embedding_id": row[7],
                "distance": float(row[8]),
            }
            for row in rows
        ]
