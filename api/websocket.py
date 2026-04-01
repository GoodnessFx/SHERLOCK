from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Set
import asyncio
import json
from datetime import datetime
from core.logger import db_logger
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        """
        if not self.active_connections:
            return
            
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                dead_connections.add(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "timestamp": datetime.now().isoformat(),
            "payload": {"message": "Connected to SHERLOCK Live Intelligence Feed"}
        }))
        
        # Keep the connection open and listen for client messages (if any)
        while True:
            # We mostly use this as a unidirectional broadcast, 
            # but we need to receive to detect disconnects.
            data = await websocket.receive_text()
            # Handle heartbeat if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Background task to monitor for new log events and broadcast them
async def log_broadcaster():
    """
    Periodically checks for new entries in the database and broadcasts them via WebSocket.
    """
    last_id = 0
    
    # Initialize last_id to current max log id
    recent_logs = db_logger.get_recent_logs(limit=1)
    if recent_logs:
        last_id = recent_logs[0]["id"]
        
    while True:
        try:
            # Check for new logs
            new_logs = db_logger.get_recent_logs(limit=50)
            if new_logs:
                # Logs are sorted by timestamp DESC, so we need to reverse and filter
                to_broadcast = []
                for log in reversed(new_logs):
                    if log["id"] > last_id:
                        to_broadcast.append(log)
                        last_id = log["id"]
                
                for log in to_broadcast:
                    # Format log for WebSocket broadcast
                    ws_message = {
                        "type": f"log_{log['type'].lower()}",
                        "timestamp": log["timestamp"],
                        "payload": {
                            "level": log["level"],
                            "type": log["type"],
                            "message": log["message"],
                            "data": json.loads(log["payload"]) if log["payload"] else None
                        }
                    }
                    await manager.broadcast(ws_message)
            
            # Sleep briefly to avoid busy waiting
            await asyncio.sleep(1.0)
        except Exception as e:
            logger.error(f"Error in log_broadcaster background task: {e}")
            await asyncio.sleep(5.0)

# The server.py will start the background task.
