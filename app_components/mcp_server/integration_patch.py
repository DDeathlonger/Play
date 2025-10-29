"""
MCP Integration Patch for Spaceship Designer

This module provides a clean integration between the existing spaceship_designer.py
and the new modular MCP server infrastructure. It replaces the embedded MCPHandler
with calls to the shared MCP server while maintaining 100% backward compatibility.

Usage:
    # Replace existing MCP server startup in spaceship_designer.py with:
    from app_components.mcp_server.integration_patch import integrate_mcp_server
    
    # In OptimizedSpaceshipGenerator.__init__:
    self.mcp_integration = integrate_mcp_server(self)
    
    # In start_mcp_server():
    return self.mcp_integration.start()
    
    # In stop_mcp_server():
    self.mcp_integration.stop()

Features:
- Drop-in replacement for existing MCPHandler functionality
- Maintains all existing endpoints and behavior
- Adds new /memory endpoint for web interface
- Improved error handling and thread safety
- No changes needed to external AI controller scripts
"""

import sys
import os
from pathlib import Path

# Add app_components to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
app_components_path = project_root / 'app_components'
if str(app_components_path) not in sys.path:
    sys.path.insert(0, str(app_components_path))

from mcp_server.mcp_server_core import get_mcp_server, MCPServiceBase
from mcp_server.legacy_ai_service import LegacyAIControllerService
from ai_memory_control.memory_service import AIMemoryControlService


class SpaceshipMCPIntegration:
    """
    Integration wrapper for spaceship designer MCP functionality.
    
    Provides a clean interface between the existing spaceship application
    and the new modular MCP server infrastructure.
    """
    
    def __init__(self, app_reference):
        self.app_ref = app_reference
        self.mcp_server = get_mcp_server()
        self.legacy_service = None
        self.memory_service = None
        self.is_running = False
        self.port = 8765
        
    def start(self, port: int = 8765) -> bool:
        """
        Start the integrated MCP server with all services.
        
        Replaces the original start_mcp_server() functionality while
        adding the new memory management capabilities.
        """
        try:
            try:
                print("🚀 Starting integrated MCP server...")
            except UnicodeEncodeError:
                print("Starting integrated MCP server...")
            
            # Start the shared MCP server
            success = self.mcp_server.start(port)
            if not success:
                return False
                
            self.port = self.mcp_server.port
            
            # Register legacy AI controller service for backward compatibility
            self.legacy_service = LegacyAIControllerService(self.app_ref)
            legacy_registered = self.mcp_server.register_service('', self.legacy_service)
            
            if not legacy_registered:
                print("⚠️ Failed to register legacy AI controller service")
                
            # Register AI memory control service
            print("🔧 Creating AI Memory Control Service...")
            self.memory_service = AIMemoryControlService()
            print(f"🔧 Memory service created: {self.memory_service}")
            print(f"🔧 Memory service initialized: {self.memory_service.is_initialized}")
            
            print("🔧 Registering memory service with /memory prefix...")
            memory_registered = self.mcp_server.register_service('/memory', self.memory_service)
            print(f"🔧 Memory registration result: {memory_registered}")
            
            if not memory_registered:
                print("⚠️ Failed to register AI memory control service")
            else:
                print("✅ AI Memory Control Service registered successfully")
                
            self.is_running = success
            
            if success:
                print(f"✅ Integrated MCP server ready on http://localhost:{self.port}")
                print(f"📡 Available endpoints:")
                print(f"   - /health, /status, /commands (legacy AI controller)")
                print(f"   - /memory (AI memory control web interface)")
                print(f"   - /memory/files, /memory/file/*, /memory/cross-refs (API endpoints)")
                print(f"   - /services (service registry status)")
                
                # Update app reference in legacy service
                if self.legacy_service:
                    self.legacy_service.update_app_reference(self.app_ref)
                
            return success
            
        except Exception as e:
            print(f"❌ Failed to start integrated MCP server: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def stop(self) -> None:
        """Stop the integrated MCP server and cleanup all services"""
        try:
            if self.is_running:
                print("🛑 Stopping integrated MCP server...")
                
                # Unregister services
                if self.legacy_service:
                    self.mcp_server.unregister_service('')
                    
                if self.memory_service:
                    self.mcp_server.unregister_service('/memory')
                    
                # Stop the server
                self.mcp_server.stop()
                
                self.is_running = False
                print("✅ Integrated MCP server stopped successfully")
                
        except Exception as e:
            print(f"⚠️ MCP server shutdown warning: {e}")
            
    def get_status(self) -> dict:
        """Get comprehensive status of the integrated MCP server"""
        if not self.is_running:
            return {
                'running': False,
                'port': self.port,
                'services': {}
            }
            
        server_status = self.mcp_server.get_server_status()
        
        return {
            'running': True,
            'port': self.port,
            'server_status': server_status,
            'legacy_service_active': self.legacy_service is not None,
            'memory_service_active': self.memory_service is not None,
            'endpoints': {
                'legacy_ai': ['/', '/health', '/status', '/commands'],
                'memory_system': ['/memory', '/memory/files', '/memory/file/*', '/memory/cross-refs'],
                'server_info': ['/services']
            }
        }
        
    def get_mcp_commands(self) -> list:
        """Get available MCP commands - maintains compatibility"""
        if self.legacy_service:
            return self.legacy_service._get_available_commands()
        return []
        
    def get_ai_connection_status(self) -> dict:
        """Get AI connection status - maintains compatibility"""
        if self.legacy_service:
            return self.legacy_service._get_ai_status()
        return {'status': 'offline', 'connected_agents': 0}
        
    def update_latest_command(self, command_data: dict) -> None:
        """Update latest command - maintains compatibility with existing UI"""
        if self.legacy_service:
            self.legacy_service.update_latest_command(command_data)
        else:
            print(f"📝 Command logged: {command_data.get('command', 'unknown')}")
            
    def update_error_log(self, error_message: str) -> None:
        """Update error log - maintains compatibility with existing UI"""
        if self.legacy_service:
            self.legacy_service.update_error_log(error_message)
        else:
            print(f"❌ Error logged: {error_message}")
            
    def force_ui_update(self) -> None:
        """Force UI update - maintains compatibility with existing UI"""
        if self.legacy_service:
            self.legacy_service.force_ui_update()
        # Signal the main app to update its UI
        if hasattr(self.app_ref, 'force_ui_update'):
            self.app_ref.force_ui_update()


def integrate_mcp_server(app_reference) -> SpaceshipMCPIntegration:
    """
    Factory function to create MCP integration for spaceship designer.
    
    Args:
        app_reference: Reference to the main spaceship application
        
    Returns:
        SpaceshipMCPIntegration: Configured integration instance
    """
    integration = SpaceshipMCPIntegration(app_reference)
    
    print("🔗 MCP integration initialized for spaceship designer")
    print("   - Legacy AI controller endpoints preserved")  
    print("   - New AI memory control system added")
    print("   - Shared MCP server infrastructure enabled")
    
    return integration


# Convenience functions for direct replacement in spaceship_designer.py
def create_mcp_integration(app_ref):
    """Create MCP integration - direct replacement function"""
    return integrate_mcp_server(app_ref)

def start_integrated_mcp_server(integration, port=8765):
    """Start integrated MCP server - direct replacement function"""
    return integration.start(port)

def stop_integrated_mcp_server(integration):
    """Stop integrated MCP server - direct replacement function"""
    integration.stop()

def get_integration_status(integration):
    """Get integration status - direct replacement function"""  
    return integration.get_status()