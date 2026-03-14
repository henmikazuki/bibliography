from flask import Flask, render_template, redirect, request, flash
from db import (
    get_books,
    get_book_detail,
    append_book_data,
    update_book_data,
    delete_book_data,
    close_db,
)

app = Flask(__name__)
app.secret_key = "secret_key"
app.teardown_appcontext(close_db)

STATUS_CHOICES = ["未読", "読書中", "読了", "破棄"]


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
        "memo": form.get("memo", ""),
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
        book_data["memo"],
        book_data["purchase_date"],
        book_data["read_date"],
    )

    return data


@app.route("/books")
def books():
    books = get_books()
    count = len(books)

    return render_template("books/index.html", books=books, count=count)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = get_book_detail(book_id)
    return render_template("books/detail.html", book=book)


@app.route("/books/new", methods=["GET", "POST"])
def new_book():
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        if not is_not_empty_required_fields(book_data):
            flash("タイトル、カテゴリー、ステータスは必須項目です。")
            return redirect("/books/new")

        return render_template("books/confirm.html", book_data=book_data, mode="create")
    if request.method == "GET":
        return render_template(
            "books/form.html", status_choices=STATUS_CHOICES, mode="create"
        )


@app.route("/books/new/confirm", methods=["GET", "POST"])
def confirm_new_book():
    if request.method == "POST":
        book = get_book_form_data(request.form)
        append_book_data(book)

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
            "books/confirm.html", book_data=book_data, book_id=book_id, mode="update"
        )
    if request.method == "GET":
        book = get_book_detail(book_id)
        return render_template(
            "books/form.html", book=book, status_choices=STATUS_CHOICES, mode="update"
        )


@app.route("/books/<int:book_id>/edit/confirm", methods=["GET", "POST"])
def confirm_edit_book(book_id):
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        update_book_data(book_id, book_data)

        flash("書籍を更新しました。")

        return redirect("/books")
    if request.method == "GET":
        return redirect(f"/books/{book_id}/edit")


@app.route("/books/<int:book_id>/delete", methods=["GET", "POST"])
def delete_book(book_id):
    if request.method == "POST":
        delete_book_data(book_id)

        flash("書籍を削除しました。")

        return redirect("/books")
    if request.method == "GET":
        book_data = get_book_detail(book_id)
        return render_template(
            "books/delete/delete.html", book_data=book_data, book_id=book_id
        )


if __name__ == "__main__":
    app.run(debug=True)
