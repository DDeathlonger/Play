#!/usr/bin/env python3
"""
AI MEMORY CONTROL SYSTEM - COMPARTMENTALIZED COMPONENT
Web-based control panel for managing the CoPilot Memory System (.github/copilot/ directory)

ARCHITECTURE INTEGRATION:
- Uses existing MCP server infrastructure (no separate Flask server)
- Extends MCPHandler with new endpoints for memory management
- Follows established app_components/ compartmentalization pattern
- Integrates through standard spaceship.py entry point

COMPONENT RESPONSIBILITIES:
- Serve web interface via existing MCP server
- Provide REST API for .md file management  
- Enable markdown viewing/editing with live preview
- Visualize cross-references between documentation files
- Maintain file metadata and relationship mapping

DEPENDENCIES:
- Extends existing MCPHandler in spaceship_designer.py
- Uses established MCP utilities and patterns
- No additional web framework dependencies required
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

class AIMemoryManager:
    """Core manager for AI Memory System operations"""
    
    def __init__(self, copilot_root: str = ".github/copilot"):
        """Initialize with copilot directory root path"""
        self.copilot_root = Path(copilot_root)
        self.base_dir = Path.cwd()
        self.memory_files = {}
        self.cross_references = {}
        self.file_metadata = {}
        self._scan_memory_files()
    
    def _scan_memory_files(self):
        """Recursively scan .github/copilot directory for .md files"""
        memory_path = self.base_dir / self.copilot_root
        
        if not memory_path.exists():
            print(f"⚠️ Memory path not found: {memory_path}")
            return
        
        print(f"🔍 Scanning AI Memory System: {memory_path}")
        
        for md_file in memory_path.rglob("*.md"):
            relative_path = md_file.relative_to(self.base_dir)
            file_key = str(relative_path).replace("\\", "/")
            
            self.memory_files[file_key] = {
                "absolute_path": str(md_file),
                "relative_path": file_key,
                "name": md_file.name,
                "directory": str(md_file.parent.relative_to(memory_path)),
                "size": md_file.stat().st_size,
                "modified": md_file.stat().st_mtime,
                "category": self._categorize_file(file_key)
            }
        
        print(f"📊 Discovered {len(self.memory_files)} memory files")
        self._analyze_cross_references()
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize memory file based on path and name"""
        path_lower = file_path.lower()
        
        if "/protocols/" in path_lower:
            return "protocol"
        elif "/guides/" in path_lower:
            return "guide"
        elif "/context/" in path_lower:
            return "context"
        elif "/reference/" in path_lower:
            return "reference"
        elif "copilot-instructions" in path_lower:
            return "core_instructions"
        elif "master_documentation" in path_lower:
            return "index"
        else:
            return "documentation"
    
    def _analyze_cross_references(self):
        """Analyze cross-references between memory files"""
        print("🔗 Analyzing cross-references...")
        
        for file_key, file_info in self.memory_files.items():
            try:
                with open(file_info["absolute_path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find markdown links [text](path.md)
                links = re.findall(r'\\[([^\\]]+)\\]\\(([^\\)]+\\.md)\\)', content)
                
                # Find direct file references
                file_refs = re.findall(r'([\\w\\-\\_]+\\.md)', content)
                
                references = set()
                for _, link_path in links:
                    # Convert relative links to match our file keys
                    if not link_path.startswith('.github/copilot/'):
                        link_path = f".github/copilot/{link_path}"
                    references.add(link_path.replace("\\", "/"))
                
                for ref in file_refs:
                    # Check if this file exists in our memory files
                    matching_files = [k for k in self.memory_files.keys() if k.endswith(ref)]
                    references.update(matching_files)
                
                self.cross_references[file_key] = list(references)
                
            except Exception as e:
                print(f"⚠️ Error analyzing {file_key}: {e}")
                self.cross_references[file_key] = []
    
    def get_file_content(self, file_key: str) -> Optional[str]:
        """Get content of a memory file"""
        if file_key not in self.memory_files:
            return None
        
        try:
            with open(self.memory_files[file_key]["absolute_path"], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Error reading {file_key}: {e}")
            return None
    
    def save_file_content(self, file_key: str, content: str) -> bool:
        """Save content to a memory file"""
        if file_key not in self.memory_files:
            return False
        
        try:
            with open(self.memory_files[file_key]["absolute_path"], 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update metadata
            file_path = Path(self.memory_files[file_key]["absolute_path"])
            self.memory_files[file_key]["size"] = file_path.stat().st_size
            self.memory_files[file_key]["modified"] = file_path.stat().st_mtime
            
            return True
        except Exception as e:
            print(f"⚠️ Error saving {file_key}: {e}")
            return False
    
    def get_file_list(self) -> Dict[str, Any]:
        """Get organized list of all memory files"""
        categories = {}
        
        for file_key, file_info in self.memory_files.items():
            category = file_info["category"]
            if category not in categories:
                categories[category] = []
            
            categories[category].append({
                "key": file_key,
                "name": file_info["name"],
                "directory": file_info["directory"],
                "size": file_info["size"],
                "modified": datetime.fromtimestamp(file_info["modified"]).isoformat(),
                "references": len(self.cross_references.get(file_key, []))
            })
        
        # Sort each category by name
        for category in categories:
            categories[category].sort(key=lambda x: x["name"])
        
        return {
            "categories": categories,
            "total_files": len(self.memory_files),
            "total_categories": len(categories)
        }
    
    def get_cross_reference_map(self) -> Dict[str, Any]:
        """Get visual cross-reference mapping for graph visualization"""
        nodes = []
        edges = []
        
        for file_key, file_info in self.memory_files.items():
            nodes.append({
                "id": file_key,
                "label": file_info["name"],
                "category": file_info["category"],
                "size": file_info["size"]
            })
        
        for source_file, references in self.cross_references.items():
            for target_file in references:
                if target_file in self.memory_files:
                    edges.append({
                        "source": source_file,
                        "target": target_file
                    })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
        }


class MCPMemoryExtension:
    """Extension for existing MCP server to handle memory control endpoints"""
    
    def __init__(self, memory_manager: AIMemoryManager):
        self.memory_manager = memory_manager
        self.static_root = Path(__file__).parent / "static"
        self.templates_root = Path(__file__).parent / "templates"
    
    def handle_memory_request(self, path: str, method: str, body: bytes = None) -> Tuple[int, str, str]:
        """
        Handle memory control requests
        Returns: (status_code, content_type, response_body)
        """
        
        # Serve static files
        if path.startswith("/memory/static/"):
            return self._serve_static_file(path[15:])  # Remove "/memory/static/"
        
        # Main memory control interface
        if path == "/memory" or path == "/memory/":
            return self._serve_main_interface()
        
        # API endpoints
        if path == "/memory/api/files" and method == "GET":
            file_list = self.memory_manager.get_file_list()
            return (200, "application/json", json.dumps(file_list))
        
        elif path == "/memory/api/cross-references" and method == "GET":
            cross_refs = self.memory_manager.get_cross_reference_map()
            return (200, "application/json", json.dumps(cross_refs))
        
        elif path.startswith("/memory/api/file/") and method == "GET":
            file_key = path[17:]  # Remove "/memory/api/file/"
            content = self.memory_manager.get_file_content(file_key)
            if content is not None:
                return (200, "text/plain", content)
            else:
                return (404, "application/json", json.dumps({"error": "File not found"}))
        
        elif path.startswith("/memory/api/file/") and method == "POST":
            file_key = path[17:]
            if body:
                try:
                    data = json.loads(body.decode('utf-8'))
                    success = self.memory_manager.save_file_content(file_key, data.get("content", ""))
                    if success:
                        return (200, "application/json", json.dumps({"success": True}))
                    else:
                        return (500, "application/json", json.dumps({"error": "Failed to save file"}))
                except Exception as e:
                    return (400, "application/json", json.dumps({"error": f"Invalid request: {e}"}))
        
        return (404, "text/plain", "Memory endpoint not found")
    
    def _serve_static_file(self, file_path: str) -> Tuple[int, str, str]:
        """Serve static CSS/JS files"""
        static_file = self.static_root / file_path
        
        if not static_file.exists():
            return (404, "text/plain", "Static file not found")
        
        # Determine content type
        if file_path.endswith('.css'):
            content_type = "text/css"
        elif file_path.endswith('.js'):
            content_type = "application/javascript"
        else:
            content_type = "text/plain"
        
        try:
            with open(static_file, 'r', encoding='utf-8') as f:
                return (200, content_type, f.read())
        except Exception as e:
            return (500, "text/plain", f"Error serving static file: {e}")
    
    def _serve_main_interface(self) -> Tuple[int, str, str]:
        """Serve the main memory control interface"""
        html_file = self.templates_root / "memory_control.html"
        
        if not html_file.exists():
            # Create basic interface if template doesn't exist
            return (200, "text/html", self._generate_basic_interface())
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                return (200, "text/html", f.read())
        except Exception as e:
            return (500, "text/html", f"<h1>Error</h1><p>{e}</p>")
    
    def _generate_basic_interface(self) -> str:
        """Generate basic HTML interface as fallback"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>AI Memory Control Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .status { background: #2a2a2a; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 AI Memory Control Panel</h1>
            <p>Loading interface...</p>
        </div>
        <div class="status">
            <p><strong>Status:</strong> Basic interface loaded. Full interface loading...</p>
            <p><strong>Note:</strong> This component extends the existing MCP server.</p>
            <p><strong>Access:</strong> <a href="/memory/api/files" style="color: #4CAF50;">/memory/api/files</a> for file list</p>
        </div>
    </div>
    <script>
        // Basic JavaScript will be added here
        setTimeout(() => {
            fetch('/memory/api/files')
                .then(response => response.json())
                .then(data => {
                    console.log('Memory files loaded:', data);
                    document.querySelector('.status p').innerHTML = 
                        '<strong>Status:</strong> Connected to Memory System - ' + 
                        data.total_files + ' files in ' + data.total_categories + ' categories';
                });
        }, 1000);
    </script>
</body>
</html>'''


# Module initialization
def get_memory_extension():
    """Get configured memory extension for integration with MCP server"""
    memory_manager = AIMemoryManager()
    return MCPMemoryExtension(memory_manager)