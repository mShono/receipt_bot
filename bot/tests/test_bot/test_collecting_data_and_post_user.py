from ...bot_utils import collecting_data_and_post_user
from .mocks import  FakeMessage

def test_collecting_data_and_post_user_positive(mock_get_data_info_positive):
    message = FakeMessage(chat_id=42, text="Some_text")

    get_user_status, user_info = collecting_data_and_post_user(message)
    assert get_user_status == True
    assert user_info == {'id': 1, 'chat_id': 12345, 'username': None, 'first_name': 'Test', 'last_name': 'User'}
    # assert user_info == {'id': 12345, 'username': None, 'first_name': 'Test', 'last_name': 'User'}


def test_collecting_data_and_post_user_negative(mock_get_data_info_negative, mock_post_data_info_positive):
    message = FakeMessage(chat_id=42, text="Some_text")

    get_user_status, user_info = collecting_data_and_post_user(message)
    assert get_user_status == True
    assert user_info == 1
