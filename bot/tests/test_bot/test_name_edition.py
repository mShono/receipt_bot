from ...bot_utils import process_name_edit, category_buttons
from .mocks import  FakeMessage
from ...messages import SUCCESSFUL_NAME_UPDATE, PPODUCT_MISSING_IN_DATABASE

def run_name_edition_positive_test(fake_context, mock_send_message, message, editted_list_position):
    old_name = editted_list_position["name"]

    process_name_edit(message, editted_list_position)

    expected_message = SUCCESSFUL_NAME_UPDATE.format(
        old_name=old_name,
        new_name=message.text
    )

    assert len(mock_send_message) == 1
    _, message_text, _= mock_send_message[0]
    assert message_text == expected_message

def test_name_edit_present_positive(fake_context, mock_get_data_info_positive, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_egg_name")
    editted_list_position = fake_context.products_present_in_database[0]
    run_name_edition_positive_test(fake_context, mock_send_message, message, editted_list_position)


def test_name_edit_absent_positive(fake_context, mock_get_data_info_positive, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_tea_name")
    editted_list_position = fake_context.products_absent_in_database[0]
    fake_context.stage = "products_absent_in_database"
    run_name_edition_positive_test(fake_context, mock_send_message, message, editted_list_position)


def run_name_edition_negative_test(monkeypatch, fake_context, mock_send_message, message, editted_list_position):
    monkeypatch.setattr("bot.bot_utils.check_existent_categories", lambda context: None)
    fake_context.existing_categories = ["Category_1", "Category_2"]
    monkeypatch.setattr("bot.bot_utils.category_buttons", lambda name, context: category_buttons(name, context))

    process_name_edit(message, editted_list_position)

    assert len(mock_send_message) == 1
    _, message_text, markup = mock_send_message[0]
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "exist_cat:Category_1, prod:New_egg_name"
            if count == 1:
                assert button.callback_data == "exist_cat:Category_2, prod:New_egg_name"
            count += 1

    expected_message = PPODUCT_MISSING_IN_DATABASE.format(
        name=editted_list_position["name"],
    )
    assert message_text == expected_message


def test_name_edit_present_negative(monkeypatch, fake_context, mock_get_data_info_negative, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_egg_name")
    editted_list_position = fake_context.products_present_in_database[0]
    run_name_edition_negative_test(monkeypatch, fake_context, mock_send_message, message, editted_list_position)


def test_name_edit_absent_negative(monkeypatch, fake_context, mock_get_data_info_negative, mock_send_message):
    message = FakeMessage(chat_id=42, text="New_egg_name")
    editted_list_position = fake_context.products_absent_in_database[0]
    fake_context.stage = "products_absent_in_database"
    run_name_edition_negative_test(monkeypatch, fake_context, mock_send_message, message, editted_list_position)
