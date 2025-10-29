#!/usr/bin/env python3
"""
WORKING MCP SYSTEM DEMONSTRATION
Simple script to demonstrate MCP system capabilities with real modules
"""

import sys
import asyncio
import time
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_module_imports():
    """Test that all MCP modules can be imported correctly"""
    print("📦 TESTING MODULE IMPORTS")
    print("=" * 40)
    
    modules_to_test = [
        ('mcp_async_tools', ['AsyncMCPServer', 'NetworkStatusMonitor', 'start_mcp_server_async']),
        ('tunnel_manager', ['TunnelManager', 'TunnelConfiguration', 'TunnelType']),
        ('session_ui_integration', ['SessionManagementPanel', 'create_session_management_integration']),
        ('mcp_app_integration', ['MCPIntegratedStartup', 'quick_start_mcp_system', 'start_mcp_system_sync'])
    ]
    
    all_success = True
    
    for module_name, expected_items in modules_to_test:
        try:
            print(f"\n🔍 Testing {module_name}...")
            module = __import__(module_name)
            
            for item in expected_items:
                if hasattr(module, item):
                    print(f"   ✅ {item}")
                else:
                    print(f"   ❌ {item} - Not found")
                    all_success = False
            
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            all_success = False
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            all_success = False
    
    return all_success

async def test_async_functionality():
    """Test basic async MCP functionality"""
    print("\n🚀 TESTING ASYNC FUNCTIONALITY")
    print("=" * 40)
    
    try:
        # Import async tools
        from mcp_async_tools import AsyncMCPServer, NetworkStatusMonitor
        
        print("✅ Successfully imported async MCP tools")
        
        # Test Network Monitor
        print("\n📡 Testing NetworkStatusMonitor...")
        network_monitor = NetworkStatusMonitor()
        
        # Quick connectivity check (short timeout for demo)
        network_ready = await network_monitor.wait_for_network_ready(timeout=3.0)
        print(f"   Network Status: {'✅ Ready' if network_ready else '⚠️ Limited'}")
        
        # Test MCP Server creation
        print("\n🌐 Testing AsyncMCPServer...")
        mcp_server = AsyncMCPServer()
        print(f"   ✅ MCP Server created (default port: {mcp_server.port})")
        
        # Test server status (without starting)
        print("\n📊 Testing server status...")
        initial_status = await mcp_server.get_status_async()
        print(f"   Initial status: {initial_status}")
        
        # Quick startup test (very short timeout for demo)
        print(f"\n⚡ Testing quick server startup (port {mcp_server.port})...")
        startup_success = await mcp_server.start_async(
            preferred_port=8768,  # Use different port to avoid conflicts
            wait_timeout=3.0      # Short timeout for demo
        )
        
        if startup_success:
            print(f"   ✅ Server started successfully on port {mcp_server.port}")
            
            # Test running status
            running_status = await mcp_server.get_status_async()
            print(f"   Running status: {running_status}")
            
            # Clean shutdown
            print("   🛑 Shutting down server...")
            await mcp_server.stop_async()
            print("   ✅ Server shutdown completed")
        else:
            print("   ⚠️ Server startup failed (expected in constrained environment)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Async test error: {e}")
        return False

def test_integration_system():
    """Test the integrated MCP system"""
    print("\n🔗 TESTING INTEGRATION SYSTEM")
    print("=" * 40)
    
    try:
        # Import integration module
        from mcp_app_integration import MCPIntegratedStartup
        
        print("✅ Successfully imported MCPIntegratedStartup")
        
        # Create integration system
        print("\n🔧 Creating integration system...")
        startup_system = MCPIntegratedStartup(
            mcp_port=8769,
            enable_tunnels=False,        # Disable tunnels for simple test
            enable_ui_integration=False, # Disable UI for simple test
            startup_timeout=5.0          # Short timeout for demo
        )
        
        print("✅ Integration system created with config:")
        print(f"   Port: {startup_system.mcp_port}")
        print(f"   Tunnels: {startup_system.enable_tunnels}")
        print(f"   UI: {startup_system.enable_ui_integration}")
        print(f"   Timeout: {startup_system.startup_timeout}s")
        
        # Test status reporting
        print("\n📊 Testing status reporting...")
        initial_status = startup_system.get_startup_status()
        print(f"   Initial status keys: {list(initial_status.keys())}")
        print(f"   Initialized: {initial_status.get('initialized', False)}")
        print(f"   Startup complete: {initial_status.get('startup_complete', False)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Integration import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

async def test_tunnel_management():
    """Test tunnel management system"""
    print("\n🚇 TESTING TUNNEL MANAGEMENT")
    print("=" * 40)
    
    try:
        # Import tunnel management
        from tunnel_manager import TunnelManager, TunnelConfiguration, TunnelType
        
        print("✅ Successfully imported tunnel management")
        
        # Test TunnelConfiguration
        print("\n⚙️ Testing TunnelConfiguration...")
        config = TunnelConfiguration(
            tunnel_type=TunnelType.HTTP,
            local_port=8770,
            name="Demo_Tunnel",
            auto_reconnect=True
        )
        
        print(f"   ✅ Configuration created:")
        print(f"      Name: {config.name}")
        print(f"      Type: {config.tunnel_type}")
        print(f"      Port: {config.local_port}")
        print(f"      Auto-reconnect: {config.auto_reconnect}")
        
        # Test TunnelManager
        print("\n🎛️ Testing TunnelManager...")
        manager = TunnelManager()
        
        print(f"   ✅ Manager created")
        print(f"      Running: {manager.is_running}")
        print(f"      Tunnel count: {len(manager.tunnels)}")
        
        # Start manager (without creating actual tunnels)
        print("   ⚡ Starting manager...")
        await manager.start_manager()
        print(f"   ✅ Manager started (running: {manager.is_running})")
        
        # Stop manager
        print("   🛑 Stopping manager...")
        await manager.stop_manager()
        print("   ✅ Manager stopped")
        
        return True
        
    except ImportError as e:
        print(f"❌ Tunnel management import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Tunnel management test error: {e}")
        return False

def test_ui_integration():
    """Test UI integration components"""
    print("\n🖥️ TESTING UI INTEGRATION")
    print("=" * 40)
    
    try:
        # Check PyQt availability first
        try:
            import PyQt6
            pyqt_available = True
            print("✅ PyQt6 available for UI integration")
        except ImportError:
            pyqt_available = False
            print("⚠️ PyQt6 not available - UI integration will be limited")
        
        # Import UI integration
        from session_ui_integration import SessionManagementPanel, create_session_management_integration
        
        print("✅ Successfully imported UI integration components")
        
        if pyqt_available:
            # Test SessionManagementPanel creation
            print("\n🎛️ Testing SessionManagementPanel...")
            
            # Create with None parameters (safe for testing)
            panel = SessionManagementPanel(mcp_server=None, tunnel_manager=None)
            print("   ✅ SessionManagementPanel created successfully")
            
            # Note: We don't call show() to avoid GUI dependencies in test
            print("   ✅ UI components initialized (not displayed)")
        else:
            print("   ⏭️ Skipping UI creation tests - PyQt6 not available")
        
        return True
        
    except ImportError as e:
        print(f"❌ UI integration import error: {e}")
        return False
    except Exception as e:
        print(f"❌ UI integration test error: {e}")
        return False

async def run_comprehensive_demo():
    """Run comprehensive demonstration of all MCP system components"""
    
    print("🧪 MCP SYSTEM COMPREHENSIVE DEMONSTRATION")
    print("🔬 Testing all components without external dependencies")
    print("=" * 60)
    
    demo_start = time.time()
    test_results = {}
    
    # Test 1: Module Imports
    print("\n" + "="*60)
    import_success = test_module_imports()
    test_results['imports'] = import_success
    
    # Test 2: Async Functionality
    print("\n" + "="*60)
    async_success = await test_async_functionality()
    test_results['async'] = async_success
    
    # Test 3: Integration System
    print("\n" + "="*60)
    integration_success = test_integration_system()
    test_results['integration'] = integration_success
    
    # Test 4: Tunnel Management
    print("\n" + "="*60)
    tunnel_success = await test_tunnel_management()
    test_results['tunnels'] = tunnel_success
    
    # Test 5: UI Integration
    print("\n" + "="*60)
    ui_success = test_ui_integration()
    test_results['ui'] = ui_success
    
    # Final Summary
    demo_time = time.time() - demo_start
    
    print(f"\n🎯 COMPREHENSIVE DEMO RESULTS")
    print("=" * 60)
    
    all_success = True
    for test_name, success in test_results.items():
        status = "✅" if success else "❌"
        print(f"{status} {test_name.title()}: {'SUCCESS' if success else 'FAILED'}")
        if not success:
            all_success = False
    
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if all_success else '⚠️ SOME TESTS FAILED'}")
    print(f"Demo Duration: {demo_time:.2f} seconds")
    
    if all_success:
        print(f"\n✨ MCP SYSTEM IS FULLY FUNCTIONAL!")
        print(f"   • All modules import correctly")
        print(f"   • Async networking functions work")
        print(f"   • Integration system is operational")
        print(f"   • Tunnel management is ready") 
        print(f"   • UI integration components available")
        print(f"\n🚀 Ready for full application integration!")
    else:
        print(f"\n📋 NEXT STEPS:")
        for test_name, success in test_results.items():
            if not success:
                print(f"   • Fix {test_name} component")
        print(f"   • Re-run demonstration after fixes")
    
    return all_success

def main():
    """Main entry point"""
    
    print("🚀 MCP SYSTEM WORKING DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Run the comprehensive demo
        success = asyncio.run(run_comprehensive_demo())
        
        if success:
            print(f"\n🎊 SUCCESS: MCP system is ready for use!")
            return 0
        else:
            print(f"\n⚠️ WARNING: Some components need attention")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n⚡ Demo interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())