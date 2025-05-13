import bot.__main__ as main_mod
from ...__main__ import callback_inline, callback_nothing_after_present, collecting_data_and_post_expense, collecting_data_and_post_item, callback_nothing_after_absent, callback_existing_category, callback_category_creation
from ...messages import RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE, UPLOAD_EXPENCE, UNSUCCESSFUL_UPLOAD_EXPENCE, SUCCESSFUL_CATEGORY_CORRECT, SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT
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
    # print(called)
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


def test_press_nothing_after_present_button_sends_absent_buttons(monkeypatch, fake_callback_query_factory, fake_context, mock_send_message):
    fake_call = fake_callback_query_factory(chat_id=42, callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
    callback_nothing_after_present(fake_call)

    assert len(mock_send_message) == 1
    _, message_text, markup = mock_send_message[0]
    assert message_text == RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Tea"
            if count == 1:
                assert button.callback_data == "Nothing_to_edit_after_ABSENT_IN_DATABASE"
            count += 1


def run_press_nothing_saves_expence_test(
        monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message, called_function
):
    def mock_collecting_data_and_post_expense(fake_call):
        return True, "not_used_data"
    monkeypatch.setattr("bot.__main__.collecting_data_and_post_expense", mock_collecting_data_and_post_expense)

    called_collecting_data_and_post_item = {}
    def mock_collecting_data_and_post_item(fake_call):
        called_collecting_data_and_post_item['status'] = True
    monkeypatch.setattr("bot.__main__.collecting_data_and_post_item", mock_collecting_data_and_post_item)

    fake_call = fake_callback_query_factory(chat_id=42, callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
    called_function(fake_call)

    assert len(mock_send_message) == 1
    _, message_text, _ = mock_send_message[0]
    assert message_text == UPLOAD_EXPENCE

    assert called_collecting_data_and_post_item['status'] == True


def test_press_nothing_after_present_button_saves_expence(monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message):
    run_press_nothing_saves_expence_test(
        monkeypatch,
        fake_callback_query_factory,
        fake_context_without_absent,
        mock_send_message,
        called_function = callback_nothing_after_present
    )


def test_press_nothing_after_absent_button_saves_expence(monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message):
    run_press_nothing_saves_expence_test(
        monkeypatch,
        fake_callback_query_factory,
        fake_context_without_absent,
        mock_send_message,
        called_function = callback_nothing_after_absent
    )


def run_press_nothing_sends_unsuccessful_message_test(
        monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message, called_function
    ):
    def mock_collecting_data_and_post_expense(fake_call):
        return False, "not_used_data"
    monkeypatch.setattr("bot.__main__.collecting_data_and_post_expense", mock_collecting_data_and_post_expense)

    fake_call = fake_callback_query_factory(chat_id=42, callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
    callback_nothing_after_present(fake_call)

    assert len(mock_send_message) == 2
    _, message_text, _ = mock_send_message[0]
    assert message_text == UPLOAD_EXPENCE
    _, message_text, _ = mock_send_message[1]
    assert message_text == UNSUCCESSFUL_UPLOAD_EXPENCE


def test_press_nothing_after_present_button_sends_unsuccessful_message(monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message):
    run_press_nothing_sends_unsuccessful_message_test(
        monkeypatch,
        fake_callback_query_factory,
        fake_context_without_absent,
        mock_send_message,
        called_function = callback_nothing_after_present
    )


def test_press_nothing_after_absent_button_sends_unsuccessful_message(monkeypatch, fake_callback_query_factory, fake_context_without_absent, mock_send_message):
    run_press_nothing_sends_unsuccessful_message_test(
        monkeypatch,
        fake_callback_query_factory,
        fake_context_without_absent,
        mock_send_message,
        called_function = callback_nothing_after_absent
    )


def test_press_existing_category_post_the_expense(monkeypatch, fake_callback_query_factory, fake_context, mock_send_message):
    context = fake_context
    context.stage = "new_expense"
    fake_call = fake_callback_query_factory(
        chat_id=42,
        callback_data="exist_cat:Grocery, prod:Tea")

    called_get_category_id = {}
    def mock_get_category_id(category_name, context):
        called_get_category_id['name'] = category_name
        return 5
    monkeypatch.setattr("bot.__main__.get_category_id", mock_get_category_id)
    monkeypatch.setattr("bot.__main__.post_data_info", lambda *args, **kwargs: (True, None))

    called_collecting_data_and_post_item = {}
    def mock_collecting_data_and_post_item(fake_call):
        called_collecting_data_and_post_item['status'] = True
    monkeypatch.setattr("bot.__main__.collecting_data_and_post_item", mock_collecting_data_and_post_item)

    callback_existing_category(fake_call)

    expected_message = SUCCESSFUL_CATEGORY_CORRECT.format(
        category_name="Grocery",
        product_name="Tea"
    )

    assert called_get_category_id['name'] == "Grocery"

    assert len(mock_send_message) == 1
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message

    assert called_collecting_data_and_post_item['status'] == True


def test_press_existing_category_sends_absent_buttons(monkeypatch, fake_callback_query_factory, fake_context, mock_send_message):
    context = fake_context
    context.stage = "products_absent_in_database"
    fake_call = fake_callback_query_factory(
        chat_id=42,
        callback_data="exist_cat:Grocery, prod:Tea")

    called_get_category_id = {}
    def mock_get_category_id(category_name, context):
        called_get_category_id['name'] = category_name
        return 5
    monkeypatch.setattr("bot.__main__.get_category_id", mock_get_category_id)
    monkeypatch.setattr("bot.__main__.post_data_info", lambda *args, **kwargs: (True, None))

    callback_existing_category(fake_call)

    expected_message = SUCCESSFUL_CATEGORY_CORRECT.format(
        category_name="Grocery",
        product_name="Tea"
    )

    assert called_get_category_id['name'] == "Grocery"

    assert len(mock_send_message) == 1
    _, message_text, markup = mock_send_message[0]
    assert message_text == expected_message

    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Tea"
            if count == 1:
                assert button.callback_data == "Nothing_to_edit_after_ABSENT_IN_DATABASE"
            count += 1


def test_press_category_creation_triggers_post_category_product(monkeypatch, captured_register_handler, fake_callback_query_factory, fake_context, mock_send_message):
    fake_call = fake_callback_query_factory(
        chat_id=42,
        callback_data="categ_cr, prod:Tea")

    expected_message = SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT.format(
        product_name="Tea"
    )

    callback_category_creation(fake_call)

    assert len(mock_send_message) == 1
    _, message_text, _ = mock_send_message[0]
    assert message_text == expected_message

    assert 'handler' in captured_register_handler
    handler = captured_register_handler['handler']

    called_post_category_product = {}
    def mock_post_category_product(fake_call, product_name):
        called_post_category_product['status'] = True
    monkeypatch.setattr("bot.__main__.post_category_product", mock_post_category_product)

    message=FakeMessage(chat_id=42, text="unused_text")

    handler(message)
    assert called_post_category_product.get('status', False) is True
