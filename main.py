from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

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


@app.route('/books')
def books():
    con, csr = db_connection()

    sql = 'SELECT id, title, category, status, purchase_date, read_date FROM books WHERE deleted = 0 ORDER BY created_at DESC'
    csr.execute(sql)
    books = csr.fetchall()
    con.close()

    return render_template('books/index.html', books=books)


@app.route('/books/new')
def new_book():
    return render_template('books/new/registration.html')


@app.route('/books/<int:book_id>/edit')
def edit_book(book_id):
    return render_template('books/edit/edit.html')


@app.route('/books/<int:book_id>/delete')
def delete_book(book_id):
    return render_template('books/delete/delete.html')


if __name__ == '__main__':
    app.run(debug=True)
