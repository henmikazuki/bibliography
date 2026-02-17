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


def get_book_form_data(form):
    """フォームから書籍データを辞書で取得"""
    return {
        "title": form.get("title", ""),
        "category": form.get("category", ""),
        "status": form.get("status", ""),
        "purchase_date": form.get("purchase_date", ""),
        "read_date": form.get("read_date", ""),
    }


@app.route("/books")
def books():
    con, csr = db_connection()

    sql = "SELECT id, title, category, status, purchase_date, read_date FROM books WHERE deleted = 0 ORDER BY created_at DESC"
    csr.execute(sql)
    books = csr.fetchall()
    con.close()

    return render_template("books/index.html", books=books)


@app.route("/books/new", methods=["GET", "POST"])
def new_book():
    if request.method == "POST":
        book_data = get_book_form_data(request.form)

        return render_template("books/new/confirm.html", book_data=book_data)
    if request.method == "GET":
        return render_template("books/new/registration.html")


@app.route("/books/new/confirm", methods=["GET", "POST"])
def confirm_book():
    if request.method == "POST":
        book = get_book_form_data(request.form)
        con, csr = db_connection()

        sql = 'INSERT INTO books (title, category, status, purchase_date, read_date, deleted, created_at, updated_at) VALUES (?, ?, ?, ?, ?, 0, datetime("now", "localtime"), datetime("now", "localtime"))'
        csr.execute(
            sql,
            (
                book["title"],
                book["category"],
                book["status"],
                book["purchase_date"],
                book["read_date"],
            ),
        )
        con.commit()
        con.close()

        flash("書籍を登録しました。")

        return redirect("/books")
    if request.method == "GET":
        return redirect("/books/new")


@app.route("/books/<int:book_id>/edit")
def edit_book(book_id):
    return render_template("books/edit/edit.html")


@app.route("/books/<int:book_id>/delete")
def delete_book(book_id):
    return render_template("books/delete/delete.html")


if __name__ == "__main__":
    app.run(debug=True)
