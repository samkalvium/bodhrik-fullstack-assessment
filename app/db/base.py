# Import all models here so Alembic can discover metadata
from app.models.base import Base  # noqa
from app.models.user import User  # noqa
from app.models.session import Session  # noqa
from app.models.evaluation import Evaluation  # noqa

