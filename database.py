import pyodbc
from tkinter import messagebox

USER_TABLE = "UsersAntiplagiat"  # This table should have columns: id, login, password
HISTORY_TABLE = "Antiplagiat"  # This table should have columns: id, login, File_Name, Originality, Citation, SelfCitation


def get_db_connection():
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=217.28.223.127,17160;"
            "DATABASE=db_8939f;"
            "UID=user_432c1;"
            "PWD=i+9X7wP=jR!"
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        messagebox.showerror(
            "Database Error", f"Cannot connect to the database. Error: {e}"
        )
        return None


def save_history(user, file_name, overall_results):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {HISTORY_TABLE} (login, File_Name, Originality, Citation, SelfCitation) VALUES (?, ?, ?, ?, ?)",
            (
                user,
                file_name,
                overall_results["average_originality"],
                overall_results["average_citation"],
                overall_results["self_plagiarism"],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving history: {e}")


def get_history(user):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT File_Name, Originality, Citation, SelfCitation FROM {HISTORY_TABLE} WHERE login = ?",
            (user,),
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error retrieving history: {e}")
        return []
