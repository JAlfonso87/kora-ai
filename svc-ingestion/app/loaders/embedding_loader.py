from pydantic import BaseModel
from app._db.pool import pool

class EMBLoader():
    def upload(self, upload_arguments, batch_size=100):
        print("<< STARTING EMBEDDING UPLOAD PROCESS >>")
        chunks, metadata = upload_arguments['chunks'], upload_arguments['metadata']

        if not chunks:
            return 0

        document_insertion = """
            INSERT INTO documents (
                filename,
                mime_type,
                source,
                file_type,
                file_size
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING document_id;
        """

        chunk_insertion = """
            INSERT INTO chunks (
                document_id,
                chunk_index,
                content_type,
                text_content
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (document_id, chunk_index)
            DO NOTHING
            RETURNING chunk_id, chunk_index;
        """

        embedding_insertion = """
            INSERT INTO embeddings (
                chunk_id,
                embedding
            )
            VALUES (%s, %s)
            ON CONFLICT (chunk_id)
            DO NOTHING;
        """

        processed = 0

        with pool.connection() as conn:
            with conn.transaction():
                with conn.cursor() as cur:
                    document_params = (
                        metadata['file_name'],
                        metadata['mime_type'],
                        metadata['source'],
                        metadata['file_type'],
                        metadata['file_size']
                    )
                    print("<< DOCUMENT PARAMS >>")
                    print(document_params)
                    cur.execute(
                        document_insertion,
                        document_params
                    )
                    result = cur.fetchone()
                    document_id = result[0]

                    for start in range(0, len(chunks), batch_size):
                        chunk_index = 0
                        batch = chunks[start:start + batch_size]
                        for chunk in batch:
                            chunk_params = (
                               document_id,
                               chunk_index + 1,
                               "plain/txt",
                               chunk['chunk'],
                            )
                            print("<< CHUNK PARAMS >>")
                            print(chunk_params)
                            cur.execute(
                                chunk_insertion,
                                chunk_params
                            )

                            result = cur.fetchone()
                            chunk_id, chunk_index = result

                            if chunk_id is None:
                                continue

                            embedding_params = (
                                chunk_id,
                                chunk['embedding'],
                            )
                            print("<< EMBEDDING PARAMS >>")
                            print(embedding_params)
                            cur.execute(
                                embedding_insertion,
                                embedding_params
                            )

                            processed += 1

        print("<< EMBEDDING UPLOAD PROCESS CONCLUDED SUCCESSFULLY >>")
        return processed