"""
    Book Alchemy Web App
    --------------------

    This Flask application allows users to manage a small digital library by adding authors and books
    to a connected SQLite database. It includes features such as book ratings, search, Wikipedia integration,
    and personalized suggestions.

    Key Routes:
    - /: Home page with sorting and keyword search
    - /add_author: Add a new author to the database
    - /add_book: Add a book linked to an existing author
    - /book/<book_id>: View book details
    - /author/<author_id>: View author details
    - /book/<book_id>/update: Update book information
    - /author/<author_id>/update: Update author information
    - /book/<book_id>/delete: Delete a book
    - /author/<author_id>/delete: Delete an author (and their books)
    - /suggest: Get a random book suggestion

    Built with Flask, SQLAlchemy, and Wikipedia API.
"""

import os
import random
import wikipedia
import logging
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy.orm import joinedload
from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "data", "library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

db.init_app(app)


logging.basicConfig(level=logging.INFO)


def fetch_wikipedia_summary_and_image(name):
    """
        Fetches a summary and the first available image for a given name from Wikipedia.

        Args:
            name (str): The name to search on Wikipedia.

        Returns:
            tuple: (summary string, image URL or None)
    """

    try:
        logging.info(f"Fetching Wikipedia data for: {name}")
        page = wikipedia.page(name, auto_suggest=False)

        summary = page.summary

        valid_images = [
            img for img in page.images
            if img.lower().endswith((".jpg", ".jpeg", ".png"))
               and "wikimedia" in img.lower()
               and not any(word in img.lower() for word in [
                "logo", "icon", "book", "cover", "symbol", "seal", "map", "house", "building"
            ])
               and any(name_part.lower() in img.lower() for name_part in name.split())
        ]

        if valid_images:
            image_url = valid_images[0]
            logging.info(f"Valid image found for {name}: {image_url}")
        else:
            image_url = None
            logging.warning(f"No valid image found for {name}")

        return summary, image_url

    except wikipedia.DisambiguationError as e:
        logging.warning(f"Disambiguation error for '{name}': {e.options}")
        return "Biography not available (disambiguation).", None
    except wikipedia.PageError:
        logging.warning(f"No Wikipedia page found for: {name}")
        return "Biography not available (not found).", None
    except Exception as e:
        logging.error(f"Unexpected error for '{name}': {e}")
        return "Biography not available (error).", None


def fetch_wikipedia_book_summary(title, author_name):
    """
       Fetches a summary of a book from Wikipedia using its title and author.

       Args:
           title (str): Book title.
           author_name (str): Author name.

       Returns:
           str: Wikipedia summary or fallback message.
    """

    try:
        page = wikipedia.page(title, auto_suggest=False)
        return page.summary
    except wikipedia.DisambiguationError as e:
        try:
            search_term = f"{title} ({author_name})"
            page = wikipedia.page(search_term, auto_suggest=True)
            return page.summary
        except Exception:
            return "Summary not available (ambiguous)."
    except Exception:
        return "Summary not available."


@app.route("/")
def home():
    """
        Home page that displays all books in the library with search and sorting options.

        Query Params:
            q (str): Keyword to search for in book titles.
            sort (str): Sort by 'title' or 'author'.
            message (str): Optional feedback message.

        Returns:
            Rendered template for the home page.
    """

    search_query = request.args.get("q", "").strip()
    sort = request.args.get("sort", "title")
    message = request.args.get("message")

    books_query = Book.query.options(joinedload(Book.author))

    if search_query:
        books_query = books_query.filter(Book.title.ilike(f"%{search_query}%"))

    if sort == "author":
        books_query = books_query.join(Author).order_by(Author.name)
    else:
        books_query = books_query.order_by(Book.title)

    books = books_query.all()

    return render_template("home.html", books=books, sort=sort,
                           search_query=search_query, message=message)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
        Page to add a new author. Uses Wikipedia for optional image and summary.

        On GET: Renders the add author form.
        On POST: Processes form submission and adds author to the database.

        Returns:
            Rendered template for the add author form.
    """

    message = None
    if request.method == "POST":
        name = request.form.get("name")
        birth_date = request.form.get("birth_date")
        date_of_death = request.form.get("date_of_death")

        if name:
            summary, image_url = fetch_wikipedia_summary_and_image(name)
            new_author = Author(name=name, birth_date=birth_date,
                                date_of_death=date_of_death, summary=summary, image_url=image_url)

            db.session.add(new_author)
            db.session.commit()
            message = f"Author '{name}' added successfully!"

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
        Page to add a new book to the library. Connects to an existing author.

        On GET: Displays form with author dropdown.
        On POST: Adds new book, pulls summary from Wikipedia.

        Returns:
            Rendered template for the add book form.
    """

    message = None
    authors = Author.query.all()

    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")
        rating = request.form.get("rating")

        if title and isbn and author_id:
            author = Author.query.get(author_id)
            summary = fetch_wikipedia_book_summary(title, author.name)

            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=publication_year,
                author_id=author_id,
                rating=rating if rating else None,
                summary=summary
            )
            db.session.add(new_book)
            db.session.commit()
            message = f"Book '{title}' added successfully!"

    return render_template("add_book.html",
                           authors=authors, message=message)


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    """
        Displays detailed view of a specific book.

        Args:
            book_id (int): ID of the book.

        Returns:
            Rendered template for the book detail page.
    """

    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html",
                           book=book)


@app.route("/book/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    """
        Handles rating submission for a specific book.

        Args:
            book_id (int): ID of the book to rate.

        Returns:
            Redirect to book detail with updated rating.
    """

    book = Book.query.get_or_404(book_id)
    new_rating = request.form.get("rating")

    if new_rating:
        try:
            book.rating = float(new_rating)
            db.session.commit()
            message = f"Rating for '{book.title}' updated to {book.rating}/10."
        except ValueError:
            message = "Invalid rating value."
    else:
        message = "No rating provided."

    return redirect(url_for("book_detail", book_id=book_id, message=message))


@app.route("/author/<int:author_id>")
def author_detail(author_id):
    """
        Displays detailed view of a specific author and their books.

        Args:
            author_id (int): ID of the author.

        Returns:
            Rendered template for author detail.
    """

    author = Author.query.get_or_404(author_id)
    return render_template("author_detail.html",
                           author=author)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
        Deletes a book from the database. Also deletes its author if no other books remain.

        Args:
            book_id (int): ID of the book to delete.

        Returns:
            Redirect to home with success message.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    if not author.books:
        db.session.delete(author)
        db.session.commit()
        message = (f"Book '{book.title}' and author '{author.name}'"
                   f" deleted successfully.")
    else:
        message = f"Book '{book.title}' deleted successfully."

    return redirect(url_for("home", message=message))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    """
        Deletes an author and all books associated with them.

        Args:
            author_id (int): ID of the author to delete.

        Returns:
            Redirect to home with success message.
    """

    author = Author.query.get_or_404(author_id)

    for book in author.books:
        db.session.delete(book)

    db.session.delete(author)
    db.session.commit()

    message = f"Author '{author.name}' and all their books were deleted."
    return redirect(url_for("home", message=message))


@app.route("/book/<int:book_id>/update", methods=["GET", "POST"])
def update_book(book_id):
    """
        Allows updating of an existing book's details.

        Args:
            book_id (int): ID of the book.

        Returns:
            Rendered update form or redirect after saving.
    """

    book = Book.query.get_or_404(book_id)
    authors = Author.query.all()

    if request.method == "POST":
        book.title = request.form.get("title")
        book.isbn = request.form.get("isbn")
        book.publication_year = request.form.get("publication_year")
        book.rating = request.form.get("rating")
        book.author_id = request.form.get("author_id")

        db.session.commit()
        return redirect(url_for("book_detail", book_id=book.id))

    return render_template("update_book.html", book=book, authors=authors)


@app.route("/author/<int:author_id>/update", methods=["GET", "POST"])
def update_author(author_id):
    """
        Updates details of an existing author.

        Args:
            author_id (int): ID of the author.

        Returns:
            Rendered update form or redirect after saving.
    """

    author = Author.query.get_or_404(author_id)

    if request.method == "POST":
        author.name = request.form.get("name")
        author.birth_date = request.form.get("birth_date")
        author.date_of_death = request.form.get("date_of_death")
        db.session.commit()
        return redirect(url_for("author_detail", author_id=author.id))

    return render_template("update_author.html", author=author)


@app.route("/suggest", methods=["GET", "POST"])
def suggest_book():
    """
        Suggests a random book from a predefined list.

        On GET: Displays current library.
        On POST: Shows a random suggestion.

        Returns:
            Rendered template for suggestion view.
    """

    books = Book.query.options(joinedload(Book.author)).all()
    message = None

    if request.method == "POST":
        suggestions = [
            "‘Autobiography of a Yogi’ by Paramahansa Yogananda",
            "‘Meditations’ by Roman Emperor Marcus Aurelius",
            "‘The Obstacle Is the Way’ by Stoic philosophy",
            "‘Wherever You Go, There You Are’ by Jon Kabat-Zinn",
            "‘The Complete Illustrated Book of Yoga’ by Swami Vishnudevananda",
            "‘Duende’ by Jason Webster",
            "‘El Arte Flamenco de la Guitarra’ by Juan Martín",
            "‘All Music Guide to the Blues’ by All Media Guide",
            "‘Exciting Concepts for Blues Guitar Soloing’ by Barry Levenson"
        ]
        message = f"We suggest you read: {random.choice(suggestions)}"

    return render_template("suggest.html", books=books, message=message)


if __name__ == "__main__":
    app.run(debug=True)
    # with app.app_context():
        # db.create_all()
