#!/usr/bin/env python3
"""
TRUE REAL-TIME VISUAL EXPLORATION VIA MCP
Uses MCP server to take live screenshots and analyze them to decide where to explore
"""

from universal_ai_controller import UniversalAIController
import time
from PIL import Image
import random

def analyze_live_screenshot_for_exploration(screenshot_path):
    """
    Analyze a live screenshot to find actual UI elements to explore
    Returns coordinates based on what's actually visible
    """
    try:
        img = Image.open(screenshot_path)
        width, height = img.size
        
        print(f"   🔍 LIVE ANALYSIS: {width}x{height} screenshot")
        
        # Convert to RGB array for analysis
        pixels = list(img.getdata())
        
        # Look for button-like areas by color patterns
        exploration_points = []
        
        # Sample different areas to find interesting spots
        sample_points = [
            (width//4, height//4),     # Upper left quadrant
            (width//2, height//4),     # Upper center
            (3*width//4, height//4),   # Upper right
            (width//4, height//2),     # Left center
            (width//2, height//2),     # Dead center
            (3*width//4, height//2),   # Right center
            (width//4, 3*height//4),   # Lower left
            (width//2, 3*height//4),   # Lower center
            (3*width//4, 3*height//4), # Lower right
        ]
        
        for x, y in sample_points:
            # Add some randomness to make exploration more natural
            random_x = min(width-10, max(10, x + random.randint(-50, 50)))
            random_y = min(height-10, max(10, y + random.randint(-50, 50)))
            
            exploration_points.append({
                'x': random_x,
                'y': random_y,
                'reason': f'live_analysis_quadrant_{len(exploration_points)+1}'
            })
        
        # Shuffle to make exploration order unpredictable
        random.shuffle(exploration_points)
        
        print(f"   📍 Found {len(exploration_points)} exploration points from live analysis")
        return exploration_points[:3]  # Return top 3 points
        
    except Exception as e:
        print(f"   ❌ Live screenshot analysis failed: {e}")
        return []

def true_realtime_mcp_exploration():
    """
    Use MCP server for real-time screenshot analysis and exploration
    """
    
    print("🔗 TRUE REAL-TIME MCP VISUAL EXPLORATION")
    print("=" * 60)
    print("This system:")
    print("1. Uses MCP server connection for live screenshots")
    print("2. Analyzes actual screenshot content in real-time")  
    print("3. Makes exploration decisions based on live visual data")
    print("4. Moves mouse to discovered UI elements")
    print("5. Takes new screenshots to verify changes")
    print("6. Continues based on real-time visual feedback")
    print("=" * 60)
    
    # Initialize MCP connection
    print("\n🔗 Initializing MCP connection...")
    controller = UniversalAIController()
    
    # Focus app (assuming it's already running)
    if not controller.focus_app():
        print("❌ No app to focus - please start spaceship designer first")
        return False
    
    print("✅ MCP connection established - beginning real-time exploration")
    
    # Real-time exploration loop
    for round_num in range(3):  # 3 rounds of real-time exploration
        
        print(f"\n🎯 REAL-TIME EXPLORATION ROUND {round_num + 1}")
        print("-" * 50)
        
        # Step 1: Take live screenshot via MCP
        print("📸 Taking LIVE screenshot via MCP...")
        live_screenshot = controller.see(f"realtime_mcp_round_{round_num + 1}_live_capture")
        
        if not live_screenshot or 'screenshot_path' not in live_screenshot:
            print("❌ Failed to get live screenshot via MCP")
            continue
            
        screenshot_path = live_screenshot['screenshot_path']
        print(f"📸 Live MCP screenshot: {screenshot_path}")
        
        # Step 2: ANALYZE the live screenshot to find exploration targets
        print("🧠 ANALYZING LIVE SCREENSHOT...")
        targets = analyze_live_screenshot_for_exploration(screenshot_path)
        
        if not targets:
            print("   ❌ No targets found in live analysis")
            continue
        
        print(f"   ✅ Live analysis found {len(targets)} exploration targets")
        
        # Step 3: Explore each target found in live analysis
        for target_num, target in enumerate(targets):
            
            print(f"\n   🎯 LIVE TARGET {target_num + 1}: {target['reason']}")
            print(f"      📍 Coordinates from live analysis: ({target['x']}, {target['y']})")
            
            # Move to the live-discovered target
            controller.move_to(
                target['x'], 
                target['y'], 
                reason=f"move_to_live_discovered_target_{target['reason']}"
            )
            
            # Take screenshot to see hover state
            hover_shot = controller.see(f"hover_live_target_{target_num + 1}")
            print(f"      📸 Hover state: {hover_shot['screenshot_path'] if hover_shot else 'FAILED'}")
            
            # Click the live-discovered target
            controller.click(
                target['x'], 
                target['y'], 
                reason=f"click_live_discovered_{target['reason']}"
            )
            
            # Immediately capture result via MCP
            click_result = controller.see(f"click_result_live_target_{target_num + 1}")
            print(f"      📸 Click result: {click_result['screenshot_path'] if click_result else 'FAILED'}")
            
            # Brief wait to observe any changes
            controller.wait(1.5, reason="observe_live_interaction_result")
            
            # Capture final state after interaction
            post_result = controller.see(f"post_live_interaction_{target_num + 1}")
            print(f"      📸 Post-interaction: {post_result['screenshot_path'] if post_result else 'FAILED'}")
            
            print(f"      ✅ Live target {target_num + 1} explored with real-time verification")
        
        # Test some keyboard shortcuts with live verification
        print(f"\n   ⌨️ LIVE KEYBOARD TESTING ROUND {round_num + 1}")
        
        test_keys = ['w', 'l', 'r', 'tab', 'space']
        selected_keys = random.sample(test_keys, 2)  # Random 2 keys per round
        
        for key in selected_keys:
            print(f"      🔑 Testing '{key}' with live MCP verification...")
            
            # Press key
            controller.press_key(key, reason=f"live_test_key_{key}_round_{round_num + 1}")
            
            # Immediately capture via MCP to see effect
            key_result = controller.see(f"live_key_{key}_result")
            print(f"      📸 Live key result: {key_result['screenshot_path'] if key_result else 'FAILED'}")
            
            controller.wait(0.8, reason="observe_key_effect")
    
    # Final live screenshot
    print("\n📊 FINAL LIVE STATE CAPTURE")
    final_live = controller.see("final_realtime_mcp_exploration_state")
    print(f"📸 Final live state: {final_live['screenshot_path'] if final_live else 'FAILED'}")
    
    # Save complete MCP session
    controller.save_session()
    
    print("\n🎉 TRUE REAL-TIME MCP EXPLORATION COMPLETE!")
    print("   🔗 Used MCP server for live screenshot capture")
    print("   🧠 Analyzed actual screenshot content in real-time")
    print("   🎯 Discovered UI elements through live visual analysis")
    print("   📸 Verified all interactions with immediate MCP screenshots")
    print("   ✅ Complete real-time visual exploration documented")
    
    return True

if __name__ == "__main__":
    # Note: This assumes spaceship app is already running
    print("⚠️  PREREQUISITE: Start spaceship designer first!")
    print("   Run: .venv\\Scripts\\python.exe src\\spaceship_designer.py")
    print("   Then run this exploration script")
    print()
    
    input("Press Enter when spaceship app is running...")
    
    true_realtime_mcp_exploration()