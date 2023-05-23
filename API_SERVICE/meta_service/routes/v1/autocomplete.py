import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector


router = APIRouter()

logger = logging.getLogger()


@router.post("")
def test():
    pass