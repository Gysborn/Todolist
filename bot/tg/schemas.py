from typing import List
from pydantic import BaseModel


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    chat: Chat
    text: str | None = None


class UpdateObj(BaseModel):
    update_id: int
    message: Message


class GetUpdatesResponse(BaseModel):
    ok: bool
    result: List[UpdateObj]  # todo


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message  # todo
