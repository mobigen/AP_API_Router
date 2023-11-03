from sqlalchemy import String, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from router.app.database.conn import Base
from libs.database.models import BaseMixin


class BaseMixinSitemng(BaseMixin):
    __table_args__ = {"schema": "sitemng"}


class TbApiInfo(BaseMixinSitemng, Base):
    __tablename__ = "api_item_bas"

    api_nm = Column(String(length=64), nullable=False)
    route_url = Column(String(length=256), nullable=False)
    url = Column(String(length=256))
    mthd = Column(String(length=64))
    cmd = Column(String(length=512))
    mode = Column(String(length=32), nullable=False)
    srvr_nm = Column(String(length=64), ForeignKey("sitemng.api_item_server_dtl.srvr_nm"), nullable=False)

    server_info = relationship("TbApiServerInfo")

    __table_args__ = (PrimaryKeyConstraint(api_nm, route_url, mthd), BaseMixinSitemng.__table_args__,)


class TbApiServerInfo(BaseMixinSitemng, Base):
    __tablename__ = "api_item_server_dtl"

    srvr_nm = Column(String(length=64), nullable=False, primary_key=True)
    ip_adr = Column(String(length=128), nullable=False)
    domn_nm = Column(String(length=256))
