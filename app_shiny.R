library(shiny)
library(bslib)
library(ragnar)
library(ellmer)
library(dplyr)
library(stringr)

# UI Definition
ui <- page_sidebar(
  title = "📚 Report Writing Knowledge Base",
  theme = bs_theme(preset = "shiny", primary = "#0066cc"),
  
  # Sidebar
  sidebar = sidebar(
    title = "⚙️ Settings",
    
    # Model selection
    selectInput(
      "model",
      "LLM Model",
      choices = c("gpt-4o", "gpt-4o-mini", "gpt-4-turbo"),
      selected = "gpt-4o"
    ),
    
    # Top-k results
    sliderInput(
      "top_k",
      "Number of chunks to retrieve",
      min = 1,
      max = 10,
      value = 3,
      step = 1
    ),
    
    hr(),
    
    # Database info
    h4("Database Status"),
    uiOutput("db_status"),
    
    hr(),
    
    # Clear history button
    actionButton(
      "clear_history",
      "🗑️ Clear Chat History",
      class = "btn-outline-danger w-100"
    )
  ),
  
  # Main panel
  card(
    card_header("Chat Interface"),
    card_body(
      uiOutput("chat_history"),
      min_height = "500px",
      max_height = "600px",
      style = "overflow-y: auto;"
    )
  ),
  
  # Input area
  layout_columns(
    col_widths = c(10, 2),
    textInput(
      "user_input",
      NULL,
      placeholder = "Ask a question about report writing...",
      width = "100%"
    ),
    actionButton(
      "send",
      "Send",
      class = "btn-primary",
      width = "100%",
      style = "margin-top: 0px;"
    )
  )
)

# Server Logic
server <- function(input, output, session) {
  
  # Reactive values for chat history
  chat_history <- reactiveVal(list())
  
  # Connect to the ragnar store
  store <- reactive({
    db_path <- "report_writing.ragnar.duckdb"
    
    req(file.exists(db_path))
    
    ragnar_store_connect(db_path, read_only = TRUE)
  })
  
  # Database status
  output$db_status <- renderUI({
    db_path <- "report_writing.ragnar.duckdb"
    
    if (file.exists(db_path)) {
      tryCatch({
        store_obj <- store()
        
        # Get chunk count
        conn <- DBI::dbConnect(duckdb::duckdb(), db_path, read_only = TRUE)
        chunk_count <- DBI::dbGetQuery(conn, "SELECT COUNT(*) as n FROM chunks")$n
        DBI::dbDisconnect(conn)
        
        div(
          tags$span(class = "badge bg-success", "✓ Connected"),
          tags$p(
            class = "mt-2 mb-0",
            tags$strong("Total Chunks: "), chunk_count
          )
        )
      }, error = function(e) {
        div(
          tags$span(class = "badge bg-danger", "✗ Error"),
          tags$p(class = "mt-2 text-danger small", e$message)
        )
      })
    } else {
      div(
        tags$span(class = "badge bg-danger", "✗ Not Found"),
        tags$p(class = "mt-2 text-danger small", "Run main.R first to create database")
      )
    }
  })
  
  # Create chat object
  chat_obj <- reactive({
    chat_openai(
      model = input$model,
      system_prompt = "You are a helpful assistant that answers questions about effective report writing. Provide clear and concise answers based on the retrieved context."
    )
  })
  
  # Handle send button click
  observeEvent(input$send, {
    req(input$user_input, nchar(trimws(input$user_input)) > 0)
    
    user_query <- input$user_input
    
    # Add user message to history
    history <- chat_history()
    history <- c(
      history,
      list(list(
        role = "user",
        content = user_query,
        timestamp = Sys.time()
      ))
    )
    chat_history(history)
    
    # Clear input
    updateTextInput(session, "user_input", value = "")
    
    # Retrieve chunks
    retrieved_chunks <- ragnar_retrieve(
      store(),
      user_query,
      top_k = input$top_k
    )
    
    # Format context
    context <- retrieved_chunks |>
      pull(text) |>
      paste(collapse = "\n\n---\n\n")
    
    # Create prompt
    prompt <- str_glue(
      "Use the following content to answer the user's query:\n\n",
      "Content:\n{context}\n\n",
      "User Query:\n{user_query}\n\n",
      "Provide a clear and concise answer based on the given content."
    )
    
    # Get response from chat
    response <- chat_obj()$chat(prompt)
    
    # Add assistant message to history
    history <- chat_history()
    history <- c(
      history,
      list(list(
        role = "assistant",
        content = as.character(response),
        chunks = retrieved_chunks,
        timestamp = Sys.time()
      ))
    )
    chat_history(history)
  })
  
  # Handle enter key in text input
  observeEvent(input$user_input, {
    if (grepl("\n$", input$user_input)) {
      shinyjs::click("send")
    }
  })
  
  # Clear chat history
  observeEvent(input$clear_history, {
    chat_history(list())
  })
  
  # Render chat history
  output$chat_history <- renderUI({
    history <- chat_history()
    
    if (length(history) == 0) {
      return(
        div(
          class = "text-center text-muted p-5",
          icon("comments", class = "fa-3x mb-3"),
          h4("Start a conversation"),
          p("Ask a question about effective report writing")
        )
      )
    }
    
    # Create chat messages
    messages <- lapply(seq_along(history), function(i) {
      msg <- history[[i]]
      
      if (msg$role == "user") {
        # User message
        div(
          class = "mb-3",
          div(
            class = "d-flex justify-content-end",
            div(
              class = "card bg-primary text-white",
              style = "max-width: 80%;",
              card_body(
                p(class = "mb-0", msg$content),
                padding = "sm"
              )
            )
          )
        )
      } else {
        # Assistant message
        div(
          class = "mb-3",
          div(
            class = "d-flex justify-content-start",
            div(
              class = "card",
              style = "max-width: 80%;",
              card_body(
                markdown(msg$content),
                
                # Show retrieved chunks
                if (!is.null(msg$chunks)) {
                  accordion(
                    accordion_panel(
                      "📄 View Retrieved Chunks",
                      lapply(seq_len(nrow(msg$chunks)), function(j) {
                        chunk <- msg$chunks[j, ]
                        div(
                          class = "mb-2",
                          tags$strong(sprintf("Chunk %d", j)),
                          if (!is.null(chunk$cosine_distance[[1]])) {
                            tags$span(
                              class = "badge bg-secondary ms-2",
                              sprintf("Similarity: %.4f", 1 - chunk$cosine_distance[[1]])
                            )
                          },
                          tags$pre(
                            class = "mt-2 p-2 bg-light",
                            style = "font-size: 0.85em; max-height: 150px; overflow-y: auto;",
                            chunk$text
                          ),
                          if (j < nrow(msg$chunks)) tags$hr()
                        )
                      })
                    )
                  )
                },
                padding = "sm"
              )
            )
          )
        )
      }
    })
    
    # Reverse order (newest first) and combine
    tagList(rev(messages))
  })
}

# Run the application
shinyApp(ui = ui, server = server)
