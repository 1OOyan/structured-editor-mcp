# Structured File Editor

A git-backed file editing system that provides structured, tracked file modifications with full history.

## Features

- **Line-based Editing**: Insert, replace, or delete specific lines
- **Git-backed Version Control**: Every edit is committed to git
- **Edit History Logging**: JSON-based history with timestamps
- **Diff Tracking**: See exactly what changed between versions
- **Revert Capability**: Roll back to any previous version
- **Workspace Management**: Organized file structure

## Installation

```bash
git clone https://github.com/1OOyan/structured-editor-mcp.git
cd structured-editor-mcp

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from structured_editor import StructuredEditor

# Create editor instance
editor = StructuredEditor()

# Import a file
editor.open_file('myfile.html')

# Make structured edits
edits = [
    {'line': 10, 'action': 'replace', 'text': 'new content'},
    {'line': 15, 'action': 'insert', 'text': 'inserted line'},
    {'line': 20, 'action': 'delete'},
]
editor.edit_file('myfile.html', edits)

# View file
editor.view_file('myfile.html')

# Check history
editor.get_history('myfile.html')

# See git diff
editor.diff_versions('myfile.html')

# Revert to previous version
editor.revert('myfile.html')
```

### Edit Operations

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `insert` | Insert a new line at position | `line`, `text` |
| `replace` | Replace existing line | `line`, `text` |
| `delete` | Remove a line | `line` |

### Edit Format

```python
edits = [
    {
        'line': 10,           # Line number (1-indexed)
        'action': 'replace',  # 'insert', 'replace', or 'delete'
        'text': 'new text'    # New content (required for insert/replace)
    },
]
```

## Directory Structure

```
structured-editor-mcp/
├── structured_editor.py      # Main module
├── mcp_server_editor.py      # MCP server
├── mcp_server/               # MCP server package
│   ├── __init__.py
│   └── server.py
├── README.md                 # Main docs
├── README_MCP.md             # MCP docs
├── mcp_config.example.json   # Config example
├── requirements.txt          # Dependencies
├── demo.py                   # Demo script
├── files/                    # Git repository with edited files
│   ├── .git/
│   └── (your files here)
└── edit_history.json         # Edit history log
```

## MCP Server

This repository includes a complete MCP (Model Context Protocol) server that exposes 11 tools:

1. `editor_open_file` - Open/import files
2. `editor_edit_file` - Apply edits
3. `editor_view_file` - View with line numbers
4. `editor_get_history` - Get edit history
5. `editor_diff_versions` - Show git diff
6. `editor_revert` - Revert to previous version
7. `editor_list_files` - List workspace files
8. `editor_export_file` - Export to destination
9. `editor_git_log` - Show commit log
10. `editor_workspace_status` - Get status info
11. `editor_init_workspace` - Initialize workspace

See [README_MCP.md](README_MCP.md) for detailed MCP server documentation.

## Methods

### Core Methods

- `open_file(filename, source_path=None)` - Import/open a file
- `edit_file(filename, edits)` - Apply structured edits
- `view_file(filename, max_lines=50)` - View file with line numbers
- `get_history(filename=None, limit=10)` - Get edit history
- `diff_versions(filename, commits=1)` - Show git diff
- `revert(filename, versions=1)` - Revert to previous version
- `list_files()` - List all files in workspace
- `export_file(filename, dest_path=None)` - Export file to destination
- `git_log(filename=None, limit=10)` - Show git commit log

## Example Workflow

```python
from structured_editor import StructuredEditor

# Initialize
editor = StructuredEditor()

# Step 1: Import a file
editor.open_file('index.html', source_path='/var/www/html/index.html')

# Step 2: Make targeted edits
edits = [
    {'line': 5, 'action': 'replace', 'text': '    <title>Updated Title</title>'},
    {'line': 15, 'action': 'insert', 'text': '    <!-- New section -->'},
]
editor.edit_file('index.html', edits)

# Step 3: Review changes
editor.get_history('index.html')
editor.diff_versions('index.html')

# Step 4: Export if satisfied
editor.export_file('index.html', '/var/www/html/index.html')

# Or revert if needed
editor.revert('index.html')
```

## Edit History Format

The edit history is stored in JSON format:

```json
{
  "edits": [
    {
      "timestamp": "2024-03-23T19:30:45.123456",
      "file": "index.html",
      "action": "edit",
      "edits": [
        {"line": 5, "action": "replace", "text": "..."}
      ],
      "changes": "@@ -4,7 +4,7 @@\n-    <title>Old</title>\n+    <title>New</title>",
      "lines_added": 1,
      "lines_removed": 1
    }
  ]
}
```

## Advantages Over Raw File Editing

| Raw Python Writes | Structured Editor |
|-------------------|-------------------|
| ❌ Rewrites entire file | ✅ Only changes specified lines |
| ❌ No change history | ✅ Full edit history in JSON |
| ❌ Can't see what changed | ✅ Git diffs show exact changes |
| ❌ No undo | ✅ Can revert to any version |
| ❌ Hard to track | ✅ Timestamped, structured log |

## Demo

Run the demo script:

```bash
python3 demo.py
```

## License

MIT License
