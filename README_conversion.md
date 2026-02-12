# Python to R RAG Conversion Guide

This document explains the conversion from the Python LangChain-based RAG script to R using `ragnar` and `ellmer` packages.

## Key Package Mappings

| Python Package | R Package | Purpose |
|----------------|-----------|---------|
| `langchain_community.document_loaders` | `ragnar::read_as_markdown()` | Document loading |
| `langchain_experimental.text_splitter.SemanticChunker` | `ragnar::markdown_chunk()` | Semantic chunking |
| `langchain_openai.embeddings.OpenAIEmbeddings` | `ragnar::embed_openai()` | Embeddings |
| `langchain_core.vectorstores.InMemoryVectorStore` | `ragnar::ragnar_store_create()` | Vector storage |
| `langchain_openai.ChatOpenAI` | `ellmer::chat_openai()` | Chat interface |
| `chatlas.ChatOllama` | `ellmer::chat_ollama()` | Local Ollama models |

## Main Differences

### 1. Document Loading
**Python:**
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(pdf_path)
pages = [page.page_content for page in loader.lazy_load()]
```

**R:**
```r
library(ragnar)
pdf_markdown <- read_as_markdown(pdf_path)
```

### 2. Chunking
**Python:**
```python
from langchain_experimental.text_splitter import SemanticChunker
text_splitter = SemanticChunker(OpenAIEmbeddings(model="text-embedding-3-large"))
chunks = text_splitter.create_documents(pages)
```

**R:**
```r
chunks <- markdown_chunk(pdf_markdown)
```

### 3. Vector Store Creation
**Python:**
```python
from langchain_core.vectorstores import InMemoryVectorStore
vectorstore = InMemoryVectorStore.from_texts(
    texts,
    embedding=OpenAIEmbeddings(model="text-embedding-3-large")
)
```

**R:**
```r
store <- ragnar_store_create(
  "store.duckdb",
  embed = \(x) embed_openai(x, model = "text-embedding-3-large")
)
ragnar_store_insert(store, chunks)
ragnar_store_build_index(store)
```

**Note:** R uses DuckDB for persistent storage instead of in-memory storage.

### 4. Retrieval
**Python:**
```python
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"score_threshold": 0.7, "k": 3}
)
retrieved_documents = retriever.invoke(user_query)
```

**R:**
```r
retrieved_chunks <- ragnar_retrieve(store, user_query, top_k = 3)
```

**Note:** `ragnar_retrieve()` combines both VSS (vector similarity) and BM25 text search.

### 5. Chat Interface
**Python:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_prompt = ChatPromptTemplate.from_template(prompt_template)
chain = structured_prompt | llm | StrOutputParser()
response = chain.invoke({"retrieved_documents": docs, "user_query": query})
```

**R:**
```r
library(ellmer)

chat <- chat_openai(
  model = "gpt-4o",
  system_prompt = "Your system prompt here"
)

# Manual retrieval approach
response <- chat$chat(formatted_prompt)

# Or use tool registration for automatic retrieval
ragnar_register_tool_retrieve(chat, store, top_k = 3)
response <- chat$chat(user_query)
```

### 6. Text Cleaning Functions
**Python:**
```python
def clean_hyphenated_linebreaks(text):
    return re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

def fix_ligatures(text):
    ligature_map = {'ﬁ': 'fi', 'ﬂ': 'fl', ...}
    for ligature, replacement in ligature_map.items():
        text = text.replace(ligature, replacement)
    return text
```

**R:**
```r
library(stringr)

clean_hyphenated_linebreaks <- function(text) {
  str_replace_all(text, "(\\w+)-\\n(\\w+)", "\\1\\2")
}

fix_ligatures <- function(text) {
  ligature_map <- c(
    "\ufb01" = "fi",  # ﬁ
    "\ufb02" = "fl",  # ﬂ
    ...
  )
  for (i in seq_along(ligature_map)) {
    text <- str_replace_all(text, names(ligature_map)[i], ligature_map[i])
  }
  return(text)
}
```

## Key Advantages of ragnar + ellmer

1. **Integrated workflow**: ragnar provides end-to-end RAG pipeline
2. **Persistent storage**: Uses DuckDB for efficient, persistent vector storage
3. **Hybrid search**: Combines VSS and BM25 automatically
4. **Tool integration**: `ragnar_register_tool_retrieve()` lets LLMs retrieve on-demand
5. **Tidyverse-friendly**: Works well with dplyr/tidyverse workflows

## Environment Setup

Make sure you have your OpenAI API key set:

```r
# In your .Renviron file (edit with usethis::edit_r_environ())
OPENAI_API_KEY="your-api-key-here"
```

## Installation

```r
install.packages("ragnar")
install.packages("ellmer")
install.packages("stringr")
```

## Running the Script

```r
source("main.R")
```
