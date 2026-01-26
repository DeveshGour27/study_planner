from sentence_transformers import SentenceTransformer
import numpy as np
from database.models import UploadedResource
from database.db_manager import SessionLocal
import pickle
import os


class RAGEngine:
    
    def __init__(self):
        # Load sentence transformer model
        self. model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings_dir = "data/embeddings"
        self._ensure_embeddings_dir()
    
    def _ensure_embeddings_dir(self):
        """Create embeddings directory if it doesn't exist"""
        if not os. path.exists(self.embeddings_dir):
            os.makedirs(self.embeddings_dir)
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk. strip():
                chunks.append(chunk)
        
        return chunks
    
    def generate_embeddings(self, resource_id: str):
        """Generate embeddings for a PDF resource"""
        db = SessionLocal()
        try:
            resource = db.query(UploadedResource).filter(
                UploadedResource.resource_id == resource_id
            ).first()
            
            if not resource or not resource.extracted_text:
                return False, "Resource not found or no text extracted"
            
            # Chunk the text
            chunks = self. chunk_text(resource.extracted_text)
            
            if not chunks:
                return False, "No text chunks created"
            
            # Generate embeddings
            embeddings = self. model. encode(chunks)
            
            # Save embeddings and chunks
            embeddings_path = os.path. join(self.embeddings_dir, f"{resource_id}.pkl")
            
            with open(embeddings_path, 'wb') as f:
                pickle.dump({
                    'embeddings': embeddings,
                    'chunks':  chunks,
                    'resource_id': resource_id,
                    'filename': resource.filename
                }, f)
            
            # Update database
            resource.embeddings_generated = True
            db.commit()
            
            return True, f"Generated embeddings for {len(chunks)} chunks"
        
        except Exception as e: 
            db.rollback()
            return False, f"Error generating embeddings: {str(e)}"
        finally:
            db.close()
    
    def search(self, user_id: str, query: str, top_k: int = 3):
        """
        Search across all user's PDFs using semantic similarity
        Returns top_k most relevant chunks
        """
        db = SessionLocal()
        try:
            # Get all user's resources with embeddings
            resources = db.query(UploadedResource).filter(
                UploadedResource.user_id == user_id,
                UploadedResource.embeddings_generated == True
            ).all()
            
            if not resources: 
                return []
            
            # Encode query
            query_embedding = self. model.encode([query])[0]
            
            all_results = []
            
            # Search in each resource
            for resource in resources: 
                embeddings_path = os.path.join(self.embeddings_dir, f"{resource.resource_id}.pkl")
                
                if not os.path.exists(embeddings_path):
                    continue
                
                # Load embeddings
                with open(embeddings_path, 'rb') as f:
                    data = pickle.load(f)
                
                embeddings = data['embeddings']
                chunks = data['chunks']
                
                # Calculate cosine similarity
                similarities = np. dot(embeddings, query_embedding) / (
                    np.linalg. norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
                )
                
                # Get top results from this resource
                top_indices = np.argsort(similarities)[::-1][:top_k]
                
                for idx in top_indices:
                    if similarities[idx] > 0.15:  # Threshold for relevance
                        all_results.append({
                            'chunk': chunks[idx],
                            'similarity': float(similarities[idx]),
                            'filename': resource.filename,
                            'resource_id':  resource.resource_id
                        })
            
            # Sort all results by similarity
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return all_results[: top_k]
        
        finally:
            db.close()
    
    def get_context_for_query(self, user_id: str, query: str):
        """Get relevant context from PDFs for a query"""
        try:
            results = self.search(user_id, query, top_k=3)
            
            if not results:
                print(f"  → Search returned 0 results")
                return None
            
            print(f"  → Search returned {len(results)} results")
            
            context = "Relevant information from your uploaded materials:\n\n"
            
            for i, result in enumerate(results, 1):
                context += f"[From {result['filename']}]\n"
                context += f"{result['chunk']}\n\n"
            
            return context
            
        except Exception as e:
            print(f"  → Error in get_context_for_query: {e}")
            import traceback
            traceback.print_exc()
            return None


# Initialize global RAG engine
rag_engine = RAGEngine()