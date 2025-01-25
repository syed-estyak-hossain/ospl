from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Path for storing uploaded books
UPLOAD_FOLDER = 'books/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database file
DATABASE = "library.db"

# Initialize the database and add predefined data if empty
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Create books and downloads tables
        cursor.execute('''
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                file TEXT NOT NULL,
                category TEXT,
                added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_downloaded TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
        ''')
        conn.commit()

        # Add predefined books automatically
        sample_books = [
            ('Python Programming', 'John Doe', 'python_programming.pdf', 'Programming'),
            ('Learn Flask', 'Jane Smith', 'learn_flask.pdf', 'Web Development'),
            ('Web Development', 'James Brown', 'web_development.pdf', 'Web Development'),
            ('Data Science Fundamentals', 'Alice Johnson', 'data_science_fundamentals.pdf', 'Data Science'),
            ('Machine Learning Basics', 'Bob White', 'machine_learning_basics.pdf', 'Machine Learning'),
            ('Introduction to Algorithms', 'Mark Lee', 'intro_to_algorithms.pdf', 'Algorithms'),
            ('Web Scraping with Python', 'Emily Clark', 'web_scraping_with_python.pdf', 'Web Scraping'),
            ('Artificial Intelligence', 'Michael Harris', 'artificial_intelligence.pdf', 'AI'),
            ('C++ Programming', 'Sarah Allen', 'cpp_programming.pdf', 'Programming'),
            ('Database Management Systems', 'David Martinez', 'dbms.pdf', 'Databases'),
            ('Cloud Computing', 'Sophia Wilson', 'cloud_computing.pdf', 'Cloud'),
            ('Networking Basics', 'Ethan Scott', 'networking_basics.pdf', 'Networking'),
            ('JavaScript for Beginners', 'Olivia Adams', 'javascript_for_beginners.pdf', 'Programming'),
        ]

        cursor.executemany('''
            INSERT INTO books (title, author, file, category)
            VALUES (?, ?, ?, ?)
        ''', sample_books)

        conn.commit()
        conn.close()

# Home route
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, file, category FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template('index.html', books=books)

# Search route
@app.route('/search', methods=['GET'])
def search():
    query_title = request.args.get('query_title')
    query_author = request.args.get('query_author')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Filter books based on title and author queries
    sql_query = "SELECT id, title, author, file, category FROM books WHERE 1=1"
    params = []
    if query_title:
        sql_query += " AND title LIKE ?"
        params.append(f"%{query_title}%")
    if query_author:
        sql_query += " AND author LIKE ?"
        params.append(f"%{query_author}%")
    
    cursor.execute(sql_query, params)
    books = cursor.fetchall()
    conn.close()
    return render_template('index.html', books=books, query_title=query_title, query_author=query_author)

# Add book route (for manual addition)
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    file = request.form['file']
    category = request.form['category']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author, file, category) VALUES (?, ?, ?, ?)", (title, author, file, category))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Delete book route
@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Download book route
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Initialize the database and add predefined data
    init_db()
    app.run(debug=True)
