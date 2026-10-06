CREATE TABLE app_user (
    user_id BIGSERIAL PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS document (
    document_id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES app_user(user_id)
        ON DELETE CASCADE,

    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,

    file_size BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_fragment (
    fragment_id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL
        REFERENCES document(document_id)
        ON DELETE CASCADE,

    fragment_index INTEGER NOT NULL,

    content_type TEXT NOT NULL,

    text_content TEXT,

    page_number INTEGER,

    metadata JSONB NOT NULL DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (document_id, fragment_index)
);

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS embedding (
    embedding_id BIGSERIAL PRIMARY KEY,

    fragment_id BIGINT NOT NULL
        REFERENCES content_fragment(fragment_id)
        ON DELETE CASCADE,

    embedding VECTOR(1536) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (fragment_id)
);