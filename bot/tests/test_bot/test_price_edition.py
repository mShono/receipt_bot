from ...bot_utils import process_price_edit
from .mocks import  FakeMessage
from ...messages import WRONG_PRICE, SUCCESSFUL_PRICE_UPDATE


def test_process_price_edit_invalid(
    fake_context,
    captured_calls,
    monkeypatch,
    mock_buttons
):
    monkeypatch.setattr(
        "bot.bot_utils.price_validation", 
        lambda price: (False, price)
    )

    message = FakeMessage(chat_id=42, text="not-a-number")
    process_price_edit(message, fake_context.products_present_in_database[0])

    assert fake_context.products_present_in_database[0]["price"] == 100

    assert len(captured_calls) == 1
    chat_id, text, markup, kwargs = captured_calls[0]

    assert chat_id == 42
    assert text == WRONG_PRICE
    assert markup is mock_buttons
    assert kwargs == {"price": "not-a-number", "product": "Eggs"}


def test_process_price_edit_valid(
    fake_context,
    captured_calls,
    monkeypatch,
    mock_buttons
):
    monkeypatch.setattr(
        "bot.bot_utils.price_validation",
        lambda price: (True, 4.5)
    )
    monkeypatch.setattr(
        "bot.bot_utils.float_to_int",
        lambda val: 450
    )

    message = FakeMessage(chat_id=42, text="4.50")
    process_price_edit(message, fake_context.products_present_in_database[0])

    assert fake_context.products_present_in_database[0]["price"] == 450

    assert len(captured_calls) == 1
    chat_id, text, markup, kwargs = captured_calls[0]

    assert chat_id == 42
    assert text == SUCCESSFUL_PRICE_UPDATE
    assert markup is mock_buttons
    assert kwargs == {"price": 4.5, "product": "Eggs"}