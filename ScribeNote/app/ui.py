import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QListWidget, QPushButton, QFileDialog,
                            QInputDialog, QMessageBox, QSplitter, QLabel, 
                            QLineEdit, QComboBox, QToolBar, QAction, QMenu)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

from .note_manager import NoteManager
from .encryption import EncryptionHandler
from .file_handler import FileHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureNotes")
        self.setMinimumSize(1000, 700)
        
        # Initialize components
        self.note_manager = NoteManager()
        self.encryption_handler = EncryptionHandler()
        self.file_handler = FileHandler()
        
        # Setup UI
        self.setup_ui()
        
        # Load notes
        self.load_notes()

    def setup_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Left panel - Note list and controls
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search notes...")
        self.search_box.textChanged.connect(self.filter_notes)
        self.left_layout.addWidget(self.search_box)
        
        # Sort options
        self.sort_layout = QHBoxLayout()
        self.sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date (newest)", "Date (oldest)", "Title (A-Z)", "Title (Z-A)"])
        self.sort_combo.currentIndexChanged.connect(self.sort_notes)
        self.sort_layout.addWidget(self.sort_label)
        self.sort_layout.addWidget(self.sort_combo)
        self.left_layout.addLayout(self.sort_layout)
        
        # Note list
        self.note_list = QListWidget()
        self.note_list.setMinimumWidth(250)
        self.note_list.currentRowChanged.connect(self.display_note)
        self.left_layout.addWidget(self.note_list)
        
        # Button controls
        self.btn_layout = QHBoxLayout()
        
        self.new_btn = QPushButton("New Note")
        self.new_btn.clicked.connect(self.create_new_note)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_note)
        
        self.btn_layout.addWidget(self.new_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.left_layout.addLayout(self.btn_layout)
        
        # Right panel - Note content
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # Note title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Note Title")
        self.title_edit.textChanged.connect(self.update_note_title)
        self.right_layout.addWidget(self.title_edit)
        
        # Note editor
        self.note_editor = QTextEdit()
        self.note_editor.setFontPointSize(12)
        self.note_editor.textChanged.connect(self.update_note_content)
        self.right_layout.addWidget(self.note_editor)
        
        # Attachment and encryption controls
        self.control_layout = QHBoxLayout()
        
        self.attach_btn = QPushButton("Attach File")
        self.attach_btn.clicked.connect(self.attach_file)
        
        self.encrypt_btn = QPushButton("Encrypt Note")
        self.encrypt_btn.clicked.connect(self.toggle_encryption)
        
        self.save_btn = QPushButton("Save Note")
        self.save_btn.clicked.connect(self.save_note)
        
        self.control_layout.addWidget(self.attach_btn)
        self.control_layout.addWidget(self.encrypt_btn)
        self.control_layout.addWidget(self.save_btn)
        self.right_layout.addLayout(self.control_layout)
        
        # Add panels to splitter
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([300, 700])
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Current note tracking
        self.current_note_id = None
        self.is_encrypted = False

    def load_notes(self):
        notes = self.note_manager.get_all_notes()
        self.note_list.clear()
        for note in notes:
            self.note_list.addItem(note['title'])
        
        if self.note_list.count() > 0:
            self.note_list.setCurrentRow(0)
        else:
            self.clear_editor()
    
    def display_note(self, row):
        if row < 0:
            self.clear_editor()
            return
            
        notes = self.note_manager.get_all_notes()
        if row < len(notes):
            note = notes[row]
            self.current_note_id = note['id']
            
            self.title_edit.setText(note['title'])
            
            content = note['content']
            if note.get('encrypted', False):
                self.is_encrypted = True
                self.encrypt_btn.setText("Decrypt Note")
                self.note_editor.setReadOnly(True)
                self.note_editor.setText("[Encrypted Note - Click 'Decrypt Note' to view]")
            else:
                self.is_encrypted = False
                self.encrypt_btn.setText("Encrypt Note")
                self.note_editor.setReadOnly(False)
                self.note_editor.setText(content)
            
            self.statusBar().showMessage(f"Note last modified: {note['modified_date']}")
    
    def clear_editor(self):
        self.current_note_id = None
        self.title_edit.clear()
        self.note_editor.clear()
        self.encrypt_btn.setText("Encrypt Note")
        self.note_editor.setReadOnly(False)
        self.is_encrypted = False
    
    def create_new_note(self):
        note_id = self.note_manager.create_note("New Note", "")
        self.load_notes()
        
        # Find and select the new note
        for i in range(self.note_list.count()):
            if self.note_manager.get_note(note_id)['title'] == self.note_list.item(i).text():
                self.note_list.setCurrentRow(i)
                break
    
    def delete_note(self):
        if self.current_note_id is None:
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Delete",
            "Are you sure you want to delete this note?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.note_manager.delete_note(self.current_note_id)
            self.load_notes()
    
    def save_note(self):
        if self.current_note_id is None:
            return
            
        title = self.title_edit.text()
        content = self.note_editor.toPlainText()
        
        if self.is_encrypted:
            password, ok = QInputDialog.getText(
                self, 
                "Encryption Password", 
                "Enter encryption password:",
                QLineEdit.Password
            )
            if ok and password:
                try:
                    content = self.encryption_handler.encrypt(content, password)
                    self.note_manager.update_note(
                        self.current_note_id, 
                        title, 
                        content, 
                        encrypted=True
                    )
                    QMessageBox.information(self, "Success", "Note encrypted successfully!")
                    self.load_notes()
                except Exception as e:
                    QMessageBox.critical(self, "Encryption Error", f"Could not encrypt note: {str(e)}")
        else:
            self.note_manager.update_note(
                self.current_note_id,
                title,
                content,
                encrypted=False
            )
            self.statusBar().showMessage("Note saved successfully")
            self.load_notes()
    
    def update_note_title(self):
        if self.current_note_id is not None:
            current_row = self.note_list.currentRow()
            if current_row >= 0:
                self.note_list.item(current_row).setText(self.title_edit.text())
    
    def update_note_content(self):
        # This will be used for auto-save functionality if implemented
        pass
    
    def toggle_encryption(self):
        if self.current_note_id is None:
            return
            
        note = self.note_manager.get_note(self.current_note_id)
        
        if note.get('encrypted', False):
            # Decrypt the note
            password, ok = QInputDialog.getText(
                self, 
                "Decryption Password", 
                "Enter decryption password:",
                QLineEdit.Password
            )
            if ok and password:
                try:
                    decrypted_content = self.encryption_handler.decrypt(note['content'], password)
                    self.note_editor.setText(decrypted_content)
                    self.note_editor.setReadOnly(False)
                    self.encrypt_btn.setText("Encrypt Note")
                    self.is_encrypted = False
                except Exception as e:
                    QMessageBox.critical(self, "Decryption Error", f"Incorrect password or corrupted data: {str(e)}")
        else:
            # Mark for encryption (actual encryption happens on save)
            self.is_encrypted = True
            self.encrypt_btn.setText("Decrypt Note")
            QMessageBox.information(
                self,
                "Encryption",
                "Note marked for encryption. Click 'Save Note' to encrypt with a password."
            )
    
    def attach_file(self):
        if self.current_note_id is None:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach File",
            "",
            "All Files (*)"
        )
        
        if file_path:
            try:
                attachment_info = self.file_handler.attach_file(self.current_note_id, file_path)
                current_text = self.note_editor.toPlainText()
                
                # Add attachment reference to note
                attachment_text = f"\n[Attachment: {os.path.basename(file_path)}]\n"
                
                if current_text:
                    self.note_editor.setText(current_text + attachment_text)
                else:
                    self.note_editor.setText(attachment_text)
                
                QMessageBox.information(self, "Success", "File attached successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not attach file: {str(e)}")
    
    def filter_notes(self, search_text):
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            item.setHidden(search_text.lower() not in item.text().lower())
    
    def sort_notes(self, index):
        current_note_id = self.current_note_id
        notes = self.note_manager.get_all_notes()
        
        # Sort based on selection
        if index == 0:  # Date (newest)
            notes.sort(key=lambda x: x['modified_date'], reverse=True)
        elif index == 1:  # Date (oldest)
            notes.sort(key=lambda x: x['modified_date'])
        elif index == 2:  # Title (A-Z)
            notes.sort(key=lambda x: x['title'].lower())
        elif index == 3:  # Title (Z-A)
            notes.sort(key=lambda x: x['title'].lower(), reverse=True)
        
        # Update the note manager
        self.note_manager.sort_notes(notes)
        
        # Reload the list
        self.load_notes()
        
        # Try to reselect the previously selected note
        if current_note_id:
            for i in range(self.note_list.count()):
                note = self.note_manager.get_note_by_index(i)
                if note and note['id'] == current_note_id:
                    self.note_list.setCurrentRow(i)
                    break
