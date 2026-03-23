#!/usr/bin/env python3
"""Demo script for the Structured Editor."""

import sys
sys.path.insert(0, '/home/stoyan/proj/editor_workspace')

from structured_editor import StructuredEditor

def main():
    print("="*70)
    print("🎯 Structured Editor Demo")
    print("="*70)
    
    # Create editor
    editor = StructuredEditor()
    
    # Show available files
    print("\n📁 Current files in workspace:")
    editor.list_files()
    
    # Show edit history
    print("\n📜 Recent edit history:")
    editor.get_history(limit=5)
    
    # Show git log
    print("\n📊 Git commit log:")
    editor.git_log(limit=5)
    
    print("\n" + "="*70)
    print("✅ Demo complete!")
    print("\n💡 Try importing and editing files:")
    print("   editor.open_file('myfile.html')")
    print("   editor.edit_file('myfile.html', edits)")
    print("   editor.view_file('myfile.html')")
    print("="*70)

if __name__ == '__main__':
    main()
