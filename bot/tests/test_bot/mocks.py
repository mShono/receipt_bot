import pytest

from telebot import types


class FakeChat:
    def __init__(self, chat_id, username=None, first_name=None, last_name=None):
        self.id = chat_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class FakeMessage:
    def __init__(self, chat_id, text):
        self.chat = FakeChat(chat_id)
        self.text = text


class FakeCallbackQuery:
    def __init__(self, chat_id, callback_data, username=None, first_name=None, last_name=None,):
        self.message = type("FakeMessage", (), {
            "chat": FakeChat(chat_id, username=username, first_name=first_name, last_name=last_name),
        })
        self.data = callback_data


class FakePhotoMessage:
    def __init__(self, chat_id, file_id):
        self.chat = FakeChat(chat_id)
        self.content_type = "photo"
        self.photo = [types.PhotoSize(
            file_id=file_id,
            file_unique_id=f"uniq_{file_id}",
            width=1,
            height=1,
            file_size=1
            )
        ]


class FakeDocumentMessage:
    def __init__(self, chat_id, file_id, mime_type="image/jpeg"):
        self.chat = FakeChat(chat_id)
        self.content_type = "document"
        self.document = types.Document(
            file_id=file_id,
            file_unique_id="unique-"+file_id,
            file_name="receipt.jpg",
            mime_type=mime_type,
            file_size=1234
        )


class FakeResponse:
    def __init__(self, status_code, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json
