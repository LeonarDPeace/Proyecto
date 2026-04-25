"""WebSocket — Chat en Tiempo Real (Sprint 4 — HU 6.1).

Maneja conexiones WebSocket por sala de negociación.
Los mensajes se persisten en la BD a través del negotiation_service.
"""

import json
import logging
import uuid
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.services import negotiation_service
from app.services.auth_service import get_user_by_id

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Gestiona conexiones WebSocket activas por sala de negociación."""

    def __init__(self):
        # negotiation_id -> list of (user_id, websocket)
        self.active_connections: dict[str, list[tuple[str, WebSocket]]] = defaultdict(
            list
        )

    async def connect(
        self, websocket: WebSocket, negotiation_id: str, user_id: str
    ) -> None:
        """Acepta y registra una conexión WebSocket en una sala."""
        await websocket.accept()
        self.active_connections[negotiation_id].append((user_id, websocket))
        logger.info(
            "WS conectado: user=%s, negotiation=%s",
            user_id,
            negotiation_id,
        )

    def disconnect(
        self, websocket: WebSocket, negotiation_id: str, user_id: str
    ) -> None:
        """Desregistra una conexión WebSocket de una sala."""
        connections = self.active_connections[negotiation_id]
        self.active_connections[negotiation_id] = [
            (uid, ws) for uid, ws in connections if ws != websocket
        ]
        if not self.active_connections[negotiation_id]:
            del self.active_connections[negotiation_id]
        logger.info(
            "WS desconectado: user=%s, negotiation=%s",
            user_id,
            negotiation_id,
        )

    async def broadcast_to_room(
        self, negotiation_id: str, message: dict, exclude_user: str | None = None
    ) -> None:
        """Envía un mensaje a todos los conectados en la sala (excepto al remitente)."""
        connections = self.active_connections.get(negotiation_id, [])
        for user_id, websocket in connections:
            if exclude_user and user_id == exclude_user:
                continue
            try:
                await websocket.send_json(message)
            except Exception:
                logger.warning(
                    "Error enviando mensaje WS a user=%s",
                    user_id,
                )

    async def send_personal(self, websocket: WebSocket, message: dict) -> None:
        """Envía un mensaje solo a una conexión específica."""
        try:
            await websocket.send_json(message)
        except Exception:
            logger.warning("Error enviando mensaje personal WS")


manager = ConnectionManager()


def _authenticate_ws(token: str) -> str | None:
    """Valida un token JWT y retorna el user_id o None."""
    payload = decode_access_token(token)
    if payload is None:
        return None
    return payload.get("sub")


@router.websocket("/ws/chat/{negotiation_id}")
async def websocket_chat(
    websocket: WebSocket,
    negotiation_id: str,
):
    """Endpoint WebSocket para chat en tiempo real dentro de una negociación.

    Protocolo:
    1. El cliente se conecta enviando un query param `token=<JWT>`.
    2. El servidor valida el token y verifica que el usuario sea parte de la negociación.
    3. Los mensajes se envían como JSON: {"content": "texto del mensaje"}
    4. El servidor persiste el mensaje y lo retransmite a la otra parte.
    """
    # --- Autenticación ---
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Token requerido")
        return

    user_id_str = _authenticate_ws(token)
    if not user_id_str:
        await websocket.close(code=4001, reason="Token inválido o expirado")
        return

    # --- Validar pertenencia a la negociación ---
    # Use a fresh DB session for the WS lifetime
    from app.core.database import async_session

    async with async_session() as db:
        try:
            user_id = uuid.UUID(user_id_str)
            user = await get_user_by_id(db, user_id)
            if not user:
                await websocket.close(code=4001, reason="Usuario no encontrado")
                return

            neg_uuid = uuid.UUID(negotiation_id)
            negotiation = await negotiation_service.get_negotiation_by_id(
                db, neg_uuid
            )

            if user_id not in (negotiation.buyer_id, negotiation.seller_id):
                await websocket.close(
                    code=4003, reason="No eres parte de esta negociación"
                )
                return
        except Exception:
            await websocket.close(code=4000, reason="Error de validación")
            return

    # --- Conectar a la sala ---
    await manager.connect(websocket, negotiation_id, user_id_str)

    # Notificar ingreso a la sala
    await manager.broadcast_to_room(
        negotiation_id,
        {
            "type": "system",
            "content": f"Usuario {user.name} se unió al chat",
            "sender_id": user_id_str,
        },
        exclude_user=user_id_str,
    )

    try:
        while True:
            # Recibir mensaje del cliente
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
                content = data.get("content", "").strip()
            except (json.JSONDecodeError, AttributeError):
                await manager.send_personal(
                    websocket,
                    {"type": "error", "content": "Formato de mensaje inválido"},
                )
                continue

            if not content:
                await manager.send_personal(
                    websocket,
                    {"type": "error", "content": "El mensaje no puede estar vacío"},
                )
                continue

            if len(content) > 2000:
                await manager.send_personal(
                    websocket,
                    {
                        "type": "error",
                        "content": "El mensaje excede los 2000 caracteres",
                    },
                )
                continue

            # Persistir el mensaje en BD
            async with async_session() as db:
                try:
                    neg_uuid = uuid.UUID(negotiation_id)
                    message = await negotiation_service.create_chat_message(
                        db, neg_uuid, user_id, content
                    )
                    await db.commit()

                    # Broadcast a toda la sala (incluido el remitente para confirmación)
                    message_payload = {
                        "type": "message",
                        "id": str(message.id),
                        "negotiation_id": negotiation_id,
                        "sender_id": user_id_str,
                        "sender_name": user.name,
                        "content": content,
                        "created_at": message.created_at.isoformat(),
                    }
                    await manager.broadcast_to_room(negotiation_id, message_payload)

                except Exception:
                    logger.exception("Error persistiendo mensaje de chat")
                    await manager.send_personal(
                        websocket,
                        {"type": "error", "content": "Error al guardar el mensaje"},
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket, negotiation_id, user_id_str)
        await manager.broadcast_to_room(
            negotiation_id,
            {
                "type": "system",
                "content": f"Usuario {user.name} salió del chat",
                "sender_id": user_id_str,
            },
        )
