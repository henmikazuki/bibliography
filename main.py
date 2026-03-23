from flask import Flask, render_template, redirect, request, flash
from db import (
    get_books,
    get_book_detail,
    append_book_data,
    update_book_data,
    delete_book_data,
    close_db,
)
from datetime import datetime

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


def validate_dates(purchase_date, read_date):
    """購入日と読了日の妥当性を確認する

    :param purchase_date: 購入日
    :param read_date: 読了日
    :return: エラーメッセージのリスト
    """
    errors = []
    if purchase_date:
        try:
            purchase_date_obj = datetime.strptime(purchase_date, "%Y-%m-%d")
            if purchase_date_obj > datetime.today():
                errors.append("購入日が未来の日付になっています。")
        except ValueError:
            errors.append("購入日の形式が正しくありません。")
    if read_date:
        try:
            read_date_obj = datetime.strptime(read_date, "%Y-%m-%d")
            if not purchase_date:
                errors.append("購入日が未入力の場合、読了日は入力できません。")
            elif read_date_obj < purchase_date_obj:
                errors.append("読了日が購入日より前になっています。")
            if read_date_obj > datetime.today():
                errors.append("読了日が未来の日付になっています。")
        except ValueError:
            errors.append("読了日の形式が正しくありません。")
    if purchase_date and read_date:
        try:
            purchase_date_obj = datetime.strptime(purchase_date, "%Y-%m-%d")
            read_date_obj = datetime.strptime(read_date, "%Y-%m-%d")
            if purchase_date_obj > read_date_obj:
                errors.append("購入日が読了日より後になっています。")
        except ValueError:
            pass
    return errors


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
    sort = request.args.get("sort", "new")
    if sort == "new":
        order_sql = "created_at DESC"
    elif sort == "old":
        order_sql = "created_at ASC"
    books = get_books(order_sql)
    count = len(books)

    return render_template("books/index.html", books=books, count=count)


@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = get_book_detail(book_id)
    return render_template("books/detail.html", book=book)


@app.route("/books/new", methods=["GET", "POST"])
def new_book(book=None):
    if request.method == "POST":
        book_data = get_book_form_data(request.form)
        if not is_not_empty_required_fields(book_data):
            flash("タイトル、カテゴリー、ステータスは必須項目です。")
            return render_template(
                "books/form.html",
                book=book_data,
                status_choices=STATUS_CHOICES,
                mode="create",
            )

        errors = validate_dates(book_data["purchase_date"], book_data["read_date"])
        if errors:
            for error in errors:
                flash(error)
            return render_template(
                "books/form.html",
                book=book_data,
                status_choices=STATUS_CHOICES,
                mode="create",
            )
        return render_template("books/confirm.html", book_data=book_data, mode="create")

    if request.method == "GET":
        return render_template(
            "books/form.html",
            status_choices=STATUS_CHOICES,
            mode="create",
            book=book,
        )


@app.route("/books/new/confirm", methods=["GET", "POST"])
def confirm_new_book():
    if request.method == "POST":
        book = get_book_form_data(request.form)
        append_book_data(book)

        flash(f"「{book['title']}」を登録しました。")

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

        flash(f"「{book_data['title']}」を更新しました。")

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
