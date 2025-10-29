import logging
import sqlite3

from typing import Optional, Tuple, List, Dict, Any
from .db.db import get_conn
from .file_operations import response_saving

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _row_to_dict(row): # done
    return dict(row) if row is not None else None

def _rows_to_list(rows):
    return [dict(r) for r in rows]

def _is_int_like(x): # done
    try:
        int(x)
        return True
    except Exception:
        return False

def _parse_period(period_str: str):
    """
    Поддерживаем форматы:
    - 'YYYY-MM-DD:YYYY-MM-DD' -> ('between', start, end)
    - 'created_at__gte=YYYY-MM-DD' -> ('>=', 'YYYY-MM-DD')
    - 'created_at__lte=YYYY-MM-DD' -> ('<=', 'YYYY-MM-DD')
    - 'YYYY-MM-DD' -> ('=', 'YYYY-MM-DD')
    Возвращает tuple (sql_fragment, params_list)
    created_at__range={three_days_ago},{datetime.date.today()
    created_at={today}
    """
    if not period_str:
        return None, []
    _, period = period_str.split(":", 1)
    return "created_at = ?", [period]

_ENDPOINT_MAP = {
    "category": {"table": "category", "name_col": "name", "pk": "id"},
    "product": {"table": "product", "name_col": "name", "pk": "id"},
    "currency": {"table": "currency", "name_col": "code", "pk": "id"},
    "user": {"table": "user", "name_col": "username", "pk": "id"},
    "expense": {"table": "expense", "name_col": None, "pk": "id"},
    "expense_item": {"table": "expense_item", "name_col": None, "pk": "id"},
}


def get_data_info_db(endpoint, data): ## done
    """
    Search entity, returns (True, first_match_dict) or (False, None).
    """
    logger.info(f"Checking the existance of the {endpoint} \"{data}\" in the database")
    try:
        spec = _ENDPOINT_MAP.get(endpoint)
        table = spec["table"]
        name_col = spec["name_col"]
        pk = spec["pk"]

        with get_conn() as conn:
            if name_col:
                sql = f"SELECT * FROM {table} WHERE {name_col} = ? LIMIT 1"
                row = conn.execute(sql, (data,)).fetchone()   # here is tuple
                if row:
                    logger.info(f"\"{data}\" is in the database")
                    return (True, _row_to_dict(row)) if row else (False, None)
                logger.info(f"\"{data}\" is not in the database")
                return False, None
            if _is_int_like(data):
                sql = f"SELECT * FROM {table} WHERE {pk} = ?"
                row = conn.execute(sql, (int(data),)).fetchone()
                if row:
                    logger.info(f"\"{data}\" is in the database")
                    return (True, _row_to_dict(row)) if row else (False, None)
                logger.info(f"\"{data}\" is not in the database")
                return False, None
    except Exception as e:
        logger.error(f"Search for '{data}' at the table '{endpoint}' failed: {e}")
        raise e


def check_existent_categories_db(context):
    """
    Check for existing categories, fills context.existing_categories.
    Return None.
    """
    logger.info("Checking the categories existing in the database")
    try:
        with get_conn() as conn:
            categories = conn.execute("SELECT id, name FROM category ORDER BY name").fetchall()
        context.existing_categories.clear()
        context.existing_categories_with_id.clear()
        dicts = _rows_to_list(categories)
        context.existing_categories_with_id.extend(dicts)
        for category in categories:
            context.existing_categories.append(category["name"])
        logger.info(f"existing_categories = {context.existing_categories}")
        logger.info(f"existing_categories_with_id = {context.existing_categories_with_id}")
    except Exception as e:
        logger.error(f"The request for database for existent categories failed: {e}")
        return None
    return


def post_data_info_db(endpoint, data):
    """
    Insert the record into the corresponding table.
    Return (True, new_id) or (False, None).
    Support: category, product, user, expense, expense_item.
    """
    logger.info(f"Posting to the endpoint \"{endpoint}\" the following data \"{data}\"")
    try:
        with get_conn() as conn:
            if endpoint == "category":
                name = data.get("name")
                cur = conn.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (name,))
                if cur.lastrowid:
                    logger.info(f"The {endpoint} data \"{data}\" was successfully posted to the database, id \"{cur.lastrowid}\"")
                    return True, cur.lastrowid
                else:
                    logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
                    row = conn.execute("SELECT id FROM category WHERE name = ?", (name,)).fetchone()
                    if row:
                        logger.info(f"The category with such name already exists, id \"{row}\"")
                    return False, None

            elif endpoint == "product":
                name = data.get("name")
                category_id = data.get("category")
                cur = conn.execute("INSERT OR IGNORE INTO product (name, category_id) VALUES (?, ?)", (name, category_id))
                if cur.lastrowid:
                    logger.info(f"The {endpoint} data \"{data}\" was successfully posted to the database, id \"{cur.lastrowid}\"")
                    return True, cur.lastrowid
                else:
                    logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
                    row = conn.execute("SELECT id FROM category WHERE name = ?", (name,)).fetchone()
                    if row:
                        logger.info(f"The category with such name already exists, id \"{row}\"")
                    return False, None

            elif endpoint == "user":
                chat_id = data.get("chat_id")
                username = data.get("username")
                first_name = data.get("first_name")
                last_name = data.get("last_name")
                cur = conn.execute(
                    'INSERT OR IGNORE INTO "user" (chat_id, username, first_name, last_name) VALUES (?, ?, ?, ?)',
                    (chat_id, username, first_name, last_name)
                )
                if cur.lastrowid:
                    logger.info(f"The {endpoint} data \"{data}\" was successfully posted to the database, id \"{cur.lastrowid}\"")
                    return True, cur.lastrowid
                else:
                    logger.info(f"Posting {endpoint} data \"{data}\" to the database was unsuccessfull")
                    row = conn.execute('SELECT id FROM "user" WHERE username = ? COLLATE NOCASE', (username,)).fetchone()
                    if row:
                        logger.info(f"The category with such name already exists, id \"{row}\"")
                    return False, None

            elif endpoint == "expense":
                user_id = data.get("user")
                cur = conn.execute("INSERT INTO expense (user_id) VALUES (?)",
                                    (user_id,))
                return True, cur.lastrowid

            elif endpoint == "expense_item": # item dict
                expense_id = data.get("expense")
                product_id = data.get("product")
                price = data.get("price")
                cur = conn.execute("INSERT INTO expense_item (expense_id, product_id, price) VALUES (?, ?, ?)",
                                   (expense_id, product_id, price))
                return True, cur.lastrowid

            # if endpoint == "currency":
            #     code = (data.get("code") or "").upper()
            #     if not code:
            #         return False, None
            #     cur = conn.execute("INSERT OR IGNORE INTO currency (code) VALUES (?)", (code,))
            #     if cur.lastrowid:
            #         return True, cur.lastrowid
            #     row = conn.execute("SELECT id FROM currency WHERE code = ?", (code,)).fetchone()
            #     return (True, row["id"]) if row else (False, None)
            logger.info(f"Posting to the unknown endpoint \"{endpoint}\" failed")
            return False, None

    except Exception as e:
        logger.error(f"Error posting {endpoint} data: {e}")
        raise e


def get_filtrated_info_db(endpoint, search_field, data, **kwargs):
    """
    Фильтрованный поиск. Возвращает (True, list_of_dicts) или (False, None).
    Поддерживаем common-сценарии:
      - product?name=... + category
      - expense?user=... + period
      - generic по колонке в той же таблице
    kwargs:
      - category: id или name (или строка формата 'category=3' — мы тоже позволяем)
      - period: см. _parse_period
    """
    try:
        endpoint = _ENDPOINT_MAP.get(endpoint)
        table = endpoint["table"]
        category = kwargs.get("category")
        period = kwargs.get("period")
        logger.info(f"Checking the existance of the {endpoint} filter \"{search_field}\" \"{data}\" in the database for category {category} period {period}")

        # Если category приходит в виде 'category=3' (как ваша старая функция),
        # попытемся извлечь значение
        if category and "=" in category:
            # пример: "category=3" -> берем правую часть
            try:
                category = category.split("=", 1)[1]
            except Exception:
                pass

        # подготовка period SQL и params
        period_sql = ""
        period_params = []
        if period:
            # return "created_at = ?", [period]
            parsed, p_params = _parse_period(period)
            if parsed:
                period_sql = f" AND {parsed}"
                period_params = p_params 

        with get_conn() as conn:
            params = []
            if endpoint == "expense":
                # поддерживаем поиск по username/user id или по id дара
                # базовый запрос — берем расходы с инфой о пользователе и валюте
                base = ("SELECT e.*, u.username as user_username, u.chat_id as user_chat_id, c.code as currency_code "
                        "FROM expense e JOIN \"user\" u ON e.user_id = u.id LEFT JOIN currency c ON e.currency_id = c.id WHERE 1=1")
                sql = base
                params = []
                # поиск по полю
                if search_field in ("user", "username"):
                    # data может быть username или id
                    if _is_int_like(data):
                        sql += " AND e.user_id = ?"
                        params.append(int(data))
                    else:
                        sql += " AND u.username LIKE '%' || ? || '%' COLLATE NOCASE"
                        params.append(data)
                elif search_field in ("id",):
                    sql += " AND e.id = ?"
                    params.append(int(data))
                # фильтр по category -> нужно связать через expense_item->product->category
                if category:
                    # join с expense_item->product->category
                    sql = ("SELECT DISTINCT e.*, u.username as user_username, u.chat_id as user_chat_id, c.code as currency_code "
                        "FROM expense e "
                        "JOIN \"user\" u ON e.user_id = u.id "
                        "LEFT JOIN currency c ON e.currency_id = c.id "
                        "JOIN expense_item ei ON ei.expense_id = e.id "
                        "JOIN product p ON p.id = ei.product_id "
                        "WHERE p.category_id = ?" )
                    params = [category]
                    # добавим поисковое поле если есть
                    if search_field in ("user", "username"):
                        if _is_int_like(data):
                            sql += " AND e.user_id = ?"
                            params.append(int(data))
                        else:
                            sql += " AND u.username LIKE '%' || ? || '%' COLLATE NOCASE"
                            params.append(data)
                    if period_sql:
                        sql += " AND " + period_sql[5:] if period_sql.startswith(" AND ") else " AND " + period_sql
                        # but easier is append period clause normally
                # period
                if period_sql:
                    # period_sql like " AND created_at BETWEEN ? AND ?"
                    # просто добавляем к sql и params
                    sql += " " + period_sql
                    params += period_params

                sql += " ORDER BY e.created_at DESC"
                rows = conn.execute(sql, params).fetchall()
                return True, _rows_to_list(rows)

            # --- generic for category/currency/user ---
            if endpoint in ("category", "currency", "user"):
                name_col = endpoint["name_col"]
                if search_field in (name_col, "search", "name", "username", "code"):
                    sql = f"SELECT * FROM {table} WHERE {name_col} LIKE '%' || ? || '%' COLLATE NOCASE ORDER BY {name_col} LIMIT 100"
                    rows = conn.execute(sql, (data,)).fetchall()
                    return True, _rows_to_list(rows)
                else:
                    # fallback: try equality on given field
                    sql = f"SELECT * FROM {table} WHERE {search_field} = ?"
                    rows = conn.execute(sql, (data,)).fetchall()
                    return True, _rows_to_list(rows)

            # --- default fallback: вернуть False (неизвестный кейс) ---
            return False, None
    except Exception as e:
        logger.error(f"Search for '{data}' at the table '{endpoint}' failed: {e}")
        raise e



