# Spaceship Designer VS Code Workspace

## Overview
This VS Code workspace provides organized access to the Spaceship Designer project with multiple folder views and integrated development tools.

## Workspace Structure

### Folder Organization
- **Spaceship Designer (Root)** - Main project folder with entry points
- **Source Code** - Core application modules (`src/`)
- **Tests** - Test files and performance benchmarks (`tests/`)
- **Examples** - Demo scripts and usage examples (`examples/`)
- **Exports** - Generated 3D models and configurations (`exports/`)
- **AI Agents** - All AI documentation and context (`.github/ai-agents/`)

## Usage Instructions

### Opening the Workspace
1. **Method 1**: Open in VS Code via File → Open Workspace from File → Select `workspace.code-workspace`
2. **Method 2**: From command line: `code workspace.code-workspace`
3. **Method 3**: Double-click `workspace.code-workspace` file (if VS Code is default)

### Development Tasks
Access via `Ctrl+Shift+P` → "Tasks: Run Task":
- **Run Optimized Spaceship Designer** (Default) - Main application entry point
- **Run Legacy Spaceship App** - Original full-featured version
- **Run Tests** - Execute test suite
- **Export Demo** - Command-line export demonstration
- **Generate Flowcharts** - Create process diagrams
- **Install Dependencies** - Install/update Python packages

### Debug Configurations
Access via `F5` or Debug panel:
- **Spaceship Designer (Optimized)** - Primary optimized application
- **Legacy Spaceship App** - Original version with full features
- **Export Demo** - Command-line export testing
- **Run Tests** - Test suite debugging
- **Generate Flowcharts** - Flowchart generation debugging

## Features

### Integrated Development Environment
- **Python IntelliSense** - Full code completion and analysis
- **Virtual Environment** - Automatic `.venv` activation
- **Code Formatting** - Auto-format with Black on save
- **Linting** - Flake8 integration for code quality
- **Git Integration** - Built-in source control

### Project-Specific Configuration
- **Python Path** - Automatically includes `src/` directory
- **Import Resolution** - Proper module discovery
- **File Associations** - Python, Markdown, JSON support
- **Search Exclusions** - Ignores cache and virtual environment files

### Extension Recommendations
The workspace automatically recommends:
- **Python** - Core Python language support
- **Pylance** - Advanced Python language server
- **GitHub Copilot** - AI-powered coding assistance
- **Black Formatter** - Code formatting
- **Flake8** - Code linting
- **PowerShell** - Windows terminal support

## Quick Start

### 1. Open Workspace
```bash
# From project directory
code .vscode/workspace.code-workspace
```

### 2. Run Application
- **Press F5** → Select "Spaceship Designer (Optimized)"
- **Or press Ctrl+F5** to run without debugging
- **Or use Ctrl+Shift+P** → "Tasks: Run Task" → "Run Optimized Spaceship Designer"

### 3. Develop and Test
- Edit files in the **Source Code** folder
- Use F5 to debug with breakpoints
- Run tests with dedicated task or debug configuration
- Generate documentation with flowchart tasks

## Folder Navigation

### Explorer Panel Structure
```
📁 SPACESHIP DESIGNER (ROOT)
├── main.py                    # 🎯 Main entry point
├── generate_flowcharts.py     # Flowchart generation
├── requirements.txt           # Dependencies
├── README.md                  # Project documentation
└── 📁 .venv/                 # Python virtual environment

📁 SOURCE CODE
├── spaceship_designer.py     # 🚀 Optimized application
├── spaceship_advanced.py     # Legacy version
├── spaceship_utils.py        # Shared utilities
└── __init__.py               # Package initialization

📁 TESTS
├── test_spaceship.py         # Comprehensive test suite
└── performance_test.py       # Performance benchmarks

📁 EXAMPLES  
├── demo_spaceships.py        # Multiple ship examples
└── export_demo.py            # Export demonstration

📁 EXPORTS
├── *.stl, *.glb, *.obj      # 3D model files
├── *_config.json            # Ship configurations
└── *_reference.png          # Visual references

📁 REFERENCES
├── 📁 ai-context/           # AI documentation
├── 📁 flowcharts/           # Process diagrams
└── FILE_STRUCTURE.md        # Organization guide
```

## Troubleshooting

### Common Issues

#### Import Errors
- Ensure Python interpreter is set to `.venv/Scripts/python.exe`
- Verify PYTHONPATH includes both root and `src/` directories
- Use `Ctrl+Shift+P` → "Python: Select Interpreter" if needed

#### Task Failures
- Check that virtual environment is activated
- Verify all dependencies are installed via "Install Dependencies" task
- Ensure working directory is set to project root

#### Debug Issues
- Confirm debug configuration references correct file paths
- Check that PYTHONPATH environment variables are set
- Restart VS Code if IntelliSense isn't working

### Getting Help
1. Check `.github/ai-agents/context/` for project documentation
2. Review `.github/ai-agents/documentation/VSCODE_GUIDE.md` for detailed integration instructions
3. Examine `.github/ai-agents/reference/flowcharts/` for visual process guides
4. Use GitHub Copilot for AI-assisted development

## Performance Notes
The workspace is optimized for:
- Fast file navigation with organized folder structure
- Efficient development with proper Python path configuration
- Quick task execution with pre-configured commands
- Smooth debugging with multiple launch configurations

Ready for productive spaceship design development! 🚀