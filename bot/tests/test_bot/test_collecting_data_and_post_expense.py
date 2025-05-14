from ...bot_utils import collecting_data_and_post_expense
from .mocks import  FakeMessage


def test_collecting_data_and_post_expence_positive(fake_context, mock_get_data_info_positive, mock_post_data_info_positive):
    message = FakeMessage(chat_id=42, text="Some_text")
    status, expense_id = collecting_data_and_post_expense(message)
    assert status == True
    assert expense_id == 1


def test_collecting_data_and_post_expence_get_user_data_negative(fake_context, mock_get_data_info_negative, mock_post_data_info_positive):
    message = FakeMessage(chat_id=42, text="Some_text")
    status, expense_id = collecting_data_and_post_expense(message)
    assert status == True
    assert expense_id == 1


def test_collecting_data_and_post_expence_post_user_negative(fake_context, mock_get_data_info_negative, mock_post_data_info_negative):
    message = FakeMessage(chat_id=42, text="Some_text")
    status, expense_id = collecting_data_and_post_expense(message)
    assert status == False
    assert expense_id == None


def test_collecting_data_and_post_expence_negative(fake_context, mock_get_data_info_positive, mock_post_data_info_negative):
    message = FakeMessage(chat_id=42, text="Some_text")
    status, expense_id = collecting_data_and_post_expense(message)
    assert status == False
    assert expense_id == None