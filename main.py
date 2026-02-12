from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents.base import Document
import re

pdf_path = "Essentials_Report_Writing_1stEd.pdf"
loader = PyPDFLoader(pdf_path)

# Load all pages and extract text content
pages = [page.page_content for page in loader.lazy_load()]

# 2. Semantic Chunking

# Initialize the text splitter
text_splitter = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"))
chunks = text_splitter.create_documents(pages)

# 3. Clean the chunks for optimal RAG performance


def clean_hyphenated_linebreaks(text):
    """Join words split by hyphens across line breaks."""
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


def fix_ligatures(text):
    """Replace ligature characters with standard letter equivalents."""
    ligature_map = {
        "ﬁ": "fi",  # U+FB01
        "ﬂ": "fl",  # U+FB02
        "ﬀ": "ff",  # U+FB00
        "ﬃ": "ffi",  # U+FB03
        "ﬄ": "ffl",  # U+FB04
    }
    for ligature, replacement in ligature_map.items():
        text = text.replace(ligature, replacement)
    return text


# Apply cleaning transformations
chunks_cleaned = []
for chunk in chunks:
    # Clean hyphenated line breaks
    cleaned_content = clean_hyphenated_linebreaks(chunk.page_content)
    # Fix ligature characters
    cleaned_content = fix_ligatures(cleaned_content)
    # Create cleaned chunk
    chunks_cleaned.append(
        Document(page_content=cleaned_content, metadata=chunk.metadata)
    )

# Filter out very short chunks (likely artifacts)
MIN_CHUNK_LENGTH = 50
chunks_final = [
    chunk for chunk in chunks_cleaned if len(chunk.page_content) >= MIN_CHUNK_LENGTH
]

print(f"Chunks after cleaning: {len(chunks)} → {len(chunks_final)}")

# storing a vector
from langchain_core.vectorstores import InMemoryVectorStore

# Prepare texts for storage (using cleaned chunks)
texts = [chunk.page_content for chunk in chunks_final]

# Create a vector store with optimized chunks
vectorstore = InMemoryVectorStore.from_texts(
    texts, embedding=OpenAIEmbeddings(model="text-embedding-3-large")
)

# Save embeddings to DuckDB for persistent storage
import duckdb
import json

db_path = "report_writing_python.duckdb"
conn = duckdb.connect(db_path)

# Create table for storing chunks and embeddings
conn.execute("""
    CREATE TABLE IF NOT EXISTS document_chunks (
        id INTEGER PRIMARY KEY,
        text TEXT,
        embedding FLOAT[],
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Get embeddings from vectorstore
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

# Insert chunks with their embeddings
for idx, (text, chunk) in enumerate(zip(texts, chunks_final)):
    embedding = embedding_model.embed_query(text)
    metadata_json = json.dumps(chunk.metadata)

    conn.execute(
        """
        INSERT INTO document_chunks (id, text, embedding, metadata)
        VALUES (?, ?, ?, ?)
        """,
        [idx, text, embedding, metadata_json],
    )

conn.commit()
print(f"\n✓ Saved {len(texts)} chunks with embeddings to {db_path}")


# Create a helper function to query from DuckDB
def query_duckdb(query_text, top_k=3):
    """Query the DuckDB vector store."""
    query_embedding = embedding_model.embed_query(query_text)

    # Calculate cosine similarity using DuckDB
    result = conn.execute(
        """
        SELECT 
            id,
            text,
            metadata,
            list_cosine_similarity(embedding, ?::FLOAT[]) as similarity
        FROM document_chunks
        ORDER BY similarity DESC
        LIMIT ?
    """,
        [query_embedding, top_k],
    ).fetchall()

    return result


# 4. Setting Up the Retriever
retriever = vectorstore.as_retriever(
    search_type="similarity", search_kwargs={"score_threshold": 0.7, "k": 3}
)

# 5. User Query
# Define the user query
user_query = (
    "What are the key components of effective report writing according to the document?"
)

# 6. Retrieval

# Retrieve the most similar text using the retriever
retrieved_documents = retriever.invoke(user_query)

# 7. Prompt Creation and Structuring the Prompt

# Create a prompt using the retrieved documents and user query
prompt_template = """
Use the following content to answer the user's query:

Content:
{retrieved_documents}

User Query:
{user_query}

Provide a clear and concise answer based on the given content.
"""

# Structure the prompt
from langchain_core.prompts import ChatPromptTemplate

structured_prompt = ChatPromptTemplate.from_template(prompt_template)

# 8. Processing Chain Creation

# Initialize the language model
llm = ChatOpenAI(model="gpt-5.2", temperature=0)

# Create the processing chain
chain = structured_prompt | llm | StrOutputParser()

# 9. Invoke the Chain

# Invoke the chain with the retrieved documents and user query
response = chain.invoke(
    {"retrieved_documents": retrieved_documents, "user_query": user_query}
)

# 10. Output the Response

# Output the generated response
print("Response:")
print(response)

# Save the response as a markdown file for later use as a prompt/instruction template
output_file = "response_template.md"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("# Response Template\n\n")
    f.write("## Original Query\n")
    f.write(f"{user_query}\n\n")
    f.write("## Generated Response\n")
    f.write(f"{response}\n\n")
    f.write("---\n")
    f.write("Generated on: " + str(__import__("datetime").datetime.now()) + "\n")

print(f"\nResponse saved to {output_file}")

# Demonstrate querying from DuckDB
print("\n=== Testing DuckDB Query ===")
duckdb_results = query_duckdb(user_query, top_k=3)
print(f"\nRetrieved {len(duckdb_results)} chunks from DuckDB:")
for idx, (doc_id, text, metadata, similarity) in enumerate(duckdb_results, 1):
    print(f"\n{idx}. Similarity: {similarity:.4f}")
    print(f"   Text preview: {text[:100]}...")

# Close DuckDB connection
conn.close()
print(f"\n✓ DuckDB connection closed")
