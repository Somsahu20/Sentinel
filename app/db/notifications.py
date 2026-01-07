from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Literal, Annotated, Union
from ..models.notifications import Status
from datetime import datetime as dt


class Notification(BaseModel):
    body: str

class EmailSend(Notification):
    channel: Literal["EMAIL"] = "EMAIL"
    recipient: EmailStr
    model_config = ConfigDict(from_attributes=True)

class PhoneSend(Notification):
    channel: Literal["SMS"] = "SMS"
    recipient: str = Field(pattern=r"^\+91-[6-9]\d{9}$")
    model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id: int
    body: str 
    recipient: str
    status: Status
    retry_cnt: int
    created_at: dt
    updated_at: dt

    model_config = ConfigDict(from_attributes=True)

NotificationSend = Annotated[
    Union[EmailSend, PhoneSend],
    Field(discriminator="channel")
]


