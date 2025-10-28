@echo off
REM Spaceship Designer - Open Workspace
REM This script opens the VS Code workspace with proper configuration

echo Opening Spaceship Designer workspace in VS Code...

REM Check if VS Code is in PATH
where code >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo VS Code found, opening workspace...
    code "%~dp0.vscode\workspace.code-workspace"
) else (
    echo VS Code not found in PATH. Attempting to find VS Code installation...
    
    REM Common VS Code installation paths
    if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" (
        echo Found VS Code, opening workspace...
        "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" "%~dp0.vscode\workspace.code-workspace"
    ) else if exist "%PROGRAMFILES%\Microsoft VS Code\Code.exe" (
        echo Found VS Code, opening workspace...
        "%PROGRAMFILES%\Microsoft VS Code\Code.exe" "%~dp0.vscode\workspace.code-workspace"
    ) else (
        echo ERROR: VS Code not found!
        echo Please install VS Code or add it to your PATH.
        echo Alternatively, double-click: .vscode\workspace.code-workspace
        pause
        exit /b 1
    )
)

echo Workspace opened successfully!
echo.
echo Quick Start:
echo - Press F5 to run the Spaceship Designer
echo - Use Ctrl+Shift+P for tasks and commands
echo - Check the References folder for documentation
echo.
pause