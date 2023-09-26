from sqlalchemy.ext.automap import automap_base
from batch_service.common.utils import SeoulOrmConnector
from libs.database.orm import SQLAlchemyConnector

db = None
seoul_db = None

Base = automap_base()
db = SQLAlchemyConnector(Base)
seoul_db = SeoulOrmConnector(Base)
