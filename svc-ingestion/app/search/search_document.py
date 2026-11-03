from app._db.pool import pool


class SearchDocument:
    def search(self, embedded_query: list[float]) -> list[dict]:
        search_query = """
            SELECT
                d.document_id,
                d.filename,
                d.file_type,
                c.chunk_index,
                c.text_content,
                e.embedding_id,
                e.embedding <=> %s::vector AS distance
            FROM documents d
            INNER JOIN chunks c ON d.document_id = c.document_id
            INNER JOIN embeddings e ON c.chunk_id = e.chunk_id
            ORDER BY distance ASC
            LIMIT 5;
        """

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(search_query, (embedded_query,))
                results = cur.fetchall()

        formatted_results = [
            {
                "document_id": row[0],
                "document_name": f"{row[1]}.{row[2]}",
                "chunk_number": row[3],
                "chunk_content": row[4],
                "embedding_id": row[5],
                "distance": float(row[6]),
            }
            for row in results
        ]

        return formatted_results
