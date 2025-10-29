# 🤖 AI DEVELOPMENT CYCLE - MANDATORY PROCESS

## ⚠️ CRITICAL: ALL AI AGENTS MUST FOLLOW THIS PROCESS

### 🔄 **Screenshot → Check → Close → Adjust → Repeat**

This is the **ONLY** approved method for AI development iterations.

---

## 🎯 **PRIMARY COMMAND:**

```bash
python ai_development_cycle.py cycle
```

### What This Does Automatically:

1. **🗑️ Clears Old Screenshots** - Removes previous cycle images
2. **🚀 Starts App** - Launches spaceship designer automatically  
3. **📸 Takes Screenshots** - Before/after every interaction
4. **🧪 Tests Functionality** - Buttons, keyboard shortcuts, UI elements
5. **🔚 Closes App** - Automatically terminates after testing
6. **📊 Analyzes Results** - Provides recommendations for fixes
7. **💾 Saves Data** - Current cycle screenshots and test results

---

## 📸 **Screenshot Persistence Rules:**

- ✅ **Screenshots persist** until next cycle starts
- ✅ **AI only analyzes** most recent screenshots (current cycle)
- ✅ **Old screenshots cleared** automatically on new cycle
- ✅ **Latest screenshot command**: `python ai_development_cycle.py latest`

---

## 🔧 **When Functionality Fails:**

1. **Run Cycle**: `python ai_development_cycle.py cycle`
2. **Review Screenshots**: Check `current_iteration_screenshots/`
3. **Check Console Output**: Look for error messages during testing
4. **Update Code**: Fix issues based on visual + console evidence
5. **Repeat Cycle**: Run again until SUCCESS status achieved

---

## 📁 **File Locations:**

- **Screenshots**: `current_iteration_screenshots/` (cleared each cycle)
- **Cycle Data**: `development_cycle.json` (test results + recommendations)
- **Latest Screenshot**: Use `ai_development_cycle.py latest` to see most recent

---

## ✅ **Success Indicators:**

- `🎯 Cycle Status: SUCCESS` (all tests passed)
- `✅ New Random Ship button is working`
- `✅ Keyboard shortcuts are working`
- `✅ N screenshots captured successfully`

## ❌ **Failure Indicators:**

- `🎯 Cycle Status: NEEDS FIXES` 
- `❌ New Random Ship button not working`
- `❌ Keyboard shortcuts not working`
- Error messages in console output

---

## 🚨 **MANDATORY FOR ALL AI AGENTS:**

1. **Always use the automated cycle** - No manual app launching
2. **Always check latest screenshots** - Visual evidence is critical
3. **Always close app after testing** - Automated in cycle system
4. **Always update code based on findings** - Screenshots + console output
5. **Always repeat until SUCCESS** - Don't stop until functionality works

---

## 🎯 **Current Status:**

- ✅ **System Tested**: Automated cycle working perfectly
- ✅ **Screenshots Working**: 5 screenshots captured in test cycle
- ✅ **UI Testing Working**: New ship button + keyboard shortcuts tested
- ✅ **App Control Working**: Automatic start/stop functioning
- ✅ **Ready for Development**: All functionality confirmed

**The automated development cycle system is LIVE and ready for AI-driven iterations!**