import bot.__main__ as main_mod
from ...__main__ import callback_inline
from .mocks import FakeMessage

def run_next_step_handler_test(captured_register_handler, monkeypatch, message, fake_call, pussed_button, next_step_function):
    callback_inline(fake_call)

    assert 'handler' in captured_register_handler
    handler = captured_register_handler['handler']

    called = {}
    def mock_next_step_function(message, list_position):
        called['status'] = True
        called['list_position'] = list_position
    monkeypatch.setattr(main_mod, next_step_function.__name__, mock_next_step_function)

    handler(message)
    print(called)
    assert called.get('status', False) is True
    assert called['list_position'] is pussed_button


def test_press_present_button_triggers_price_edit(captured_register_handler, monkeypatch, fake_callback_query_factory, fake_context):
    run_next_step_handler_test(
        captured_register_handler,
        monkeypatch,
        message=FakeMessage(chat_id=42, text="unused_text"),
        fake_call=fake_callback_query_factory(chat_id=42, callback_data="Eggs"),
        pussed_button=fake_context.products_present_in_database[0],
        next_step_function = main_mod.process_price_edit
    )


def test_press_absent_button_triggers_name_edit(fake_context, captured_register_handler, fake_callback_query_factory, monkeypatch):
    run_next_step_handler_test(
        captured_register_handler,
        monkeypatch,
        message=FakeMessage(chat_id=42, text="NewTea"),
        fake_call=fake_callback_query_factory(chat_id=42, callback_data="Tea"),
        pussed_button=fake_context.products_absent_in_database[0],
        next_step_function = main_mod.process_name_edit
    )
