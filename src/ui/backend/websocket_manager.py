"""
WebSocket Manager

Manages WebSocket connections for real-time updates in the UI.
Provides real-time notifications, progress updates, and system monitoring.
"""

import json
import logging
import asyncio
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    id: Optional[str] = None


class ConnectionInfo(BaseModel):
    """WebSocket connection information."""
    connection_id: str
    user_id: Optional[str]
    connected_at: datetime
    subscriptions: Set[str]
    last_activity: datetime


class WebSocketManager:
    """
    Manages WebSocket connections and real-time messaging.
    """
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_info: Dict[str, ConnectionInfo] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # topic -> connection_ids
        self.message_queue: Dict[str, List[WebSocketMessage]] = {}  # connection_id -> messages
        
        # Start background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background tasks for WebSocket management."""
        # Cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
        self._background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._background_tasks.discard)
        
        # Heartbeat task
        heartbeat_task = asyncio.create_task(self._send_heartbeat())
        self._background_tasks.add(heartbeat_task)
        heartbeat_task.add_done_callback(self._background_tasks.discard)
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: Optional user ID for the connection
            
        Returns:
            Connection ID
        """
        await websocket.accept()
        
        connection_id = str(uuid4())
        self.active_connections[connection_id] = websocket
        
        connection_info = ConnectionInfo(
            connection_id=connection_id,
            user_id=user_id,
            connected_at=datetime.utcnow(),
            subscriptions=set(),
            last_activity=datetime.utcnow()
        )
        self.connection_info[connection_id] = connection_info
        self.message_queue[connection_id] = []
        
        logger.info(f"WebSocket connection established: {connection_id} (user: {user_id})")
        
        # Send welcome message
        await self.send_to_connection(connection_id, {
            "type": "connection_established",
            "data": {
                "connection_id": connection_id,
                "server_time": datetime.utcnow().isoformat()
            }
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """
        Disconnect a WebSocket connection.
        
        Args:
            connection_id: Connection ID to disconnect
        """
        if connection_id in self.active_connections:
            # Remove from subscriptions
            if connection_id in self.connection_info:
                for topic in self.connection_info[connection_id].subscriptions:
                    if topic in self.subscriptions:
                        self.subscriptions[topic].discard(connection_id)
                        if not self.subscriptions[topic]:
                            del self.subscriptions[topic]
            
            # Clean up
            del self.active_connections[connection_id]
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]
            if connection_id in self.message_queue:
                del self.message_queue[connection_id]
            
            logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def disconnect_all(self):
        """Disconnect all WebSocket connections."""
        connection_ids = list(self.active_connections.keys())
        for connection_id in connection_ids:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket {connection_id}: {e}")
            finally:
                await self.disconnect(connection_id)
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        logger.info("All WebSocket connections closed")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Target connection ID
            message: Message to send
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Connection {connection_id} not found")
            return
        
        try:
            websocket = self.active_connections[connection_id]
            
            # Create message with metadata
            ws_message = WebSocketMessage(
                type=message.get("type", "message"),
                data=message.get("data", {}),
                timestamp=datetime.utcnow(),
                id=str(uuid4())
            )
            
            await websocket.send_text(ws_message.json())
            
            # Update last activity
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket {connection_id} disconnected during send")
            await self.disconnect(connection_id)
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)
    
    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        """
        Broadcast message to all connections subscribed to a topic.
        
        Args:
            topic: Topic to broadcast to
            message: Message to broadcast
        """
        if topic not in self.subscriptions:
            logger.debug(f"No subscribers for topic: {topic}")
            return
        
        connection_ids = list(self.subscriptions[topic])
        
        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)
        
        logger.debug(f"Broadcasted message to {len(connection_ids)} connections on topic: {topic}")
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """
        Broadcast message to all active connections.
        
        Args:
            message: Message to broadcast
        """
        connection_ids = list(self.active_connections.keys())
        
        for connection_id in connection_ids:
            await self.send_to_connection(connection_id, message)
        
        logger.debug(f"Broadcasted message to {len(connection_ids)} connections")
    
    async def subscribe_to_topic(self, connection_id: str, topic: str):
        """
        Subscribe a connection to a topic.
        
        Args:
            connection_id: Connection ID
            topic: Topic to subscribe to
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Connection {connection_id} not found for subscription")
            return
        
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        
        self.subscriptions[topic].add(connection_id)
        
        if connection_id in self.connection_info:
            self.connection_info[connection_id].subscriptions.add(topic)
        
        logger.debug(f"Connection {connection_id} subscribed to topic: {topic}")
        
        # Send confirmation
        await self.send_to_connection(connection_id, {
            "type": "subscription_confirmed",
            "data": {"topic": topic}
        })
    
    async def unsubscribe_from_topic(self, connection_id: str, topic: str):
        """
        Unsubscribe a connection from a topic.
        
        Args:
            connection_id: Connection ID
            topic: Topic to unsubscribe from
        """
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(connection_id)
            if not self.subscriptions[topic]:
                del self.subscriptions[topic]
        
        if connection_id in self.connection_info:
            self.connection_info[connection_id].subscriptions.discard(topic)
        
        logger.debug(f"Connection {connection_id} unsubscribed from topic: {topic}")
        
        # Send confirmation
        await self.send_to_connection(connection_id, {
            "type": "unsubscription_confirmed",
            "data": {"topic": topic}
        })
    
    async def handle_message(self, connection_id: str, message: str):
        """
        Handle incoming message from WebSocket connection.
        
        Args:
            connection_id: Source connection ID
            message: Received message
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_data = data.get("data", {})
            
            if message_type == "subscribe":
                topic = message_data.get("topic")
                if topic:
                    await self.subscribe_to_topic(connection_id, topic)
            
            elif message_type == "unsubscribe":
                topic = message_data.get("topic")
                if topic:
                    await self.unsubscribe_from_topic(connection_id, topic)
            
            elif message_type == "ping":
                await self.send_to_connection(connection_id, {
                    "type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            else:
                logger.warning(f"Unknown message type from {connection_id}: {message_type}")
            
            # Update last activity
            if connection_id in self.connection_info:
                self.connection_info[connection_id].last_activity = datetime.utcnow()
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from connection {connection_id}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {connection_id}: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": sum(len(subs) for subs in self.subscriptions.values()),
            "topics": list(self.subscriptions.keys()),
            "connections_by_topic": {
                topic: len(connections) 
                for topic, connections in self.subscriptions.items()
            }
        }
    
    async def _cleanup_inactive_connections(self):
        """Background task to cleanup inactive connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                inactive_connections = []
                
                for connection_id, info in self.connection_info.items():
                    # Consider connection inactive after 5 minutes of no activity
                    if (current_time - info.last_activity).total_seconds() > 300:
                        inactive_connections.append(connection_id)
                
                for connection_id in inactive_connections:
                    logger.info(f"Cleaning up inactive connection: {connection_id}")
                    await self.disconnect(connection_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def _send_heartbeat(self):
        """Background task to send heartbeat messages."""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if self.active_connections:
                    await self.broadcast_to_all({
                        "type": "heartbeat",
                        "data": {
                            "timestamp": datetime.utcnow().isoformat(),
                            "active_connections": len(self.active_connections)
                        }
                    })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat task: {e}")


# WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket, websocket_manager: WebSocketManager):
    """
    WebSocket endpoint handler.
    
    Args:
        websocket: WebSocket connection
        websocket_manager: WebSocket manager instance
    """
    connection_id = None
    
    try:
        # Accept connection
        connection_id = await websocket_manager.connect(websocket)
        
        # Handle messages
        while True:
            try:
                message = await websocket.receive_text()
                await websocket_manager.handle_message(connection_id, message)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {e}")
                break
    
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {e}")
    
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)


# Utility functions for sending specific types of messages

async def send_extraction_progress(
    websocket_manager: WebSocketManager,
    extraction_id: str,
    progress: float,
    status: str,
    details: Optional[str] = None
):
    """Send extraction progress update."""
    await websocket_manager.broadcast_to_topic("extraction_progress", {
        "type": "extraction_progress",
        "data": {
            "extraction_id": extraction_id,
            "progress": progress,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    })


async def send_system_alert(
    websocket_manager: WebSocketManager,
    alert_type: str,
    severity: str,
    title: str,
    message: str
):
    """Send system alert notification."""
    await websocket_manager.broadcast_to_topic("system_alerts", {
        "type": "system_alert",
        "data": {
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    })


async def send_validation_update(
    websocket_manager: WebSocketManager,
    validation_id: str,
    status: str,
    accuracy: Optional[float] = None,
    feedback: Optional[str] = None
):
    """Send validation update."""
    await websocket_manager.broadcast_to_topic("validation_updates", {
        "type": "validation_update",
        "data": {
            "validation_id": validation_id,
            "status": status,
            "accuracy": accuracy,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
    })

