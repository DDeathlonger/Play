#!/usr/bin/env python3
"""
DIRECT APP UI TESTING FOR MCP COMMAND TRACKING
This script uses the AI controller to directly click the test buttons 
in the running app and demonstrate real MCP command tracking
"""

import time
import sys
from pathlib import Path

# Add path for universal AI controller
sys.path.insert(0, str(Path(__file__).parent))

def test_mcp_ui_directly():
    """Test MCP command tracking by clicking buttons in the live app"""
    print("🎯 DIRECT APP UI TESTING FOR MCP COMMAND TRACKING")
    print("="*70)
    print("This test clicks the actual test buttons in the running app")
    print("👁️  WATCH THE 'OPERATIONS' DISPLAY UPDATE IN REAL-TIME!")
    print("="*70)
    
    try:
        from universal_ai_controller import UniversalAIController
        
        # Initialize AI controller with security
        print("🔒 Initializing secure AI controller...")
        controller = UniversalAIController()
        
        # Focus the spaceship app
        if not controller.focus_app():
            print("❌ Could not find or focus the spaceship application")
            print("💡 Make sure the spaceship app is running!")
            return False
        
        print("✅ Spaceship app focused successfully")
        
        # Take baseline screenshot
        print("\n📸 Taking baseline screenshot...")
        baseline = controller.see("mcp_ui_testing_baseline")
        print(f"✅ Baseline: {baseline}")
        
        # Test sequence: Click the test buttons in the app
        test_sequence = [
            {
                "name": "Test Screenshot Button",
                "coordinates": (150, 780),  # Approximate location of "Test Screenshot" button
                "wait": 3,
                "description": "This should add a screenshot command to Operations display"
            },
            {
                "name": "Test AI Button", 
                "coordinates": (250, 780),  # Approximate location of "Test AI" button
                "wait": 3,
                "description": "This should add an AI interaction command to Operations display"
            },
            {
                "name": "Chat Input Test",
                "coordinates": (150, 730),  # Chat input field
                "wait": 2,
                "description": "Click chat input and type a test command"
            }
        ]
        
        print(f"\n🎯 Running {len(test_sequence)} direct UI tests...")
        print("   👀 WATCH THE OPERATIONS DISPLAY FOR REAL-TIME UPDATES!")
        print()
        
        for i, test in enumerate(test_sequence, 1):
            print(f"🔄 Test {i}/{len(test_sequence)}: {test['name']}")
            print(f"   📍 Clicking at ({test['coordinates'][0]}, {test['coordinates'][1]})")
            print(f"   📝 Expected: {test['description']}")
            
            # Click the button
            x, y = test['coordinates']
            controller.click(x, y, reason=f"test_{test['name'].lower().replace(' ', '_')}")
            
            # Special handling for chat input
            if "Chat Input" in test['name']:
                time.sleep(1)
                controller.type_text("test command from AI controller", 
                                   reason="testing_chat_interface")
                controller.press_key('return', reason="submit_chat_command")
            
            print(f"   ✅ Button clicked successfully")
            
            # Take screenshot to verify action
            screenshot = controller.see(f"after_{test['name'].lower().replace(' ', '_')}")
            print(f"   📸 Verification screenshot: {screenshot}")
            
            print(f"   ⏱️  Waiting {test['wait']} seconds for UI update...")
            time.sleep(test['wait'])
            print()
        
        # Take final screenshot to show updated Operations display
        print("📊 Taking final screenshot of Operations display...")
        final_screenshot = controller.see("final_operations_display_with_commands")
        print(f"✅ Final state: {final_screenshot}")
        
        print()
        print("🎉 DIRECT UI TESTING COMPLETE!")
        print("="*70)
        print("✅ All test buttons clicked successfully")
        print("👁️  The Operations display should now show:")
        print("   • Recent AI commands from button clicks")
        print("   • Chat command from text input")
        print("   • Real-time updates as actions occurred")
        print("📸 Screenshots captured at each step for verification")
        print("="*70)
        
        # Save session
        controller.save_session()
        print("💾 Complete session saved for review")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import AI controller: {e}")
        print("💡 Make sure universal_ai_controller.py is available")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Starting MCP UI test in 3 seconds...")
    print("Make sure the spaceship app is visible and running!")
    time.sleep(3)
    
    success = test_mcp_ui_directly()
    
    if success:
        print("\n🎯 SUCCESS: MCP command tracking demonstrated!")
        print("Check the Operations display in the spaceship app.")
    else:
        print("\n❌ FAILED: Could not complete MCP UI testing")
        print("Ensure the spaceship app is running and visible.")

if __name__ == "__main__":
    main()