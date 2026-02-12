# Semantic Chunking

This repository provides implementations of semantic text chunking in both Python and R for processing documents and building Retrieval-Augmented Generation (RAG) systems.

## Description

Semantic chunking splits text into meaningful segments based on semantic boundaries, rather than fixed lengths or syntactic units. This approach uses embeddings and similarity measures to create coherent chunks that preserve context and improve downstream tasks like retrieval and summarization.

The repository includes example implementations in Python using LangChain and in R using the ragnar package.

## Features

- Semantic text segmentation using embeddings
- Configurable similarity thresholds
- Support for various embedding models (OpenAI)
- Text cleaning and preprocessing (hyphenated breaks, ligatures)
- Vector storage and retrieval for RAG applications
- Integration with language models for question answering

## Installation

### Python

Install the required packages:

```bash
pip install langchain langchain-community langchain-experimental langchain-openai
```

### R

You can install the development version from GitHub:

```r
# install.packages("devtools")
devtools::install_github("brainworkup/semantic-chunking")
```

For the ragnar-based implementation, install ragnar and ellmer:

```r
# Install ragnar from GitHub
# install.packages("pak")
pak::pkg_install("tidyverse/ragnar")

# Install ellmer
install.packages("ellmer")
```

## Usage

### Python Version

The Python implementation uses LangChain's `SemanticChunker` for chunking, with OpenAI embeddings, and includes a complete RAG pipeline with retrieval and LLM response generation.

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load and chunk PDF
pdf_path = "your_document.pdf"
loader = PyPDFLoader(pdf_path)
pages = [page.page_content for page in loader.lazy_load()]

text_splitter = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"))
chunks = text_splitter.create_documents(pages)

# Clean chunks (hyphenated breaks, ligatures)
# ... cleaning functions ...

# Create vector store
vectorstore = InMemoryVectorStore.from_texts(
    [chunk.page_content for chunk in chunks_final], 
    embedding=OpenAIEmbeddings(model="text-embedding-3-large")
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Query and retrieve
user_query = "What are the key components?"
retrieved_docs = retriever.invoke(user_query)

# Generate response with LLM
prompt = ChatPromptTemplate.from_template("""
Use the following content to answer: {docs}
Query: {query}
""")

chain = prompt | ChatOpenAI(model="gpt-4") | StrOutputParser()
response = chain.invoke({"docs": retrieved_docs, "query": user_query})
print(response)
```

### R Version

The R implementation uses the ragnar package for semantic chunking and vector storage, with OpenAI embeddings via ellmer.

```r
library(ragnar)
library(ellmer)

# Load and chunk PDF
pdf_path <- "your_document.pdf"
pdf_markdown <- read_as_markdown(pdf_path)
chunks <- markdown_chunk(pdf_markdown)

# Clean chunks
# ... cleaning functions ...

# Create vector store
store <- ragnar_store_create(
  "store.duckdb",
  embed = \(x) embed_openai(x, model = "text-embedding-3-large")
)
ragnar_store_insert(store, chunks_final)
ragnar_store_build_index(store)

# Retrieve
user_query <- "What are the key components?"
retrieved_chunks <- ragnar_retrieve(store, user_query, top_k = 3)

# Prompt template for LLM
prompt_template <- "
Use the following content: {retrieved_documents}
Query: {user_query}
"
```

## Comparison between Python and R Implementations

Both implementations provide similar functionality but use different libraries:

- **Chunking**: Python uses LangChain's `SemanticChunker`; R uses ragnar's `markdown_chunk()`
- **Embeddings**: Both use OpenAI's `text-embedding-3-large`
- **Vector Storage**: Python uses in-memory store; R uses DuckDB-based persistent storage
- **Retrieval**: Python uses similarity search with threshold; R combines VSS and BM25
- **LLM Integration**: Both support prompt templates, but Python includes a complete chain with response parsing
- **Text Cleaning**: Identical preprocessing for hyphens and ligatures
- **Dependencies**: Python relies on LangChain ecosystem; R uses ragnar and tidyverse packages

The Python version is more focused on LangChain's modular pipeline, while the R version emphasizes persistent storage and hybrid search.

## Dependencies

### Python
- langchain
- langchain-community
- langchain-experimental
- langchain-openai

### R
- ragnar
- ellmer
- stringr
- dplyr

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.