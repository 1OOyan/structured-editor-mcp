# MCP Server for Structured File Editor

A Model Context Protocol (MCP) server that exposes the Structured File Editor functionality as tools.

## Overview

This MCP server provides **11 tools** for structured file editing with git-backed version control:

| Tool | Description |
|------|-------------|
| `editor_open_file` | Open/import a file for editing |
| `editor_edit_file` | Apply structured edits (insert/replace/delete) |
| `editor_view_file` | View file contents with line numbers |
| `editor_get_history` | Get edit history |
| `editor_diff_versions` | Show git diff between versions |
| `editor_revert` | Revert to previous version |
| `editor_list_files` | List files in workspace |
| `editor_export_file` | Export file to destination |
| `editor_git_log` | Show git commit log |
| `editor_workspace_status` | Get workspace status info |
| `editor_init_workspace` | Initialize/reset workspace |

## Installation

```bash
git clone https://github.com/1OOyan/structured-editor-mcp.git
cd structured-editor-mcp
```

## Running the Server

### Option 1: Standalone Mode

```bash
python3 mcp_server_editor.py
```

### Option 2: As Python Module

```bash
python3 -m mcp_server.editor
```

### Option 3: Via MCP Proxy

Add this to your MCP proxy configuration:

```json
{
  "mcp": {
    "servers": {
      "structured-editor": {
        "command": "python3",
        "args": ["/path/to/mcp_server_editor.py"],
        "env": {}
      }
    }
  }
}
```

See `mcp_config.example.json` for a complete example.

## Tool Usage Examples

### 1. Open a File

```json
{
  "tool": "editor_open_file",
  "parameters": {
    "filename": "index.html",
    "source_path": "/var/www/html/index.html"
  }
}
```

**Response:**
```
Imported: index.html (from /var/www/html/index.html)
   Lines: 150
   Size: 5432 bytes
```

### 2. Make Structured Edits

```json
{
  "tool": "editor_edit_file",
  "parameters": {
    "filename": "index.html",
    "edits": [
      {
        "line": 5,
        "action": "replace",
        "text": "    <title>Updated Title</title>"
      },
      {
        "line": 10,
        "action": "insert",
        "text": "    <!-- New comment -->"
      },
      {
        "line": 20,
        "action": "delete"
      }
    ]
  }
}
```

**Response:**
```
Edited: index.html
   Applied 3 changes
   Lines: +2 -1
```

### 3. View Edit History

```json
{
  "tool": "editor_get_history",
  "parameters": {
    "filename": "index.html",
    "limit": 5
  }
}
```

**Response:**
```
Edit History (5 entries):
======================================================================
2024-03-23 19:30:45 | index.html             | edit       |
      +2 -1 lines
2024-03-23 19:28:30 | index.html             | import     |
      +150 -0 lines
======================================================================
```

### 4. Revert Changes

```json
{
  "tool": "editor_revert",
  "parameters": {
    "filename": "index.html",
    "versions": 1
  }
}
```

**Response:**
```
Reverted: index.html to 1 version(s) ago
```

### 5. Check Workspace Status

```json
{
  "tool": "editor_workspace_status",
  "parameters": {}
}
```

**Response:**
```
Workspace Status:
  Workspace: /path/to/files
  History: /path/to/edit_history.json
  Files: 3
  Git Commits: 15
  History Entries: 23
```

## Edit Operations

The `editor_edit_file` tool supports three types of edits:

### Insert
Add a new line at a specific position:
```json
{
  "line": 10,
  "action": "insert",
  "text": "new line content"
}
```

### Replace
Replace an existing line:
```json
{
  "line": 5,
  "action": "replace",
  "text": "replacement content"
}
```

### Delete
Remove a line:
```json
{
  "line": 15,
  "action": "delete"
}
```

## Workspace Structure

```
structured-editor-mcp/
├── files/                    # Git repository with edited files
│   ├── .git/
│   └── (your files here)
└── edit_history.json         # Edit history log
```

## Features

- **Line-based Editing**: Target specific lines for modification
- **Git-backed**: Every edit is committed to git
- **History Tracking**: JSON log with timestamps and diffs
- **Version Control**: Full git history in workspace
- **Revert Capability**: Roll back to any previous version
- **Diff Tracking**: See exactly what changed

## Error Handling

All tools return error messages in the response text if something goes wrong:

```
Error: File not found: nonexistent.html
```

## Testing the Server

You can test the server directly:

```bash
python3 -c "
from mcp_server.server import create_server

server, editor = create_server()
print('Server created successfully!')
print(f'Workspace: {editor.workspace}')
print(f'History: {editor.history_file}')
"
```

## License

MIT License
