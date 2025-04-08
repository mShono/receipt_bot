STAGE = ""
PRODUCTS_PRESENT_IN_DATABASE = []
PRODUCTS_ABSENT_IN_DATABASE = []
NEW_EXPENSE = []
EXISTING_CATEGORIES = []
EXISTING_CATEGORIES_WITH_ID = []


class Context:
    chat_id: str
    stage = ""
    products_present_in_database = []
    products_absent_in_database = []
    expense_id = None
    new_expense = []
    existing_categories = []
    existing_categories_with_id = []


UserContext = {
}  # user_id -> Context