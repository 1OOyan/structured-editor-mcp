#!/usr/bin/env python3
"""
MCP Server for Structured File Editor
======================================
Provides MCP tools for structured file editing with git-backed version control.

Usage:
    # Run as standalone server
    python3 mcp_server_editor.py
    
    # Run as module
    python3 -m mcp_server.editor
    
    # Add to MCP proxy config:
    {
      "servers": {
        "editor": {
          "command": "python3",
          "args": ["/path/to/mcp_server_editor.py"]
        }
      }
    }
"""

import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from structured_editor import StructuredEditor

# Initialize the editor
editor = StructuredEditor()

# Create MCP server
server = Server("structured-file-editor")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available editor tools."""
    return [
        Tool(
            name="editor_open_file",
            description="Open or import a file for structured editing",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file in workspace"
                    },
                    "source_path": {
                        "type": "string",
                        "description": "Optional source path (default: /tmp/{filename})"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="editor_edit_file",
            description="Apply structured edits to a file (insert/replace/delete lines)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to edit"
                    },
                    "edits": {
                        "type": "array",
                        "description": "List of edit operations",
                        "items": {
                            "type": "object",
                            "properties": {
                                "line": {
                                    "type": "integer",
                                    "description": "Line number (1-indexed)"
                                },
                                "action": {
                                    "type": "string",
                                    "enum": ["insert", "replace", "delete"],
                                    "description": "Edit action"
                                },
                                "text": {
                                    "type": "string",
                                    "description": "New text (required for insert/replace)"
                                }
                            },
                            "required": ["line", "action"]
                        }
                    }
                },
                "required": ["filename", "edits"]
            }
        ),
        Tool(
            name="editor_view_file",
            description="View file contents with line numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to view"
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum lines to display (default: 50)"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="editor_get_history",
            description="Get edit history for a file or all files",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Optional filename to filter by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum entries to show (default: 10)"
                    }
                }
            }
        ),
        Tool(
            name="editor_diff_versions",
            description="Show git diff between versions",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file"
                    },
                    "commits": {
                        "type": "integer",
                        "description": "Number of commits back to compare (default: 1)"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="editor_revert",
            description="Revert file to previous version",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to revert"
                    },
                    "versions": {
                        "type": "integer",
                        "description": "Number of versions to revert back (default: 1)"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="editor_list_files",
            description="List all files in workspace",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="editor_export_file",
            description="Export a file from workspace to destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file in workspace"
                    },
                    "dest_path": {
                        "type": "string",
                        "description": "Destination path (default: /tmp/{filename})"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="editor_git_log",
            description="Show git commit log",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Optional filename to filter by"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum commits to show (default: 10)"
                    }
                }
            }
        ),
        Tool(
            name="editor_workspace_status",
            description="Get workspace status information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="editor_init_workspace",
            description="Initialize or reset the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Workspace path (default: ./editor_workspace/files)"
                    },
                    "history_file": {
                        "type": "string",
                        "description": "History file path (default: ./edit_history.json)"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "editor_open_file":
            filename = arguments.get("filename")
            source_path = arguments.get("source_path")
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                content = editor.open_file(filename, source_path)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_edit_file":
            filename = arguments.get("filename")
            edits = arguments.get("edits", [])
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                content = editor.edit_file(filename, edits)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_view_file":
            filename = arguments.get("filename")
            max_lines = arguments.get("max_lines", 50)
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                content = editor.view_file(filename, max_lines)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_get_history":
            filename = arguments.get("filename")
            limit = arguments.get("limit", 10)
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                history = editor.get_history(filename, limit)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_diff_versions":
            filename = arguments.get("filename")
            commits = arguments.get("commits", 1)
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                diff = editor.diff_versions(filename, commits)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_revert":
            filename = arguments.get("filename")
            versions = arguments.get("versions", 1)
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                success = editor.revert(filename, versions)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_list_files":
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                files = editor.list_files()
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_export_file":
            filename = arguments.get("filename")
            dest_path = arguments.get("dest_path")
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                path = editor.export_file(filename, dest_path)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_git_log":
            filename = arguments.get("filename")
            limit = arguments.get("limit", 10)
            import io
            from contextlib import redirect_stdout
            
            f = io.StringIO()
            with redirect_stdout(f):
                log = editor.git_log(filename, limit)
            output = f.getvalue()
            return [TextContent(type="text", text=output)]
        
        elif name == "editor_workspace_status":
            import os
            
            workspace = editor.workspace
            history_file = editor.history_file
            
            file_count = len([f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))])
            
            os.chdir(workspace)
            result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'], capture_output=True, text=True)
            commit_count = int(result.stdout.strip()) if result.stdout.strip() else 0
            
            history = editor._load_history()
            history_count = len(history.get('edits', []))
            
            status = f"""Workspace Status:
  Workspace: {workspace}
  History: {history_file}
  Files: {file_count}
  Git Commits: {commit_count}
  History Entries: {history_count}"""
            
            return [TextContent(type="text", text=status)]
        
        elif name == "editor_init_workspace":
            workspace = arguments.get("workspace")
            history_file = arguments.get("history_file")
            
            return [TextContent(type="text", text=f"Workspace: {editor.workspace}\nHistory: {editor.history_file}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    print("🚀 Starting MCP Server for Structured File Editor...")
    print(f"   Workspace: {editor.workspace}")
    print(f"   History: {editor.history_file}")
    print("   Ready for MCP connections via stdio...")
    asyncio.run(main())
