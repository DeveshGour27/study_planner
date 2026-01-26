import os
from datetime import datetime
import PyPDF2
from database.models import UploadedResource
from database.db_manager import SessionLocal
import hashlib


class PDFProcessor:
    
    UPLOAD_DIR = "data/uploads"
    
    @staticmethod
    def ensure_upload_dir():
        """Create upload directory if it doesn't exist"""
        if not os.path.exists(PDFProcessor. UPLOAD_DIR):
            os.makedirs(PDFProcessor. UPLOAD_DIR)
    
    @staticmethod
    def upload_pdf(user_id:  str, uploaded_file, topic: str = None):
        """
        Upload and process PDF file
        Returns: (success:  bool, message: str, resource_id: str or None)
        """
        try:
            PDFProcessor.ensure_upload_dir()
            
            # Generate unique filename
            file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
            uploaded_file.seek(0)  # Reset file pointer
            
            filename = uploaded_file.name
            safe_filename = f"{user_id}_{file_hash}_{filename}"
            file_path = os.path.join(PDFProcessor.UPLOAD_DIR, safe_filename)
            
            # Save file
            with open(file_path, "wb") as f:
                f. write(uploaded_file.getbuffer())
            
            # Extract text
            extracted_text = PDFProcessor._extract_text_from_pdf(file_path)
            
            if not extracted_text:
                os.remove(file_path)
                return False, "Failed to extract text from PDF.  File might be empty or corrupted.", None
            
            # Save to database
            db = SessionLocal()
            try:
                resource = UploadedResource(
                    user_id=user_id,
                    filename=filename,
                    file_path=file_path,
                    file_type='pdf',
                    topic=topic,
                    processed=True,
                    extracted_text=extracted_text,
                    embeddings_generated=False
                )
                
                db.add(resource)
                db.commit()
                db.refresh(resource)
                
                return True, f"✅ PDF uploaded successfully!  Extracted {len(extracted_text)} characters.", resource.resource_id
                
            except Exception as e:
                db.rollback()
                os.remove(file_path)
                return False, f"Database error: {str(e)}", None
            finally:
                db.close()
        
        except Exception as e: 
            return False, f"Upload failed: {str(e)}", None
    
    @staticmethod
    def _extract_text_from_pdf(file_path:  str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text += page. extract_text() + "\n\n"
            
            return text.strip()
        
        except Exception as e:
            print(f"Error extracting text:  {e}")
            return ""
    
    @staticmethod
    def get_user_pdfs(user_id: str):
        """Get all PDFs uploaded by user"""
        db = SessionLocal()
        try:
            resources = db.query(UploadedResource).filter(
                UploadedResource.user_id == user_id,
                UploadedResource. file_type == 'pdf'
            ).order_by(UploadedResource.uploaded_at.desc()).all()
            
            return resources
        finally:
            db.close()
    
    @staticmethod
    def get_pdf_by_id(resource_id: str):
        """Get PDF by ID"""
        db = SessionLocal()
        try:
            return db.query(UploadedResource).filter(
                UploadedResource.resource_id == resource_id
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def delete_pdf(resource_id: str):
        """Delete PDF file and database record"""
        db = SessionLocal()
        try:
            resource = db.query(UploadedResource).filter(
                UploadedResource.resource_id == resource_id
            ).first()
            
            if not resource:
                return False, "PDF not found"
            
            # Delete file
            if os.path.exists(resource. file_path):
                os. remove(resource.file_path)
            
            # Delete from database
            db.delete(resource)
            db.commit()
            
            return True, "PDF deleted successfully"
        
        except Exception as e:
            db.rollback()
            return False, f"Delete failed: {str(e)}"
        finally:
            db.close()
    
    @staticmethod
    def search_in_pdf(resource_id: str, query: str, context_chars: int = 500):
        """Simple keyword search in PDF"""
        resource = PDFProcessor.get_pdf_by_id(resource_id)
        
        if not resource or not resource.extracted_text:
            return []
        
        text = resource.extracted_text. lower()
        query_lower = query.lower()
        
        results = []
        start = 0
        
        while True:
            pos = text.find(query_lower, start)
            if pos == -1:
                break
            
            # Get context around match
            context_start = max(0, pos - context_chars // 2)
            context_end = min(len(text), pos + len(query_lower) + context_chars // 2)
            
            context = resource.extracted_text[context_start:context_end]
            
            # Add ellipsis if needed
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."
            
            results.append({
                "position": pos,
                "context": context,
                "filename": resource.filename
            })
            
            start = pos + 1
            
            # Limit results
            if len(results) >= 5:
                break
        
        return results