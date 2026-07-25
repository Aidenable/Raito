import pytest
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendMessage

from raito.utils.errors import SuppressNotModifiedError


def _bad_request(message):
    return TelegramBadRequest(method=SendMessage(chat_id=1, text="x"), message=message)


def test_suppresses_not_modified_error():
    with SuppressNotModifiedError():
        raise _bad_request("Bad Request: message is not modified")


def test_reraises_other_bad_request():
    with pytest.raises(TelegramBadRequest):
        with SuppressNotModifiedError():
            raise _bad_request("Bad Request: chat not found")


def test_does_not_suppress_other_exception_types():
    with pytest.raises(ValueError):
        with SuppressNotModifiedError():
            raise ValueError("boom")


def test_no_exception_passes_through():
    with SuppressNotModifiedError():
        value = 1 + 1
    assert value == 2


def test_custom_ignore_message():
    with SuppressNotModifiedError(ignore_message="custom marker"):
        raise _bad_request("Bad Request: custom marker here")


def test_custom_ignore_message_does_not_match_default():
    with pytest.raises(TelegramBadRequest):
        with SuppressNotModifiedError(ignore_message="custom marker"):
            raise _bad_request("Bad Request: message is not modified")
