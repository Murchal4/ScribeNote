import os
import shutil
import uuid
import sqlite3
import datetime
import mimetypes
from PIL import Image

class FileHandler:
    def __init__(self, storage_dir=None):
        if storage_dir is None:
            # Use default path
            self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "attachments")
        else:
            self.storage_dir = storage_dir
            
        # Create attachments directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "notes.db")
    
    def attach_file(self, note_id, file_path):
        """
        Attach a file to a note
        
        Args:
            note_id: ID of the note to attach the file to
            file_path: Path to the file to attach
            
        Returns:
            Dictionary with information about the attachment
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate a unique ID for the attachment
        attachment_id = str(uuid.uuid4())
        
        # Get file information
        filename = os.path.basename(file_path)
        file_type, _ = mimetypes.guess_type(file_path)
        
        # Create a directory for this note's attachments if it doesn't exist
        note_attachments_dir = os.path.join(self.storage_dir, note_id)
        os.makedirs(note_attachments_dir, exist_ok=True)
        
        # Copy the file to the attachments directory
        destination = os.path.join(note_attachments_dir, filename)
        
        # If a file with the same name already exists, add a unique identifier
        if os.path.exists(destination):
            base_name, ext = os.path.splitext(filename)
            filename = f"{base_name}_{attachment_id[:8]}{ext}"
            destination = os.path.join(note_attachments_dir, filename)
        
        shutil.copy2(file_path, destination)
        
        # Store attachment information in the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO attachments (id, note_id, filename, file_path, file_type, created_date) VALUES (?, ?, ?, ?, ?, ?)",
            (attachment_id, note_id, filename, destination, file_type, now)
        )
        
        conn.commit()
        conn.close()
        
        return {
            'id': attachment_id,
            'note_id': note_id,
            'filename': filename,
            'file_path': destination,
            'file_type': file_type
        }
    
    def get_attachment(self, attachment_id):
        """Get information about an attachment"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM attachments WHERE id = ?", (attachment_id,))
        attachment = cursor.fetchone()
        
        conn.close()
        
        if attachment:
            return dict(attachment)
        return None
    
    def delete_attachment(self, attachment_id):
        """Delete an attachment"""
        # Get attachment information first
        attachment = self.get_attachment(attachment_id)
        
        if not attachment:
            return False
        
        # Delete the file
        if os.path.exists(attachment['file_path']):
            os.remove(attachment['file_path'])
        
        # Remove from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        
        conn.commit()
        conn.close()
        
        return True
