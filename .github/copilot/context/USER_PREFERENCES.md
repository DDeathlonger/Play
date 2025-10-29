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

**2025-10-28**: **MEMORY TRACKING AND WEIGHTING SYSTEM**  
User Statement: "next, in the memory system, the ai should track the number of repeated occurances in themes to reflect the users' intensity of feeling and the ai should then use these tracked statistics to weigh the weight and relevancy of the memories. (this is to ensure the memory files never get too long or bloated)"

**ESTABLISHED MEMORY WEIGHTING PROTOCOL:**
1. **Track repeated theme occurrences** to measure user intensity
2. **Use statistical weighting** based on repetition frequency
3. **Apply relevancy scoring** using tracked statistics
4. **Prevent memory file bloat** through intelligent pruning
5. **Maintain high-priority memories** based on user emphasis patterns
6. **Archive low-weight memories** when files become too long

**2025-10-28**: **CRITICAL - DESTRUCTIVE AI BEHAVIOR PREVENTION**  
User Statement: "well to update some of my most annoying things with ai is unnecessarily destructive or dismissive edits or outright deletion, with no regard to the large scope of the project as a whole, already likely containing the necessary tooling as ai would otherwise just try to recreate for the 5th time in a row. ultimately leading to bloat and confusing projects. mismatching naming conventions, directories, duplicate functions, conflicting functions, duplicate dependancies, conflicting dependancies, and so many more common issues I fight with ai over so often because ai usually fails to consider the larger context without taking forever or losing track of focus."

**CRITICAL ANTI-DESTRUCTIVE PROTOCOLS (WEIGHT: 1.0 - MAXIMUM PRIORITY):**
1. **NEVER make destructive edits** without understanding project scope
2. **ALWAYS check for existing tooling** before recreating functionality
3. **MAINTAIN consistent naming conventions** across entire project
4. **PREVENT duplicate functions** by searching codebase first
5. **AVOID conflicting dependencies** by checking existing requirements
6. **CONSIDER larger context** before making ANY significant changes
7. **PRESERVE existing working systems** rather than rebuilding
8. **RESEARCH project structure** thoroughly before proposing changes

**2025-10-28**: **"BACK TO FRONT" DEVELOPMENT METHODOLOGY**  
User Statement: "If so, before jumping into flash, couldn't you generate a location in the project for html and css files, then ensure they are hosted on the existing mcp server? You could even keep restricted JS scripts in the control panel designated directory... before you got creating files, you should make sure you consider before you ever create a new feature, you should reflect on the existing project architecture, framework, systems, and blend the new features in to the existing app in an already predesignated location, all associated dependencies the feature may rely on, including other related scripts, should always be closely grouped with one another. Then you should always go through the standard entry point systematically to figure out the most logical place to start adding new features (Features aka components)"

**ESTABLISHED "BACK TO FRONT" WORKFLOW (WEIGHT: 1.0 - MAXIMUM PRIORITY):**
1. **USE existing MCP server infrastructure** - never create separate web servers
2. **REFLECT on existing architecture** before creating any new features
3. **BLEND new features into existing app** at predesignated locations
4. **GROUP related dependencies** and scripts closely together
5. **WORK through standard entry point systematically** to find logical integration points
6. **COMPARTMENTALIZE components** based on functional relationships and dependencies
7. **FOLLOW "back to front" methodology** - familiarize with structure deeply, then work systematically from beginning towards goal

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

**2025-10-28**: **MODULAR ARCHITECTURE DESIGN PRINCIPLES**  
User Statement: "User mandated 'back to front' methodology requiring existing architecture analysis before new component creation. User emphasized modular design, abstractions, rigidity, comprehensive testing, and avoiding destructive changes to existing functionality."

**ESTABLISHED MODULAR DESIGN PRINCIPLES:**
1. **ALWAYS analyze existing architecture** before creating new components
2. **USE modular design patterns** with clear abstractions
3. **IMPLEMENT rigid structural boundaries** between components  
4. **REQUIRE comprehensive testing** for all new functionality
5. **AVOID destructive changes** to existing working systems
6. **FOLLOW service-oriented architecture** patterns where applicable

**2025-10-28**: **MCP SERVER INTEGRATION MANDATE**  
User Statement: "User mandated using existing MCP server infrastructure and proper component compartmentalization rather than creating separate web servers."

**ESTABLISHED MCP INTEGRATION REQUIREMENTS:**
1. **ALWAYS use existing MCP server** at localhost:8765
2. **NEVER create separate web servers** - integrate with existing infrastructure
3. **IMPLEMENT proper service registration** using modular patterns
4. **MAINTAIN backward compatibility** with existing AI controller endpoints
5. **USE thread-safe service registry** for dynamic endpoint routing
6. **FOLLOW singleton patterns** for core server components

**2025-10-28**: **WEB INTERFACE DEVELOPMENT STANDARDS**  
User Statement: "Complete web interface with tabs for viewing/editing/visualization. Modern responsive design with file tree, markdown editor, search functionality."

**ESTABLISHED WEB INTERFACE REQUIREMENTS:**
1. **CREATE responsive tabbed interfaces** for complex functionality
2. **IMPLEMENT file tree navigation** for document management
3. **PROVIDE markdown editing capabilities** with syntax highlighting
4. **INCLUDE search functionality** across document collections
5. **USE modern CSS3 design patterns** with dark themes
6. **MAINTAIN accessibility standards** in web components

**2025-10-28**: **PYTEST ENHANCEMENT AND TESTING MANDATES**  
User Statement: "Enhanced pytest system with emoji output and comprehensive visual feedback. 80% pass rate target with core functionality validated."

**ESTABLISHED TESTING STANDARDS:**
1. **USE enhanced pytest with emoji reporters** for visual feedback
2. **MAINTAIN 80%+ pass rate** as minimum acceptable standard
3. **IMPLEMENT comprehensive test coverage** for new components
4. **VALIDATE core functionality** through end-to-end testing
5. **USE visual feedback systems** for rapid issue identification
6. **AUTOMATE test execution** during development iterations

**2025-10-28**: **ZERO TOLERANCE FOR FILE CREATION WITHOUT INTEGRATION**  
User Statement: "Successfully identified that modular components were created but never integrated with existing application. Critical importance of actual integration testing beyond component-level validation."

**CRITICAL INTEGRATION REQUIREMENTS (WEIGHT: 1.0 - MAXIMUM PRIORITY):**
1. **NEVER create components without integration** into existing systems
2. **ALWAYS verify actual functionality** beyond unit tests
3. **REQUIRE end-to-end validation** of new features
4. **MODIFY existing entry points** to use new modular components
5. **TEST complete workflows** rather than isolated functionality
6. **ENSURE seamless replacement** of legacy systems with new modular ones

**2025-10-28**: **COMPREHENSIVE CRASH RESOLUTION SUCCESS**  
User Statement: "Test Screenshot and Test Command buttons do not crash it anymore. Memory endpoint returns proper HTML content. Memory/files shows complete file listing with 36 files. Rate limiting, mouse boundary checking, and command logging working."

**PROVEN WORKING SYSTEMS (WEIGHT: 1.0 - MAXIMUM PRIORITY):**
1. **UI Test buttons fully functional** - No more AttributeError crashes
2. **MCP Server integration complete** - Both Legacy AI and Memory services registered
3. **Path routing fixed** - Longest-match algorithm and relative path handling working
4. **Web interface operational** - AI Memory Control Panel serving complete HTML
5. **Security features active** - Rate limiting (30 commands/minute), mouse boundary validation, command logging
6. **API endpoints functional** - /memory, /memory/files, /services all working correctly

**2025-10-28**: **EXTERNAL COMMAND CRASH PATTERN IDENTIFIED**  
User Statement: "App runs completely stable until external MCP commands are sent. The UI buttons work fine. Only crashes when API requests sent from PowerShell/external sources."

**CRITICAL DEBUGGING REQUIREMENTS (WEIGHT: 1.0 - MAXIMUM PRIORITY):**
1. **NEVER claim completion without testing** - Must validate every endpoint systematically
2. **DISTINGUISH internal vs external command processing** - Different thread/security handling
3. **EXECUTE full iterative development cycles** - AI tool → pytest → screenshots → fixes
4. **RESOLVE thread safety issues** in external command handling
5. **MAINTAIN internal button functionality** while fixing external API crashes
6. **VALIDATE all security features** without causing instability

### **New Preferences Added:**
- 2025-10-28: Terminal command restrictions  
- 2025-10-28: Testing system usage priority
- 2025-10-28: Memory retention mandate
- 2025-10-28: Visual output enhancement preference
- 2025-10-28: Modular architecture design principles
- 2025-10-28: MCP server integration mandate
- 2025-10-28: Web interface development standards  
- 2025-10-28: Pytest enhancement and testing mandates
- 2025-10-28: Zero tolerance for file creation without integration

This file must be updated immediately whenever new user preferences or "remember" statements are made.