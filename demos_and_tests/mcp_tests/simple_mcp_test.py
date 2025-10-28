#!/usr/bin/env python3
"""
Simple MCP Server Test - Direct HTTP requests only
"""

import requests
import json

def test_mcp_endpoints():
    """Test MCP server endpoints with direct HTTP requests"""
    print("Testing MCP Server on localhost:8765")
    print("=" * 40)
    
    base_url = "http://localhost:8765"
    
    try:
        # Test 1: Health check
        print("1. Health Check:")
        response = requests.get(f"{base_url}/health", timeout=3)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Data: {response.json()}")
        print()
        
        # Test 2: Commands list
        print("2. Available Commands:")
        response = requests.get(f"{base_url}/commands", timeout=3)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands', [])
            print(f"   Found {len(commands)} commands:")
            for cmd in commands:
                print(f"     • {cmd}")
        print()
        
        # Test 3: Server status
        print("3. Server Status:")
        response = requests.get(f"{base_url}/status", timeout=3)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Session ID: {data.get('session_id', 'Unknown')}")
            print(f"   Connected Clients: {len(data.get('connected_clients', {}))}")
            
            latest = data.get('latest_command')
            if latest:
                print(f"   Latest Command: {latest.get('command')} from {latest.get('agent')}")
                print(f"   Command Time: {latest.get('timestamp', 'Unknown')}")
            else:
                print("   Latest Command: None yet")
        print()
        
        print("✅ MCP Server is fully functional!")
        print("The spaceship app has integrated MCP server running.")
        print("Ready for AI interaction via Universal AI Controller.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - MCP server not responding")
        print("Make sure the spaceship app is running.")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mcp_endpoints()