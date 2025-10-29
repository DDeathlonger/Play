#!/usr/bin/env python3
"""
SPACESHIP DESIGNER WITH INTEGRATED MCP SYSTEM
Demonstrates seamless integration of MCP server, tunnel management, 
and session monitoring with the spaceship designer application.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Import MCP integration system
try:
    from mcp_app_integration import (
        MCPIntegratedStartup,
        integrate_mcp_with_spaceship_app,
        start_mcp_system_sync
    )
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MCP system not available: {e}")
    MCP_AVAILABLE = False

# Import spaceship application
try:
    from spaceship_designer import OptimizedSpaceshipGenerator
    SPACESHIP_APP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Spaceship application not available: {e}")
    SPACESHIP_APP_AVAILABLE = False

class IntegratedSpaceshipApp:
    """Spaceship Designer with integrated MCP system"""
    
    def __init__(self, enable_mcp: bool = True, mcp_port: int = 8765):
        self.enable_mcp = enable_mcp and MCP_AVAILABLE
        self.mcp_port = mcp_port
        
        # Core components
        self.spaceship_app = None
        self.mcp_system = None
        self.session_panel = None
        
        # State tracking
        self.app_running = False
        self.mcp_running = False
        
        print(f"🚀 Initializing Integrated Spaceship Designer...")
        print(f"   MCP Integration: {'✅ Enabled' if self.enable_mcp else '❌ Disabled'}")
    
    def start_application(self):
        """Start the complete integrated application"""
        
        startup_start = time.time()
        
        try:
            # Step 1: Initialize MCP system (if enabled)
            if self.enable_mcp:
                print("\n🌐 Starting MCP System...")
                mcp_start = time.time()
                
                self.mcp_system = start_mcp_system_sync(
                    port=self.mcp_port,
                    enable_tunnels=True,
                    enable_ui=True
                )
                
                if self.mcp_system and self.mcp_system.startup_complete:
                    self.mcp_running = True
                    mcp_time = time.time() - mcp_start
                    print(f"✅ MCP System ready in {mcp_time:.2f}s")
                    
                    # Show MCP status
                    status = self.mcp_system.get_startup_status()
                    self._print_mcp_status(status)
                else:
                    print("⚠️ MCP System started with warnings")
            
            # Step 2: Start Spaceship Application
            if SPACESHIP_APP_AVAILABLE:
                print("\n🎯 Starting Spaceship Designer...")
                app_start = time.time()
                
                self.spaceship_app = OptimizedSpaceshipGenerator()
                
                # Integrate MCP system with spaceship app
                if self.mcp_running and self.spaceship_app:
                    print("🔗 Integrating MCP with Spaceship Application...")
                    
                    # Add spaceship-specific MCP handlers
                    self._setup_spaceship_mcp_handlers()
                    
                    # Create UI integration
                    self.session_panel = self.mcp_system.integrate_with_main_app(
                        self.spaceship_app
                    )
                
                self.app_running = True
                app_time = time.time() - app_start
                print(f"✅ Spaceship Designer ready in {app_time:.2f}s")
                
                # Show the main application
                self.spaceship_app.show()
            
            else:
                print("❌ Spaceship Designer not available")
            
            # Final summary
            total_time = time.time() - startup_start
            print(f"\n🎉 INTEGRATED APPLICATION READY!")
            print(f"   Total startup time: {total_time:.2f}s")
            print(f"   Spaceship App: {'✅' if self.app_running else '❌'}")
            print(f"   MCP System: {'✅' if self.mcp_running else '❌'}")
            
            if self.mcp_running:
                mcp_info = self.mcp_system.get_startup_status()
                components = mcp_info.get('components', {})
                mcp_server = components.get('mcp_server', {})
                if mcp_server.get('running'):
                    print(f"   MCP Server: http://localhost:{mcp_server.get('port')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Application startup failed: {e}")
            return False
    
    def _setup_spaceship_mcp_handlers(self):
        """Setup MCP handlers specific to spaceship application"""
        
        def handle_generate_spaceship(command_data):
            """Handle spaceship generation requests from MCP"""
            try:
                if self.spaceship_app:
                    # Trigger spaceship generation
                    self.spaceship_app.generate_spaceship()
                    return {
                        'status': 'success',
                        'message': 'Spaceship generated successfully',
                        'timestamp': time.time()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Spaceship application not available'
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Generation failed: {str(e)}'
                }
        
        def handle_export_spaceship(command_data):
            """Handle spaceship export requests from MCP"""
            try:
                export_format = command_data.get('format', 'stl')
                filename = command_data.get('filename', f'spaceship_{int(time.time())}')
                
                if self.spaceship_app:
                    # Trigger export
                    success = self.spaceship_app.export_mesh(
                        format=export_format,
                        filename=filename
                    )
                    
                    if success:
                        return {
                            'status': 'success',
                            'message': f'Spaceship exported as {filename}.{export_format}',
                            'format': export_format,
                            'filename': filename
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': 'Export failed'
                        }
                else:
                    return {
                        'status': 'error',
                        'message': 'Spaceship application not available'
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Export failed: {str(e)}'
                }
        
        def handle_get_spaceship_status(command_data):
            """Get current spaceship application status"""
            try:
                if self.spaceship_app:
                    # Get current configuration
                    current_config = getattr(self.spaceship_app, 'current_configuration', {})
                    
                    return {
                        'status': 'success',
                        'app_running': self.app_running,
                        'configuration': current_config,
                        'timestamp': time.time()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Spaceship application not available'
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Status check failed: {str(e)}'
                }
        
        def handle_toggle_wireframe(command_data):
            """Toggle wireframe mode in spaceship viewer"""
            try:
                if self.spaceship_app:
                    # Toggle wireframe (simulate 'W' key press)
                    viewer = getattr(self.spaceship_app, 'viewer', None)
                    if viewer:
                        viewer.wireframe_mode = not getattr(viewer, 'wireframe_mode', False)
                        return {
                            'status': 'success',
                            'wireframe_enabled': viewer.wireframe_mode,
                            'message': f"Wireframe {'enabled' if viewer.wireframe_mode else 'disabled'}"
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': 'Viewer not available'
                        }
                else:
                    return {
                        'status': 'error',
                        'message': 'Spaceship application not available'
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Wireframe toggle failed: {str(e)}'
                }
        
        # Register all handlers
        handlers = {
            'generate_spaceship': handle_generate_spaceship,
            'export_spaceship': handle_export_spaceship,
            'get_spaceship_status': handle_get_spaceship_status,
            'toggle_wireframe': handle_toggle_wireframe
        }
        
        for action, handler in handlers.items():
            self.mcp_system.add_custom_mcp_handler(action, handler)
            print(f"   ✅ Registered MCP handler: {action}")
    
    def _print_mcp_status(self, status):
        """Print detailed MCP system status"""
        print("\n📊 MCP SYSTEM STATUS")
        print("=" * 30)
        
        # Overall status
        print(f"Initialized: {'✅' if status.get('initialized') else '❌'}")
        print(f"Startup Complete: {'✅' if status.get('startup_complete') else '❌'}")
        
        # Component status
        components = status.get('components', {})
        
        mcp_server = components.get('mcp_server', {})
        print(f"MCP Server: {'✅' if mcp_server.get('running') else '❌'} " +
              f"(Port: {mcp_server.get('port')})")
        
        tunnel_manager = components.get('tunnel_manager', {})
        print(f"Tunnel Manager: {'✅' if tunnel_manager.get('running') else '❌'} " +
              f"(Tunnels: {tunnel_manager.get('tunnel_count', 0)})")
        
        ui_integration = components.get('ui_integration', {})
        print(f"UI Integration: {'✅' if ui_integration.get('available') else '❌'}")
        
        # Timing information
        timing = status.get('timing', {})
        if timing:
            print("\n⏱️ TIMING:")
            for phase, time_taken in timing.items():
                print(f"   {phase.replace('_', ' ').title()}: {time_taken:.2f}s")
        
        # Errors
        errors = status.get('errors', [])
        if errors:
            print(f"\n⚠️ ERRORS ({len(errors)}):")
            for error in errors:
                print(f"   • {error}")
    
    async def send_test_mcp_commands(self):
        """Send test commands to MCP system"""
        if not self.mcp_running:
            print("❌ MCP system not running, cannot send test commands")
            return
        
        print("\n🧪 Testing MCP Commands...")
        
        test_commands = [
            ('get_spaceship_status', {}),
            ('generate_spaceship', {}),
            ('toggle_wireframe', {}),
            ('export_spaceship', {'format': 'stl', 'filename': 'test_ship'})
        ]
        
        for command, params in test_commands:
            try:
                print(f"   📤 Sending: {command}")
                response = await self.mcp_system.send_mcp_command(command, **params)
                
                if response and response.get('status') == 'success':
                    print(f"   ✅ Response: {response.get('message', 'Success')}")
                else:
                    error_msg = response.get('message') if response else 'No response'
                    print(f"   ❌ Error: {error_msg}")
                
            except Exception as e:
                print(f"   ❌ Command failed: {e}")
            
            # Small delay between commands
            await asyncio.sleep(0.5)
    
    def run_application(self):
        """Run the integrated application"""
        
        # Start the application
        if self.start_application():
            
            # If MCP is running, demonstrate some test commands
            if self.mcp_running:
                print(f"\n🎮 MCP Integration Active")
                print(f"   Available commands:")
                print(f"   • generate_spaceship - Generate new spaceship")
                print(f"   • export_spaceship - Export current spaceship")
                print(f"   • get_spaceship_status - Get app status")
                print(f"   • toggle_wireframe - Toggle wireframe mode")
                print(f"\n   Test with: python -c \"import asyncio; from integrated_spaceship_app import test_mcp_commands; asyncio.run(test_mcp_commands())\"")
            
            # Enter the main event loop if we have a PyQt app
            if self.spaceship_app and hasattr(self.spaceship_app, 'app'):
                print(f"\n🎯 Starting PyQt application...")
                return self.spaceship_app.app.exec()
            else:
                print(f"\n⏳ Application running (no GUI event loop)")
                return 0
        
        else:
            print(f"❌ Application startup failed")
            return 1
    
    def shutdown(self):
        """Shutdown the integrated application"""
        print("\n🛑 Shutting down integrated application...")
        
        # Shutdown MCP system
        if self.mcp_system:
            try:
                # Run shutdown in event loop if available
                if hasattr(self.mcp_system, 'event_loop') and self.mcp_system.event_loop:
                    future = asyncio.run_coroutine_threadsafe(
                        self.mcp_system.shutdown_async(),
                        self.mcp_system.event_loop
                    )
                    future.result(timeout=5.0)
                print("✅ MCP system shutdown complete")
            except Exception as e:
                print(f"⚠️ MCP shutdown error: {e}")
        
        # Close spaceship app
        if self.spaceship_app:
            try:
                if hasattr(self.spaceship_app, 'close'):
                    self.spaceship_app.close()
                print("✅ Spaceship application closed")
            except Exception as e:
                print(f"⚠️ Spaceship app shutdown error: {e}")
        
        print("🏁 Shutdown complete")

async def test_mcp_commands():
    """Test function to demonstrate MCP commands"""
    print("🧪 Testing MCP Commands...")
    
    # This would be called from an external script to test MCP integration
    # For now, just demonstrate the concept
    test_commands = [
        "get_spaceship_status",
        "generate_spaceship", 
        "toggle_wireframe",
        "export_spaceship"
    ]
    
    print("Available MCP commands for testing:")
    for cmd in test_commands:
        print(f"   • {cmd}")

def main():
    """Main entry point for integrated application"""
    
    print("🚀 SPACESHIP DESIGNER WITH MCP INTEGRATION")
    print("=" * 50)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Spaceship Designer with MCP Integration')
    parser.add_argument('--no-mcp', action='store_true', help='Disable MCP integration')
    parser.add_argument('--mcp-port', type=int, default=8765, help='MCP server port')
    parser.add_argument('--test-mcp', action='store_true', help='Run MCP command tests')
    
    args = parser.parse_args()
    
    # Create and run integrated application
    app = IntegratedSpaceshipApp(
        enable_mcp=not args.no_mcp,
        mcp_port=args.mcp_port
    )
    
    try:
        if args.test_mcp:
            # Run MCP tests
            asyncio.run(test_mcp_commands())
            return 0
        else:
            # Run the main application
            return app.run_application()
    
    except KeyboardInterrupt:
        print("\n⚡ Interrupted by user")
        app.shutdown()
        return 0
    
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        app.shutdown()
        return 1

if __name__ == "__main__":
    sys.exit(main())