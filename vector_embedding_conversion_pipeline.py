import hashlib
import json
from sentence_transformers import SentenceTransformer
import os

class VectorEmbeddingConversionPipeline:
    def _compute_checksum(self, content):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def convertJsontoVector(self, file_paths, param2):
        """
        Convert extracted JSON files to vector embeddings and compute similarities.
        
        Args:
            file_paths: List of paths to extracted JSON files
            param2: Unused parameter (kept for backward compatibility)
            
        Returns:
            List of similarity results for each resume-JD pair
        """
        print("Converting JSON to vector with input:", file_paths, "and param2:", param2)
        import json
        from sentence_transformers import SentenceTransformer
        import os
        from pathlib import Path
        
        model = SentenceTransformer('Qwen/Qwen3-Embedding-0.6B')
        
        # Categorize files into resumes and job descriptions
        resumes = []
        job_descriptions = []
        
        for path in file_paths:
            with open(path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            doc_type = content.get('document_type', '').lower()
            if doc_type == 'resume':
                resumes.append({'path': path, 'data': content})
            elif doc_type == 'jd':
                job_descriptions.append({'path': path, 'data': content})
            else:
                # Try to infer from filename if document_type is not set
                filename = Path(path).name.lower()
                if 'resume' in filename or 'cv' in filename:
                    resumes.append({'path': path, 'data': content})
                elif 'jd' in filename or 'job' in filename:
                    job_descriptions.append({'path': path, 'data': content})
        
        print(f"Found {len(resumes)} resume(s) and {len(job_descriptions)} job description(s)")
        
        # Create vector output directory
        vector_output_dir = os.path.join(os.path.dirname(file_paths[0]), "../vector_output")
        os.makedirs(vector_output_dir, exist_ok=True)
        
        # Convert all files to vector embeddings
        vector_files = []
        for item in resumes + job_descriptions:
            path = item['path']
            data = item['data']
            
            # Prepare output structure
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

            # Save vector file
            base_name = os.path.basename(str(path))
            out_path = os.path.join(vector_output_dir, base_name + ".vector.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Vector embedding output written to: {out_path}")
            
            vector_files.append({
                'original_path': path,
                'vector_path': out_path,
                'document_type': output.get('document_type'),
                'data': output
            })
        
        # Compute similarities between all resume-JD pairs
        similarity_results = []
        
        if not job_descriptions:
            print("Warning: No job descriptions found. Cannot compute similarities.")
            return similarity_results
        
        if not resumes:
            print("Warning: No resumes found. Cannot compute similarities.")
            return similarity_results
        
        from vector_similarity_extractor import VectorSimilarityExtractor
        similarity_extractor = VectorSimilarityExtractor()
        
        # For each JD, compute similarity with all resumes
        for jd in job_descriptions:
            jd_vector_file = [v for v in vector_files if v['original_path'] == jd['path']][0]
            
            for resume in resumes:
                resume_vector_file = [v for v in vector_files if v['original_path'] == resume['path']][0]
                
                print(f"\nComputing similarity between:")
                print(f"  JD: {Path(jd['path']).name}")
                print(f"  Resume: {Path(resume['path']).name}")
                
                # Read vector files
                with open(jd_vector_file['vector_path'], 'r', encoding='utf-8') as f1, \
                     open(resume_vector_file['vector_path'], 'r', encoding='utf-8') as f2:
                    jd_vector_content = f1.read()
                    resume_vector_content = f2.read()
                
                # Compute similarity
                similarity_report = similarity_extractor.compute_similarity(
                    jd_vector_content, 
                    resume_vector_content
                )
                
                # Store result with metadata
                result = {
                    'jd_file': jd['path'],
                    'resume_file': resume['path'],
                    'resume_data': resume['data'],
                    'jd_data': jd['data'],
                    'similarity_score': similarity_report.get('overall_score', 0.0),
                    'section_scores': {
                        'summary': similarity_report.get('summary', 0.0),
                        'skills': similarity_report.get('skills', 0.0),
                        'responsibilities': similarity_report.get('responsibilities', 0.0),
                        'certifications': similarity_report.get('certifications', 0.0)
                    }
                }
                similarity_results.append(result)
        
        # Save similarity results to output directory
        output_dir = os.path.join(os.path.dirname(file_paths[0]), "../output")
        os.makedirs(output_dir, exist_ok=True)
        
        results_file = os.path.join(output_dir, "similarity_results.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(similarity_results, f, indent=2, ensure_ascii=False)
        print(f"\nSimilarity results saved to: {results_file}")
        
        return similarity_results
