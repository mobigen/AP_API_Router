from sqlalchemy.orm import declarative_base

from login_service.common.config import settings
from libs.database.tibero import TiberoConnector
from libs.database.orm import SQLAlchemyConnector

Base = declarative_base()
db = SQLAlchemyConnector(Base) if settings.DB_INFO.type != "tibero" else TiberoConnector()
