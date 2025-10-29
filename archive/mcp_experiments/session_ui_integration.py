#!/usr/bin/env python3
"""
SESSION MANAGEMENT UI INTEGRATION
Real-time session monitoring and management integrated with the UI system
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QProgressBar, QGroupBox,
                            QListWidget, QListWidgetItem, QTabWidget,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt

from .mcp_async_tools import AsyncMCPServer, NetworkStatusMonitor
from .tunnel_manager import TunnelManager, TunnelConfiguration, TunnelType, TunnelStatus

class SessionStatusWorker(QThread):
    """Worker thread for session status monitoring"""
    
    # Signals for UI updates
    status_updated = pyqtSignal(dict)
    connection_changed = pyqtSignal(str, bool)  # session_id, connected
    performance_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str, str)  # error_type, message
    
    def __init__(self, mcp_server: AsyncMCPServer, tunnel_manager: TunnelManager):
        super().__init__()
        self.mcp_server = mcp_server
        self.tunnel_manager = tunnel_manager
        self.running = False
        self.update_interval = 2.0  # seconds
    
    def run(self):
        """Run status monitoring in background thread"""
        self.running = True
        
        while self.running:
            try:
                # Get MCP server status
                if self.mcp_server:
                    server_status = self.mcp_server.get_server_status()
                    self.status_updated.emit(server_status)
                
                # Get tunnel manager statistics
                if self.tunnel_manager and self.tunnel_manager.is_running:
                    tunnel_stats = self.tunnel_manager.get_manager_statistics()
                    self.performance_updated.emit(tunnel_stats)
                
                # Sleep for update interval
                self.msleep(int(self.update_interval * 1000))
            
            except Exception as e:
                self.error_occurred.emit("monitoring", str(e))
                self.msleep(5000)  # Wait longer after error
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        self.quit()
        self.wait()

class MCPConnectionStatus(QWidget):
    """Widget displaying MCP server connection status"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.server_status = {}
    
    def setup_ui(self):
        """Setup connection status UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🌐 MCP Server Status")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Status indicators
        status_layout = QHBoxLayout()
        
        # Connection indicator
        self.connection_label = QLabel("⚫ Disconnected")
        self.connection_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.connection_label)
        
        # Port information
        self.port_label = QLabel("Port: --")
        status_layout.addWidget(self.port_label)
        
        # Uptime
        self.uptime_label = QLabel("Uptime: --")
        status_layout.addWidget(self.uptime_label)
        
        layout.addLayout(status_layout)
        
        # Performance metrics
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        # Connection count
        self.connections_label = QLabel("Connections: 0")
        perf_layout.addWidget(self.connections_label)
        
        # Network status
        self.network_label = QLabel("Network: Unknown")
        perf_layout.addWidget(self.network_label)
        
        # Last activity
        self.activity_label = QLabel("Last Activity: Never")
        perf_layout.addWidget(self.activity_label)
        
        layout.addWidget(perf_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.restart_button = QPushButton("🔄 Restart Server")
        self.restart_button.clicked.connect(self.restart_server_requested)
        button_layout.addWidget(self.restart_button)
        
        self.ping_button = QPushButton("📡 Ping")
        self.ping_button.clicked.connect(self.ping_server_requested)
        button_layout.addWidget(self.ping_button)
        
        layout.addLayout(button_layout)
    
    def update_status(self, status: Dict[str, Any]):
        """Update display with new status"""
        self.server_status = status
        
        # Connection status
        if status.get('running', False) and status.get('ready', False):
            self.connection_label.setText("🟢 Connected")
            self.connection_label.setStyleSheet("color: green; font-weight: bold;")
        elif status.get('running', False):
            self.connection_label.setText("🟡 Starting")
            self.connection_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.connection_label.setText("🔴 Disconnected")
            self.connection_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Port and uptime
        self.port_label.setText(f"Port: {status.get('port', '--')}")
        
        uptime = status.get('uptime', 0)
        if uptime > 0:
            uptime_str = f"{uptime:.1f}s"
            if uptime > 60:
                uptime_str = f"{uptime/60:.1f}m"
            if uptime > 3600:
                uptime_str = f"{uptime/3600:.1f}h"
            self.uptime_label.setText(f"Uptime: {uptime_str}")
        else:
            self.uptime_label.setText("Uptime: --")
        
        # Performance
        self.connections_label.setText(f"Connections: {status.get('connection_count', 0)}")
        
        # Network status
        network_status = status.get('network_status', {})
        network_health = network_status.get('status', 'unknown')
        network_color = {
            'healthy': 'green',
            'degraded': 'orange', 
            'poor': 'red'
        }.get(network_health, 'gray')
        
        self.network_label.setText(f"Network: {network_health.title()}")
        self.network_label.setStyleSheet(f"color: {network_color};")
        
        # Last activity
        last_activity = status.get('last_activity')
        if last_activity:
            activity_ago = time.time() - last_activity
            if activity_ago < 60:
                activity_str = f"{activity_ago:.0f}s ago"
            else:
                activity_str = f"{activity_ago/60:.1f}m ago"
            self.activity_label.setText(f"Last Activity: {activity_str}")
        else:
            self.activity_label.setText("Last Activity: Never")
    
    def restart_server_requested(self):
        """Signal that server restart was requested"""
        # This would be connected to actual restart logic
        print("🔄 MCP Server restart requested")
    
    def ping_server_requested(self):
        """Signal that server ping was requested"""
        print("📡 MCP Server ping requested")

class TunnelStatusWidget(QWidget):
    """Widget displaying tunnel connection status"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.tunnels = {}
    
    def setup_ui(self):
        """Setup tunnel status UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🚇 Tunnel Connections")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Tunnel list
        self.tunnel_list = QTableWidget()
        self.tunnel_list.setColumnCount(6)
        self.tunnel_list.setHorizontalHeaderLabels([
            "Name", "Type", "Status", "Local Port", "Data Sent", "Data Received"
        ])
        
        # Auto-resize columns
        header = self.tunnel_list.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.tunnel_list)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.add_tunnel_button = QPushButton("➕ Add Tunnel")
        self.add_tunnel_button.clicked.connect(self.add_tunnel_requested)
        button_layout.addWidget(self.add_tunnel_button)
        
        self.remove_tunnel_button = QPushButton("➖ Remove")
        self.remove_tunnel_button.clicked.connect(self.remove_tunnel_requested)
        button_layout.addWidget(self.remove_tunnel_button)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.refresh_requested)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
    
    def update_tunnels(self, tunnel_stats: Dict[str, Any]):
        """Update tunnel display"""
        tunnels = tunnel_stats.get('tunnels', [])
        
        # Update table
        self.tunnel_list.setRowCount(len(tunnels))
        
        for i, tunnel in enumerate(tunnels):
            # Name
            name_item = QTableWidgetItem(tunnel.get('name', 'Unknown'))
            self.tunnel_list.setItem(i, 0, name_item)
            
            # Type (would come from tunnel config)
            type_item = QTableWidgetItem('HTTP')  # Default for now
            self.tunnel_list.setItem(i, 1, type_item)
            
            # Status with color
            status = tunnel.get('status', 'unknown')
            status_item = QTableWidgetItem(status.title())
            
            # Color code status
            if status == 'connected':
                status_item.setBackground(QColor(144, 238, 144))  # Light green
            elif status == 'connecting':
                status_item.setBackground(QColor(255, 255, 0))    # Yellow
            elif status == 'error':
                status_item.setBackground(QColor(255, 182, 193))  # Light red
            
            self.tunnel_list.setItem(i, 2, status_item)
            
            # Local port (would come from config)
            port_item = QTableWidgetItem('8765')  # Default for now
            self.tunnel_list.setItem(i, 3, port_item)
            
            # Data sent
            bytes_sent = tunnel.get('bytes_sent', 0)
            sent_item = QTableWidgetItem(self._format_bytes(bytes_sent))
            self.tunnel_list.setItem(i, 4, sent_item)
            
            # Data received
            bytes_received = tunnel.get('bytes_received', 0)
            received_item = QTableWidgetItem(self._format_bytes(bytes_received))
            self.tunnel_list.setItem(i, 5, received_item)
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes for display"""
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024*1024:
            return f"{bytes_count/1024:.1f} KB"
        else:
            return f"{bytes_count/(1024*1024):.1f} MB"
    
    def add_tunnel_requested(self):
        """Signal to add new tunnel"""
        print("➕ Add tunnel requested")
    
    def remove_tunnel_requested(self):
        """Signal to remove selected tunnel"""
        current_row = self.tunnel_list.currentRow()
        if current_row >= 0:
            print(f"➖ Remove tunnel at row {current_row} requested")
    
    def refresh_requested(self):
        """Signal to refresh tunnel data"""
        print("🔄 Refresh tunnels requested")

class SessionLogWidget(QWidget):
    """Widget for displaying session logs and activities"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.max_log_entries = 1000
    
    def setup_ui(self):
        """Setup log display UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        header = QLabel("📋 Session Logs")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        # Log level filter
        self.filter_button = QPushButton("🔍 Filter")
        header_layout.addWidget(self.filter_button)
        
        # Clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_logs)
        header_layout.addWidget(self.clear_button)
        
        layout.addLayout(header_layout)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier New", 9))
        layout.addWidget(self.log_display)
    
    def add_log_entry(self, level: str, message: str, timestamp: datetime = None):
        """Add log entry to display"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format entry
        time_str = timestamp.strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            'INFO': 'black',
            'WARNING': 'orange', 
            'ERROR': 'red',
            'SUCCESS': 'green',
            'DEBUG': 'gray'
        }
        
        color = colors.get(level.upper(), 'black')
        
        formatted_entry = f'<span style="color: {color};">[{time_str}] {level.upper()}: {message}</span><br>'
        
        # Add to display
        self.log_display.insertHtml(formatted_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Limit entries (simple approach)
        # In a real implementation, you'd want more sophisticated log management
    
    def clear_logs(self):
        """Clear all log entries"""
        self.log_display.clear()

class SessionManagementPanel(QWidget):
    """Main session management panel integrating all components"""
    
    def __init__(self, mcp_server: AsyncMCPServer = None, tunnel_manager: TunnelManager = None):
        super().__init__()
        self.mcp_server = mcp_server
        self.tunnel_manager = tunnel_manager
        self.setup_ui()
        self.setup_monitoring()
    
    def setup_ui(self):
        """Setup main UI layout"""
        layout = QVBoxLayout(self)
        
        # Tab widget for organization
        self.tab_widget = QTabWidget()
        
        # Connection status tab
        self.connection_status = MCPConnectionStatus()
        self.tab_widget.addTab(self.connection_status, "🌐 Server Status")
        
        # Tunnel status tab  
        self.tunnel_status = TunnelStatusWidget()
        self.tab_widget.addTab(self.tunnel_status, "🚇 Tunnels")
        
        # Session logs tab
        self.session_logs = SessionLogWidget()
        self.tab_widget.addTab(self.session_logs, "📋 Logs")
        
        layout.addWidget(self.tab_widget)
        
        # Overall status bar
        status_layout = QHBoxLayout()
        
        self.overall_status = QLabel("🔴 Disconnected")
        self.overall_status.setStyleSheet("font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self.overall_status)
        
        status_layout.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh = QPushButton("🔄 Auto-Refresh: ON")
        self.auto_refresh.setCheckable(True)
        self.auto_refresh.setChecked(True)
        self.auto_refresh.clicked.connect(self.toggle_auto_refresh)
        status_layout.addWidget(self.auto_refresh)
        
        layout.addLayout(status_layout)
    
    def setup_monitoring(self):
        """Setup background monitoring"""
        if self.mcp_server or self.tunnel_manager:
            self.status_worker = SessionStatusWorker(self.mcp_server, self.tunnel_manager)
            
            # Connect signals
            self.status_worker.status_updated.connect(self.update_server_status)
            self.status_worker.performance_updated.connect(self.update_tunnel_status)
            self.status_worker.connection_changed.connect(self.handle_connection_change)
            self.status_worker.error_occurred.connect(self.handle_error)
            
            # Start monitoring
            self.status_worker.start()
            
            self.session_logs.add_log_entry("INFO", "Session monitoring started")
    
    def update_server_status(self, status: Dict[str, Any]):
        """Update server status display"""
        self.connection_status.update_status(status)
        
        # Update overall status
        if status.get('running', False) and status.get('ready', False):
            self.overall_status.setText("🟢 All Systems Operational")
            self.overall_status.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        elif status.get('running', False):
            self.overall_status.setText("🟡 Starting Up")
            self.overall_status.setStyleSheet("color: orange; font-weight: bold; font-size: 14px;")
        else:
            self.overall_status.setText("🔴 Disconnected")
            self.overall_status.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
    
    def update_tunnel_status(self, stats: Dict[str, Any]):
        """Update tunnel status display"""
        self.tunnel_status.update_tunnels(stats)
        
        # Log significant changes
        active_tunnels = stats.get('active_tunnels', 0)
        if hasattr(self, '_last_active_tunnels'):
            if active_tunnels > self._last_active_tunnels:
                self.session_logs.add_log_entry("SUCCESS", f"Tunnel connected (Total: {active_tunnels})")
            elif active_tunnels < self._last_active_tunnels:
                self.session_logs.add_log_entry("WARNING", f"Tunnel disconnected (Total: {active_tunnels})")
        
        self._last_active_tunnels = active_tunnels
    
    def handle_connection_change(self, session_id: str, connected: bool):
        """Handle connection state changes"""
        if connected:
            self.session_logs.add_log_entry("SUCCESS", f"Session {session_id[:8]}... connected")
        else:
            self.session_logs.add_log_entry("WARNING", f"Session {session_id[:8]}... disconnected")
    
    def handle_error(self, error_type: str, message: str):
        """Handle error notifications"""
        self.session_logs.add_log_entry("ERROR", f"{error_type}: {message}")
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh monitoring"""
        if self.auto_refresh.isChecked():
            self.auto_refresh.setText("🔄 Auto-Refresh: ON")
            if hasattr(self, 'status_worker'):
                self.status_worker.start()
            self.session_logs.add_log_entry("INFO", "Auto-refresh enabled")
        else:
            self.auto_refresh.setText("⏸️ Auto-Refresh: OFF")
            if hasattr(self, 'status_worker'):
                self.status_worker.stop()
            self.session_logs.add_log_entry("INFO", "Auto-refresh disabled")
    
    def closeEvent(self, event):
        """Handle widget close"""
        if hasattr(self, 'status_worker'):
            self.status_worker.stop()
        event.accept()

# Integration function for main application
def create_session_management_integration(main_window, mcp_server=None, tunnel_manager=None):
    """Create and integrate session management panel into main application"""
    session_panel = SessionManagementPanel(mcp_server, tunnel_manager)
    
    # Add as a dockable widget or tab
    # This depends on your main window structure
    if hasattr(main_window, 'addDockWidget'):
        from PyQt6.QtWidgets import QDockWidget
        from PyQt6.QtCore import Qt
        
        dock = QDockWidget("Session Management", main_window)
        dock.setWidget(session_panel)
        main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    
    elif hasattr(main_window, 'addTab'):
        main_window.addTab(session_panel, "Session Management")
    
    return session_panel