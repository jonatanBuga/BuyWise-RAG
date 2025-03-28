import os
import sys
from dotenv import load_dotenv
from .helper_functions import *


# Load environment variables from a .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key in environment variables.")

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))


def encode_pdf(path, chunk_size=1000, chunk_overlap=200):
    """
    Encodes a PDF book into a vector store using OpenAI embeddings.

    Args:
        path: The path to the PDF file.
        chunk_size: The desired size of each text chunk.
        chunk_overlap: The amount of overlap between consecutive chunks.

    Returns:
        A FAISS vector store containing the encoded book content.
    """

    # Load PDF documents
    loader = PyPDFLoader(path)
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    texts = text_splitter.split_documents(documents)
    cleaned_texts = replace_t_with_space(texts)

    # Create embeddings (Tested with OpenAI and Amazon Bedrock)
    embeddings = get_langchain_embedding_provider(EmbeddingProvider.OPENAI)
    
    # Create vector store
    vectorstore = FAISS.from_documents(cleaned_texts, embeddings)

    return vectorstore


def context_from_query(query):
    # encode pdf 
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, 'data', 'simple_food_blog.pdf')
    pdf_path = os.path.normpath(pdf_path)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
    
    chunks_vector_store = encode_pdf(pdf_path, chunk_size=1000, chunk_overlap=200)

    #create retriver 
    chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 2})
    context = retrieve_context_per_question(query, chunks_query_retriever)
    #show_context(context)

    #context is list of 2 items(string,string)
    return context

