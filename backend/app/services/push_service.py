"""Service — Web Push Notifications (HU 2.3).

Lógica para enviar notificaciones push a través de pywebpush.
"""

import os

from pywebpush import WebPushException, webpush

# Keys for VAPID configuration
# Se deben configurar en .env: VAPID_PRIVATE_KEY, VAPID_SUBSCRIBER_EMAIL
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "generate_a_new_vapid_key")
VAPID_SUBSCRIBER_EMAIL = os.getenv(
    "VAPID_SUBSCRIBER_EMAIL", "mailto:test@veramarket.com"
)


def send_push_notification(subscription_info: dict, payload_data: str):
    """
    Envía una notificación push mediante pywebpush a un único client endpoint.

    Args:
        subscription_info: Detalle de la suscripción (endpoint, keys, etc).
        payload_data: Contenido string (usualmente en formato JSON text).
    """
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload_data,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBSCRIBER_EMAIL},
        )
    except WebPushException as ex:
        # Aquí se podría registrar o procesar un status 410 Gone si la suscripción expiró.
        print("Error sending web push:", repr(ex))
        if ex.response and ex.response.json():
            print(ex.response.json())
