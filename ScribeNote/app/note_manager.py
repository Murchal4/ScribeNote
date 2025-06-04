import sqlite3
import os
import json
import datetime
import uuid

class NoteManager:
    def __init__(self, db_path=None):
        if db_path is None:
            # Use default path
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "notes.db")
        else:
            self.db_path = db_path
            
        self.initialize_db()
    
    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create notes table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            created_date TEXT NOT NULL,
            modified_date TEXT NOT NULL,
            metadata TEXT,
            encrypted INTEGER DEFAULT 0
        )
        ''')
        
        # Create attachments table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id TEXT PRIMARY KEY,
            note_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT,
            created_date TEXT NOT NULL,
            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_note(self, title, content, metadata=None, encrypted=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        note_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()
        
        metadata_json = json.dumps(metadata) if metadata else "{}"
        
        cursor.execute(
            "INSERT INTO notes (id, title, content, created_date, modified_date, metadata, encrypted) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (note_id, title, content, now, now, metadata_json, 1 if encrypted else 0)
        )
        
        conn.commit()
        conn.close()
        
        return note_id
    
    def get_note(self, note_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        conn.close()
        
        if note:
            return dict(note)
        return None
    
    def get_note_by_index(self, index):
        notes = self.get_all_notes()
        if 0 <= index < len(notes):
            return notes[index]
        return None
    
    def get_all_notes(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notes ORDER BY modified_date DESC")
        notes = cursor.fetchall()
        
        conn.close()
        
        return [dict(note) for note in notes]
    
    def update_note(self, note_id, title, content, metadata=None, encrypted=False):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.datetime.now().isoformat()
        
        if metadata is not None:
            metadata_json = json.dumps(metadata)
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, modified_date = ?, metadata = ?, encrypted = ? WHERE id = ?",
                (title, content, now, metadata_json, 1 if encrypted else 0, note_id)
            )
        else:
            cursor.execute(
                "UPDATE notes SET title = ?, content = ?, modified_date = ?, encrypted = ? WHERE id = ?",
                (title, content, now, 1 if encrypted else 0, note_id)
            )
        
        conn.commit()
        conn.close()
    
    def delete_note(self, note_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First delete any attachments
        cursor.execute("DELETE FROM attachments WHERE note_id = ?", (note_id,))
        
        # Then delete the note
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        
        conn.commit()
        conn.close()
    
    def get_attachments(self, note_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM attachments WHERE note_id = ?", (note_id,))
        attachments = cursor.fetchall()
        
        conn.close()
        
        return [dict(attachment) for attachment in attachments]
    
    def sort_notes(self, notes):
        # This method is used to reorder notes in the database
        # based on the sorted list provided
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # For now we don't actually change the database order
        # The UI handles the sorting display
        
        conn.close()
