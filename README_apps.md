# RAG Application UIs

This directory contains interactive web applications for querying your RAG knowledge base.

## 🐍 Python - Streamlit App

### Installation

First, install Streamlit:

```bash
pip install streamlit
```

### Running the App

```bash
streamlit run app_streamlit.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Features

- 💬 **Chat Interface**: Interactive conversation with chat history
- 🔍 **Vector Search**: Retrieves relevant chunks using DuckDB vector similarity
- 📊 **Configurable Settings**: 
  - Choose between GPT-4o, GPT-4o-mini, or GPT-4-turbo
  - Adjust temperature for creativity
  - Set number of chunks to retrieve (1-10)
- 📄 **View Retrieved Chunks**: Expandable sections showing source context
- 📈 **Database Stats**: See total chunk count in sidebar
- 🗑️ **Clear History**: Reset conversation at any time

### Requirements

- `streamlit`
- `duckdb`
- `langchain-openai`
- `langchain-core`
- `openai`

---

## 📊 R - Shiny App

### Installation

First, install the required packages:

```r
install.packages(c("shiny", "bslib", "ragnar", "ellmer", "dplyr", "stringr", "DBI", "duckdb"))
```

### Running the App

In R or RStudio:

```r
shiny::runApp("app_shiny.R")
```

Or from the terminal:

```bash
Rscript -e "shiny::runApp('app_shiny.R')"
```

The app will open at `http://localhost:3838` (or your configured port)

### Features

- 💬 **Chat Interface**: Beautiful conversation UI with message history
- 🔍 **Ragnar Integration**: Uses ragnar's hybrid VSS + BM25 search
- 📊 **Configurable Settings**:
  - Choose between GPT-4o, GPT-4o-mini, or GPT-4-turbo
  - Set number of chunks to retrieve (1-10)
- 📄 **Collapsible Chunks**: Accordion-style view of retrieved context
- 📈 **Database Status**: Real-time connection and chunk count
- 🗑️ **Clear History**: Reset conversation at any time
- 🎨 **Modern UI**: Built with Bootstrap 5 via bslib

### Requirements

- `shiny`
- `bslib`
- `ragnar`
- `ellmer`
- `dplyr`
- `stringr`
- `DBI`
- `duckdb`

---

## 🚀 Quick Start

### Step 1: Generate the Knowledge Base

**Python:**
```bash
python main.py
```

**R:**
```r
source("main.R")
```

This creates the DuckDB databases with embeddings.

### Step 2: Launch Your Preferred UI

**Python (Streamlit):**
```bash
streamlit run app_streamlit.py
```

**R (Shiny):**
```r
shiny::runApp("app_shiny.R")
```

---

## 📸 Screenshots

### Streamlit App
- Clean, minimalist design
- Sidebar configuration panel
- Chat-style message interface
- Expandable chunk viewer with similarity scores

### Shiny App
- Modern Bootstrap 5 design
- Sidebar with real-time database stats
- Accordion-style chunk display
- Responsive layout

---

## 🔧 Environment Variables

Make sure your OpenAI API key is set:

**Bash/Zsh:**
```bash
export OPENAI_API_KEY="your-key-here"
```

**R (.Renviron):**
```r
# Edit with: usethis::edit_r_environ()
OPENAI_API_KEY="your-key-here"
```

---

## 🎯 Key Differences

| Feature | Streamlit (Python) | Shiny (R) |
|---------|-------------------|-----------|
| **Search** | Pure vector similarity (cosine) | Hybrid VSS + BM25 |
| **Database** | Direct DuckDB queries | ragnar store abstraction |
| **UI Framework** | Streamlit | Shiny + bslib |
| **Temperature Control** | ✅ Yes | ❌ No (but easily added) |
| **Message Format** | Markdown | Markdown via bslib |
| **Chunk Display** | Expander | Accordion |

---

## 💡 Tips

- **Python**: Use `streamlit run --server.port 8502 app_streamlit.py` to change the port
- **R**: Add `options(shiny.port = 3839)` in the script to change the port
- Both apps work best with the database already created (run `main.py` or `main.R` first)
- Chat history is stored in session state and resets when you refresh the page

---

## 🐛 Troubleshooting

**"Database not found" error:**
- Run `main.py` (Python) or `source("main.R")` (R) first to create the database

**"API key not found" error:**
- Set your `OPENAI_API_KEY` environment variable

**Port already in use:**
- Change the port using the tips above
- Or kill the existing process

**Streamlit not updating:**
- Use `streamlit run --server.runOnSave true app_streamlit.py` for auto-reload

---

Enjoy your RAG applications! 🎉
