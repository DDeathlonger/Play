#!/usr/bin/env python3
"""
TUNNEL CREATION AND MANAGEMENT MODULE
Secure tunnel management with session persistence and connection monitoring
"""

import asyncio
import json
import time
import socket
import threading
import uuid
import subprocess
import platform
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import hashlib
import ssl
import websockets
import aiohttp

class TunnelType(Enum):
    """Supported tunnel types"""
    HTTP = "http"
    WEBSOCKET = "websocket"
    TCP = "tcp"
    SSH = "ssh"
    SECURE_HTTP = "https"

class TunnelStatus(Enum):
    """Tunnel connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    AUTHENTICATING = "authenticating"

class TunnelConfiguration:
    """Tunnel configuration and settings"""
    
    def __init__(self, 
                 tunnel_type: TunnelType,
                 local_port: int,
                 remote_host: str = "localhost",
                 remote_port: int = None,
                 name: str = None,
                 auto_reconnect: bool = True,
                 max_retries: int = 5,
                 retry_delay: float = 2.0,
                 timeout: float = 30.0,
                 authentication: Dict[str, Any] = None):
        
        self.tunnel_type = tunnel_type
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port or local_port
        self.name = name or f"{tunnel_type.value}_{local_port}"
        self.auto_reconnect = auto_reconnect
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.authentication = authentication or {}
        
        # Generate unique ID
        self.tunnel_id = str(uuid.uuid4())
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'tunnel_id': self.tunnel_id,
            'name': self.name,
            'tunnel_type': self.tunnel_type.value,
            'local_port': self.local_port,
            'remote_host': self.remote_host,
            'remote_port': self.remote_port,
            'auto_reconnect': self.auto_reconnect,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'timeout': self.timeout,
            'created_at': self.created_at.isoformat()
        }

class TunnelConnection:
    """Individual tunnel connection management"""
    
    def __init__(self, config: TunnelConfiguration):
        self.config = config
        self.status = TunnelStatus.DISCONNECTED
        self.connection = None
        self.last_activity = None
        self.connection_attempts = 0
        self.error_count = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
        
        # Events
        self.status_changed = asyncio.Event()
        self.connection_ready = asyncio.Event()
        self.shutdown_requested = asyncio.Event()
        
        # Monitoring
        self.connection_log = []
        self.performance_metrics = {
            'connect_time': 0.0,
            'last_ping': 0.0,
            'avg_response_time': 0.0,
            'uptime': 0.0
        }
    
    async def connect(self) -> bool:
        """Establish tunnel connection"""
        if self.status == TunnelStatus.CONNECTED:
            return True
        
        self._set_status(TunnelStatus.CONNECTING)
        connect_start = time.time()
        
        try:
            if self.config.tunnel_type == TunnelType.HTTP:
                success = await self._connect_http()
            elif self.config.tunnel_type == TunnelType.WEBSOCKET:
                success = await self._connect_websocket()
            elif self.config.tunnel_type == TunnelType.TCP:
                success = await self._connect_tcp()
            elif self.config.tunnel_type == TunnelType.SSH:
                success = await self._connect_ssh()
            else:
                success = False
            
            if success:
                self.performance_metrics['connect_time'] = time.time() - connect_start
                self._set_status(TunnelStatus.CONNECTED)
                self.connection_ready.set()
                self.last_activity = time.time()
                self._log_connection_event("connected", "Successfully established connection")
                return True
            else:
                self._set_status(TunnelStatus.ERROR)
                return False
        
        except Exception as e:
            self._set_status(TunnelStatus.ERROR)
            self._log_connection_event("error", f"Connection failed: {str(e)}")
            return False
    
    async def _connect_http(self) -> bool:
        """Connect HTTP tunnel"""
        try:
            connector = aiohttp.TCPConnector(limit=10)
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            
            self.connection = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            # Test connection
            async with self.connection.get(f"http://{self.config.remote_host}:{self.config.remote_port}/") as response:
                return response.status < 500
        
        except Exception as e:
            print(f"HTTP tunnel error: {e}")
            return False
    
    async def _connect_websocket(self) -> bool:
        """Connect WebSocket tunnel"""
        try:
            uri = f"ws://{self.config.remote_host}:{self.config.remote_port}"
            self.connection = await websockets.connect(
                uri,
                timeout=self.config.timeout
            )
            
            # Send ping to verify
            await self.connection.ping()
            return True
        
        except Exception as e:
            print(f"WebSocket tunnel error: {e}")
            return False
    
    async def _connect_tcp(self) -> bool:
        """Connect TCP tunnel"""
        try:
            reader, writer = await asyncio.open_connection(
                self.config.remote_host,
                self.config.remote_port
            )
            
            self.connection = {'reader': reader, 'writer': writer}
            return True
        
        except Exception as e:
            print(f"TCP tunnel error: {e}")
            return False
    
    async def _connect_ssh(self) -> bool:
        """Connect SSH tunnel (simplified implementation)"""
        try:
            # This would use a proper SSH library in production
            # For now, just simulate SSH tunnel creation
            cmd = [
                'ssh', '-N', '-L',
                f"{self.config.local_port}:{self.config.remote_host}:{self.config.remote_port}",
                f"user@{self.config.remote_host}"
            ]
            
            # In real implementation, use asyncio.create_subprocess_exec
            print(f"SSH tunnel would be created with: {' '.join(cmd)}")
            return True
        
        except Exception as e:
            print(f"SSH tunnel error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect tunnel"""
        self.shutdown_requested.set()
        
        if self.connection:
            try:
                if self.config.tunnel_type == TunnelType.HTTP:
                    await self.connection.close()
                elif self.config.tunnel_type == TunnelType.WEBSOCKET:
                    await self.connection.close()
                elif self.config.tunnel_type == TunnelType.TCP:
                    if 'writer' in self.connection:
                        self.connection['writer'].close()
                        await self.connection['writer'].wait_closed()
            
            except Exception as e:
                print(f"Disconnect error: {e}")
        
        self._set_status(TunnelStatus.DISCONNECTED)
        self.connection_ready.clear()
        self._log_connection_event("disconnected", "Connection closed")
    
    async def send_data(self, data: bytes) -> bool:
        """Send data through tunnel"""
        if self.status != TunnelStatus.CONNECTED:
            return False
        
        try:
            if self.config.tunnel_type == TunnelType.WEBSOCKET and self.connection:
                await self.connection.send(data)
                self.total_bytes_sent += len(data)
                self.last_activity = time.time()
                return True
            elif self.config.tunnel_type == TunnelType.TCP and self.connection:
                self.connection['writer'].write(data)
                await self.connection['writer'].drain()
                self.total_bytes_sent += len(data)
                self.last_activity = time.time()
                return True
        
        except Exception as e:
            print(f"Send data error: {e}")
            return False
        
        return False
    
    async def receive_data(self) -> Optional[bytes]:
        """Receive data from tunnel"""
        if self.status != TunnelStatus.CONNECTED:
            return None
        
        try:
            if self.config.tunnel_type == TunnelType.WEBSOCKET and self.connection:
                data = await self.connection.recv()
                if isinstance(data, str):
                    data = data.encode()
                self.total_bytes_received += len(data)
                self.last_activity = time.time()
                return data
            elif self.config.tunnel_type == TunnelType.TCP and self.connection:
                data = await self.connection['reader'].read(1024)
                self.total_bytes_received += len(data)
                self.last_activity = time.time()
                return data
        
        except Exception as e:
            print(f"Receive data error: {e}")
        
        return None
    
    async def ping(self) -> float:
        """Ping tunnel connection and return response time"""
        if self.status != TunnelStatus.CONNECTED:
            return -1.0
        
        start_time = time.time()
        
        try:
            if self.config.tunnel_type == TunnelType.WEBSOCKET and self.connection:
                pong = await self.connection.ping()
                await pong
                response_time = time.time() - start_time
                self.performance_metrics['last_ping'] = response_time
                return response_time
        
        except Exception as e:
            print(f"Ping error: {e}")
        
        return -1.0
    
    def _set_status(self, status: TunnelStatus):
        """Set connection status and notify listeners"""
        if self.status != status:
            self.status = status
            self.status_changed.set()
            self.status_changed.clear()
    
    def _log_connection_event(self, event_type: str, message: str):
        """Log connection event"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'message': message,
            'status': self.status.value
        }
        
        self.connection_log.append(event)
        
        # Keep only recent events
        if len(self.connection_log) > 100:
            self.connection_log = self.connection_log[-50:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get connection statistics"""
        uptime = 0.0
        if self.status == TunnelStatus.CONNECTED and self.last_activity:
            uptime = time.time() - self.last_activity
        
        return {
            'tunnel_id': self.config.tunnel_id,
            'name': self.config.name,
            'status': self.status.value,
            'uptime': uptime,
            'connection_attempts': self.connection_attempts,
            'error_count': self.error_count,
            'bytes_sent': self.total_bytes_sent,
            'bytes_received': self.total_bytes_received,
            'performance': self.performance_metrics,
            'last_activity': self.last_activity
        }

class TunnelManager:
    """Manage multiple tunnel connections with monitoring and auto-reconnect"""
    
    def __init__(self):
        self.tunnels: Dict[str, TunnelConnection] = {}
        self.is_running = False
        self.monitoring_task = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Statistics
        self.total_connections_created = 0
        self.total_reconnections = 0
        self.manager_start_time = None
    
    async def start_manager(self):
        """Start tunnel manager with monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.manager_start_time = time.time()
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitor_tunnels())
        
        print("🚇 Tunnel Manager started")
    
    async def stop_manager(self):
        """Stop tunnel manager and all connections"""
        self.is_running = False
        
        # Stop monitoring
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect all tunnels
        disconnect_tasks = [
            tunnel.disconnect() 
            for tunnel in self.tunnels.values()
        ]
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)
        
        self.tunnels.clear()
        print("🚇 Tunnel Manager stopped")
    
    async def create_tunnel(self, config: TunnelConfiguration) -> str:
        """Create and start a new tunnel"""
        tunnel = TunnelConnection(config)
        self.tunnels[config.tunnel_id] = tunnel
        self.total_connections_created += 1
        
        # Connect tunnel
        success = await tunnel.connect()
        
        if success:
            self._emit_event('tunnel_connected', {
                'tunnel_id': config.tunnel_id,
                'name': config.name,
                'type': config.tunnel_type.value
            })
        else:
            self._emit_event('tunnel_failed', {
                'tunnel_id': config.tunnel_id,
                'name': config.name,
                'error': 'Failed to establish connection'
            })
        
        return config.tunnel_id
    
    async def remove_tunnel(self, tunnel_id: str) -> bool:
        """Remove and disconnect tunnel"""
        if tunnel_id not in self.tunnels:
            return False
        
        tunnel = self.tunnels[tunnel_id]
        await tunnel.disconnect()
        
        del self.tunnels[tunnel_id]
        
        self._emit_event('tunnel_removed', {
            'tunnel_id': tunnel_id,
            'name': tunnel.config.name
        })
        
        return True
    
    def get_tunnel(self, tunnel_id: str) -> Optional[TunnelConnection]:
        """Get tunnel by ID"""
        return self.tunnels.get(tunnel_id)
    
    def list_tunnels(self) -> List[Dict[str, Any]]:
        """List all tunnels with their status"""
        return [
            tunnel.get_statistics() 
            for tunnel in self.tunnels.values()
        ]
    
    def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive manager statistics"""
        active_tunnels = sum(
            1 for tunnel in self.tunnels.values() 
            if tunnel.status == TunnelStatus.CONNECTED
        )
        
        total_bytes_sent = sum(
            tunnel.total_bytes_sent 
            for tunnel in self.tunnels.values()
        )
        
        total_bytes_received = sum(
            tunnel.total_bytes_received 
            for tunnel in self.tunnels.values()
        )
        
        uptime = time.time() - self.manager_start_time if self.manager_start_time else 0
        
        return {
            'manager_uptime': uptime,
            'total_tunnels': len(self.tunnels),
            'active_tunnels': active_tunnels,
            'total_connections_created': self.total_connections_created,
            'total_reconnections': self.total_reconnections,
            'total_bytes_sent': total_bytes_sent,
            'total_bytes_received': total_bytes_received,
            'tunnels': self.list_tunnels()
        }
    
    async def _monitor_tunnels(self):
        """Monitor tunnel health and handle reconnections"""
        while self.is_running:
            try:
                for tunnel in self.tunnels.values():
                    await self._check_tunnel_health(tunnel)
                
                await asyncio.sleep(5.0)  # Check every 5 seconds
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Tunnel monitoring error: {e}")
                await asyncio.sleep(1.0)
    
    async def _check_tunnel_health(self, tunnel: TunnelConnection):
        """Check individual tunnel health"""
        if tunnel.status == TunnelStatus.CONNECTED:
            # Check if tunnel is responsive
            ping_time = await tunnel.ping()
            
            if ping_time < 0:  # Ping failed
                if tunnel.config.auto_reconnect and tunnel.connection_attempts < tunnel.config.max_retries:
                    await self._reconnect_tunnel(tunnel)
        
        elif tunnel.status == TunnelStatus.ERROR:
            if tunnel.config.auto_reconnect and tunnel.connection_attempts < tunnel.config.max_retries:
                await asyncio.sleep(tunnel.config.retry_delay)
                await self._reconnect_tunnel(tunnel)
    
    async def _reconnect_tunnel(self, tunnel: TunnelConnection):
        """Attempt to reconnect failed tunnel"""
        tunnel.connection_attempts += 1
        tunnel._set_status(TunnelStatus.RECONNECTING)
        
        self._emit_event('tunnel_reconnecting', {
            'tunnel_id': tunnel.config.tunnel_id,
            'attempt': tunnel.connection_attempts
        })
        
        success = await tunnel.connect()
        
        if success:
            self.total_reconnections += 1
            self._emit_event('tunnel_reconnected', {
                'tunnel_id': tunnel.config.tunnel_id,
                'attempt': tunnel.connection_attempts
            })
        else:
            tunnel.error_count += 1
            self._emit_event('tunnel_reconnect_failed', {
                'tunnel_id': tunnel.config.tunnel_id,
                'attempt': tunnel.connection_attempts
            })
    
    def subscribe_to_events(self, event_type: str, handler: Callable):
        """Subscribe to tunnel events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
    
    def unsubscribe_from_events(self, event_type: str, handler: Callable):
        """Unsubscribe from tunnel events"""
        if event_type in self.event_handlers:
            try:
                self.event_handlers[event_type].remove(handler)
            except ValueError:
                pass
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to subscribers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_type, data)
                except Exception as e:
                    print(f"Event handler error: {e}")

# Convenience functions for common tunnel types
async def create_mcp_tunnel(local_port: int = 8765, remote_port: int = 8765) -> TunnelConnection:
    """Create tunnel for MCP server connection"""
    config = TunnelConfiguration(
        tunnel_type=TunnelType.HTTP,
        local_port=local_port,
        remote_port=remote_port,
        name=f"MCP_Tunnel_{local_port}",
        auto_reconnect=True
    )
    
    tunnel = TunnelConnection(config)
    await tunnel.connect()
    return tunnel

async def create_websocket_tunnel(local_port: int, remote_host: str = "localhost") -> TunnelConnection:
    """Create WebSocket tunnel for real-time communication"""
    config = TunnelConfiguration(
        tunnel_type=TunnelType.WEBSOCKET,
        local_port=local_port,
        remote_host=remote_host,
        name=f"WebSocket_Tunnel_{local_port}",
        auto_reconnect=True
    )
    
    tunnel = TunnelConnection(config)
    await tunnel.connect()
    return tunnel