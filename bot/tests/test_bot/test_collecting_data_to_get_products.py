import os
from ...bot_utils import collecting_data_to_get_products

def test_collecting_data_to_get_products(monkeypatch, mock_get_data_info_mixed, fake_context_without_absent):
    test_filepath = os.path.join(os.getcwd(), "test_receipts", "test_recognised_receipt.json")
    fake_context_without_absent.products_present_in_database = []

    collecting_data_to_get_products(test_filepath, fake_context_without_absent)

    products_present_in_database = [{"name": "Eggs", "price": 100, "id": 1}, {"name": "Apples", "price": 200, "id": 2}]
    products_absent_in_database = [{"name": "Tea", "price": 114}, {"name": "Coffee", "price": 550}]
    assert fake_context_without_absent.products_present_in_database == products_present_in_database
    assert fake_context_without_absent.products_absent_in_database == products_absent_in_database