from ...bot_utils import collecting_data_and_post_item
from .mocks import  FakeMessage
from ...messages import SUCCESSFUL_UPLOAD_EXPENCE, PPODUCT_MISSING_IN_DATABASE, UNSUCCESSFUL_UPLOAD_EXPENCE


def test_collecting_data_and_post_item_positive(fake_context, mock_get_data_info_positive, mock_post_data_info_positive, mock_send_message):
    message = FakeMessage(chat_id=42, text="Some_text")
    fake_context.new_expense.extend(fake_context.products_present_in_database)
    fake_context.new_expense.extend(fake_context.products_absent_in_database)

    collecting_data_and_post_item(message)

    assert fake_context.expense_id == None
    _, message_text, _ = mock_send_message[0]
    assert message_text == SUCCESSFUL_UPLOAD_EXPENCE


def test_collecting_data_and_post_item_negative(fake_context, mock_get_data_info_positive, mock_post_data_info_negative, mock_send_message):
    message = FakeMessage(chat_id=42, text="Some_text")
    fake_context.new_expense.extend(fake_context.products_present_in_database)
    fake_context.new_expense.extend(fake_context.products_absent_in_database)

    collecting_data_and_post_item(message)

    assert fake_context.expense_id == None
    _, message_text, _ = mock_send_message[0]
    assert message_text == UNSUCCESSFUL_UPLOAD_EXPENCE


def test_collecting_data_and_post_item_get_data_info_negative(fake_context, monkeypatch, mock_get_data_info_negative, mock_send_message):
    message = FakeMessage(chat_id=42, text="Some_text")
    fake_context.new_expense.extend(fake_context.products_present_in_database)
    fake_context.new_expense.extend(fake_context.products_absent_in_database)

    def fake_check_existent_categories(fake_context):
        fake_context.existing_categories.append("first_category")
    monkeypatch.setattr("bot.bot_utils.check_existent_categories", fake_check_existent_categories)

    collecting_data_and_post_item(message)

    first_item = fake_context.new_expense[0]
    expected_message = PPODUCT_MISSING_IN_DATABASE.format(
        name=first_item["name"],
    )

    _, message_text, markup = mock_send_message[0]
    assert message_text == expected_message

    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == f"exist_cat:first_category, prod:{first_item["name"]}"
            if count == 1:
                assert button.callback_data == f"categ_cr, prod:{first_item["name"]}"
            count += 1
