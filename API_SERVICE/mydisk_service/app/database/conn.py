from sqlalchemy.ext.automap import automap_base

from libs.database.orm import SQLAlchemyConnector

Base = automap_base()
db = SQLAlchemyConnector(Base)
