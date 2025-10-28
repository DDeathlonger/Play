#!/usr/bin/env python3
"""
MCP Client Integration for Maximum Security AI System
Provides secure access to Pylance MCP Server functionality
"""

import json
import subprocess
import sys
import time
import threading
import queue
from pathlib import Path
from datetime import datetime

class SecureMCPClient:
    """Secure MCP client with validation and containment"""
    
    def __init__(self, workspace_root=None):
        self.workspace_root = workspace_root or str(Path.cwd())
        self.session_id = f"mcp_{int(time.time())}"
        self.command_history = []
        self.security_log = []
        
        # Security configuration
        self.allowed_commands = {
            # Safe Pylance commands
            "pylanceWorkspaceRoots": {"risk": "low", "description": "Get workspace roots"},
            "pylanceWorkspaceUserFiles": {"risk": "low", "description": "List user files"},
            "pylanceSettings": {"risk": "low", "description": "Get Pylance settings"},
            "pylancePythonEnvironments": {"risk": "low", "description": "Get Python environments"},
            "pylanceInstalledTopLevelModules": {"risk": "low", "description": "Get installed modules"},
            "pylanceImports": {"risk": "medium", "description": "Analyze imports"},
            "pylanceFileSyntaxErrors": {"risk": "medium", "description": "Check syntax errors"},
            "pylanceSyntaxErrors": {"risk": "medium", "description": "Validate code syntax"},
            "pylanceRunCodeSnippet": {"risk": "high", "description": "Execute code snippet"},
            "pylanceInvokeRefactoring": {"risk": "high", "description": "Apply code refactoring"},
            "pylanceUpdatePythonEnvironment": {"risk": "high", "description": "Change Python environment"}
        }
        
        # Blocked patterns for security
        self.blocked_patterns = [
            "import os", "import sys", "import subprocess", "exec(", "eval(", 
            "__import__", "open(", "file(", "input(", "raw_input(",
            "system(", "popen(", "shell=True"
        ]
        
        self._log_security("MCP_CLIENT_INITIALIZED", {
            "workspace_root": self.workspace_root,
            "allowed_commands": len(self.allowed_commands),
            "security_patterns": len(self.blocked_patterns)
        })
    
    def _log_security(self, event_type, data):
        """Log MCP security events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data
        }
        self.security_log.append(log_entry)
        print(f"🔐 MCP SECURITY: {event_type}")
    
    def _validate_command_security(self, command_name, params):
        """Validate MCP command for security risks"""
        # Check if command is allowed
        if command_name not in self.allowed_commands:
            raise SecurityError(f"MCP command not allowed: {command_name}")
        
        command_info = self.allowed_commands[command_name]
        risk_level = command_info["risk"]
        
        # Additional validation for high-risk commands
        if risk_level == "high":
            if command_name == "pylanceRunCodeSnippet":
                code = params.get("codeSnippet", "")
                self._validate_code_snippet(code)
            
            elif command_name == "pylanceInvokeRefactoring":
                # Limit to safe refactorings
                safe_refactorings = ["source.unusedImports", "source.convertImportFormat", "source.fixAll.pylance"]
                refactoring_name = params.get("name", "")
                if refactoring_name not in safe_refactorings:
                    raise SecurityError(f"Unsafe refactoring: {refactoring_name}")
        
        self._log_security("COMMAND_VALIDATED", {
            "command": command_name,
            "risk_level": risk_level,
            "params_count": len(params)
        })
    
    def _validate_code_snippet(self, code):
        """Validate code snippet for dangerous patterns"""
        if not code:
            return
        
        code_lower = code.lower()
        for pattern in self.blocked_patterns:
            if pattern in code_lower:
                raise SecurityError(f"Dangerous code pattern detected: {pattern}")
        
        # Additional checks
        if len(code) > 10000:  # Limit code size
            raise SecurityError("Code snippet too large")
        
        if code.count('\n') > 100:  # Limit line count
            raise SecurityError("Code snippet has too many lines")
    
    def get_workspace_info(self):
        """Get comprehensive workspace information safely"""
        try:
            self._validate_command_security("pylanceWorkspaceRoots", {})
            
            # Simulate MCP call (in production, use actual MCP client)
            result = {
                "workspace_roots": [self.workspace_root],
                "current_directory": str(Path.cwd()),
                "python_files_count": len(list(Path(self.workspace_root).glob("**/*.py"))),
                "total_files": len(list(Path(self.workspace_root).glob("**/*"))),
                "security_validated": True
            }
            
            self._log_security("WORKSPACE_INFO_RETRIEVED", result)
            return result
            
        except Exception as e:
            self._log_security("WORKSPACE_INFO_ERROR", {"error": str(e)})
            raise
    
    def get_user_files(self):
        """Get list of user Python files safely"""
        try:
            self._validate_command_security("pylanceWorkspaceUserFiles", {
                "workspaceRoot": self.workspace_root
            })
            
            # Get Python files (simulated - in production use actual MCP)
            python_files = []
            for py_file in Path(self.workspace_root).glob("**/*.py"):
                if py_file.is_file():
                    python_files.append({
                        "path": str(py_file),
                        "name": py_file.name,
                        "size": py_file.stat().st_size,
                        "relative_path": str(py_file.relative_to(self.workspace_root))
                    })
            
            result = {
                "files": python_files[:50],  # Limit to first 50 files
                "total_count": len(python_files),
                "workspace_root": self.workspace_root
            }
            
            self._log_security("USER_FILES_RETRIEVED", {
                "file_count": len(python_files),
                "returned_count": len(result["files"])
            })
            
            return result
            
        except Exception as e:
            self._log_security("USER_FILES_ERROR", {"error": str(e)})
            raise
    
    def check_syntax_errors(self, file_path):
        """Check syntax errors in a specific file safely"""
        try:
            # Validate file path is within workspace
            file_path = Path(file_path)
            workspace_path = Path(self.workspace_root)
            
            if not file_path.is_relative_to(workspace_path):
                raise SecurityError(f"File path outside workspace: {file_path}")
            
            self._validate_command_security("pylanceFileSyntaxErrors", {
                "workspaceRoot": self.workspace_root,
                "fileUri": str(file_path)
            })
            
            # Simulate syntax checking (in production use actual MCP)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # Basic Python syntax check
                compile(code, str(file_path), 'exec')
                
                result = {
                    "file_path": str(file_path),
                    "syntax_errors": [],
                    "is_valid": True,
                    "checked_at": datetime.now().isoformat()
                }
                
            except SyntaxError as e:
                result = {
                    "file_path": str(file_path),
                    "syntax_errors": [{
                        "line": e.lineno,
                        "column": e.offset,
                        "message": str(e.msg),
                        "type": "SyntaxError"
                    }],
                    "is_valid": False,
                    "checked_at": datetime.now().isoformat()
                }
            
            self._log_security("SYNTAX_CHECK_COMPLETE", {
                "file_path": str(file_path),
                "is_valid": result["is_valid"],
                "error_count": len(result["syntax_errors"])
            })
            
            return result
            
        except Exception as e:
            self._log_security("SYNTAX_CHECK_ERROR", {"error": str(e)})
            raise
    
    def get_python_environment_info(self):
        """Get Python environment information safely"""
        try:
            self._validate_command_security("pylancePythonEnvironments", {
                "workspaceRoot": self.workspace_root
            })
            
            # Get current Python environment info
            result = {
                "current_python": sys.executable,
                "python_version": sys.version,
                "workspace_root": self.workspace_root,
                "virtual_env": sys.prefix != sys.base_prefix,
                "environment_type": "venv" if sys.prefix != sys.base_prefix else "system"
            }
            
            self._log_security("PYTHON_ENV_INFO", result)
            return result
            
        except Exception as e:
            self._log_security("PYTHON_ENV_ERROR", {"error": str(e)})
            raise
    
    def run_safe_code_snippet(self, code, context="safe_execution"):
        """Run a code snippet with maximum security validation"""
        try:
            # Strict validation for code execution
            self._validate_command_security("pylanceRunCodeSnippet", {
                "codeSnippet": code,
                "workspaceRoot": self.workspace_root
            })
            
            # Additional security for code execution
            if len(code.strip()) == 0:
                raise SecurityError("Empty code snippet")
            
            # Only allow very safe code patterns for demo
            safe_patterns = [
                "print(", "len(", "str(", "int(", "float(",
                "range(", "enumerate(", "zip(", "list(", "dict(",
                "2 + 2", "hello world", "math.", "datetime."
            ]
            
            if not any(pattern in code for pattern in safe_patterns):
                raise SecurityError("Code snippet does not contain recognized safe patterns")
            
            self._log_security("SAFE_CODE_EXECUTION", {
                "code_length": len(code),
                "context": context,
                "security_level": "maximum"
            })
            
            # In production, this would use actual MCP pylanceRunCodeSnippet
            # For now, return simulated result
            result = {
                "executed": True,
                "context": context,
                "code_snippet": code[:100] + "..." if len(code) > 100 else code,
                "security_validated": True,
                "execution_time": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            self._log_security("SAFE_CODE_ERROR", {"error": str(e)})
            raise
    
    def get_security_summary(self):
        """Get comprehensive security summary of MCP operations"""
        return {
            "session_id": self.session_id,
            "workspace_root": self.workspace_root,
            "command_history_count": len(self.command_history),
            "security_events": len(self.security_log),
            "allowed_commands": list(self.allowed_commands.keys()),
            "blocked_patterns": len(self.blocked_patterns),
            "session_duration": time.time() - int(self.session_id.split('_')[1])
        }

class SecurityError(Exception):
    """MCP Security exception"""
    pass

# Example usage and testing functions
def test_mcp_client():
    """Test the secure MCP client functionality"""
    print("🔧 Testing Secure MCP Client...")
    
    client = SecureMCPClient()
    
    try:
        # Test workspace info
        print("\n1️⃣ Testing workspace info...")
        workspace_info = client.get_workspace_info()
        print(f"✅ Workspace info: {workspace_info['python_files_count']} Python files")
        
        # Test user files
        print("\n2️⃣ Testing user files...")
        user_files = client.get_user_files()
        print(f"✅ User files: {user_files['total_count']} files found")
        
        # Test Python environment
        print("\n3️⃣ Testing Python environment...")
        env_info = client.get_python_environment_info()
        print(f"✅ Python environment: {env_info['environment_type']}")
        
        # Test safe code execution
        print("\n4️⃣ Testing safe code execution...")
        safe_code = "print('Hello from secure MCP!')"
        code_result = client.run_safe_code_snippet(safe_code, "security_test")
        print(f"✅ Safe code execution: {code_result['executed']}")
        
        # Test security summary
        print("\n5️⃣ Testing security summary...")
        summary = client.get_security_summary()
        print(f"✅ Security summary: {summary['security_events']} events logged")
        
        print(f"\n🎯 MCP Client test complete - {len(client.security_log)} security events")
        
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")

if __name__ == "__main__":
    test_mcp_client()