from sqlalchemy.orm import declarative_base

from login_service.common.config import settings
from libs.database.conn import TiberoConnector
from libs.database.conn import SQLAlchemy

Base = declarative_base()
db = SQLAlchemy(Base) if settings.DB_INFO.type != "tibero" else TiberoConnector()
