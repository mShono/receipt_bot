import os

import bot.__main__ as main_mod
from .mocks import  FakeMessage
from .test_receipt_upload import run_receipt_test
from ...bot_utils import process_price_edit, process_name_edit, post_category_product
from ...__main__ import callback_register, wake_up, callback_upload_receipt, callback_inline, callback_nothing_after_present, callback_category_creation, callback_nothing_after_absent, callback_existing_category
from ...messages import SUCCESSFUL_REGISTRATION, UPLOAD_RECEIRT, SUCCESSFUL_RECOGNITION, CORRECTING_PRICE, WRONG_PRICE, SUCCESSFUL_PRICE_UPDATE, RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE, CORRECTING_NAME, PPODUCT_MISSING_IN_DATABASE, SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT, SUCCESSFUL_CATEGORY_CORRECT, UPLOAD_EXPENCE, PPODUCT_MISSING_IN_DATABASE, SUCCESSFUL_UPLOAD_EXPENCE
from ...state import UserContext


def test_full_expense_flow_positive(monkeypatch, fake_context, mock_send_message, fake_callback_query_factory, mock_get_data_info_negative, mock_post_data_info_positive, mock_photo_message, captured_register_handler):
    chat_id = 42

    # Pushing the "/start" button
    message = FakeMessage(chat_id=chat_id, text="/start")
    wake_up(message)

    assert len(mock_send_message) == 1
    _, _, markup = mock_send_message[-1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Register"

    # Pushing the "Register" button
    call = fake_callback_query_factory(chat_id=chat_id, callback_data="Register")
    callback_register(call)

    assert len(mock_send_message) == 3
    _, message_text, _ = mock_send_message[-2]
    assert message_text == SUCCESSFUL_REGISTRATION
    _, _, markup = mock_send_message[-1]
    for row in markup.keyboard:
        for button in row:
            assert button.callback_data == "Upload receipt"

    # Pushing the "Upload receipt" button
    call = fake_callback_query_factory(chat_id=chat_id, callback_data="Upload receipt")
    callback_upload_receipt(call)

    assert len(mock_send_message) == 4
    _, message_text, _ = mock_send_message[-1]
    assert message_text == UPLOAD_RECEIRT

    # Sending a receipt picture
    incoming_data = {
        "Eggs":   (True,  {"id": 1}),
        "Apples": (True,  {"id": 2}),
        "Tea":    (False, None),
        "Coffee": (False, None),
    }
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_recognised_receipt.json")
    run_receipt_test(
        monkeypatch, mock_photo_message, mock_send_message,
        incoming_data,
        expected_present=[{"name":"Eggs","price":1.0,"id":1}, {"name":"Apples","price":2.0,"id":2}],
        expected_absent=[{"name":"Tea","price":114},{"name":"Coffee","price":550}],
        expected_message=SUCCESSFUL_RECOGNITION,
        test_filepath=test_filepath
    )
    count = 0
    _, _, markup = mock_send_message[-1]
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Eggs"
            if count == 1:
                assert button.callback_data == "Apples"
            if count == 2:
                assert button.callback_data == "Nothing_to_edit_after_PRESENT_IN_DATABASE"
            count += 1

    # Pushing a button of present_in_database product to correct the price
    call = fake_callback_query_factory(chat_id=chat_id, callback_data="Eggs")
    callback_inline(call)

    assert 'handler' in captured_register_handler
    handler = captured_register_handler['handler']

    context = UserContext[42]
    edited_list_position = context.products_present_in_database[0]
    expected_message = CORRECTING_PRICE.format(
        name = edited_list_position["name"],
        price = edited_list_position["price"]
    )
    _, message_text, _ = mock_send_message[-1]
    assert message_text == expected_message
    called = {}
    def fake_process_price_edit(message, list_position):
        called['status'] = True
        called['list_position'] = list_position
    monkeypatch.setattr("bot.__main__.process_price_edit", fake_process_price_edit)

    # Sending a message with invalid price
    message = FakeMessage(chat_id=chat_id, text="price")
    handler(message)
    assert called.get('status', False) is True
    assert called['list_position'] == edited_list_position

    process_price_edit(message, edited_list_position)
    print(f"edited_list_position_price = {edited_list_position["price"]}")

    expected_message = WRONG_PRICE.format(
        product = edited_list_position["name"],
        price = message.text
    )
    _, message_text, markup = mock_send_message[-1]
    assert message_text == expected_message
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Eggs"
            if count == 1:
                assert button.callback_data == "Apples"
            if count == 2:
                assert button.callback_data == "Nothing_to_edit_after_PRESENT_IN_DATABASE"
            count += 1

    # Sending a message with valid price
    message = FakeMessage(chat_id=chat_id, text="3")
    process_price_edit(message, edited_list_position)

    assert edited_list_position["price"] == 3.0

    expected_message = SUCCESSFUL_PRICE_UPDATE.format(
        product = edited_list_position["name"],
        price = message.text
    )
    _, message_text, markup = mock_send_message[-1]
    assert message_text == expected_message
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Eggs"
            if count == 1:
                assert button.callback_data == "Apples"
            if count == 2:
                assert button.callback_data == "Nothing_to_edit_after_PRESENT_IN_DATABASE"
            count += 1

    # Pushing "Nothing_to_edit_after_PRESENT_IN_DATABASE" button
    call = fake_callback_query_factory(chat_id=chat_id, callback_data="Nothing_to_edit_after_PRESENT_IN_DATABASE")
    callback_nothing_after_present(call)
    assert context.stage == "products_absent_in_database"
    _, message_text, markup = mock_send_message[-1]
    assert message_text == RECOGNIZED_PRODUCTS_MISSING_IN_DATABASE
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Tea"
            if count == 1:
                assert button.callback_data == "Coffee"
            if count == 2:
                assert button.callback_data == "Nothing_to_edit_after_ABSENT_IN_DATABASE"
            count += 1

    # Pushing a button of absent_in_database product to correct the name
    edited_list_position = context.products_absent_in_database[0]
    call = fake_callback_query_factory(chat_id=chat_id, callback_data=edited_list_position["name"])
    callback_inline(call)

    assert 'handler' in captured_register_handler
    handler = captured_register_handler['handler']

    expected_message = CORRECTING_NAME.format(
        name = edited_list_position["name"],
    )
    _, message_text, _ = mock_send_message[-1]
    assert message_text == expected_message

    called = {}
    def fake_process_name_edit(message, list_position):
        called['status'] = True
        called['list_position'] = list_position
    monkeypatch.setattr("bot.__main__.process_name_edit", fake_process_name_edit)

    # Sending a message with product name
    message = FakeMessage(chat_id=chat_id, text="Tea_edited")
    handler(message)
    assert called.get('status', False) is True
    assert called['list_position'] == edited_list_position

    monkeypatch.setattr("bot.bot_utils.check_existent_categories", lambda context: None)
    context.existing_categories = ["Category_1", "Category_2"]
    process_name_edit(message, edited_list_position)
    expected_message = PPODUCT_MISSING_IN_DATABASE.format(
        name = message.text,
    )
    _, message_text, markup = mock_send_message[-1]
    assert message_text == expected_message
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == f"exist_cat:Category_1, prod:{edited_list_position["name"]}"
            if count == 1:
                assert button.callback_data == f"exist_cat:Category_2, prod:{edited_list_position["name"]}"
            if count == 2:
                assert button.callback_data == f"categ_cr, prod:{edited_list_position["name"]}"
            count += 1

    called = {}
    def fake_post_category_product(message, list_position):
        called['status'] = True
        called['list_position'] = list_position
    monkeypatch.setattr("bot.__main__.post_category_product", fake_post_category_product)

    # Pushing a new category creation button
    call = fake_callback_query_factory(chat_id=chat_id, callback_data=f"categ_cr, prod:{edited_list_position["name"]}")
    callback_category_creation(call)

    expected_message = SUGGESTION_TO_ENTER_CATEGORY_FOR_PRODUCT.format(
        product_name = edited_list_position["name"],
    )
    _, message_text, _ = mock_send_message[-1]
    assert message_text == expected_message

    # Sending a message with category name
    message = FakeMessage(chat_id=chat_id, text="New category")
    handler(message)
    assert called.get('status', False) is True
    assert called['list_position'] == edited_list_position

    post_category_product(message, edited_list_position["name"])
    expected_message = SUCCESSFUL_CATEGORY_CORRECT.format(
        category_name = message.text,
        product_name = edited_list_position["name"]
    )
    _, message_text, markup = mock_send_message[-1]
    assert message_text == expected_message
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == "Tea_edited"
            if count == 1:
                assert button.callback_data == "Coffee"
            if count == 2:
                assert button.callback_data == "Nothing_to_edit_after_ABSENT_IN_DATABASE"
            count += 1

    # Pushing "Nothing_to_edit_after_ABSENT_IN_DATABASE" button
    call = fake_callback_query_factory(chat_id=chat_id, callback_data="Nothing_to_edit_after_ABSENT_IN_DATABASE")
    responses = [
        (True, {"id": 1}),
        (True, {
            "id": 1,
            "name": "Eggs"
        }),
        (True, {
            "id": 2,
            "name": "Apples"
        }),
        (True, {
            "id": 3,
            "name": "Tea_edited"
        }),
        (False, None),
        (True, {
            "id": 4,
            "name": "Coffee"
        }),
        (True, {"id": 1})
    ]
    def fake_get_data_info(endpoint, name):
        while responses:
            return responses.pop(0)
    monkeypatch.setattr("bot.bot_utils.get_data_info", fake_get_data_info)

    callback_nothing_after_absent(call)

    assert context.new_expense == [{'name': 'Coffee', 'price': 5.5}]
    assert context.products_present_in_database == []
    assert context.products_absent_in_database ==[]

    product_missing_category = context.new_expense[0]
    _, message_text, _ = mock_send_message[-2]
    assert message_text == UPLOAD_EXPENCE
    expected_message = PPODUCT_MISSING_IN_DATABASE.format(
        name = product_missing_category["name"]
    )
    _, message_text, markup = mock_send_message[-1]
    assert message_text == expected_message
    count = 0
    for row in markup.keyboard:
        for button in row:
            if count == 0:
                assert button.callback_data == f"exist_cat:Category_1, prod:{product_missing_category["name"]}"
            if count == 1:
                assert button.callback_data == f"exist_cat:Category_2, prod:{product_missing_category["name"]}"
            if count == 2:
                assert button.callback_data == f"categ_cr, prod:{product_missing_category["name"]}"
            count += 1

    # Pushing an existing category button
    call = fake_callback_query_factory(
        chat_id=chat_id,
        callback_data=f"exist_cat:Category_1, prod:{product_missing_category["name"]}"
    )
    context.existing_categories_with_id = [{"name": "Category_1", "id": "1"},{"name": "Category_2", "id": "2"}]

    callback_existing_category(call)

    _, message_text, _ = mock_send_message[-1]
    assert message_text == SUCCESSFUL_UPLOAD_EXPENCE
    assert context.new_expense == []

