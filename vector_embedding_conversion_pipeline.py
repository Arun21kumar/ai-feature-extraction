class VectorEmbeddingConversionPipeline:
    def convertJsontoVector(self, file_path, param2):
        print("Converting JSON to vector with input:", file_path, "and param2:", param2)
        import json
        from sentence_transformers import SentenceTransformer
        import os
        model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
        file_contents = []
        for path in file_path:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_contents.append(content)
        print("Loaded file contents:", file_contents)

        vector_output_dir = os.path.join(os.path.dirname(file_path[0]), "../vector_output")
        os.makedirs(vector_output_dir, exist_ok=True)
        for idx, content in enumerate(file_contents):
            try:
                data = json.loads(content)
            except Exception as e:
                print(f"Error loading JSON from file {file_path[idx]}: {e}")
                continue

            # Prepare output structure
            output = {}
            # Copy metadata fields as-is (not embedded)
            for meta_field in ["document_type", "experience_years"]:
                if meta_field in data:
                    output[meta_field] = data[meta_field]
                else:
                    output[meta_field] = None

            # Embedding fields
            embedding_fields = ["summary", "skills", "responsibilities", "certifications"]
            embeddings = {}
            for field in embedding_fields:
                value = data.get(field)
                if value is None:
                    embeddings[field] = []
                elif isinstance(value, list):
                    if value:
                        vectors = model.encode([str(v) for v in value])
                        embeddings[field] = [vec.tolist() for vec in vectors]
                    else:
                        embeddings[field] = []
                else:
                    vec = model.encode(str(value)).tolist()
                    embeddings[field] = [vec]
            output["embeddings"] = embeddings

            # Ensure all embeddings have the same dimension
            dims = [len(vec[0]) for vec in embeddings.values() if vec]
            if dims and not all(d == dims[0] for d in dims):
                print(f"Warning: Not all embeddings have the same dimension in file {file_path[idx]}")

            base_name = os.path.basename(str(file_path[idx]))
            out_path = os.path.join(vector_output_dir, base_name + ".vector.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Vector embedding output written to: {out_path}")

        # After all files processed, call VectorSimilarityExtractor.compute_similarity with the two files' contents
        from vector_similarity_extractor import VectorSimilarityExtractor
        file2 = "/Users/poojamanikandan/ai-feature-extraction/output/../vector_output/Rajesh_Kummara-NetworkL3-SME-11yrs-BLR.docx.json.vector.json"
        file1 = "/Users/poojamanikandan/ai-feature-extraction/output/../vector_output/Sr_Network_Engineer_(US049I_E).json.vector.json"
        try:
            with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
                content1 = f1.read()
                content2 = f2.read()
        except Exception as e:
            print(f"Error reading vector files for similarity: {e}")
            return
        similarity_extractor = VectorSimilarityExtractor()
        similarity_extractor.compute_similarity(content1, content2)