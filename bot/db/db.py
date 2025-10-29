import sqlite3
from contextlib import contextmanager
from typing import Optional, Tuple, List, Dict, Any

DB_PATH = "bot_data.sqlite"

def _connect():
    """
    Возвращает соединение, настраивает полезные pragma.
    Используйте это для каждого нового соединения.
    """
    # conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Включаем foreign keys и WAL для лучшей работы
    conn.execute("PRAGMA foreign_keys = ON;")
    # conn.execute("PRAGMA journal_mode = WAL;")
    # conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

@contextmanager
def get_conn():
    """Контекстный менеджер: автоматически commit/rollback при выходе."""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Создаёт таблицы, если их ещё нет."""
    schema = """
    CREATE TABLE IF NOT EXISTS currency (
        id INTEGER PRIMARY KEY,
        code TEXT NOT NULL CHECK (length(code) <= 3)
    );
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY,
        name TEXT COLLATE NOCASE NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY,
        name TEXT COLLATE NOCASE NOT NULL UNIQUE,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        username TEXT UNIQUE,
        first_name TEXT,
        last_name TEXT,
        default_currency_id INTEGER,
        FOREIGN KEY (default_currency_id) REFERENCES currency(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS expense (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        currency_id INTEGER,
        created_at DATE DEFAULT (DATE('now')),
        FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
        FOREIGN KEY (currency_id) REFERENCES currency(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS expense_item (
        id INTEGER PRIMARY KEY,
        expense_id INTEGER NOT NULL,
        product_id INTEGER,
        price INTEGER NOT NULL CHECK (price > 0),
        FOREIGN KEY (expense_id) REFERENCES expense(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE SET NULL
    );
    """
    with get_conn() as conn:
        conn.executescript(schema)

        categories = [
                ("Grocery",),
                ("Toys",),
                ("Car",),
                ("Housing",),
                ("Household needs",),
                ("Entertainments",),
            ]
        conn.executemany("INSERT OR IGNORE INTO category (name) VALUES (?)", categories)

# # -----------------------
# # CRUD: Currency
# # -----------------------
# def add_currency(code: str) -> int:
#     with get_conn() as conn:
#         cur = conn.execute("INSERT INTO currency (code) VALUES (?)", (code.upper(),))
#         return cur.lastrowid

# def get_currency_by_code(code: str) -> Optional[sqlite3.Row]:
#     with get_conn() as conn:
#         cur = conn.execute("SELECT * FROM currency WHERE code = ?", (code.upper(),))
#         return cur.fetchone()

# # -----------------------
# # CRUD: Category & Product
# # -----------------------
# def add_category(name: str) -> int:
#     with get_conn() as conn:
#         cur = conn.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (name,))
#         return cur.lastrowid or conn.execute("SELECT id FROM category WHERE name = ?", (name,)).fetchone()["id"]

# def add_product(name: str, category_id: int) -> int:
#     with get_conn() as conn:
#         cur = conn.execute("INSERT INTO product (name, category_id) VALUES (?, ?)", (name, category_id))
#         return cur.lastrowid

# def get_products_by_category(category_id: int) -> List[sqlite3.Row]:
#     with get_conn() as conn:
#         cur = conn.execute("SELECT * FROM product WHERE category_id = ?", (category_id,))
#         return cur.fetchall()

# # -----------------------
# # CRUD: User
# # -----------------------
# def add_user(chat_id: int, username: str, first_name: str = "", last_name: str = "") -> int:
#     with get_conn() as conn:
#         cur = conn.execute(
#             "INSERT OR IGNORE INTO \"user\" (chat_id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
#             (chat_id, username, first_name, last_name)
#         )
#         if cur.lastrowid:
#             return cur.lastrowid
#         # если уже был такой username — вернуть id
#         row = conn.execute("SELECT id FROM \"user\" WHERE username = ?", (username,)).fetchone()
#         return row["id"]

# def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
#     with get_conn() as conn:
#         return conn.execute("SELECT * FROM \"user\" WHERE username = ?", (username,)).fetchone()

# def update_user_default_currency(user_id: int, currency_id: Optional[int]):
#     with get_conn() as conn:
#         conn.execute("UPDATE \"user\" SET default_currency_id = ? WHERE id = ?", (currency_id, user_id))

# # -----------------------
# # CRUD: Expense & ExpenseItem
# # -----------------------
# def add_expense(user_id: int, currency_id: Optional[int] = None, created_at: Optional[str] = None) -> int:
#     """
#     Если currency_id is None — используем default_currency пользователя (если задан).
#     created_at — строка 'YYYY-MM-DD' или None (по умолчанию DATE('now')).
#     """
#     with get_conn() as conn:
#         if currency_id is None:
#             row = conn.execute("SELECT default_currency_id FROM \"user\" WHERE id = ?", (user_id,)).fetchone()
#             currency_id = row["default_currency_id"] if row else None
#         if created_at:
#             cur = conn.execute(
#                 "INSERT INTO expense (user_id, currency_id, created_at) VALUES (?, ?, ?)",
#                 (user_id, currency_id, created_at)
#             )
#         else:
#             cur = conn.execute(
#                 "INSERT INTO expense (user_id, currency_id) VALUES (?, ?)",
#                 (user_id, currency_id)
#             )
#         return cur.lastrowid

# def add_expense_items(expense_id: int, items: List[Dict]):
#     """
#     items: список словарей {'product_id': int or None, 'price': int}
#     Использует executemany для скорости.
#     """
#     params = [(expense_id, it.get("product_id"), it["price"]) for it in items]
#     with get_conn() as conn:
#         conn.executemany("INSERT INTO expense_item (expense_id, product_id, price) VALUES (?, ?, ?)", params)

# def get_expense_with_items(expense_id: int) -> Optional[Dict]:
#     with get_conn() as conn:
#         exp = conn.execute(
#             "SELECT e.*, u.username, c.code as currency_code "
#             "FROM expense e "
#             "JOIN \"user\" u ON e.user_id = u.id "
#             "LEFT JOIN currency c ON e.currency_id = c.id "
#             "WHERE e.id = ?",
#             (expense_id,)
#         ).fetchone()
#         if not exp:
#             return None
#         items = conn.execute(
#             "SELECT ei.*, p.name as product_name FROM expense_item ei LEFT JOIN product p ON ei.product_id = p.id WHERE ei.expense_id = ?",
#             (expense_id,)
#         ).fetchall()
#         return {
#             "expense": dict(exp),
#             "items": [dict(r) for r in items]
#         }

# # Пример удаления (product)
# def delete_product(product_id: int):
#     with get_conn() as conn:
#         conn.execute("DELETE FROM product WHERE id = ?", (product_id,))


