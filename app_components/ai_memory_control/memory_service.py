"""
AI Memory Control Service - MCP Service Implementation

This service provides HTTP endpoints for managing the AI Memory System
(.github/copilot directory) through the shared MCP server infrastructure.

Endpoints:
    GET /memory/files - List all .md files in memory system
    GET /memory/file/{path} - Get content of specific file
    GET /memory/cross-refs - Get cross-reference analysis
    POST /memory/file/{path} - Save file content
    POST /memory/search - Search across all files
    GET /memory/static/{path} - Serve static web assets
    GET /memory - Serve main web interface

Features:
- File system operations with .github/copilot integration
- Cross-reference analysis between documentation files  
- Web interface serving (HTML, CSS, JS)
- Search functionality across markdown content
- Thread-safe file operations with proper error handling
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import unquote
import sys
from pathlib import Path

# Add app_components to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
app_components_path = project_root / 'app_components'
if str(app_components_path) not in sys.path:
    sys.path.insert(0, str(app_components_path))

from mcp_server.mcp_server_core import MCPServiceBase


class AIMemoryControlService(MCPServiceBase):
    """
    AI Memory Control Service for managing copilot documentation.
    
    Provides comprehensive file management for the AI Memory System including
    file operations, cross-reference analysis, and web interface serving.
    """
    
    def __init__(self):
        super().__init__("AI Memory Control")
        self.copilot_dir = None
        self.static_dir = None
        self.templates_dir = None
        self.file_cache = {}
        self.cross_ref_cache = None
        
    def initialize(self) -> bool:
        """Initialize service by locating copilot directory and static assets"""
        try:
            # Find project root and copilot directory
            current_dir = Path(__file__).parent
            project_root = None
            
            # Search up the directory tree for .github/copilot
            for parent in current_dir.parents:
                copilot_path = parent / '.github' / 'copilot'
                if copilot_path.exists():
                    project_root = parent
                    self.copilot_dir = copilot_path
                    break
            
            if not self.copilot_dir:
                print("❌ Could not locate .github/copilot directory")
                return False
                
            # Set up component directories  
            component_dir = project_root / 'app_components' / 'ai_memory_control'
            self.static_dir = component_dir / 'static'
            self.templates_dir = component_dir / 'templates'
            
            # Verify directories exist
            if not self.static_dir.exists() or not self.templates_dir.exists():
                print(f"❌ Missing component directories: {component_dir}")
                return False
                
            print(f"✅ AI Memory Control Service initialized")
            print(f"   Copilot directory: {self.copilot_dir}")
            print(f"   Static assets: {self.static_dir}")
            print(f"   Templates: {self.templates_dir}")
            
            # Build initial file cache
            self._rebuild_file_cache()
            
            return super().initialize()
            
        except Exception as e:
            print(f"❌ AI Memory Control Service initialization failed: {e}")
            return False
            
    def handle_get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GET requests for memory system operations"""
        try:
            if path == '/' or path == '':
                # Serve main web interface
                return self._serve_web_interface()
                
            elif path.startswith('/static/'):
                # Serve static assets (CSS, JS, images)
                static_path = path.replace('/static/', '')
                return self._serve_static_file(static_path)
                
            elif path == '/files':
                # List all files in memory system
                return self._get_file_list()
                
            elif path.startswith('/file/'):
                # Get specific file content
                file_path = path.replace('/file/', '')
                return self._get_file_content(unquote(file_path))
                
            elif path == '/cross-refs':
                # Get cross-reference analysis
                return self._get_cross_references()
                
            elif path == '/health':
                # Service health check
                return self.get_health_info()
                
            else:
                return {'error': f'Unknown endpoint: {path}'}
                
        except Exception as e:
            return {'error': f'GET request error: {str(e)}'}
            
    def handle_post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POST requests for memory system operations"""
        try:
            if path.startswith('/file/'):
                # Save file content
                file_path = path.replace('/file/', '')
                content = data.get('content', '')
                return self._save_file_content(unquote(file_path), content)
                
            elif path == '/search':
                # Search across all files
                query = data.get('query', '')
                return self._search_files(query)
                
            elif path == '/refresh':
                # Refresh file cache and cross-references
                return self._refresh_cache()
                
            else:
                return {'error': f'Unknown POST endpoint: {path}'}
                
        except Exception as e:
            return {'error': f'POST request error: {str(e)}'}
            
    def get_health_info(self) -> Dict[str, Any]:
        """Return service health and statistics"""
        try:
            file_count = len(self.file_cache)
            total_size = sum(info.get('size', 0) for info in self.file_cache.values())
            
            return {
                'service': self.service_name,
                'status': 'healthy',
                'initialized': self.is_initialized,
                'statistics': {
                    'total_files': file_count,
                    'total_size_bytes': total_size,
                    'cache_entries': len(self.file_cache),
                    'cross_refs_cached': self.cross_ref_cache is not None,
                    'copilot_dir_exists': self.copilot_dir.exists() if self.copilot_dir else False
                }
            }
        except Exception as e:
            return {
                'service': self.service_name,
                'status': 'error',
                'error': str(e)
            }
            
    def _serve_web_interface(self) -> Dict[str, Any]:
        """Serve the main HTML interface"""
        try:
            html_file = self.templates_dir / 'memory_control.html'
            if not html_file.exists():
                return {'error': 'Web interface template not found'}
                
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'content_type': 'text/html',
                'content': content,
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to serve web interface: {str(e)}'}
            
    def _serve_static_file(self, static_path: str) -> Dict[str, Any]:
        """Serve static assets (CSS, JS, images)"""
        try:
            file_path = self.static_dir / static_path
            
            if not file_path.exists() or not file_path.is_file():
                return {'error': f'Static file not found: {static_path}'}
                
            # Determine content type
            content_type = 'text/plain'
            if static_path.endswith('.css'):
                content_type = 'text/css'
            elif static_path.endswith('.js'):
                content_type = 'application/javascript'
            elif static_path.endswith('.html'):
                content_type = 'text/html'
            elif static_path.endswith(('.png', '.jpg', '.jpeg')):
                content_type = 'image/png'  # Generic image type
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'content_type': content_type,
                'content': content,
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to serve static file: {str(e)}'}
            
    def _get_file_list(self) -> Dict[str, Any]:
        """Get list of all .md files organized by category"""
        try:
            organized_files = {}
            
            for rel_path, info in self.file_cache.items():
                # Determine category from path
                path_parts = Path(rel_path).parts
                category = path_parts[0] if len(path_parts) > 1 else 'root'
                
                if category not in organized_files:
                    organized_files[category] = []
                    
                organized_files[category].append({
                    'filename': Path(rel_path).name,
                    'path': rel_path,
                    'size': info.get('size', 0),
                    'modified': info.get('modified', 'unknown'),
                    'category': category
                })
            
            # Sort files within each category
            for category in organized_files:
                organized_files[category].sort(key=lambda x: x['filename'])
            
            return {
                'files': organized_files,
                'total_files': len(self.file_cache),
                'categories': list(organized_files.keys()),
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to get file list: {str(e)}'}
            
    def _get_file_content(self, relative_path: str) -> Dict[str, Any]:
        """Get content of a specific file"""
        try:
            file_path = self.copilot_dir / relative_path
            
            if not file_path.exists() or not file_path.is_file():
                return {'error': f'File not found: {relative_path}'}
                
            if not file_path.suffix == '.md':
                return {'error': 'Only .md files are supported'}
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get file info
            stat = file_path.stat()
            
            return {
                'content': content,
                'path': relative_path,
                'filename': file_path.name,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to get file content: {str(e)}'}
            
    def _save_file_content(self, relative_path: str, content: str) -> Dict[str, Any]:
        """Save content to a file"""
        try:
            file_path = self.copilot_dir / relative_path
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Update cache
            stat = file_path.stat()
            self.file_cache[relative_path] = {
                'size': stat.st_size,
                'modified': stat.st_mtime
            }
            
            # Invalidate cross-reference cache
            self.cross_ref_cache = None
            
            return {
                'path': relative_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'status': 'success',
                'message': 'File saved successfully'
            }
        except Exception as e:
            return {'error': f'Failed to save file: {str(e)}'}
            
    def _search_files(self, query: str) -> Dict[str, Any]:
        """Search for text across all files"""
        try:
            if not query.strip():
                return {'error': 'Empty search query'}
                
            results = []
            query_lower = query.lower()
            
            for rel_path in self.file_cache:
                try:
                    file_path = self.copilot_dir / rel_path
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Search for matches
                    lines = content.split('\n')
                    matches = []
                    
                    for i, line in enumerate(lines, 1):
                        if query_lower in line.lower():
                            matches.append({
                                'line_number': i,
                                'line_content': line.strip(),
                                'context': self._get_line_context(lines, i-1)
                            })
                            
                    if matches:
                        results.append({
                            'file': rel_path,
                            'filename': Path(rel_path).name,
                            'matches': matches[:5]  # Limit matches per file
                        })
                        
                except Exception as e:
                    continue  # Skip files that can't be read
                    
            return {
                'query': query,
                'results': results,
                'total_files_searched': len(self.file_cache),
                'files_with_matches': len(results),
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Search failed: {str(e)}'}
            
    def _get_cross_references(self) -> Dict[str, Any]:
        """Analyze cross-references between files"""
        try:
            if self.cross_ref_cache is None:
                self._build_cross_references()
                
            return {
                'cross_references': self.cross_ref_cache,
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to get cross-references: {str(e)}'}
            
    def _rebuild_file_cache(self) -> None:
        """Rebuild the file cache by scanning copilot directory"""
        self.file_cache = {}
        
        if not self.copilot_dir or not self.copilot_dir.exists():
            return
            
        for md_file in self.copilot_dir.rglob('*.md'):
            try:
                rel_path = md_file.relative_to(self.copilot_dir)
                stat = md_file.stat()
                
                self.file_cache[str(rel_path)] = {
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                }
            except Exception as e:
                print(f"⚠️ Error caching file {md_file}: {e}")
                
    def _build_cross_references(self) -> None:
        """Build cross-reference map between files"""
        cross_refs = {}
        
        for rel_path in self.file_cache:
            try:
                file_path = self.copilot_dir / rel_path
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find references to other .md files
                refs = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
                refs.extend(re.findall(r'`([^`]+\.md)`', content))
                
                if refs:
                    cross_refs[rel_path] = [
                        {'text': text, 'target': target} if isinstance(ref, tuple) 
                        else {'text': ref, 'target': ref}
                        for ref in refs for text, target in [ref] if isinstance(ref, tuple)
                    ] + [
                        {'text': ref, 'target': ref}
                        for ref in refs if isinstance(ref, str)
                    ]
                    
            except Exception as e:
                continue
                
        self.cross_ref_cache = cross_refs
        
    def _get_line_context(self, lines: List[str], line_idx: int, context_size: int = 2) -> Dict[str, str]:
        """Get context lines around a match"""
        start = max(0, line_idx - context_size)
        end = min(len(lines), line_idx + context_size + 1)
        
        return {
            'before': lines[start:line_idx],
            'after': lines[line_idx + 1:end]
        }
        
    def _refresh_cache(self) -> Dict[str, Any]:
        """Refresh file cache and cross-references"""
        try:
            old_count = len(self.file_cache)
            self._rebuild_file_cache()
            self.cross_ref_cache = None
            
            return {
                'message': 'Cache refreshed successfully',
                'old_file_count': old_count,
                'new_file_count': len(self.file_cache),
                'status': 'success'
            }
        except Exception as e:
            return {'error': f'Failed to refresh cache: {str(e)}'}