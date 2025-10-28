#!/usr/bin/env python3
"""
DIRECT MCP COMMAND TRACKING TEST
Tests MCP command tracking by directly calling the spaceship app's MCP manager
"""

import sys
import time
import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mcp_command_tracking():
    """Test MCP command tracking without HTTP requests"""
    print("🧪 DIRECT MCP COMMAND TRACKING TEST")
    print("="*60)
    
    try:
        # Import the MCP manager
        from spaceship_designer import IntegratedMCPManager
        
        # Create test MCP manager
        mcp_manager = IntegratedMCPManager()
        print("✅ MCP Manager initialized")
        
        # Simulate UI displays (normally connected by app)
        class MockTextEdit:
            def __init__(self, name):
                self.name = name
                self.text = ""
            
            def setText(self, text):
                self.text = text
                print(f"📄 {self.name}: {text}")
            
            def append(self, text):
                self.text += text + "\n"
                print(f"📝 {self.name}: {text}")
        
        # Connect mock UI displays
        mcp_manager.operations_display = MockTextEdit("Operations Display")
        mcp_manager.error_log_display = MockTextEdit("Error Log Display")  
        mcp_manager.chat_display = MockTextEdit("Chat Display")
        
        print("✅ Mock UI displays connected")
        print()
        
        # Test commands
        test_commands = [
            {
                "command": "take_screenshot",
                "agent": "test_ai_1", 
                "reason": "UI testing",
                "parameters": {"location": "main_window"}
            },
            {
                "command": "click_generate",
                "agent": "test_ai_2",
                "reason": "Generate new spaceship", 
                "parameters": {"x": 150, "y": 450}
            },
            {
                "command": "press_key_w",
                "agent": "test_ai_3",
                "reason": "Toggle wireframe",
                "parameters": {"key": "w"}
            },
            {
                "command": "export_stl", 
                "agent": "test_ai_4",
                "reason": "Save design",
                "parameters": {"format": "STL"}
            },
            {
                "command": "analyze_mesh",
                "agent": "test_ai_5", 
                "reason": "Quality check",
                "parameters": {"vertices": 424, "faces": 736}
            }
        ]
        
        print(f"📡 Testing {len(test_commands)} MCP commands...")
        print("   Commands will appear in Operations Display (last 3)")
        print()
        
        for i, cmd_data in enumerate(test_commands, 1):
            print(f"🔄 Test {i}/{len(test_commands)}: {cmd_data['command']}")
            
            # Send command to MCP manager
            mcp_manager.update_latest_command(cmd_data)
            
            print(f"   ✅ Command processed")
            time.sleep(1)
            print()
        
        print("🎯 TEST COMPLETE!")
        print("="*60)
        print("📊 FINAL OPERATIONS DISPLAY STATE:")
        print(mcp_manager.operations_display.text)
        print()
        print(f"📈 Command History: {len(mcp_manager.command_history)} total commands")
        print("🔍 Last 3 commands in operations display:")
        for cmd in mcp_manager.command_history[-3:]:
            action = cmd.get('command', 'unknown')
            agent = cmd.get('agent', 'unknown') 
            time_str = cmd.get('formatted_time', 'unknown')
            print(f"   • {time_str} - {action} ({agent})")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_command_tracking()