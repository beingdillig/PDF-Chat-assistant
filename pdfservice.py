"""PDF processing service."""
from pypdf import PdfReader


class PDFService:
    """Handle PDF text extraction and chunking."""
    
    def __init__(self, chunk_size=500, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process_pdf(self, filepath):
        """Extract and chunk text from PDF."""
        reader = PdfReader(filepath)
        chunks = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                page_chunks = self._chunk_text(text, page_num)
                chunks.extend(page_chunks)
        
        return chunks
    
    def _chunk_text(self, text, page_num):
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append({
                    "text": chunk,
                    "page": page_num
                })
            
            start += self.chunk_size - self.overlap
        
        return chunks
    
    def get_page_count(self, filepath):
        """Get number of pages in PDF."""
        reader = PdfReader(filepath)
        return len(reader.pages)