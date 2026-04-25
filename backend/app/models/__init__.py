"""VeraMarket — Models package.

Importar todos los modelos aquí para que Alembic los detecte.
"""

from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.gmv_metric import GmvMetric  # noqa: F401
from app.models.location import Location  # noqa: F401
from app.models.negotiation import Negotiation  # noqa: F401
from app.models.otp import OTPCode  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_search_quota import UserSearchQuota  # noqa: F401
