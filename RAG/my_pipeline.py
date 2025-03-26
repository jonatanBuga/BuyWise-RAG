import os
import sys
from typing import List
from dotenv import load_dotenv
import faiss
import json
from fpdf import FPDF
from PyPDF2 import PdfFileMerger
# LlamaIndex (GPT Index) imports
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import BaseNode, TransformComponent
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()  # Load .env if present
# OpenAI Key
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# Embedding dimension for the "text-embedding-3-small"
EMBED_DIMENSION = 512

# Global chunking strategy
CHUNK_SIZE = 200
CHUNK_OVERLAP = 50

# LlamaIndex global settings:
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    dimensions=EMBED_DIMENSION
)

class TextCleaner(TransformComponent):
    """
    Cleans clutters from texts before embedding.
    Replaces tabs, extra newlines, etc.
    """
    def __call__(self, nodes: List[BaseNode], **kwargs) -> List[BaseNode]:
        for node in nodes:
            node.text = node.text.replace('\t', ' ')
            node.text = node.text.replace(' \n', ' ')
        return nodes

def build_retriever(data_path: str) -> VectorStoreIndex:
    """
    Given a directory with data (PDFs, etc.), set up the entire pipeline:
    1. Load docs
    2. Transform docs (TextCleaner, SentenceSplitter)
    3. Store in Faiss
    4. Create and return a VectorStoreIndex with retrieval ability.
    """
    #Load documents from directory
    node_parser = SimpleDirectoryReader(
        input_dir=data_path, 
        required_exts=['.pdf']
    )
    documents = node_parser.load_data()

    #Faiss vector store
    faiss_index = faiss.IndexFlatL2(EMBED_DIMENSION)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    text_splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )

    pipeline = IngestionPipeline(
        transformations=[TextCleaner(), text_splitter],
        vector_store=vector_store
    )
    nodes = pipeline.run(documents=documents)

    vector_store_index = VectorStoreIndex(nodes)
    return vector_store_index

def get_retriever(vector_store_index: VectorStoreIndex, top_k: int = 2):
    """Return a retriever object from a VectorStoreIndex."""
    return vector_store_index.as_retriever(similarity_top_k=top_k)

def show_context(context_list: List[BaseNode]):
    """
    Print out each context chunk from the retrieval step.
    """
    for i, c in enumerate(context_list):
        print(f"Context {i+1}:")
        print(c.text)
        print("\n")

def retrieve_context(retriever, query: str) -> List[BaseNode]:
    """
    Passes the query to the given retriever and returns the retrieved contexts.
    """
    return retriever.retrieve(query)

if __name__ == "__main__":
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # data_path = os.path.join(current_dir, "data/recipes_data.pdf")
    vstore_index = build_retriever("/Users/jonatanbuga/Desktop/BuyWise-RAG/RAG/data/recipes_data.pdf")
    retriever = get_retriever(vstore_index, top_k=2)
    
    # Test retrieval
    test_query = "\n\"fish\": \"800 gr\",\n\"potatoes\": \"600 gr\",\n\"onions\": \"4 units\",\n\"carrots\": \"4 units\",\n\"garlic\": \"4 units\",\n\"olive oil\": \"200 ml\",\n\"lemon\": \"2 units\",\n\"parsley\": \"1 bunch\",\n\"spices\": \"to taste\",\n\"rice\": \"400 gr\"\n"
    context = retrieve_context(retriever, test_query)
    show_context(context)