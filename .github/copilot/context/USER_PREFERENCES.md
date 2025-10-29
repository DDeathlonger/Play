# USER PREFERENCES - COPILOT MEMORY SYSTEM

## 🎯 **CRITICAL USER PREFERENCES**

This file contains all user preferences and statements that must be remembered to avoid repetition and confusion looping.

## 💻 **TERMINAL AND COMMAND EXECUTION**

### **Command Execution Restrictions**
**Date**: October 28, 2025  
**User Statement**: "AI cannot use '&&' in the cmd console, all commands should be first via the venv option, or PowerShell, unless it is one cmd command, one at a time is acceptable."

**Action Required**:
- ❌ **NEVER use `&&`** in cmd console  
- ✅ **Use venv Python path**: `C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe`
- ✅ **Use PowerShell** for multi-command sequences
- ✅ **Single cmd commands** acceptable in cmd console one at a time
- ✅ **Prefer PowerShell** for complex operations

**Examples**:
```bash
# ❌ WRONG (cmd with &&)
cd src && python spaceship.py

# ✅ CORRECT (separate commands)  
cd src
python spaceship.py

# ✅ CORRECT (venv path)
C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe spaceship.py

# ✅ CORRECT (PowerShell)
cd src; C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe spaceship.py
```

## 🧪 **TESTING AND DEVELOPMENT**

### **Testing System Usage Priority**
**Date**: October 28, 2025  
**Context**: Enhanced Pytest Testing System implementation

**User Expectations**:
- **Use testing system frequently** throughout iterations for debugging
- **Update tests automatically** when corruption or issues detected
- **Run comprehensive tests** before and after major changes  
- **Leverage visual feedback** for rapid issue identification and resolution

**Required Actions**:
```bash
# Use this command frequently for debugging
C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe -m pytest tests\ -v

# Always verify after fixes
C:\Users\dante\OneDrive\Desktop\Play\.venv\Scripts\python.exe -m pytest tests\test_spaceship.py -v
```

## 📚 **DOCUMENTATION AND MEMORY SYSTEM**

### **CoPilot Memory System References**
**Date**: October 28, 2025
**Official Names**: 
- **"CoPilot Memory System"** (official name)
- **"AI Memory System"** (colloquial)  
- **"Memory System"** (short form)

**System Purpose**:
- Maintain all .md files in `.github/copilot/` structure
- Serve as comprehensive AI agent instruction system
- Prevent information repetition and confusion loops
- Enable consistent AI behavior across sessions

### **Memory Retention Mandate**
**Date**: October 28, 2025
**User Requirement**: "If I EVER say ANYTHING SIMILAR to 'Remember...', 'I've already said before....', or similar sentiment, I expect the following statement to be retained in the memory system as to avoid repeated annoyances or confusion looping."

**Trigger Phrases**:
- "Remember..."
- "I've already said before..."  
- "You should know this..."
- "I told you earlier..."
- "We discussed this..."
- "As I mentioned..."
- Any expression of frustration about repeating information

**Required Response**: Immediate retention of the statement in appropriate CoPilot Memory System file.

### **RETAINED STATEMENTS (Memory Log)**

**2025-10-28**: **ITERATIVE DEVELOPMENT CYCLE PROCESS**  
User Statement: "Remember all AI should remember the correct usage of the iterative dev cycle should be including all previously mentioned processes such as in the ai ui automated tool thingy, and how to check the app, you then execute the unit tests and the pytests, whichever is done faster can be first, you then compare screenshots if the new ones are available, then you determine what to do and what might need fixed to accomplish the user's requests."

**ESTABLISHED MANDATORY PROCESS ORDER:**
1. **Use AI UI automated tool** (true_intelligent_demo.py) to check the app
2. **Execute unit tests AND pytests** (whichever completes first can run first)
3. **Compare screenshots** (if new ones available from AI tool)
4. **Determine actions needed** based on all results
5. **Fix issues identified** to accomplish user requests

**2025-10-28**: **COMMIT WORKFLOW PROCESS**  
User Statement: "Now please remember all ai's should, when I ask you to commit it, note that this implies a notable version and you should always (so another expected workflow here...) run at least the most basic and fastest test, if it shows decent success, I want you to then commit the current project as it is with a generated short summary of the changes made since previous git commits... You should at least briefly check the last one or two commits titles and perhaps contents briefly if you need additional context for the commit message. Lastly you should always sync it and attempt to use the flowchart tool if it works. then wait for additional instructions"

**ESTABLISHED MANDATORY COMMIT WORKFLOW:**
1. **Run most basic and fastest test** first
2. **If decent success** → proceed with commit process
3. **Generate short summary** of changes since previous git commits
4. **Check last 1-2 commit titles and contents** briefly for context
5. **Commit current project** with generated summary
6. **Sync/push changes** to repository
7. **Attempt to use flowchart tool** if it works
8. **Wait for additional instructions** after completion

## 🎨 **USER INTERFACE AND VISUAL PREFERENCES**

### **Enhanced Visual Output**
**Date**: October 28, 2025
**User Request**: "can you adjust the visual output to have more of that emoji flair you add to logs a lot without interfering in the normal pytest functionality"

**Preference**: User enjoys and wants emoji enhancement in visual outputs while maintaining functionality.

**Implementation**: Enhanced pytest configuration with emoji reporters and visual flair added successfully.

## 🔄 **DEVELOPMENT WORKFLOW PREFERENCES**

### **Systematic Approach**
**Pattern Observed**: User prefers systematic, step-by-step approaches with clear explanations of:
- What will be done
- Why it's being done  
- Expected outcomes
- Verification steps

### **Documentation First**
**Pattern Observed**: User values comprehensive documentation and expects:
- Updates to memory system when changes occur
- Clear cross-references between related information
- Systematic organization of information
- Retention of important decisions and preferences

## ⚠️ **CRITICAL REMINDERS**

### **Always Check This File**
Before taking any significant action, AI agents must:
1. **Review this file** for relevant preferences
2. **Apply stated preferences** without asking for clarification
3. **Update this file** when new preferences are stated
4. **Reference previous decisions** when relevant

### **Never Repeat Information**
If information is documented in this file:
- ❌ **Don't ask for clarification** on documented preferences
- ❌ **Don't repeat questions** about documented decisions  
- ✅ **Apply preferences automatically**
- ✅ **Reference previous context** when relevant

## 📈 **PREFERENCE EVOLUTION**

### **New Preferences Added:**
- 2025-10-28: Terminal command restrictions  
- 2025-10-28: Testing system usage priority
- 2025-10-28: Memory retention mandate
- 2025-10-28: Visual output enhancement preference

This file must be updated immediately whenever new user preferences or "remember" statements are made.