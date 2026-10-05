"""Online Quiz Application - Python + SQLite
Features: category selection, timer per question, automatic scoring,
result summary, and saved results in a database.
"""
import sqlite3
import time
import random

DB_NAME = "quiz.db"
TIME_LIMIT = 15  # seconds per question


def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT, question TEXT,
        option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
        answer TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT, category TEXT, score INTEGER, total INTEGER,
        played_on TEXT DEFAULT CURRENT_TIMESTAMP)""")
    if cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0:
        data = [
            ("Python", "Which keyword defines a function in Python?", "func", "def", "define", "function", "B"),
            ("Python", "Which data type is immutable in Python?", "list", "dict", "tuple", "set", "C"),
            ("Python", "What does len([1, 2, 3]) return?", "2", "3", "4", "Error", "B"),
            ("Python", "Which symbol starts a comment in Python?", "//", "/*", "#", "--", "C"),
            ("Python", "Which function prints output on screen?", "echo()", "print()", "show()", "write()", "B"),
            ("DBMS", "What does SQL stand for?", "Structured Query Language", "Simple Query Logic", "Sequential Query Language", "Standard Query List", "A"),
            ("DBMS", "Which key uniquely identifies a row in a table?", "Foreign key", "Primary key", "Candidate list", "Index key", "B"),
            ("DBMS", "Which command removes all rows but keeps the table structure?", "DROP", "DELETE TABLE", "TRUNCATE", "REMOVE", "C"),
            ("DBMS", "Which SQL clause filters rows?", "ORDER BY", "GROUP BY", "WHERE", "SELECT", "C"),
            ("DBMS", "Which normal form removes partial dependency?", "1NF", "2NF", "3NF", "BCNF", "B"),
            ("Web", "What does HTML stand for?", "Hyper Text Markup Language", "High Text Machine Language", "Hyper Tool Multi Language", "Home Text Markup Language", "A"),
            ("Web", "Which language is used to style web pages?", "Java", "Python", "CSS", "SQL", "C"),
            ("Web", "Which tag creates a hyperlink?", "<link>", "<a>", "<href>", "<url>", "B"),
            ("Web", "Which language adds interactivity to web pages?", "JavaScript", "C", "SQL", "XML", "A"),
            ("Web", "Which HTTP method is used to fetch data?", "POST", "PUT", "GET", "DELETE", "C"),
        ]
        cur.executemany("""INSERT INTO questions
            (category, question, option_a, option_b, option_c, option_d, answer)
            VALUES (?,?,?,?,?,?,?)""", data)
    conn.commit()
    return conn


def choose_category(conn):
    cats = [r[0] for r in conn.execute("SELECT DISTINCT category FROM questions")]
    print("\nAvailable categories:")
    for i, c in enumerate(cats, 1):
        print(f"  {i}. {c}")
    while True:
        choice = input("Choose a category number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(cats):
            return cats[int(choice) - 1]
        print("Invalid choice, try again.")


def ask_question(number, q):
    _, _, text, a, b, c, d, correct = q
    print(f"\nQ{number}. {text}")
    print(f"  A. {a}\n  B. {b}\n  C. {c}\n  D. {d}")
    start = time.time()
    while True:
        ans = input(f"Your answer (A/B/C/D) [{TIME_LIMIT}s]: ").strip().upper()
        if ans in ("A", "B", "C", "D"):
            break
        print("Please enter A, B, C or D.")
    if time.time() - start > TIME_LIMIT:
        print("Time is up! Answer not counted.")
        return False
    if ans == correct:
        print("Correct!")
        return True
    print(f"Wrong. Correct answer: {correct}")
    return False


def save_result(conn, player, category, score, total):
    conn.execute("INSERT INTO results (player, category, score, total) VALUES (?,?,?,?)",
                 (player, category, score, total))
    conn.commit()


def show_leaderboard(conn, category):
    rows = conn.execute("""SELECT player, score, total FROM results
        WHERE category=? ORDER BY score DESC, id ASC LIMIT 5""", (category,)).fetchall()
    print(f"\n--- Top 5 in {category} ---")
    for i, (p, s, t) in enumerate(rows, 1):
        print(f"{i}. {p}: {s}/{t}")


def main():
    conn = setup_database()
    print("=== Online Quiz Application ===")
    player = input("Enter your name: ").strip() or "Guest"
    while True:
        category = choose_category(conn)
        questions = conn.execute("SELECT * FROM questions WHERE category=?", (category,)).fetchall()
        random.shuffle(questions)
        score = sum(ask_question(i, q) for i, q in enumerate(questions, 1))
        total = len(questions)
        percent = score / total * 100
        print("\n=== Result Summary ===")
        print(f"Player: {player} | Category: {category}")
        print(f"Score: {score}/{total} ({percent:.0f}%)")
        print("Grade:", "Excellent" if percent >= 80 else "Good" if percent >= 60 else "Keep practicing")
        save_result(conn, player, category, score, total)
        show_leaderboard(conn, category)
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("Thanks for playing!")
            break
    conn.close()


if __name__ == "__main__":
    main()
