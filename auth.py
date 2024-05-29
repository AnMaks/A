from tkinter import messagebox
import customtkinter as ctk
from database import get_db_connection, USER_TABLE
from gui import display_main_window, apply_settings

from translations import translate


def check_credentials(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {USER_TABLE} WHERE login = ? AND password = ?",
            (username, password),
        )
        user = cursor.fetchone()
        conn.close()
        return user is not None
    except Exception as e:
        print(f"Error checking credentials: {e}")
        messagebox.showerror("Error", f"Error checking credentials: {e}")
        return False


def register_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {USER_TABLE} WHERE login = ?", (username,))
        user = cursor.fetchone()
        if user:
            conn.close()
            return False

        cursor.execute(
            f"INSERT INTO {USER_TABLE} (login, password) VALUES (?, ?)",
            (username, password),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        messagebox.showerror("Error", f"Error registering user: {e}")
        return False


def logout(user):
    user = None
    display_login()


def display_login():
    global login_window
    login_window = ctk.CTk()
    login_window.title(translate("login"))
    login_window.geometry("300x350")

    ctk.CTkLabel(login_window, text=translate("login"), font=("Arial", 18)).pack(
        pady=20
    )

    username_label = ctk.CTkLabel(
        login_window, text=translate("username"), font=("Arial", 14)
    )
    username_label.pack(pady=5)
    username_entry = ctk.CTkEntry(login_window)
    username_entry.pack(pady=5)

    password_label = ctk.CTkLabel(
        login_window, text=translate("password"), font=("Arial", 14)
    )
    password_label.pack(pady=5)
    password_entry = ctk.CTkEntry(login_window, show="*")
    password_entry.pack(pady=5)

    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        if check_credentials(username, password):
            login_window.destroy()
            display_main_window(username)
        else:
            messagebox.showerror(translate("login"), translate("invalid_credentials"))

    ctk.CTkButton(login_window, text=translate("login_button"), command=on_login).pack(
        pady=10
    )
    ctk.CTkButton(
        login_window,
        text=translate("register_button"),
        command=lambda: [login_window.destroy(), display_register()],
    ).pack(pady=10)

    login_window.mainloop()


def display_register():
    register_window = ctk.CTk()
    register_window.title(translate("register"))
    register_window.geometry("400x450")

    ctk.CTkLabel(register_window, text=translate("register"), font=("Arial", 18)).pack(
        pady=20
    )

    username_label = ctk.CTkLabel(
        register_window, text=translate("username"), font=("Arial", 14)
    )
    username_label.pack(pady=5)
    username_entry = ctk.CTkEntry(register_window)
    username_entry.pack(pady=5)

    password_label = ctk.CTkLabel(
        register_window, text=translate("password"), font=("Arial", 14)
    )
    password_label.pack(pady=5)
    password_entry = ctk.CTkEntry(register_window, show="*")
    password_entry.pack(pady=5)

    confirm_password_label = ctk.CTkLabel(
        register_window, text=translate("confirm_password"), font=("Arial", 14)
    )
    confirm_password_label.pack(pady=5)
    confirm_password_entry = ctk.CTkEntry(register_window, show="*")
    confirm_password_entry.pack(pady=5)

    def on_register():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        if password != confirm_password:
            messagebox.showerror(
                translate("register"), translate("passwords_not_match")
            )
        elif register_user(username, password):
            messagebox.showinfo(
                translate("register"), translate("registration_success")
            )
            register_window.destroy()
            display_login()
        else:
            messagebox.showerror(
                translate("register"), translate("invalid_credentials")
            )

    ctk.CTkButton(
        register_window, text=translate("register_button"), command=on_register
    ).pack(pady=10)
    ctk.CTkButton(
        register_window,
        text=translate("login_button"),
        command=lambda: [register_window.destroy(), display_login()],
    ).pack(pady=10)

    register_window.mainloop()
