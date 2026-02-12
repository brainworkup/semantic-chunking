# Semantic Chunking

A package for semantic text chunking in R.

## Description

This R package provides tools to split text into semantically meaningful chunks. Unlike traditional chunking methods that rely on fixed lengths or syntactic boundaries, semantic chunking uses embeddings and similarity measures to create coherent text segments that preserve context and meaning.

## Features

- Semantic text segmentation using embeddings
- Configurable similarity thresholds
- Support for various embedding models
- Efficient processing for large texts

## Installation

You can install the development version from GitHub:

```r
# install.packages("devtools")
devtools::install_github("brainworkup/semantic-chunking")
```

## Usage

```r
library(semantic.chunking)

# Example text
text <- "This is a long document. It has multiple sentences. Each sentence conveys different ideas. Some sentences are related, while others introduce new topics."

# Chunk the text
chunks <- chunk_text(text, threshold = 0.7)

# View chunks
print(chunks)
```

## Dependencies

- text2vec
- stringr
- purrr

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.