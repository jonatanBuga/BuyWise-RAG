from sentence_transformers import SentenceTransformer
from functools import lru_cache
import gensim.downloader as api
import numpy as np

@lru_cache(maxsize=1)
def get_minilm():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@lru_cache(maxsize=1)
def get_word2vec():
    kv = api.load("word2vec-google-news-300")       
    kv.fill_norms()                                  
    return kv