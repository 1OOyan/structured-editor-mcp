#!/usr/bin/env python3
"""
Structured File Editor
=====================
A git-backed file editing system that tracks all changes with full history.

Features:
- Line-based editing (insert/replace/delete)
- Git-backed version control
- Edit history logging (JSON)
- Diff tracking between versions
- Revert capability
- Workspace management

Usage:
    from structured_editor import StructuredEditor
    
    editor = StructuredEditor()
    editor.open_file("myfile.html")
    editor.edit_file("myfile.html", [
        {"line": 10, "action": "replace", "text": "new content"},
        {"line": 15, "action": "insert", "text": "inserted line"},
        {"line": 20, "action": "delete"},
    ])
    editor.get_history()
    editor.diff_versions("myfile.html")
    editor.revert("myfile.html")
"""

import os
import json
import subprocess
import difflib
from datetime import datetime
from typing import Dict, List, Optional
import shutil


class StructuredEditor:
    """A git-backed structured file editor with full change tracking."""
    
    def __init__(self, workspace: str = None, history_file: str = None):
        """
        Initialize the structured editor.
        
        Args:
            workspace: Path to the workspace directory
            history_file: Path to the edit history JSON file
        """
        if workspace:
            self.workspace = workspace
        else:
            self.workspace = os.path.join(os.path.dirname(__file__), 'files')
            
        if history_file:
            self.history_file = history_file
        else:
            self.history_file = os.path.join(os.path.dirname(__file__), 'edit_history.json')
        
        os.makedirs(self.workspace, exist_ok=True)
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        os.chdir(self.workspace)
        
        if not os.path.exists(os.path.join(self.workspace, '.git')):
            self._init_git()
    
    def _init_git(self):
        """Initialize git repository in workspace."""
        subprocess.run(['git', 'init'], capture_output=True, text=True)
        subprocess.run(['git', 'config', 'user.email', 'editor@local'], capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'File Editor'], capture_output=True)
        print(f"Initialized Git repository in {self.workspace}")
    
    def _load_history(self) -> Dict:
        """Load edit history from JSON file."""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {'edits': []}
    
    def _save_history(self, history: Dict):
        """Save edit history to JSON file."""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def open_file(self, filename: str, source_path: str = None) -> Optional[str]:
        """Open or import a file for editing."""
        filepath = os.path.join(self.workspace, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            print(f"Opened: {filename}")
            print(f"   Lines: {len(content.splitlines())}")
            print(f"   Size: {len(content)} bytes")
            return content
        
        if source_path:
            src_file = source_path
        else:
            src_file = f'/tmp/{filename}'
        
        if os.path.exists(src_file):
            with open(src_file, 'r') as f:
                content = f.read()
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"Imported: {filename} (from {src_file})")
            
            subprocess.run(['git', 'add', filename], capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'Initial: Import {filename}'], capture_output=True)
            
            history = self._load_history()
            history['edits'].append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'action': 'import',
                'source': src_file,
                'changes': 'Initial import',
                'lines_added': len(content.splitlines()),
                'lines_removed': 0
            })
            self._save_history(history)
            
            return content
        
        print(f"File not found: {filename}")
        return None
    
    def edit_file(self, filename: str, edits: List[dict]) -> Optional[str]:
        """Apply structured edits to a file."""
        filepath = os.path.join(self.workspace, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            return None
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        original = ''.join(lines)
        
        for edit in sorted(edits, key=lambda x: x['line'], reverse=True):
            line_num = edit['line'] - 1
            action = edit.get('action', 'replace')
            
            if action == 'insert':
                text = edit.get('text', '')
                lines.insert(line_num, text + '\n')
            elif action == 'replace':
                text = edit.get('text', '')
                lines[line_num] = text + '\n'
            elif action == 'delete':
                del lines[line_num]
        
        new_content = ''.join(lines)
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        diff = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f'a/{filename}',
            tofile=f'b/{filename}',
            lineterm=''
        ))
        
        subprocess.run(['git', 'add', filename], capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Edit: {filename} ({len(edits)} changes)'], capture_output=True)
        
        lines_added = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
        lines_removed = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
        
        history = self._load_history()
        history['edits'].append({
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'action': 'edit',
            'edits': edits,
            'changes': '\n'.join(diff[:30]) if diff else 'No changes',
            'lines_added': lines_added,
            'lines_removed': lines_removed
        })
        self._save_history(history)
        
        print(f"Edited: {filename}")
        print(f"   Applied {len(edits)} changes")
        print(f"   Lines: +{lines_added} -{lines_removed}")
        
        return new_content
    
    def view_file(self, filename: str, max_lines: int = 50) -> Optional[str]:
        """View file contents with line numbers."""
        filepath = os.path.join(self.workspace, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            return None
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        print(f"\n{filename} ({len(lines)} lines):")
        print("=" * 70)
        for i, line in enumerate(lines[:max_lines], 1):
            print(f"{i:4d}: {line.rstrip()}")
        if len(lines) > max_lines:
            print(f"... ({len(lines) - max_lines} more lines)")
        print("=" * 70)
        
        return ''.join(lines)
    
    def get_history(self, filename: str = None, limit: int = 10) -> List[dict]:
        """Get edit history."""
        history = self._load_history()
        
        if filename:
            edits = [e for e in history['edits'] if e['file'] == filename]
        else:
            edits = history['edits']
        
        print(f"\nEdit History ({len(edits)} entries):")
        print("=" * 70)
        for edit in edits[-limit:]:
            timestamp = edit['timestamp'][:19].replace('T', ' ')
            print(f"{timestamp} | {edit['file']:30s} | {edit['action']:10s}")
            if 'lines_added' in edit:
                print(f"      +{edit['lines_added']} -{edit['lines_removed']} lines")
        print("=" * 70)
        
        return edits
    
    def diff_versions(self, filename: str, commits: int = 1) -> Optional[str]:
        """Show git diff between versions."""
        filepath = os.path.join(self.workspace, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            return None
        
        result = subprocess.run(['git', 'diff', f'HEAD~{commits}:HEAD', filename], capture_output=True, text=True)
        
        if result.stdout:
            print(f"\nGit Diff ({filename}, last {commits} commit(s)):")
            print("=" * 70)
            print(result.stdout)
            print("=" * 70)
            return result.stdout
        else:
            print(f"No changes found for {filename}")
            return None
    
    def revert(self, filename: str, versions: int = 1) -> bool:
        """Revert file to previous version."""
        filepath = os.path.join(self.workspace, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filename}")
            return False
        
        result = subprocess.run(['git', 'checkout', f'HEAD~{versions}', '--', filename], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Reverted: {filename} to {versions} version(s) ago")
            
            history = self._load_history()
            history['edits'].append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'action': 'revert',
                'versions': versions,
                'changes': f'Reverted to {versions} version(s) ago'
            })
            self._save_history(history)
            
            return True
        else:
            print(f"Could not revert: {filename}")
            print(f"   Error: {result.stderr}")
            return False
    
    def list_files(self) -> List[str]:
        """List all files in workspace."""
        files = [f for f in os.listdir(self.workspace) if os.path.isfile(os.path.join(self.workspace, f))]
        
        print(f"\nFiles in workspace ({len(files)}):")
        print("=" * 70)
        for f in sorted(files):
            filepath = os.path.join(self.workspace, f)
            stat = os.stat(filepath)
            print(f"   {f:40s} {stat.st_size:8d} bytes")
        print("=" * 70)
        
        return files
    
    def export_file(self, filename: str, dest_path: str = None) -> Optional[str]:
        """Export a file from workspace to destination."""
        src_path = os.path.join(self.workspace, filename)
        
        if not os.path.exists(src_path):
            print(f"File not found: {filename}")
            return None
        
        if dest_path is None:
            dest_path = f'/tmp/{filename}'
        
        shutil.copy2(src_path, dest_path)
        print(f"Exported: {filename} -> {dest_path}")
        
        return dest_path
    
    def git_log(self, filename: str = None, limit: int = 10) -> str:
        """Show git commit log."""
        if filename:
            cmd = ['git', 'log', '--oneline', f'--{limit}', '--', filename]
        else:
            cmd = ['git', 'log', '--oneline', f'--{limit}']
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(f"\nGit Log ({limit} commits):")
        print("=" * 70)
        print(result.stdout)
        print("=" * 70)
        
        return result.stdout
