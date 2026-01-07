from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy import TIMESTAMP, text, BigInteger
from enum import Enum
from datetime import datetime as dt


class Base(DeclarativeBase):
    pass

class Status(Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    QUEUED = "QUEUED"
    FAILED = "FAILED"

class Channel(Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"

class Notification(Base):

    __tablename__ = "notifications"


    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    body: Mapped[str] = mapped_column(nullable=False)
    recipient: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[Status] = mapped_column(nullable=False, server_default=Status.PENDING.value)
    channel: Mapped[Channel] = mapped_column(nullable=False)
    retry_cnt: Mapped[int] = mapped_column(nullable=False, server_default=text('0'))
    created_at: Mapped[dt] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at: Mapped[dt] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    
