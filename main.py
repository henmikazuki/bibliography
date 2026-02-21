from flask import Flask, render_template, redirect, request, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"


def get_db_connection(db_path):
    """データベースの接続情報を取得する

    :param db_path: データベースファイルのパス
    """
    con = sqlite3.connect(db_path)
    return con


def db_connection():
    """データベースに接続する

    :return: データベースの接続情報、カーソル
    """
    db = "books.db"
    con = get_db_connection(db)
    csr = con.cursor()

    return con, csr


def is_not_empty_required_fields(book_data):
    """必須項目が空でないかを確認する

    :param book_data: 書籍データの辞書
    :return: 必須項目が空でない場合はTrue、空の場合はFalse
    """
    required_fields = ["title", "category", "status"]
    for field in required_fields:
        if not book_data.get(field):
            return False
    return True


def get_book_form_data(form):
    """フォームから書籍データを辞書で取得
    :param form: フォームデータ
    :return: 書籍データの辞書
    """
    return {
        "title": form.get("title", ""),
        "category": form.get("category", ""),
        "status": form.get("status", ""),
        "purchase_date": form.get("purchase_date", ""),
        "read_date": form.get("read_date", ""),
    }


def sql_statement_construction(book_data):
    """SQL文の構築に必要な値を取得する
    :param book_data: 書籍データの辞書
    :return: SQL文の構築に必要な値
    """
    data = (
        book_data["title"],
        book_data["category"],
        book_data["status"],
        book_data["purchase_date"],
        book_data["read_date"],
    )

    return data


@app.route("/books")
def books():
    con, csr = db_connection()

    sql = (
        "SELECT id, title, category, status, purchase_date, read_date "
        "FROM books WHERE deleted = 0 ORDER BY created_at DESC"
    )
    csr.execute(sql)
    books = csr.fetchall()
    con.close()

    return render_template("books/index.html", books=books)


@app.route("/books/new", methods=["GET", "POST"])
def new_book():
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        if not is_not_empty_required_fields(book_data):
            flash("タイトル、カテゴリー、ステータスは必須項目です。")
            return redirect("/books/new")

        return render_template("books/new/confirm.html", book_data=book_data)
    if request.method == "GET":
        return render_template("books/new/registration.html")


@app.route("/books/new/confirm", methods=["GET", "POST"])
def confirm_new_book():
    if request.method == "POST":
        book = get_book_form_data(request.form)
        con, csr = db_connection()

        sql = (
            "INSERT INTO books (title, category, status, purchase_date, read_date, "
            "deleted, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, 0, "
            'datetime("now", "localtime"), datetime("now", "localtime"))'
        )
        csr.execute(
            sql,
            sql_statement_construction(book),
        )
        con.commit()
        con.close()

        flash("書籍を登録しました。")

        return redirect("/books")
    if request.method == "GET":
        return redirect("/books/new")


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        if not is_not_empty_required_fields(book_data):
            flash("タイトル、カテゴリー、ステータスは必須項目です。")
            return redirect(f"/books/{book_id}/edit")

        return render_template(
            "books/edit/confirm.html", book_data=book_data, book_id=book_id
        )
    if request.method == "GET":
        con, csr = db_connection()
        sql = (
            "SELECT id, title, category, status, purchase_date, read_date FROM books "
            "WHERE id = ?"
        )
        csr.execute(sql, (book_id,))
        book = csr.fetchone()
        con.close()

        return render_template("books/edit/edit.html", book=book)


@app.route("/books/<int:book_id>/edit/confirm", methods=["GET", "POST"])
def confirm_edit_book(book_id):
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        con, csr = db_connection()
        sql = (
            "UPDATE books SET title = ?, category = ?, status = ?, "
            "purchase_date = ?, read_date = ?, updated_at = "
            'datetime("now", "localtime") WHERE id = ?'
        )
        csr.execute(sql, sql_statement_construction(book_data) + (book_id,))
        con.commit()
        con.close()

        flash("書籍を更新しました。")

        return redirect("/books")
    if request.method == "GET":
        return redirect(f"/books/{book_id}/edit")


@app.route("/books/<int:book_id>/delete", methods=["GET", "POST"])
def delete_book(book_id):
    con, csr = db_connection()
    if request.method == "POST":
        sql = (
            "UPDATE books SET deleted = 1, updated_at = datetime('now', 'localtime') "
            "WHERE id = ?"
        )
        csr.execute(sql, (book_id,))
        con.commit()
        con.close()

        flash("書籍を削除しました。")

        return redirect("/books")
    if request.method == "GET":
        sql = (
            "SELECT id, title, category, status, purchase_date, read_date "
            "FROM books WHERE id = ?"
        )
        csr.execute(sql, (book_id,))
        book = csr.fetchone()
        book_data = {
            "title": book[1],
            "category": book[2],
            "status": book[3],
            "purchase_date": book[4],
            "read_date": book[5],
        }
        con.close()
        return render_template(
            "books/delete/delete.html", book_data=book_data, book_id=book_id
        )


if __name__ == "__main__":
    app.run(debug=True)
