"""
Streamlit RAG Application
Query the report writing knowledge base with an interactive UI
"""

import streamlit as st
import duckdb
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon="📚",
    layout="wide"
)

# Title and description
st.title("📚 Report Writing Knowledge Base")
st.markdown("Ask questions about effective report writing based on the stored document.")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model selection
    model = st.selectbox(
        "LLM Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        index=0
    )
    
    # Temperature slider
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )
    
    # Top-k results
    top_k = st.slider(
        "Number of chunks to retrieve",
        min_value=1,
        max_value=10,
        value=3,
        step=1
    )
    
    st.divider()
    
    # Database info
    db_path = "report_writing_python.duckdb"
    if os.path.exists(db_path):
        st.success(f"✅ Connected to database")
        
        # Show database stats
        conn = duckdb.connect(db_path)
        chunk_count = conn.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]
        st.metric("Total Chunks", chunk_count)
        conn.close()
    else:
        st.error("❌ Database not found. Run main.py first.")
        st.stop()
    
    st.divider()
    
    # Clear history button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Helper functions
@st.cache_resource
def get_embedding_model():
    """Get the embedding model (cached)."""
    return OpenAIEmbeddings(model="text-embedding-3-large")

def query_duckdb(query_text, top_k=3):
    """Query the DuckDB vector store."""
    embedding_model = get_embedding_model()
    query_embedding = embedding_model.embed_query(query_text)
    
    conn = duckdb.connect(db_path)
    result = conn.execute("""
        SELECT 
            id,
            text,
            metadata,
            list_cosine_similarity(embedding, ?::FLOAT[]) as similarity
        FROM document_chunks
        ORDER BY similarity DESC
        LIMIT ?
    """, [query_embedding, top_k]).fetchall()
    conn.close()
    
    return result

def get_llm_response(user_query, retrieved_chunks, model_name, temp):
    """Generate LLM response based on retrieved chunks."""
    
    # Format retrieved chunks
    context = "\n\n---\n\n".join([chunk[1] for chunk in retrieved_chunks])
    
    # Create prompt
    prompt_template = """Use the following content to answer the user's query:

Content:
{context}

User Query:
{query}

Provide a clear and concise answer based on the given content. If the content doesn't contain relevant information, say so."""
    
    prompt = ChatPromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(model=model_name, temperature=temp)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"context": context, "query": user_query})
    return response, retrieved_chunks

# Main interface
# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show retrieved chunks for assistant messages
        if message["role"] == "assistant" and "chunks" in message:
            with st.expander("📄 View Retrieved Chunks"):
                for idx, (doc_id, text, metadata, similarity) in enumerate(message["chunks"], 1):
                    st.markdown(f"**Chunk {idx}** (Similarity: {similarity:.4f})")
                    st.text_area(
                        f"chunk_{idx}",
                        value=text,
                        height=100,
                        key=f"chunk_{message['timestamp']}_{idx}",
                        label_visibility="collapsed"
                    )
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask a question about report writing..."):
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            # Retrieve relevant chunks
            retrieved_chunks = query_duckdb(prompt, top_k)
            
        with st.spinner("Generating response..."):
            # Get LLM response
            response, chunks = get_llm_response(prompt, retrieved_chunks, model, temperature)
            
        # Display response
        st.markdown(response)
        
        # Show retrieved chunks
        with st.expander("📄 View Retrieved Chunks"):
            for idx, (doc_id, text, metadata, similarity) in enumerate(chunks, 1):
                st.markdown(f"**Chunk {idx}** (Similarity: {similarity:.4f})")
                st.text_area(
                    f"chunk_{idx}",
                    value=text,
                    height=100,
                    key=f"chunk_current_{idx}",
                    label_visibility="collapsed"
                )
                st.divider()
    
    # Add assistant message to chat history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "chunks": chunks,
        "timestamp": datetime.now()
    })

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    Built with Streamlit • Powered by OpenAI • Vector search with DuckDB
    </div>
    """,
    unsafe_allow_html=True
)
