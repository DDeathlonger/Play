#!/usr/bin/env python3
"""
Test coordinate functionality with the fixed code
"""

from universal_ai_controller import UniversalAIController
import subprocess
import sys
import time

def test_coordinate_functionality():
    """Test the coordinate functionality with SECURE CONTAINMENT"""
    
    print("🎯 TESTING COORDINATE FUNCTIONALITY WITH CONTAINMENT")
    print("=" * 60)
    
    # Use secure startup process
    from secure_startup import SecureStartupController
    
    startup_controller = SecureStartupController()
    
    print("🔒 Starting secure contained app...")
    if not startup_controller.run_secure_startup():
        print("❌ Secure startup failed")
        return False
    
    print("✅ App started with full containment")
    
    # Initialize AI controller (MCP server now safe to use)
    controller = UniversalAIController()
    
    # App should already be focused by secure startup
    print("✅ App is contained and focused")
    
    # Take initial screenshot
    initial = controller.see("coordinate_test_initial")
    print(f"📸 Initial state: {initial}")
    
    # Test X coordinate change
    print("\n--- Testing X Coordinate ---")
    controller.click(1450, 200, reason="click_x_coordinate")
    controller.wait(0.5, reason="wait_for_focus")
    controller.press_key('ctrl+a', reason="select_all_x")
    controller.type_text("4", reason="set_x_to_4")
    controller.press_key('enter', reason="confirm_x_change")
    controller.wait(2.0, reason="wait_for_x_coordinate_update")
    
    x_result = controller.see("after_x_coordinate_change")
    print(f"📸 After X change: {x_result}")
    
    # Test Y coordinate change
    print("\n--- Testing Y Coordinate ---")
    controller.click(1450, 240, reason="click_y_coordinate")
    controller.wait(0.5, reason="wait_for_y_focus")
    controller.press_key('ctrl+a', reason="select_all_y")
    controller.type_text("2", reason="set_y_to_2")
    controller.press_key('enter', reason="confirm_y_change")
    controller.wait(2.0, reason="wait_for_y_coordinate_update")
    
    y_result = controller.see("after_y_coordinate_change")
    print(f"📸 After Y change: {y_result}")
    
    # Test Z coordinate change
    print("\n--- Testing Z Coordinate ---")
    controller.click(1450, 280, reason="click_z_coordinate")
    controller.wait(0.5, reason="wait_for_z_focus")
    controller.press_key('ctrl+a', reason="select_all_z")
    controller.type_text("6", reason="set_z_to_6")
    controller.press_key('enter', reason="confirm_z_change")
    controller.wait(2.0, reason="wait_for_z_coordinate_update")
    
    z_result = controller.see("after_z_coordinate_change")
    print(f"📸 After Z change: {z_result}")
    
    # Test Update Module button
    print("\n--- Testing Update Module ---")
    controller.click(1400, 500, reason="click_update_module")
    controller.wait(3.0, reason="wait_for_module_update")
    
    final_result = controller.see("final_coordinate_test_result")
    print(f"📸 Final result: {final_result}")
    
    # Clean up
    startup_controller.shutdown()
    controller.save_session()
    
    print("\n" + "=" * 60)
    print("✅ COORDINATE FUNCTIONALITY TEST COMPLETE WITH CONTAINMENT")
    print("📁 Check ai_sessions/ for screenshots")
    print("🔒 App was fully contained during entire test")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_coordinate_functionality()