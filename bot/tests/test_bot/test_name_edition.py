from ...bot_utils import process_name_edit
from .mocks import  FakeMessage
from ...messages import SUCCESSFUL_NAME_UPDATE

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
    run_name_edition_positive_test(fake_context, mock_send_message, message, editted_list_position)