"""
    Database Models for Book Alchemy
    --------------------------------

    Defines SQLAlchemy ORM models used in the Book Alchemy Flask app.

    Models:
    - Author: Represents an author with optional image, summary, and birth/death dates.
    - Book: Represents a book linked to an author, with ISBN, title, rating, and optional description.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
        Represents an author in the database.

        Attributes:
            id (int): Primary key.
            name (str): Full name of the author.
            birth_date (str): Optional birth date.
            date_of_death (str): Optional date of death.
            summary (str): Summary (e.g., from Wikipedia).
            image_url (str): URL to author's image.
            books (relationship): One-to-many with Book.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.String)
    date_of_death = db.Column(db.String)
    summary = db.Column(db.Text)
    image_url = db.Column(db.String)

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        return self.name


class Book(db.Model):
    """
        Represents a book in the database.

        Attributes:
            id (int): Primary key.
            title (str): Book title.
            isbn (str): ISBN number.
            publication_year (str): Year of publication.
            rating (float): Rating out of 5.
            summary (str): Book description.
            author_id (int): Foreign key to Author.
            author (relationship): Backref to author.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id', ondelete="CASCADE"), nullable=False)
    summary = db.Column(db.Text)

    author = db.relationship("Author", backref=db.backref("books", cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<Book {self.title}>"

    def __str__(self):
        return self.title
