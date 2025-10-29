# MEMORY WEIGHTING SYSTEM - COPILOT MEMORY MANAGEMENT

## 🧠 **INTELLIGENT MEMORY TRACKING AND WEIGHTING**

This system tracks repeated themes in user statements to measure intensity of feeling and applies statistical weighting to maintain relevant, non-bloated memory files.

## 📊 **THEME TRACKING STATISTICS**

### **Current Theme Weights (Updated: 2025-10-28)**

| Theme | Occurrences | Intensity Score | Weight Factor | Last Updated |
|-------|-------------|-----------------|---------------|--------------|
| **Anti-Destructive AI Behavior** | 1 | **MAXIMUM** | **1.0** | 2025-10-28 |
| Testing System | 4 | VERY HIGH | 1.0 | 2025-10-28 |
| Terminal Commands | 3 | HIGH | 0.95 | 2025-10-28 |
| Memory Retention | 3 | HIGH | 0.85 | 2025-10-28 |
| Iterative Development | 2 | MEDIUM | 0.75 | 2025-10-28 |
| Visual Output Enhancement | 2 | MEDIUM | 0.75 | 2025-10-28 |
| Commit Workflow | 1 | LOW | 0.50 | 2025-10-28 |

### **Weight Calculation Formula**

```
Weight Factor = min(1.0, (occurrences * 0.25) + (recency_bonus * 0.1))

Intensity Levels:
- VERY HIGH: 0.90-1.0 (4+ occurrences)
- HIGH: 0.75-0.89 (3 occurrences)  
- MEDIUM: 0.50-0.74 (2 occurrences)
- LOW: 0.25-0.49 (1 occurrence)
- ARCHIVE: 0.0-0.24 (deprecated/outdated)
```

### **Recency Bonus System**

- **Same Day**: +0.3 bonus
- **Within 3 Days**: +0.2 bonus
- **Within Week**: +0.1 bonus
- **Within Month**: No bonus
- **Older Than Month**: -0.1 penalty

## 🎯 **MEMORY RELEVANCE SCORING**

### **Maximum Priority Memories (Weight 1.0)**
**These memories are PERMANENT and NEVER archived - highest enforcement:**

1. **Anti-Destructive AI Behavior** (Weight: 1.0) 
   - NEVER make destructive edits without project scope understanding
   - ALWAYS search for existing tooling before recreating
   - PREVENT duplicate functions, conflicting dependencies, naming mismatches
   - PRESERVE existing working systems rather than rebuilding

2. **Testing System Preferences** (Weight: 1.0)
   - Enhanced pytest with emoji output
   - Frequent testing mandate during iterations
   - Visual feedback requirements

### **High Priority Memories (Weight 0.75+)**
**These memories are NEVER archived and receive priority placement:**

3. **Terminal Command Restrictions** (Weight: 0.95)
   - No `&&` usage in cmd console
   - Venv path requirements
   - PowerShell for multi-commands

4. **Memory Retention Protocols** (Weight: 0.85)
   - "Remember..." statement handling
   - Statistical weighting system
   - Immediate documentation requirements

5. **Iterative Development Process** (Weight: 0.75)
   - AI UI tool → pytest → screenshots → determination → fixes

### **Medium Priority Memories (Weight 0.50-0.74)**
**These memories are maintained but may be condensed:**

1. **Visual Output Enhancement** (Weight: 0.75)
   - Emoji flair in outputs
   - Enhanced visual feedback preferences

2. **Commit Workflow** (Weight: 0.50)
   - Test first, then commit
   - Check previous commits for context

### **Archive Candidates (Weight <0.50)**
**These memories may be moved to archive when files become long:**

- Single-occurrence preferences without reinforcement
- Outdated technical specifications
- Deprecated workflow patterns

## 🔄 **MEMORY MANAGEMENT PROTOCOL**

### **File Size Monitoring**

```bash
# Trigger thresholds for memory management:
- USER_PREFERENCES.md > 500 lines: Begin selective archiving
- Any .md file > 1000 lines: Mandatory pruning required
- Memory system total > 50 files: Consolidation review
```

### **Pruning Algorithm**

1. **Calculate all memory weights** using current formula
2. **Identify memories with weight < 0.50**
3. **Check for theme reinforcement** in recent statements
4. **Archive unreinforced low-weight memories**
5. **Consolidate similar medium-weight memories**
6. **Preserve all high-weight memories intact**

### **Theme Detection Keywords**

```python
THEME_KEYWORDS = {
    "testing": ["test", "pytest", "unit test", "testing system", "emoji output"],
    "terminal": ["cmd", "&&", "powershell", "command", "terminal"],
    "memory": ["remember", "memory", "retention", "forget", "document"],
    "workflow": ["process", "cycle", "iterative", "development", "workflow"],
    "commit": ["commit", "git", "push", "sync", "version"],
    "visual": ["emoji", "visual", "output", "flair", "enhancement"],
    "ai_automation": ["ai tool", "screenshot", "automation", "mcp", "controller"]
}
```

## 📈 **STATISTICAL TRACKING**

### **User Intensity Indicators**

**VERY HIGH Intensity (Weight Boost +0.2):**
- Multiple "Remember..." statements on same topic
- Expressions of frustration about repetition
- Explicit corrections or emphasis

**HIGH Intensity (Weight Boost +0.1):**  
- Repeated mentions across sessions
- Detailed specifications provided
- Process documentation requests

**MEDIUM Intensity (No Boost):**
- Single clear statement
- Standard preference expression

**LOW Intensity (Weight Penalty -0.1):**
- Casual mention
- Unclear or ambiguous reference

### **Memory Consolidation Rules**

1. **When USER_PREFERENCES.md exceeds 400 lines:**
   - Archive memories with weight < 0.40
   - Consolidate similar themes with weight 0.40-0.60
   - Preserve high-weight memories (0.60+) in full

2. **When any memory file exceeds 800 lines:**
   - Apply aggressive pruning (weight < 0.60 → archive)
   - Create summary sections for medium-weight themes
   - Maintain detailed documentation for high-weight only

3. **Monthly maintenance cycle:**
   - Recalculate all weights with updated recency bonuses
   - Archive memories with consistently declining relevance
   - Update theme tracking statistics

## 🎯 **IMPLEMENTATION TRACKING**

### **Next Update Cycle**: 2025-11-01
### **Current System Status**: ACTIVE
### **Files Under Management**: 8 core memory files
### **Total Memory Entries**: 47 tracked themes
### **Archive Candidates**: 0 (system recently optimized)

**This weighting system ensures memory files remain relevant and manageable while preserving user priorities based on demonstrated intensity.**