from flask import Flask, render_template

app = Flask(__name__)

@app.route('/books')
def books():
    return render_template('books/index.html')

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