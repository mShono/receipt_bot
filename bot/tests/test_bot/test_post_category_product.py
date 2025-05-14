from ...bot_utils import post_category_product
from .mocks import  FakeMessage
from ...messages import SUCCESSFUL_CATEGORY_CORRECT, UNSUCCESSFUL_CATEGORY_CREATION, UNSUCCESSFUL_PPRODUCT_CREATION


def test_post_category_product_absent_positive(fake_context, mock_post_data_info_positive, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_tea_name")
    product_name = fake_context.products_absent_in_database[0]["name"]
    fake_context.stage = "products_absent_in_database"

    expected_message = SUCCESSFUL_CATEGORY_CORRECT.format(
        category_name=message.text,
        product_name=product_name
    )

    post_category_product(message, product_name)

    assert len(mock_send_message) == 1
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message


def test_post_category_product_new_expense_positive(monkeypatch, fake_context, mock_post_data_info_positive, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_tea_name")
    product_name = fake_context.products_absent_in_database[0]["name"]
    fake_context.stage = "new_expense"

    calls = []
    def fake_collecting_data_and_post_item(message):
        calls.append(True)
    monkeypatch.setattr(
        "bot.bot_utils.collecting_data_and_post_item",
        fake_collecting_data_and_post_item
    )

    post_category_product(message, product_name)

    expected_message = SUCCESSFUL_CATEGORY_CORRECT.format(
        category_name=message.text,
        product_name=product_name
    )

    assert len(mock_send_message) == 1
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message
    assert len(calls) == 1


def test_post_category_product_negative_category(monkeypatch, fake_context, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_tea_name")
    product_name = fake_context.products_absent_in_database[0]["name"]
    fake_context.stage = "products_absent_in_database"

    def fake_post_data_info(endpoint, data):
        if endpoint == "category":
            return False, None
        return True, 123

    monkeypatch.setattr("bot.bot_utils.post_data_info", fake_post_data_info)

    post_category_product(message, product_name)

    expected_message = UNSUCCESSFUL_CATEGORY_CREATION.format(
        product_name = product_name
    )
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message


def test_post_category_product_negative_product(monkeypatch, fake_context, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_tea_name")
    product_name = fake_context.products_absent_in_database[0]["name"]
    fake_context.stage = "products_absent_in_database"

    def fake_post_data_info(endpoint, data):
        if endpoint == "product":
            return False, None
        return True, 123

    monkeypatch.setattr("bot.bot_utils.post_data_info", fake_post_data_info)

    post_category_product(message, product_name)

    expected_message = UNSUCCESSFUL_PPRODUCT_CREATION.format(
        product_name = product_name
    )
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message
