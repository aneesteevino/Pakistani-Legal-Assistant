-- Enable pgvector extension
create extension if not exists vector;

-- Create legal documents table
create table if not exists legal_docs (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  embedding vector(1536),
  source text not null,
  law_name text,
  section text,
  created_at timestamp with time zone default now()
);

-- Create index for vector similarity search
create index if not exists legal_docs_embedding_idx 
on legal_docs using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Create function for document matching
create or replace function match_documents (
  query_embedding vector(1536),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  source text,
  law_name text,
  section text,
  similarity float
)
language sql stable
as $$
  select
    legal_docs.id,
    legal_docs.content,
    legal_docs.source,
    legal_docs.law_name,
    legal_docs.section,
    1 - (legal_docs.embedding <=> query_embedding) as similarity
  from legal_docs
  where 1 - (legal_docs.embedding <=> query_embedding) > match_threshold
  order by legal_docs.embedding <=> query_embedding
  limit match_count;
$$;

-- Create RLS policies (optional, for security)
alter table legal_docs enable row level security;

-- Allow read access to all users (adjust as needed)
create policy "Allow read access to legal_docs" on legal_docs
  for select using (true);

-- Allow insert for authenticated users (adjust as needed)
create policy "Allow insert to legal_docs" on legal_docs
  for insert with check (true);