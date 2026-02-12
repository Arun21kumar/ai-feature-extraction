import hashlib
import json
from sentence_transformers import SentenceTransformer
import os

class VectorEmbeddingConversionPipeline:
    def _compute_checksum(self, content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def convertJsontoVector(self, file_paths, param2):
        print("Converting JSON to vector with input:", file_paths, "and param2:", param2)
        model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
        vector_output_dir = os.path.join(os.path.dirname(file_paths[0]), "../vector_output")
        os.makedirs(vector_output_dir, exist_ok=True)
        for path in file_paths:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            checksum = self._compute_checksum(content)
            base_name = os.path.basename(str(path))
            out_path = os.path.join(vector_output_dir, base_name + ".vector.json")
            # Check for stale vector file
            if os.path.exists(out_path):
                with open(out_path, 'r', encoding='utf-8') as vf:
                    try:
                        vdata = json.load(vf)
                        if vdata.get('checksum') == checksum:
                            print(f"Vector file up-to-date: {out_path}")
                            continue
                        else:
                            print(f"Stale vector file detected, regenerating: {out_path}")
                    except Exception:
                        print(f"Corrupt vector file, regenerating: {out_path}")
            try:
                data = json.loads(content)
            except Exception as e:
                print(f"Error loading JSON from file {path}: {e}")
                continue
            output = {}
            output['checksum'] = checksum
            for meta_field in ["document_type", "experience_years"]:
                output[meta_field] = data.get(meta_field, None)
            embedding_fields = ["summary", "skills", "responsibilities", "certifications"]
            embeddings = {}
            for field in embedding_fields:
                value = data.get(field)
                if value is None:
                    embeddings[field] = []
                elif isinstance(value, list):
                    clean_values = [v for v in value if isinstance(v, str)]
                    if clean_values:
                        vectors = model.encode(clean_values)
                        embeddings[field] = [vec.tolist() for vec in vectors]
                    else:
                        embeddings[field] = []
                else:
                    if isinstance(value, str):
                        vec = model.encode(value).tolist()
                        embeddings[field] = [vec]
                    else:
                        embeddings[field] = []
            output["embeddings"] = embeddings
            # Log vector shapes and stats
            for field, vecs in embeddings.items():
                if vecs:
                    print(f"Field '{field}' - {len(vecs)} vectors, dim {len(vecs[0]) if vecs else 0}")
                    arr = [v for v in vecs]
                    flat = [item for sublist in arr for item in sublist]
                    print(f"Stats for '{field}': min={min(flat):.4f}, max={max(flat):.4f}, mean={sum(flat)/len(flat):.4f}")
            out_path = os.path.join(vector_output_dir, base_name + ".vector.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Vector embedding output written to: {out_path}")


        # Dynamic similarity computation
        from vector_similarity_extractor import VectorSimilarityExtractor
        vector_files = [os.path.join(vector_output_dir, os.path.basename(str(p)) + ".vector.json") for p in file_paths]
        if len(vector_files) >= 2:
            print(f"Comparing vectors: {vector_files[0]} vs {vector_files[1]}")
            with open(vector_files[0], 'r', encoding='utf-8') as f1, open(vector_files[1], 'r', encoding='utf-8') as f2:
                content1 = f1.read()
                content2 = f2.read()
            similarity_extractor = VectorSimilarityExtractor()
            similarity_extractor.compute_similarity(content1, content2)
