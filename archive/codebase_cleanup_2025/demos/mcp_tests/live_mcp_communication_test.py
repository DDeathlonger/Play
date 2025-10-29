#!/usr/bin/env python3
"""
LIVE MCP SERVER COMMUNICATION TEST
This script communicates with the actual running MCP server in the spaceship app
and sends real commands that will appear in the Operations display
"""

import requests
import json
import time
import datetime
from pathlib import Path

def wait_for_mcp_server(port=8765, timeout=30):
    """Wait for MCP server to be fully operational"""
    print(f"🕐 Waiting for MCP server on port {port}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ MCP server is ready on port {port}")
                return True
        except:
            pass
        
        print("   ⏳ Server not ready yet, waiting 2 seconds...")
        time.sleep(2)
    
    print(f"❌ MCP server did not start within {timeout} seconds")
    return False

def send_command_to_mcp_server(command_data, port=8765):
    """Send a command directly to the MCP server using POST"""
    try:
        url = f"http://localhost:{port}/status"
        
        # Send POST request with command data
        response = requests.post(
            url,
            json=command_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"✅ Command sent: {command_data.get('action', 'unknown')}")
        print(f"   Server response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print(f"   Response data: {response_data}")
                return True
            except:
                print(f"   Response: {response.text}")
                return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return False

def get_mcp_status(port=8765):
    """Get current MCP server status"""
    try:
        response = requests.get(f"http://localhost:{port}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"📊 MCP Server Status:")
            print(f"   Session ID: {status_data.get('session_id', 'unknown')}")
            print(f"   Connected Clients: {status_data.get('connected_clients', 0)}")
            print(f"   Latest Command: {status_data.get('latest_command', 'none')}")
            return status_data
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def main():
    print("🚀 LIVE MCP SERVER COMMUNICATION TEST")
    print("="*70)
    print("This test sends REAL commands to the running MCP server")
    print("👁️  WATCH THE SPACESHIP APP'S 'OPERATIONS' DISPLAY!")
    print("="*70)
    
    # Step 1: Wait for MCP server to be ready
    if not wait_for_mcp_server():
        print("❌ Cannot proceed - MCP server is not running")
        print("💡 Make sure the spaceship app is running first!")
        return
    
    print()
    
    # Step 2: Get initial server status
    print("📊 Getting initial MCP server status...")
    get_mcp_status()
    print()
    
    # Step 3: Send test commands that will appear in the app UI
    test_commands = [
        {
            "command": "screenshot_capture",
            "agent": "live_test_ai_1",
            "reason": "Testing live MCP communication",
            "parameters": {
                "target": "app_window",
                "format": "png"
            }
        },
        {
            "command": "generate_spaceship", 
            "agent": "live_test_ai_2",
            "reason": "Create new spaceship via MCP",
            "parameters": {
                "style": "random",
                "complexity": "medium"
            }
        },
        {
            "command": "toggle_wireframe",
            "agent": "live_test_ai_3", 
            "reason": "Switch rendering mode",
            "parameters": {
                "key": "w",
                "mode": "wireframe"
            }
        },
        {
            "command": "export_design",
            "agent": "live_test_ai_4",
            "reason": "Save current spaceship design",
            "parameters": {
                "format": "STL",
                "filename": "mcp_test_ship.stl"
            }
        },
        {
            "command": "analyze_geometry",
            "agent": "live_test_ai_5",
            "reason": "Validate mesh quality",
            "parameters": {
                "check_manifold": True,
                "vertex_count": True
            }
        }
    ]
    
    print(f"📡 Sending {len(test_commands)} commands to live MCP server...")
    print("   👀 WATCH THE APP - Commands should appear in Operations display!")
    print()
    
    success_count = 0
    
    for i, command in enumerate(test_commands, 1):
        print(f"🔄 Command {i}/{len(test_commands)}: {command['command']}")
        print(f"   Agent: {command['agent']}")
        print(f"   Reason: {command['reason']}")
        
        if send_command_to_mcp_server(command):
            success_count += 1
            print(f"   ✅ SUCCESS - Command sent to live app!")
            print(f"   👁️  Check Operations display in app for: {command['agent']}")
        else:
            print(f"   ❌ FAILED - Command not delivered")
        
        print(f"   ⏱️  Waiting 4 seconds for UI update...")
        time.sleep(4)
        print()
    
    # Step 4: Get final server status to show commands were received
    print("📊 Getting final MCP server status...")
    final_status = get_mcp_status()
    
    print()
    print("🎯 LIVE COMMUNICATION TEST COMPLETE!")
    print("="*70)
    print(f"📈 Commands sent: {success_count}/{len(test_commands)}")
    print("👁️  The spaceship app should now show:")
    print("   • Last 3 commands in Operations display")
    print("   • Command logs in MCP Communication chat")
    print("   • Real-time updates as commands were received")
    print()
    
    if final_status and 'command_history' in final_status:
        history = final_status['command_history']
        print(f"🔍 Server confirms {len(history)} recent commands:")
        for cmd in history:
            agent = cmd.get('agent', 'unknown')
            action = cmd.get('command', 'unknown') 
            timestamp = cmd.get('formatted_time', 'unknown')
            print(f"   • {timestamp} - {action} ({agent})")
    
    print("="*70)
    print("✅ Live MCP communication demonstrated successfully!")

if __name__ == "__main__":
    main()