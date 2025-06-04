# Secure Notes - Local Note-Taking App

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python main.py
```

## Usage

### Creating Notes
- Click the "New Note" button to create a new note
- Enter a title and content for your note
- Click "Save Note" to save your changes

### Encrypting Notes
- Click "Encrypt Note" to encrypt a note
- Enter a password when prompted
- Click "Save Note" to save the encrypted note
- To decrypt, click "Decrypt Note" and enter the password

### Attaching Files
- Click "Attach File" to attach a file to your note
- Select the file you want to attach
- The file will be copied to the application's data directory

### Searching and Sorting
- Use the search box to find notes by title
- Use the sort dropdown to sort notes by date or title

## Security

- All encryption is performed locally using the cryptography library
- Passwords are never stored, only used to derive encryption keys
- Notes are stored in a local SQLite database
