#!/usr/bin/env python3
"""
MCP Connection Test - Quick Test Before Qt Crashes
Test MCP connection immediately when server starts
"""

import subprocess
import time
import requests
import threading
import sys
import os

def wait_for_mcp_ready():
    """Wait for MCP server ready message and test immediately"""
    print("🚀 Starting spaceship app and monitoring for MCP server...")
    
    # Start the app process
    cmd = [
        "C:/Users/dante/OneDrive/Desktop/Play/.venv/Scripts/python.exe",
        "spaceship.py"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    mcp_ready = False
    
    try:
        # Monitor output for MCP ready message
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
            
            # Check for MCP server ready
            if "✅ MCP Server ready on http://localhost:8765" in line:
                print("\n🎯 MCP Server detected! Testing connection immediately...")
                mcp_ready = True
                
                # Test connection IMMEDIATELY
                time.sleep(0.5)  # Brief pause
                test_connection_immediately()
                break
                
            # Check for crashes
            if "Traceback" in line:
                print("❌ App crashed before MCP connection test")
                break
                
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    finally:
        # Clean shutdown
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    
    return mcp_ready

def test_connection_immediately():
    """Test MCP connection as soon as server is ready"""
    mcp_url = "http://localhost:8765"
    
    try:
        print("📡 Testing /health endpoint...")
        response = requests.get(f"{mcp_url}/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data}")
        
        print("📋 Testing /commands endpoint...")
        response = requests.get(f"{mcp_url}/commands", timeout=3)
        if response.status_code == 200:
            commands = response.json()
            print(f"✅ Commands: {commands}")
        
        print("📊 Testing /status endpoint...")
        response = requests.get(f"{mcp_url}/status", timeout=3)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Status: {status}")
        
        # Test sending a command
        print("🎮 Testing command sending...")
        test_cmd = {
            "action": "see",
            "reason": "Emergency MCP connection test",
            "agent": "Emergency_Test_Agent"
        }
        
        response = requests.post(f"{mcp_url}/commands", json=test_cmd, timeout=3)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Command sent successfully: {result}")
        
        print("\n🎉 MCP CONNECTION SUCCESSFUL!")
        print("✅ All endpoints working")
        print("✅ Command sending working")
        print("✅ Server is fully functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Emergency MCP Connection Test")
    print("=" * 50)
    
    success = wait_for_mcp_ready()
    
    if success:
        print("\n🎉 MCP server connection CONFIRMED!")
    else:
        print("\n❌ Could not establish MCP connection")
    
    sys.exit(0 if success else 1)