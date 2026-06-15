"""
XRPL Documentation LLM Integration

This script demonstrates how to use the scraped XRPL-py documentation
with various LLM integration techniques including embeddings and 
retrieval augmented generation (RAG).
"""

import os
import json
import glob
from typing import List, Dict, Any, Optional

# For embeddings and vector search
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# For demonstration purposes - in a real application you'd use an actual LLM API
# such as OpenAI, Anthropic, or an open source model

class XRPLDocStore:
    """
    A class for loading, indexing, and searching XRPL documentation
    for use with LLM models
    """
    
    def __init__(self, docs_dir: str = "xrpl_docs"):
        """
        Initialize the doc store
        
        Args:
            docs_dir: Directory containing the scraped documentation
        """
        self.docs_dir = docs_dir
        self.documents = []
        self.index = {}
        self.embeddings = {}
        self.embedding_model = None  # Would connect to an embedding model
        
        # Load the documents
        self.load_documents()
    
    def load_documents(self) -> None:
        """
        Load all JSON documents from the docs directory
        """
        # Load the index file
        index_path = os.path.join(self.docs_dir, "index.json")
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading index file: {e}")
            self.index = {"sections": {}}
        
        # Load all JSON files from each section
        for section, info in self.index.get("sections", {}).items():
            section_dir = os.path.join(self.docs_dir, section)
            if not os.path.exists(section_dir):
                continue
                
            for file_info in glob.glob(f"{section_dir}/*.json"):
                try:
                    with open(file_info, 'r', encoding='utf-8') as f:
                        doc = json.load(f)
                        self.documents.append(doc)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error loading document {file_info}: {e}")
        
        print(f"Loaded {len(self.documents)} documents")
    
    def create_document_chunks(self) -> List[Dict[str, Any]]:
        """
        Split documents into smaller chunks for better retrieval
        
        Returns:
            List of document chunks with metadata
        """
        chunks = []
        
        for doc in self.documents:
            # Add module level chunks
            module_text = f"{doc.get('name', '')}\n{doc.get('description', '')}"
            chunks.append({
                "text": module_text,
                "metadata": {
                    "type": "module",
                    "name": doc.get("name", ""),
                    "section": doc.get("section", ""),
                    "url": doc.get("url", "")
                }
            })
            
            # Add class level chunks
            for cls in doc.get("classes", []):
                class_text = f"{cls.get('name', '')}\n{cls.get('signature', '')}\n{cls.get('description', '')}"
                chunks.append({
                    "text": class_text,
                    "metadata": {
                        "type": "class",
                        "name": cls.get("name", ""),
                        "module": doc.get("name", ""),
                        "section": doc.get("section", ""),
                        "url": f"{doc.get('url', '')}#{cls.get('id', '')}"
                    }
                })
                
                # Add method level chunks for class methods
                for method in cls.get("methods", []):
                    method_text = (
                        f"{method.get('name', '')}\n"
                        f"{method.get('signature', '')}\n"
                        f"{method.get('description', '')}\n"
                    )
                    
                    # Add parameters
                    if method.get("parameters"):
                        method_text += "Parameters:\n" + "\n".join(method.get("parameters", []))
                    
                    # Add returns
                    if method.get("returns"):
                        method_text += "\nReturns:\n" + "\n".join(method.get("returns", []))
                    
                    # Add examples
                    if method.get("examples"):
                        method_text += "\nExamples:\n" + "\n".join(method.get("examples", []))
                    
                    chunks.append({
                        "text": method_text,
                        "metadata": {
                            "type": "method",
                            "name": method.get("name", ""),
                            "class": cls.get("name", ""),
                            "module": doc.get("name", ""),
                            "section": doc.get("section", ""),
                            "url": f"{doc.get('url', '')}#{method.get('id', '')}"
                        }
                    })
            
            # Add module-level method chunks
            for method in doc.get("methods", []):
                method_text = (
                    f"{method.get('name', '')}\n"
                    f"{method.get('signature', '')}\n"
                    f"{method.get('description', '')}\n"
                )
                
                # Add parameters
                if method.get("parameters"):
                    method_text += "Parameters:\n" + "\n".join(method.get("parameters", []))
                
                # Add returns
                if method.get("returns"):
                    method_text += "\nReturns:\n" + "\n".join(method.get("returns", []))
                
                # Add examples
                if method.get("examples"):
                    method_text += "\nExamples:\n" + "\n".join(method.get("examples", []))
                
                chunks.append({
                    "text": method_text,
                    "metadata": {
                        "type": "method",
                        "name": method.get("name", ""),
                        "module": doc.get("name", ""),
                        "section": doc.get("section", ""),
                        "url": f"{doc.get('url', '')}#{method.get('id', '')}"
                    }
                })
        
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Generate embeddings for document chunks
        
        In a real application, you would use an actual embedding model
        like OpenAI's text-embedding-ada-002 or a local model.
        
        Args:
            chunks: List of document chunks
        """
        # This is a mock implementation - in a real application,
        # you would use an actual embedding model
        print("Generating embeddings for chunks...")
        
        # In a real application:
        # 1. Connect to embedding API (OpenAI, Cohere, etc.)
        # 2. Generate embeddings for each chunk
        # 3. Store embeddings in memory or vector database
        
        # Mock implementation with random embeddings
        mock_embedding_dim = 384  # Common embedding dimension
        self.chunk_data = chunks
        self.chunk_embeddings = {
            i: np.random.randn(mock_embedding_dim) / np.sqrt(mock_embedding_dim)
            for i in range(len(chunks))
        }
        
        print(f"Generated {len(self.chunk_embeddings)} embeddings")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documentation based on a query
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of relevant document chunks
        """
        # In a real application, you would:
        # 1. Generate an embedding for the query
        # 2. Calculate similarity with all document embeddings
        # 3. Return the most similar documents
        
        # Mock implementation - in a real application you'd use actual embeddings
        # and a vector database for efficient search
        
        # For demonstration purposes, we'll do a simple text search
        query = query.lower()
        results = []
        
        for i, chunk in enumerate(self.chunk_data):
            text = chunk["text"].lower()
            # Simple keyword matching (in a real app, use embeddings)
            if any(term in text for term in query.split()):
                # In a real application, you'd use the embedding similarity
                # similarity = cosine_similarity([query_embedding], [self.chunk_embeddings[i]])[0][0]
                # Mock similarity score based on word overlap
                similarity = sum(term in text for term in query.split()) / len(query.split())
                
                results.append({
                    "chunk": chunk,
                    "similarity": similarity
                })
        
        # Sort by similarity and take top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return [r["chunk"] for r in results[:top_k]]
    
    def format_for_llm(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format document chunks for inclusion in an LLM prompt
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Formatted text for LLM prompt
        """
        formatted_chunks = []
        
        for chunk in chunks:
            metadata = chunk["metadata"]
            formatted_chunk = f"--- {metadata['type'].upper()}: {metadata['name']} ---\n"
            
            if metadata['type'] == 'method':
                if metadata.get('class'):
                    formatted_chunk += f"Class: {metadata['class']}\n"
                formatted_chunk += f"Module: {metadata['module']}\n"
            elif metadata['type'] == 'class':
                formatted_chunk += f"Module: {metadata['module']}\n"
            
            formatted_chunk += f"Documentation: {chunk['text']}\n"
            formatted_chunk += f"URL: {metadata['url']}\n"
            
            formatted_chunks.append(formatted_chunk)
        
        return "\n\n".join(formatted_chunks)

def create_rag_prompt(query: str, context: str) -> str:
    """
    Create a RAG (Retrieval Augmented Generation) prompt
    
    Args:
        query: User query
        context: Document context from retrieval
        
    Returns:
        Formatted prompt for LLM
    """
    return f"""
You are an assistant specialized in the XRPL-py library. Answer the user's question based on the retrieved documentation.

RETRIEVED DOCUMENTATION:
{context}

USER QUESTION: {query}

Provide a clear, concise answer based on the documentation. If the documentation doesn't contain enough information to answer fully, acknowledge that. Include relevant code examples if available.
"""

def fine_tuning_example_generator(doc_store: XRPLDocStore) -> List[Dict[str, Any]]:
    """
    Generate examples for fine-tuning an LLM on XRPL-py documentation
    
    Args:
        doc_store: XRPLDocStore object with loaded documents
        
    Returns:
        List of fine-tuning examples
    """
    examples = []
    chunks = doc_store.create_document_chunks()
    
    for chunk in chunks:
        metadata = chunk["metadata"]
        
        if metadata["type"] == "method":
            # Generate a question about how to use this method
            question = f"How do I use the {metadata['name']} method in XRPL-py?"
            
            # Format the answer based on the documentation
            answer = f"To use the `{metadata['name']}` method in the XRPL-py library:\n\n"
            
            # Add description
            answer += chunk["text"].split("\n")[2] + "\n\n"  # Extract description from chunk
            
            # Add example if available
            if "Examples:" in chunk["text"]:
                example_text = chunk["text"].split("Examples:")[1].strip()
                answer += f"Here's an example:\n```python\n{example_text}\n```\n\n"
            
            # Add reference
            answer += f"For more details, see the documentation at: {metadata['url']}"
            
            examples.append({
                "input": question,
                "output": answer
            })
        
        elif metadata["type"] == "class":
            # Generate a question about this class
            question = f"What is the {metadata['name']} class in XRPL-py used for?"
            
            # Format the answer
            answer = f"The `{metadata['name']}` class in the XRPL-py library:\n\n"
            
            # Add description
            answer += chunk["text"].split("\n")[2] + "\n\n"  # Extract description from chunk
            
            # Add reference
            answer += f"For more details, see the documentation at: {metadata['url']}"
            
            examples.append({
                "input": question,
                "output": answer
            })
    
    return examples

def main():
    """
    Example usage of the XRPLDocStore
    """
    # Initialize the document store
    doc_store = XRPLDocStore()
    
    # Create chunks and generate embeddings
    chunks = doc_store.create_document_chunks()
    doc_store.generate_embeddings(chunks)
    
    # Example query
    query = "How to create an XRPL wallet"
    
    # Search for relevant documentation
    print(f"Searching for: '{query}'")
    results = doc_store.search(query)
    
    # Format for LLM prompt
    context = doc_store.format_for_llm(results)
    
    # Create RAG prompt
    rag_prompt = create_rag_prompt(query, context)
    
    print("\nRAG Prompt Example:")
    print("=" * 80)
    print(rag_prompt)
    print("=" * 80)
    
    # Example of fine-tuning data generation
    print("\nGenerating fine-tuning examples...")
    fine_tuning_examples = fine_tuning_example_generator(doc_store)
    print(f"Generated {len(fine_tuning_examples)} fine-tuning examples")
    
    # Print a couple of examples
    print("\nFine-tuning Example:")
    print("=" * 80)
    example = fine_tuning_examples[0] if fine_tuning_examples else {"input": "No examples", "output": "No examples"}
    print(f"Input: {example['input']}")
    print(f"Output: {example['output']}")
    print("=" * 80)

if __name__ == "__main__":
    main()
