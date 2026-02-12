library(ragnar)
library(ellmer)
library(stringr)
library(dplyr)
library(glue)

# 1. Load PDF and extract text
pdf_path <- "Essentials_Report_Writing_1stEd.pdf"

# Convert PDF to markdown
pdf_markdown <- read_as_markdown(pdf_path)

# 2. Semantic Chunking
# ragnar's markdown_chunk() function automatically does semantic chunking
# by identifying semantic boundaries in the document
chunks <- markdown_chunk(pdf_markdown)

# 3. Clean the chunks for optimal RAG performance

# Function to clean hyphenated linebreaks
clean_hyphenated_linebreaks <- function(text) {
  str_replace_all(text, "(\\w+)-\\n(\\w+)", "\\1\\2")
}

# Function to fix ligatures
fix_ligatures <- function(text) {
  ligature_map <- c(
    "\ufb01" = "fi",  # ﬁ
    "\ufb02" = "fl",  # ﬂ
    "\ufb00" = "ff",  # ﬀ
    "\ufb03" = "ffi", # ﬃ
    "\ufb04" = "ffl"  # ﬄ
  )
  
  for (i in seq_along(ligature_map)) {
    text <- str_replace_all(text, names(ligature_map)[i], ligature_map[i])
  }
  
  return(text)
}

# Apply cleaning transformations
# Assuming chunks is a tibble with a 'text' column
chunks_cleaned <- chunks |>
  mutate(
    text = text |>
      clean_hyphenated_linebreaks() |>
      fix_ligatures()
  )

# Filter out very short chunks (likely artifacts)
MIN_CHUNK_LENGTH <- 50
chunks_final <- chunks_cleaned |>
  filter(nchar(text) >= MIN_CHUNK_LENGTH)

message(sprintf("Chunks after cleaning: %d → %d", 
                nrow(chunks), nrow(chunks_final)))

# 4. Create vector store and insert chunks
# Create a DuckDB-based store with OpenAI embeddings
# Using version = 1 to allow text modification before insertion
# If the file exists, delete it
if (file.exists("report_writing.ragnar.duckdb")) {
  file.remove("report_writing.ragnar.duckdb")  
}
store_location <- "report_writing.ragnar.duckdb"

store <- ragnar_store_create(
  store_location,
  embed = \(x) embed_openai(x, model = "text-embedding-3-large"),
  version = 1
)

# Insert the cleaned chunks into the store
ragnar_store_insert(store, chunks_final)

# Build the index for efficient retrieval
ragnar_store_build_index(store)

# 5. User Query
user_query <- "What are the key components of effective report writing according to the document?"

# 6. Retrieval
# Retrieve the most similar text using ragnar_retrieve
# This combines VSS (vector similarity search) and BM25 text search
retrieved_chunks <- ragnar_retrieve(
  store, 
  user_query, 
  top_k = 3
)

# Display retrieved chunks
print("Retrieved chunks:")
print(retrieved_chunks)

# 7. Create prompt template for chat
prompt_template <- "
Use the following content to answer the user's query:

Content:
{retrieved_documents}

User Query:
{user_query}

Provide a clear and concise answer based on the given content.
"

# 8. Create chat with OpenAI
chat <- chat_openai(
  model = "gpt-4o",
  system_prompt = "You are a helpful assistant that answers questions based on provided context."
)

# 9. Format the retrieved documents for the prompt
retrieved_text <- retrieved_chunks |>
  pull(text) |>
  paste(collapse = "\n\n---\n\n")

# Create the full prompt
full_prompt <- str_glue(
  prompt_template,
  retrieved_documents = retrieved_text,
  user_query = user_query
)

# 10. Get response from chat
response <- chat$chat(full_prompt)

# Output the response
cat("\nResponse:\n")
cat(response, "\n")

# Alternative: Register ragnar retrieval tool with ellmer chat
# This allows the LLM to retrieve chunks on-demand during conversation

cat("\n\n=== Example with ragnar tool registration ===\n\n")

# Create a new chat with system prompt
chat_with_tool <- chat_openai(
  system_prompt = "You are a helpful assistant. Use the search_store tool to retrieve relevant information before answering questions.",
  model = "gpt-4o"
)

# Register the ragnar retrieval tool
ragnar_register_tool_retrieve(chat_with_tool, store, top_k = 3)

# Now the chat can automatically retrieve relevant chunks
response_with_tool <- chat_with_tool$chat(user_query)

cat("\nResponse with tool:\n")
cat(response_with_tool, "\n")

# For interactive console usage (similar to chatlas console mode):
# Uncomment the following line to start an interactive chat session
chat_with_tool$console()
