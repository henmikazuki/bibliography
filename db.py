import sqlite3
from flask import g


DATABASE = "books.db"


def get_db():
    """データベースに接続する

    :return: データベースの接続情報
    """
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """データベースの接続を閉じる"""
    db = g.pop("db", None)

    if db is not None:
        db.close()


# TODO: フィルタ未選択時はパラメータに乗せないようにする。優先度低め。
def get_books(filter_sql, params, order="DESC"):
    """書籍データを取得する
    :param filter: フィルタの内容
    :param order: 書籍データの並び順（ASCまたはDESC）
    :return: 書籍データのリスト
    """
    sql = f"SELECT * FROM books WHERE deleted = 0 {filter_sql} ORDER BY created_at {order}"

    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def get_book_detail(book_id):
    """書籍の詳細データを取得する
    :param book_id: 書籍ID
    :return: 書籍データの辞書
    """
    sql = (
        "SELECT id, title, category, status, memo, purchase_date, read_date "
        "FROM books WHERE id = ? AND deleted = 0"
    )

    with get_db() as conn:
        return conn.execute(sql, (book_id,)).fetchone()


def append_book_data(book_data):
    """書籍データを追加する
    :param book_data: 書籍データの辞書
    """
    sql = (
        "INSERT INTO books (title, category, status, memo, purchase_date, "
        "read_date, deleted, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, 0, "
        'datetime("now", "localtime"), datetime("now", "localtime"))'
    )
    data = (
        book_data["title"],
        book_data["category"],
        book_data["status"],
        book_data["memo"],
        book_data["purchase_date"] if book_data["purchase_date"] else None,
        book_data["read_date"] if book_data["read_date"] else None,
    )

    with get_db() as conn:
        conn.execute(sql, data)


def update_book_data(book_id, book_data):
    """書籍データを更新する
    :param book_id: 書籍ID
    :param book_data: 書籍データの辞書
    """
    sql = (
        "UPDATE books SET title = ?, category = ?, status = ?, memo = ?, "
        "purchase_date = ?, read_date = ?, updated_at = "
        'datetime("now", "localtime") WHERE id = ?'
    )
    data = (
        book_data["title"],
        book_data["category"],
        book_data["status"],
        book_data["memo"],
        book_data["purchase_date"] if book_data["purchase_date"] else None,
        book_data["read_date"] if book_data["read_date"] else None,
        book_id,
    )

    with get_db() as conn:
        conn.execute(sql, data)


def delete_book_data(book_id):
    """書籍データを削除する
    :param book_id: 書籍ID
    """
    sql = (
        "UPDATE books SET deleted = 1, updated_at = datetime('now', 'localtime') "
        "WHERE id = ?"
    )

    with get_db() as conn:
        conn.execute(sql, (book_id,))
