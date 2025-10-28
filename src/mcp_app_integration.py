#!/usr/bin/env python3
"""
MCP SERVER INTEGRATION WITH PRIMARY APP STARTUP
Seamless integration of async MCP server, tunnel management, and session monitoring
"""

import asyncio
import sys
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import signal
import atexit

# Core imports
try:
    from .mcp_async_tools import AsyncMCPServer, NetworkStatusMonitor, start_mcp_server_async
    from .tunnel_manager import TunnelManager, TunnelConfiguration, TunnelType, create_mcp_tunnel
    from .session_ui_integration import SessionManagementPanel, create_session_management_integration
except ImportError:
    # Handle relative import issues during testing
    try:
        from src.mcp_async_tools import AsyncMCPServer, NetworkStatusMonitor, start_mcp_server_async
        from src.tunnel_manager import TunnelManager, TunnelConfiguration, TunnelType, create_mcp_tunnel
        from src.session_ui_integration import SessionManagementPanel, create_session_management_integration
    except ImportError as e:
        print(f"⚠️ Import warning: {e}")
        # Define minimal classes for testing
        class AsyncMCPServer:
            def __init__(self): 
                self.is_running = False
            async def start_async(self, port=8765, timeout=30.0): 
                return False
        class TunnelManager:
            def __init__(self): 
                self.is_running = False
            async def start_manager(self): 
                pass
        class SessionManagementPanel:
            def __init__(self, server=None, manager=None): 
                pass

class MCPIntegratedStartup:
    """Manages integrated startup of MCP server, tunnels, and UI components"""
    
    def __init__(self, 
                 mcp_port: int = 8765,
                 enable_tunnels: bool = True,
                 enable_ui_integration: bool = True,
                 startup_timeout: float = 60.0):
        
        self.mcp_port = mcp_port
        self.enable_tunnels = enable_tunnels
        self.enable_ui_integration = enable_ui_integration
        self.startup_timeout = startup_timeout
        
        # Core components
        self.mcp_server: Optional[AsyncMCPServer] = None
        self.tunnel_manager: Optional[TunnelManager] = None
        self.session_panel: Optional[SessionManagementPanel] = None
        
        # State management
        self.is_initialized = False
        self.startup_complete = False
        self.shutdown_requested = False
        
        # Event loop management
        self.event_loop = None
        self.loop_thread = None
        
        # Startup tracking
        self.startup_phases = {
            'network_check': False,
            'mcp_server': False,
            'tunnel_manager': False,
            'ui_integration': False
        }
        
        self.startup_times = {}
        self.startup_errors = []
        
        # Register cleanup handlers
        atexit.register(self.cleanup_on_exit)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        asyncio.create_task(self.shutdown_async())
    
    async def initialize_async(self) -> bool:
        """Initialize all components asynchronously with proper sequencing"""
        if self.is_initialized:
            return True
        
        print("🚀 Starting MCP Integrated System...")
        overall_start = time.time()
        
        try:
            # Phase 1: Network readiness check
            phase_start = time.time()
            print("📡 Phase 1: Checking network connectivity...")
            
            network_monitor = NetworkStatusMonitor()
            network_ready = await network_monitor.wait_for_network_ready(timeout=10.0)
            
            self.startup_times['network_check'] = time.time() - phase_start
            self.startup_phases['network_check'] = network_ready
            
            if network_ready:
                print("✅ Network connectivity confirmed")
            else:
                print("⚠️ Network not fully ready, continuing with limited connectivity")
            
            # Phase 2: MCP Server startup
            phase_start = time.time()
            print(f"🌐 Phase 2: Starting MCP server on port {self.mcp_port}...")
            
            self.mcp_server = AsyncMCPServer()
            mcp_success = await self.mcp_server.start_async(
                preferred_port=self.mcp_port,
                wait_timeout=self.startup_timeout / 3
            )
            
            self.startup_times['mcp_server'] = time.time() - phase_start
            self.startup_phases['mcp_server'] = mcp_success
            
            if mcp_success:
                print(f"✅ MCP server ready on http://localhost:{self.mcp_server.port}")
            else:
                print("❌ MCP server startup failed")
                self.startup_errors.append("MCP server failed to start")
            
            # Phase 3: Tunnel Manager (if enabled)
            if self.enable_tunnels:
                phase_start = time.time()
                print("🚇 Phase 3: Initializing tunnel manager...")
                
                self.tunnel_manager = TunnelManager()
                await self.tunnel_manager.start_manager()
                
                # Create default MCP tunnel if server is running
                if mcp_success:
                    try:
                        tunnel_config = TunnelConfiguration(
                            tunnel_type=TunnelType.HTTP,
                            local_port=self.mcp_server.port,
                            name="MCP_Default_Tunnel",
                            auto_reconnect=True
                        )
                        
                        await self.tunnel_manager.create_tunnel(tunnel_config)
                        print("✅ Default MCP tunnel created")
                    except Exception as e:
                        print(f"⚠️ Default tunnel creation failed: {e}")
                
                self.startup_times['tunnel_manager'] = time.time() - phase_start
                self.startup_phases['tunnel_manager'] = True
                print("✅ Tunnel manager operational")
            else:
                print("⏭️ Tunnel management disabled")
                self.startup_phases['tunnel_manager'] = True
            
            # Phase 4: UI Integration (if enabled and PyQt available)
            if self.enable_ui_integration:
                phase_start = time.time()
                print("🖥️ Phase 4: Setting up UI integration...")
                
                try:
                    import PyQt6
                    
                    self.session_panel = SessionManagementPanel(
                        mcp_server=self.mcp_server,
                        tunnel_manager=self.tunnel_manager
                    )
                    
                    self.startup_times['ui_integration'] = time.time() - phase_start
                    self.startup_phases['ui_integration'] = True
                    print("✅ Session management UI ready")
                
                except ImportError:
                    print("⚠️ PyQt6 not available, UI integration disabled")
                    self.startup_phases['ui_integration'] = False
                except Exception as e:
                    print(f"⚠️ UI integration error: {e}")
                    self.startup_phases['ui_integration'] = False
                    self.startup_errors.append(f"UI integration failed: {e}")
            else:
                print("⏭️ UI integration disabled")
                self.startup_phases['ui_integration'] = True
            
            # Final validation
            total_time = time.time() - overall_start
            critical_phases = ['mcp_server']  # Only MCP server is truly critical
            
            critical_success = all(
                self.startup_phases[phase] 
                for phase in critical_phases
            )
            
            self.is_initialized = True
            self.startup_complete = critical_success
            
            if critical_success:
                print(f"🎉 MCP Integrated System ready! (Total: {total_time:.2f}s)")
                self._print_startup_summary()
                return True
            else:
                print(f"⚠️ System partially ready with errors (Total: {total_time:.2f}s)")
                self._print_startup_summary()
                return False
        
        except Exception as e:
            print(f"❌ Critical startup error: {e}")
            self.startup_errors.append(f"Critical error: {e}")
            return False
    
    def initialize_sync(self) -> bool:
        """Initialize synchronously by running async initialization in thread"""
        if self.is_initialized:
            return True
        
        # Create event loop in separate thread
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        # Wait for loop to be ready
        timeout = 5.0
        start_time = time.time()
        while self.event_loop is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if self.event_loop is None:
            print("❌ Failed to create event loop")
            return False
        
        # Run initialization
        future = asyncio.run_coroutine_threadsafe(
            self.initialize_async(), 
            self.event_loop
        )
        
        try:
            return future.result(timeout=self.startup_timeout)
        except Exception as e:
            print(f"❌ Sync initialization failed: {e}")
            return False
    
    def _run_event_loop(self):
        """Run event loop in dedicated thread"""
        try:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()
        except Exception as e:
            print(f"Event loop error: {e}")
        finally:
            if self.event_loop:
                self.event_loop.close()
    
    def get_startup_status(self) -> Dict[str, Any]:
        """Get comprehensive startup status"""
        return {
            'initialized': self.is_initialized,
            'startup_complete': self.startup_complete,
            'phases': self.startup_phases.copy(),
            'timing': self.startup_times.copy(),
            'errors': self.startup_errors.copy(),
            'components': {
                'mcp_server': {
                    'available': self.mcp_server is not None,
                    'running': self.mcp_server.is_running if self.mcp_server else False,
                    'port': self.mcp_server.port if self.mcp_server else None
                },
                'tunnel_manager': {
                    'available': self.tunnel_manager is not None,
                    'running': self.tunnel_manager.is_running if self.tunnel_manager else False,
                    'tunnel_count': len(self.tunnel_manager.tunnels) if self.tunnel_manager else 0
                },
                'ui_integration': {
                    'available': self.session_panel is not None
                }
            }
        }
    
    def _print_startup_summary(self):
        """Print detailed startup summary"""
        print("\n📊 STARTUP SUMMARY")
        print("=" * 40)
        
        for phase, success in self.startup_phases.items():
            timing = self.startup_times.get(phase, 0)
            status = "✅" if success else "❌"
            print(f"{status} {phase.replace('_', ' ').title()}: {timing:.2f}s")
        
        if self.startup_errors:
            print(f"\n⚠️ Errors ({len(self.startup_errors)}):")
            for error in self.startup_errors:
                print(f"  • {error}")
        
        total_time = sum(self.startup_times.values())
        print(f"\nTotal initialization time: {total_time:.2f}s")
    
    async def shutdown_async(self):
        """Shutdown all components gracefully"""
        if self.shutdown_requested:
            return
        
        self.shutdown_requested = True
        print("🛑 Starting graceful shutdown...")
        
        # Shutdown in reverse order of startup
        if self.tunnel_manager:
            try:
                print("🚇 Stopping tunnel manager...")
                await self.tunnel_manager.stop_manager()
            except Exception as e:
                print(f"Tunnel manager shutdown error: {e}")
        
        if self.mcp_server:
            try:
                print("🌐 Stopping MCP server...")
                await self.mcp_server.stop_async()
            except Exception as e:
                print(f"MCP server shutdown error: {e}")
        
        if self.session_panel:
            try:
                print("🖥️ Closing session UI...")
                # UI cleanup would happen here
            except Exception as e:
                print(f"UI shutdown error: {e}")
        
        print("✅ Shutdown complete")
    
    def cleanup_on_exit(self):
        """Cleanup when process exits"""
        if not self.shutdown_requested and self.is_initialized:
            print("\n🧹 Emergency cleanup on exit...")
            
            if self.event_loop and not self.event_loop.is_closed():
                try:
                    # Schedule shutdown in the event loop
                    future = asyncio.run_coroutine_threadsafe(
                        self.shutdown_async(), 
                        self.event_loop
                    )
                    future.result(timeout=5.0)
                except Exception as e:
                    print(f"Emergency cleanup error: {e}")
    
    def integrate_with_main_app(self, main_app_window=None):
        """Integrate session management with main application window"""
        if not self.session_panel:
            print("⚠️ No session panel available for integration")
            return None
        
        if main_app_window:
            try:
                return create_session_management_integration(
                    main_app_window,
                    self.mcp_server,
                    self.tunnel_manager
                )
            except Exception as e:
                print(f"App integration error: {e}")
                return None
        
        return self.session_panel
    
    async def wait_for_ready(self, timeout: float = None) -> bool:
        """Wait for system to be fully ready"""
        if timeout is None:
            timeout = self.startup_timeout
        
        start_time = time.time()
        
        while not self.startup_complete and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.5)
        
        return self.startup_complete
    
    def add_custom_mcp_handler(self, action: str, handler: Callable):
        """Add custom MCP command handler"""
        if self.mcp_server:
            self.mcp_server.register_handler(action, handler)
            print(f"✅ Registered MCP handler: {action}")
        else:
            print("⚠️ MCP server not available for handler registration")
    
    async def send_mcp_command(self, action: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Send command to MCP server"""
        if self.mcp_server and self.mcp_server.is_running:
            return await self.mcp_server.send_command_async(action, **kwargs)
        return None

# Convenience functions for main application integration

async def quick_start_mcp_system(port: int = 8765, 
                                enable_tunnels: bool = True,
                                enable_ui: bool = True) -> MCPIntegratedStartup:
    """Quick start MCP system with default configuration"""
    system = MCPIntegratedStartup(
        mcp_port=port,
        enable_tunnels=enable_tunnels,
        enable_ui_integration=enable_ui
    )
    
    success = await system.initialize_async()
    
    if success:
        print("🚀 MCP system ready for use!")
    else:
        print("⚠️ MCP system started with warnings")
    
    return system

def start_mcp_system_sync(port: int = 8765,
                         enable_tunnels: bool = True,
                         enable_ui: bool = True) -> MCPIntegratedStartup:
    """Start MCP system synchronously (for non-async applications)"""
    system = MCPIntegratedStartup(
        mcp_port=port,
        enable_tunnels=enable_tunnels,
        enable_ui_integration=enable_ui
    )
    
    success = system.initialize_sync()
    
    if success:
        print("🚀 MCP system ready!")
    else:
        print("⚠️ MCP system started with warnings")
    
    return system

def integrate_mcp_with_spaceship_app(spaceship_app_window):
    """Specific integration for spaceship designer application"""
    
    # Start MCP system
    mcp_system = start_mcp_system_sync(
        port=8765,
        enable_tunnels=True,
        enable_ui=True
    )
    
    # Add spaceship-specific handlers
    def handle_generate_ship(command_data):
        """Handle ship generation requests from MCP"""
        return {
            'status': 'success',
            'message': 'Ship generation requested',
            'timestamp': time.time()
        }
    
    def handle_export_ship(command_data):
        """Handle ship export requests from MCP"""
        return {
            'status': 'success', 
            'message': 'Ship export requested',
            'format': command_data.get('format', 'stl')
        }
    
    mcp_system.add_custom_mcp_handler('generate_ship', handle_generate_ship)
    mcp_system.add_custom_mcp_handler('export_ship', handle_export_ship)
    
    # Integrate UI
    session_panel = mcp_system.integrate_with_main_app(spaceship_app_window)
    
    return mcp_system, session_panel

# Example usage and testing
if __name__ == "__main__":
    async def test_mcp_system():
        """Test the MCP system startup"""
        print("🧪 Testing MCP Integrated System...")
        
        system = MCPIntegratedStartup(
            mcp_port=8765,
            enable_tunnels=True,
            enable_ui_integration=False  # Disable UI for testing
        )
        
        success = await system.initialize_async()
        
        if success:
            print("✅ Test successful!")
            
            # Test MCP command
            response = await system.send_mcp_command('ping')
            print(f"Ping response: {response}")
            
            # Show status
            status = system.get_startup_status()
            print(f"System status: {status}")
        
        # Cleanup
        await system.shutdown_async()
    
    # Run test
    asyncio.run(test_mcp_system())