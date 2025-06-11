from deep_translator import GoogleTranslator
from clientSupabase import *
import json,sys, os,numpy as np
from sentence_transformers import SentenceTransformer, util
from embeddings import *
FILE_NAME = "translations.json"  




class Transformer:
    def __init__(self,backend = "minilm"):
        self.backend = backend.lower()
        if self.backend == "word2vec":
            self.model = get_word2vec()
            self.dim   = 300
        else:                         # default MiniLM
            self.model = get_minilm()
            self.dim   = 384
    def encode_word(self,phrase):
        if self.backend == "word2vec":
            tokens = phrase.lower().split()
            vecs= []
            kv= self.model
            for t in tokens:
                if t in kv:
                    vecs.append(kv.get_vector(t, norm=True))   # already unit-norm
            if not vecs:
                return np.zeros(self.dim, dtype="float32")
            return np.mean(vecs, axis=0)
        else:   # MiniLM
            return self.model.encode(phrase, normalize_embeddings=True)
    def load_existing(self):
        if os.path.isfile(FILE_NAME):
            with open(FILE_NAME, encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def products_in_en(self,names):
        translations = self.load_existing()     
        for name in names:
            en_word = GoogleTranslator(
                source="iw", target="en"
            ).translate(name[0])
            print(f"source:{name[0]}, translate:{en_word}")
            vec = self.encode_word(en_word).tolist() 
            translations[name[1]] = [en_word,vec]
            print(name[0], "→", en_word,f"at index{name[1]}")
        with open(FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)

    def load_vectors(self,path:str | None=None):
        path = path or FILE_NAME
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        dirty   = False
        vectors = {}

        for pid, (en_word, vec) in data.items():
            if len(vec) != self.dim:          # dimension mismatch → regenerate
                vec = self.encode_word(en_word).tolist()
                data[pid] = [en_word, vec]
                dirty = True
            vectors[pid] = (en_word, np.array(vec, dtype="float32"))

        if dirty:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅  {path} normalised to {self.dim}-dim vectors")

        return vectors
    
    def most_similar(self,products,topk=5):
        query_keys = list(products.keys())
        q_matrix = np.stack([self.encode_word(q) for q in query_keys])

        VECTORS = self.load_vectors(FILE_NAME)
        ids, cat_vecs = zip(*[(pid, vec) for pid, (_, vec) in VECTORS.items()])
        cat_mat = np.stack(cat_vecs)

        scores = np.dot(q_matrix, cat_mat.T)

        result = {}
        for i, key in enumerate(query_keys):
            best = scores[i].argsort()[-topk:][::-1]              # indices of top-k sims
            result[key] = [(ids[j], float(scores[i, j])) for j in best]

        return result
if __name__=="__main__":
    model = Transformer()
    db = instanceDB()
    heb_names = db.fetch_product_names()
    products = {'Beef steaks': '5 pieces',
  'Chicken breasts': '4 pieces',
  'BBQ sauce': '1 bottle',
  'Potatoes': '1 kg',
  'Mixed salad greens': '200 g',
  'Cherry tomatoes': '250 g',
  'Olive oil': '1 bottle',
  'Salt': '1 pack',
  'Black pepper': '1 pack',
  'Red wine': '2 bottles',
  'Garlic cloves': '5 pieces',
  'Fresh rosemary': '1 bunch',
  'Bread (baguette or similar)': '1 loaf'}
    #model.products_in_en(heb_names)
    for query_key, matches in model.most_similar(products).items():
        print(f"query->{query_key}")
        for prod_id,score in matches:
            print(f"{prod_id}:  {score:.3f}")
    


