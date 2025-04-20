# 📚 Book Alchemy

Book Alchemy is a cozy digital library built with Flask and SQLAlchemy where you can:

- Add and manage books and authors
- View detailed pages for each book and author
- Rate books on a scale from 1 to 5
- Get AI-powered book suggestions
- Search and sort your library
- Enjoy a fully redesigned UI styled for elegance and readability

---

## ✨ Features

- 📖 Add, view, update, and delete books and authors
- 🌟 Book ratings (1–5)
- 🔍 Search by title with sorting options: title, author, rating, or year
- 💡 AI-style random book suggestions (based on genres like spirituality, stoicism, music, etc.)
- 💻 Responsive and animated UI built with custom CSS
- 🔗 Wikipedia integration for summaries and images

---

## 🛠 Tech Stack

- Python + Flask
- SQLAlchemy + SQLite
- HTML + Jinja Templates
- CSS3 (fully custom and responsive)
- Wikipedia API (via `wikipedia` Python package)

---

## 🚀 Running the App

1. **Create the environment**:
   ```bash
   python3 -m venv .venv

2. **Activate it**:

- macOS/Linux:
  ```bash
  source .venv/bin/activate

- Windows:
  ```bash
  .venv\Scripts\activate

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

4. **Run the Flask app**:
   ```bash
   python3 app.py

5. Visit http://localhost:5000 in your browser.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE). 
See the [LICENSE](LICENSE) file for full details.

---

## 👊🏼 Contributing
Have a fix or a feature to add? Feel free to submit a Pull Request. 
For any large changes, please open an issue first to discuss.