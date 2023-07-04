from sqlalchemy.ext.automap import automap_base

from common_service.common.config import settings
from libs.database.tibero import TiberoConnector
from libs.database.orm import SQLAlchemyConnector


from sqlalchemy.orm import declarative_base

from common_service.common.config import settings

Base = automap_base()
db = None
if settings.DB_INFO.type == "tibero":
    from libs.database.tibero import TiberoConnector

    db = TiberoConnector()
elif settings.DB_INFO.type == "orm":
    from libs.database.orm import SQLAlchemyConnector

    db = SQLAlchemyConnector(Base)
