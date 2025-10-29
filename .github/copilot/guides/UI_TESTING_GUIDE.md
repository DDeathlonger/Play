# AI Development Testing System

## 🤖 Automated Screenshot → Check → Close → Adjust → Repeat Cycle

This system provides fully automated development iterations with screenshot persistence and UI testing to track functionality and debug issues.

## 🔄 CRITICAL: AI Development Cycle Process

**ALL AI AGENTS MUST USE THIS CYCLE:**

1. **Screenshot** - Capture current UI state automatically
2. **Check** - Test functionality and verify expected behavior  
3. **Close** - Automatically close app after testing
4. **Adjust** - Update code based on findings
5. **Repeat** - Start new cycle until functionality is complete

## Setup Complete ✅

The following components are now installed and ready:

### Core Components:
1. **AI Development Cycle Controller** (`ai_development_cycle.py`) - **PRIMARY TOOL**
2. **UI Testing System** (`src/ui_testing_system.py`) - Screenshots and UI automation
3. **AI Testing Controller** (`src/ai_testing_controller.py`) - Development iteration management  
4. **Development Helper** (`dev_helper.py`) - Simple command interface

### Required Packages Installed:
- `pyautogui` - Screenshot and UI automation
- `pillow` - Image processing
- `pywin32` - Windows window management

## Usage During Development

### 🔥 PRIMARY COMMAND - AI Development Cycle:

```bash
# MAIN COMMAND: Full automated development cycle
python ai_development_cycle.py cycle
```

**This command automatically:**
- Clears old screenshots (new cycle starts fresh)
- Starts app
- Takes screenshots before/after interactions  
- Tests UI functionality (buttons, shortcuts)
- Closes app automatically
- Analyzes results and provides recommendations
- Saves only current cycle screenshots (AI sees latest only)

### Additional Commands:

```bash
# Quick screenshot test
python ai_development_cycle.py screenshot

# Start app only (for manual testing)
python ai_development_cycle.py start

# Close app only  
python ai_development_cycle.py close

# Show latest screenshot for AI analysis
python ai_development_cycle.py latest

# Legacy commands (still available)
python dev_helper.py screenshot
python dev_helper.py test_ui
python dev_helper.py flowcharts
```

### Manual Testing:

```bash
# Direct screenshot capture
python src/ai_testing_controller.py screenshot

# Quick functionality check
python src/ai_testing_controller.py quick

# Full testing session
python src/ai_testing_controller.py full
```

## How It Works

### 🔄 Screenshot Persistence Strategy
- **NEW CYCLE**: Screenshots saved to `current_iteration_screenshots/` 
- **CYCLE START**: Previous screenshots automatically cleared
- **AI ANALYSIS**: AI only looks at most recent screenshots (current cycle only)
- **PERSISTENCE**: Screenshots persist until next app reboot/cycle start
- **FOCUSED CAPTURE**: Automatically detects and crops to spaceship designer window

### Automated Development Cycle
1. **Clear Old Data**: Each new cycle clears previous screenshots
2. **App Launch**: Automatically starts spaceship designer
3. **UI Testing**: Tests buttons, keyboard shortcuts, interactions
4. **Screenshot Capture**: Before/after every interaction  
5. **App Closure**: Automatically closes app after testing
6. **Analysis**: Provides recommendations for next iteration

### UI Interaction Testing
- Simulates button clicks ("New Random Ship", "Update Module", etc.)
- Tests keyboard shortcuts (W, L, R keys)
- Captures before/after states of interactions
- Analyzes visual changes between screenshots

### AI Integration
- Tracks iteration count automatically
- Generates recommendations based on test results
- Saves testing results to `ai_testing_log.json`
- Integrates with flowchart generation

### 🤖 AI Development Workflow Integration

**CRITICAL: All AI agents must follow this workflow:**

1. **Start Development Cycle**: `python ai_development_cycle.py cycle`
2. **Review Latest Screenshots**: AI analyzes most recent images only
3. **Identify Issues**: Based on test results and visual evidence
4. **Update Code**: Make necessary fixes/improvements
5. **Repeat Cycle**: Run again until all functionality works

**Key Rules:**
- ✅ **Always close app** after testing (automated)
- ✅ **Always start fresh** each cycle (screenshots cleared)  
- ✅ **Only analyze latest** screenshots (current cycle only)
- ✅ **Update code based on** visual evidence + test results
- ✅ **Repeat until successful** (all tests pass)

## Screenshot Analysis

The system automatically:
- Captures screenshots at key interaction points
- Compares file sizes to detect visual changes
- Identifies significant UI changes between iterations
- Generates reports with recommendations

## AI Recommendations

Based on test results, the system provides:
- Button functionality status
- 3D interaction status  
- Flowchart alignment check
- Next iteration suggestions

## Files Generated

### During Each Iteration:
- `ui_testing_screenshots/` - All captured screenshots
- `ai_testing_log.json` - Test results and recommendations
- `.github/ai-agents/reference/flowcharts/` - Updated flowcharts

### Log Format:
```json
{
  "current_iteration": 1,
  "timestamp": "2025-10-28T07:26:34",
  "button_tests": {"new_random_ship": {"tested": true}},
  "3d_tests": {"wireframe_mode": {"tested": true}},
  "flowchart_analysis": {"status": "flowcharts_exist"},
  "ai_recommendations": ["✅ All buttons functional"]
}
```

## Integration with AI Development

### When to Use:
- After implementing new features
- Before/after bug fixes  
- During UI layout changes
- When testing user interactions

### AI Benefits:
- Visual confirmation of changes
- Automatic regression testing
- Documentation of development progress
- Data-driven iteration recommendations

## Example Development Session:

```bash
# 1. Start development iteration
python dev_helper.py iterate

# 2. Make code changes to spaceship_designer.py

# 3. Test changes
python dev_helper.py screenshot
python dev_helper.py test_ui

# 4. Review results
# Check ui_testing_screenshots/ folder
# Check ai_testing_log.json recommendations

# 5. Update flowcharts if needed
python dev_helper.py flowcharts
```

## Troubleshooting

### If Screenshots Fail:
- Ensure `pyautogui` is installed: `pip install pyautogui pillow`
- Check Windows permissions for screen capture
- Make sure spaceship app is visible on screen

### If UI Tests Fail:
- Verify app is running: `python main.py`
- Check window focus and visibility
- Review console output for specific errors

### Performance Considerations:
- Screenshots are purged between iterations to save space
- System designed for periodic use during development
- Background monitoring has minimal impact on app performance

## Future Enhancements

Potential additions:
- OCR text recognition for button detection
- Automated performance benchmarking
- Integration with git commits
- Visual diff analysis between screenshots
- Automated bug report generation

---

The system is now ready to assist with AI-driven development iterations by providing automated UI testing and visual feedback!