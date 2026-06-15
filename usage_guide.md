# XRPL Documentation Scraper Usage Guide

This document explains how to use the XRPL-py documentation scraper and how the extracted data is structured for optimal use with LLMs and AI models.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages: requests, beautifulsoup4

### Installation

1. Clone the repository or download the scraper script
2. Install the required dependencies:

```bash
pip install requests beautifulsoup4
```

## Running the Scraper

To run the scraper, simply execute the main script:

```bash
python xrpl_scraper.py
```

By default, the script will:
1. Create an `xrpl_docs` directory to store the extracted documentation
2. Scrape all the main sections of the XRPL-py documentation
3. Save the extracted information as JSON files
4. Create an index file (`index.json`) that provides an overview of all scraped content

## Configuration Options

You can customize the scraper behavior by modifying the parameters when creating an instance of `XRPLDocScraper`:

```python
# Example with custom parameters
scraper = XRPLDocScraper(
    base_url="https://xrpl-py.readthedocs.io/en/stable/",
    output_dir="custom_output_directory"
)
```

## Output Structure

The scraper organizes the extracted documentation as follows:

### Directory Structure

```
xrpl_docs/
├── index.json                 # Main index with links to all sections
├── account/                   # Account methods
│   ├── account_module.json
│   ├── ...
├── ledger/                    # Ledger methods
│   ├── ledger_module.json
│   ├── ...
├── transaction/               # Transaction methods
├── wallet/                    # Wallet methods
├── clients/                   # Network clients
├── models/                    # XRPL models
├── utils/                     # Utilities
├── core/                      # XRPL core codecs
└── asyncio/                   # Async support
```

### File Format

Each JSON file contains structured information about a module, including:

- Module metadata (name, URL, description)
- Classes defined in the module
- Methods defined in the module
- Submodules and their links

See the JSON schema documentation for a detailed breakdown of the data structure.

## Using the Data with LLMs

### Data Preparation for LLM Training/Fine-tuning

The extracted JSON files provide a clean, structured representation of the XRPL-py documentation that is well-suited for LLM training. Consider these approaches:

1. **Direct JSON Loading**: Load the JSON files directly into your LLM training pipeline.

2. **Conversion to Training Examples**: Transform the JSON structure into training examples with appropriate prompts and responses.

3. **Text Extraction for Embeddings**: Extract text content for embedding-based retrieval systems.

### Integration with RAG (Retrieval-Augmented Generation)

The structured documentation is ideal for RAG systems:

1. **Generate Embeddings**: Create embeddings for each module, class, and method.

2. **Build a Vector Database**: Store these embeddings in a vector database (like Pinecone, Faiss, or Milvus).

3. **Implement a Retrieval System**: When a query is received, find the most relevant documentation sections.

4. **Augment LLM Prompts**: Include the retrieved documentation in your LLM prompts to provide context.

Example RAG implementation (pseudocode):

```python
# When receiving a query about XRPL
query = "How do I create an XRPL wallet?"

# 1. Convert query to embedding
query_embedding = embed_text(query)

# 2. Find relevant docs using vector similarity
relevant_docs = vector_db.search(query_embedding, top_k=3)

# 3. Format context from retrieved docs
context = format_docs_as_context(relevant_docs)

# 4. Augment LLM prompt
augmented_prompt = f"""
Based on the following XRPL-py documentation:
{context}

Answer the user's question: {query}
"""

# 5. Send to LLM
response = llm.generate(augmented_prompt)
```

## Extending the Scraper

To extend the scraper for additional needs:

1. **Additional Sections**: Modify the `scrape_main_sections` method to include new URLs.

2. **Custom Extraction Logic**: Add new methods to extract specific types of content.

3. **Output Formats**: Modify the `save_module_info` method to support different output formats.

## Troubleshooting

Common issues and solutions:

- **Connection Errors**: If you encounter connection errors, try increasing the delay between requests by modifying the `time.sleep()` value.

- **Parsing Errors**: If the parser fails to extract expected content, check if the documentation structure has changed and update the selectors accordingly.

- **Missing Content**: Some content might not be properly extracted if it doesn't follow the expected HTML structure. Check the log file for warnings and errors.

## Monitoring and Logging

The scraper logs its activity to both the console and a `scraper.log` file. Check this file for detailed information about the scraping process and any errors encountered.
