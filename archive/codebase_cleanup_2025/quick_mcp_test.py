#!/usr/bin/env python3
"""
Simple MCP Connection Test
Quick test to connect to running MCP server
"""

import requests
import sys
import time

def simple_mcp_test():
    """Quick connection test"""
    mcp_url = "http://localhost:8765"
    
    print("🔍 Quick MCP Connection Test")
    print("-" * 30)
    
    try:
        print("Testing connection to MCP server...")
        response = requests.get(f"{mcp_url}/health", timeout=3)
        
        if response.status_code == 200:
            print("✅ MCP server is running!")
            data = response.json()
            print(f"📡 Status: {data.get('status', 'Unknown')}")
            print(f"🕐 Uptime: {data.get('uptime', 'Unknown')}")
            
            # Test commands
            cmd_response = requests.get(f"{mcp_url}/commands", timeout=3)
            if cmd_response.status_code == 200:
                commands = cmd_response.json().get('commands', [])
                print(f"🎮 Available commands: {len(commands)}")
                for cmd in commands[:3]:  # Show first 3
                    print(f"   • {cmd}")
            
            return True
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect - MCP server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_mcp_test()
    sys.exit(0 if success else 1)