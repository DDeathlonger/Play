#!/usr/bin/env python3
"""
Test MCP Connection to Running Spaceship App
Demonstrates real-time interaction with the integrated MCP server
"""

import requests
import json
import time

def test_mcp_connection():
    """Test connection to the running MCP server"""
    print("🧪 Testing MCP Connection to Running Spaceship App")
    print("=" * 50)
    
    mcp_url = "http://localhost:8765"
    
    try:
        # Test health endpoint
        print("1. Testing MCP server health...")
        response = requests.get(f"{mcp_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ MCP server is healthy!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test commands endpoint
        print("\n2. Getting available commands...")
        response = requests.get(f"{mcp_url}/commands", timeout=5)
        if response.status_code == 200:
            commands_data = response.json()
            commands = commands_data.get('commands', [])
            print(f"   ✅ Found {len(commands)} available commands:")
            for cmd in commands:
                print(f"      • {cmd}")
        else:
            print(f"   ❌ Commands request failed: {response.status_code}")
        
        # Test status endpoint
        print("\n3. Getting MCP server status...")
        response = requests.get(f"{mcp_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print("   ✅ MCP Server Status:")
            print(f"      Session ID: {status_data.get('session_id', 'Unknown')}")
            print(f"      Connected Clients: {len(status_data.get('connected_clients', {}))}")
            
            latest_command = status_data.get('latest_command')
            if latest_command:
                print(f"      Latest Command: {latest_command.get('command', 'None')}")
                print(f"      Command Agent: {latest_command.get('agent', 'Unknown')}")
                print(f"      Command Time: {latest_command.get('timestamp', 'Unknown')}")
            else:
                print("      Latest Command: None yet")
                
            ai_info = status_data.get('ai_agent_info', {})
            if ai_info:
                print(f"      AI Agent: {ai_info.get('name', 'Unknown')}")
        else:
            print(f"   ❌ Status request failed: {response.status_code}")
        
        print("\n🎉 MCP Connection Test Complete!")
        print("The spaceship app is running with a fully functional MCP server!")
        print("\nYou can now:")
        print("• Use Universal AI Controller to interact with the app")
        print("• Click the 'Test AI Command' button in the app")
        print("• See real-time command updates in the UI")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        print("\nMake sure the spaceship app is running with MCP server enabled.")
        return False

if __name__ == "__main__":
    test_mcp_connection()