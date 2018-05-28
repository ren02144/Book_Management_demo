from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
'''
This is a program for a simple books management system.
'''

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ren921107@localhost/flaskbook'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hahaha'
db = SQLAlchemy(app)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)

    books = db.relationship('Book', backref='author')

    def __repr__(self):
        return 'Author: %s' % self.name


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __repr__(self):
        return 'Book: %s %s' % (self.name, self.author_id)


class AuthorForm(FlaskForm):
    author = StringField('Author', validators=[DataRequired()])
    book = StringField('Book', validators=[DataRequired()])
    submit = SubmitField('Submit', validators=[DataRequired()])


@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        try:
            Book.query.filter_by(author_id=author.id).delete()
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('Delete author failed')
            db.session.rollback()

    else:
        flash('Can\'t find author')

    return redirect(url_for('hello_world'))


@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('Delete book failed')
            db.session.rollback()

    else:
        flash('Can\'t find book')

    return redirect(url_for('hello_world'))


@app.route('/', methods=['GET', 'POST'])
def hello_world():

    authorform = AuthorForm()

    # Get input for new author and books
    if authorform.validate_on_submit():
        author_name = authorform.author.data
        book_name = authorform.book.data

        author = Author.query.filter_by(name=author_name).first()

        if author:
            book = Book.query.filter_by(name=book_name).first()
            if book:
                flash('Book exists already')
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    flash('Adding new book failed')
                    db.session.rollback()

        else:
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()
                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(e)
                flash('Adding new author and book failed')
                db.session.rollback()

    else:
        if request.method == 'POST':
            flash('Input Error')

    authors = Author.query.all()
    return render_template('books.html', authors=authors, form=authorform)


if __name__ == '__main__':
    db.drop_all()
    db.create_all()

    au1 = Author(name='Wang')
    au2 = Author(name='Liu')
    au3 = Author(name='Zhang')
    db.session.add_all([au1, au2, au3])
    db.session.commit()

    bk1 = Book(name='The Hunger Games', author_id=au1.id)
    bk2 = Book(name='To Kill a Mockingbird', author_id=au1.id)
    bk3 = Book(name='The Book Thief', author_id=au2.id)
    bk4 = Book(name='Animal Farm', author_id=au3.id)
    bk5 = Book(name='Gone with the Wind', author_id=au3.id)
    db.session.add_all([bk1, bk2, bk3, bk4, bk5])
    db.session.commit()

    app.run(debug=True)
