#!/usr/bin/env python3
"""
MCP COMMAND TRACKING DEMONSTRATION
This script sends commands to the running MCP server to demonstrate 
real-time command tracking in the Operations display
"""

import requests
import json
import time
import datetime
from pathlib import Path

def send_mcp_command(command_data, port=8765):
    """Send a command to the MCP server"""
    try:
        url = f"http://localhost:{port}/status"
        response = requests.post(url, 
                               json=command_data, 
                               timeout=5,
                               headers={'Content-Type': 'application/json'})
        
        print(f"✅ Command sent: {command_data['action']}")
        print(f"   Response: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return False

def main():
    print("🚀 MCP COMMAND TRACKING DEMONSTRATION")
    print("="*60)
    print("This will send commands to the running MCP server.")
    print("Watch the 'Operations' section in the app to see commands appear!")
    print("="*60)
    
    # Test commands to demonstrate tracking
    test_commands = [
        {
            "action": "take_screenshot",
            "agent": "demo_ai_1", 
            "reason": "Testing UI visibility",
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": {"location": "main_window", "type": "full"}
        },
        {
            "action": "click_button", 
            "agent": "demo_ai_2",
            "reason": "Generate new spaceship",
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": {"button": "generate", "x": 150, "y": 450}
        },
        {
            "action": "keyboard_input",
            "agent": "demo_ai_3", 
            "reason": "Toggle wireframe mode",
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": {"key": "w", "modifier": None}
        },
        {
            "action": "export_model",
            "agent": "demo_ai_4",
            "reason": "Save current design", 
            "timestamp": datetime.datetime.now().isoformat(),
            "parameters": {"format": "STL", "filename": "test_ship.stl"}
        },
        {
            "action": "analyze_mesh",
            "agent": "demo_ai_5",
            "reason": "Validate mesh quality",
            "timestamp": datetime.datetime.now().isoformat(), 
            "parameters": {"vertices": 424, "faces": 736, "quality": "good"}
        }
    ]
    
    print(f"📡 Sending {len(test_commands)} test commands...")
    print("   👁️ WATCH THE APP'S 'OPERATIONS' DISPLAY!")
    print()
    
    for i, command in enumerate(test_commands, 1):
        print(f"📤 {i}/{len(test_commands)}: {command['action']} from {command['agent']}")
        
        if send_mcp_command(command):
            print(f"   ✅ Command should now appear in Operations display!")
        else:
            print(f"   ❌ Command failed to send")
        
        print(f"   ⏱️ Waiting 3 seconds for visual confirmation...")
        time.sleep(3)
        print()
    
    print("🎯 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("✅ All commands sent to MCP server")
    print("👁️ Check the app's Operations display to see the last 3 commands")
    print("💬 Check the MCP Communication chat for command logs")
    print("🔍 Recent AI Commands should show:")
    for cmd in test_commands[-3:]:
        print(f"   • {cmd['action']} ({cmd['agent']})")
    print("="*60)

if __name__ == "__main__":
    main()