from sqlalchemy.orm import declarative_base

from app.common.config import settings

Base = declarative_base()
db = None
if settings.DB_INFO.type == "tibero":
    from libs.database.tibero import TiberoConnector

    db = TiberoConnector()
elif settings.DB_INFO.type == "orm":
    from libs.database.orm import SQLAlchemyConnector

    db = SQLAlchemyConnector(Base)
