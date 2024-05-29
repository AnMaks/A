import os
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from analysis import (
    run_analysis,
    current_results,
    current_overall_results,
    analysis_saved,
    query_file_name,
)
from database import get_history, save_history
from translations import translate

current_mode = "System"  # Default mode
current_theme = "blue"  # Default theme
current_language = "Russian"  # Default language
login_window = None
register_winow = None


def apply_current_settings(window):
    if window:
        window.set_appearance_mode(current_mode)  # Применение режима вида
        window.set_default_color_theme(current_theme)  # Применение темы
        # Тут можно добавить дополнительные обновления, например, перевод текстов


def update_interface():
    apply_current_settings(login_window)
    apply_current_settings(register_winow)
    # По аналогии, вызывайте apply_current_settings для других окон


def logout(user):
    from auth import display_login

    # Эта функция должна закрывать приложение
    try:
        root.destroy()  # Пытаемся закрыть основное окно
        display_login()
    except Exception as e:
        print(f"Error closing the application: {e}")


def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Supported Files", "*.docx *.pdf *.txt")]
    )
    return file_path


def save_settings():
    settings = {
        "mode": current_mode,
        "theme": current_theme,
        "language": current_language,
    }
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        print("Settings saved successfully")
    except Exception as e:
        print(f"Error saving settings: {e}")


def load_settings():
    global current_mode, current_theme, current_language
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            current_mode = settings.get("mode", "System")
            current_theme = settings.get("theme", "blue")
            current_language = settings.get("language", "Russian")

        # Применение загруженных настроек
        ctk.set_appearance_mode(current_mode)
        ctk.set_default_color_theme(current_theme)
        update_texts()
        update_menu_color()
    except FileNotFoundError:
        # Файл настроек не найден, используем значения по умолчанию
        current_mode = "System"
        current_theme = "blue"
        current_language = "Russian"
        # Применяем значения по умолчанию
        ctk.set_appearance_mode(current_mode)
        ctk.set_default_color_theme(current_theme)
        update_texts()
        update_menu_color()
    except Exception as e:
        print(f"Error loading settings: {e}")


def select_folder():
    folder_path = filedialog.askdirectory()
    return folder_path


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def display_results(results, overall_results, user):
    clear_frame(content_frame)

    table_frame = ctk.CTkFrame(content_frame)
    table_frame.pack(expand=True, fill="both", padx=10, pady=10)

    table = ttk.Treeview(table_frame, columns=list(results.columns), show="headings")
    for col in results.columns:
        table.heading(col, text=col)
        table.column(col, width=150)

    for index, row in results.iterrows():
        table.insert("", "end", values=list(row))

    table.pack(expand=True, fill="both")

    summary_frame = ctk.CTkFrame(content_frame)
    summary_frame.pack(pady=10)

    style = ttk.Style()
    style.configure(
        "blue.Horizontal.TProgressbar",
        troughcolor="white",
        background="blue",
        thickness=10,
    )

    for key in ["average_originality", "average_citation", "self_plagiarism"]:
        label = ctk.CTkLabel(
            summary_frame,
            text=f"{translate(key)}: {overall_results[key]:.2f}%",
            font=("Arial", 12),
        )
        label.pack()
        progress = ttk.Progressbar(
            summary_frame,
            length=200,
            maximum=100,
            value=overall_results[key],
            style="blue.Horizontal.TProgressbar",
        )
        progress.pack(pady=5)

    ctk.CTkButton(
        content_frame,
        text=translate("run_new_analysis"),
        command=lambda: reset_analysis(user),
    ).pack(pady=10)


def display_history(user):
    save_current_analysis_if_needed(user)
    clear_frame(content_frame)

    rows = get_history(user)

    if not rows:
        messagebox.showinfo(translate("history"), translate("no_history"))
        return

    table_frame = ctk.CTkFrame(content_frame)
    table_frame.pack(expand=True, fill="both", padx=10, pady=10)

    columns = ["File Name", "Originality", "Citation", "Self-Citation"]
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    table["columns"] = columns
    for col in columns:
        table.heading(
            col, text=translate(col.lower().replace("-", "_").replace(" ", "_"))
        )
        table.column(col, width=150)

    for row in rows:
        table.insert("", "end", values=[x.strip() for x in row])

    table.pack(expand=True, fill="both")


def display_settings(user):
    save_current_analysis_if_needed(user)
    clear_frame(content_frame)
    ctk.CTkLabel(
        content_frame, text=translate("settings_title"), font=("Arial", 18)
    ).pack(pady=20)

    # Mode selection
    mode_label = ctk.CTkLabel(
        content_frame, text=translate("select_mode"), font=("Arial", 14)
    )
    mode_label.pack(pady=5)
    mode_var = ctk.StringVar(value=current_mode)
    mode_options = ["System", "Dark", "Light"]
    mode_menu = ctk.CTkOptionMenu(
        content_frame, variable=mode_var, values=mode_options, command=set_mode
    )
    mode_menu.pack(pady=5)

    # Theme selection
    theme_label = ctk.CTkLabel(
        content_frame, text=translate("select_theme"), font=("Arial", 14)
    )
    theme_label.pack(pady=5)
    theme_var = ctk.StringVar(value=current_theme)
    theme_options = ["blue", "green"]
    theme_menu = ctk.CTkOptionMenu(
        content_frame, variable=theme_var, values=theme_options, command=set_theme
    )
    theme_menu.pack(pady=5)

    # Language selection
    language_label = ctk.CTkLabel(
        content_frame, text=translate("select_language"), font=("Arial", 14)
    )
    language_label.pack(pady=5)
    language_var = ctk.StringVar(value=current_language)
    language_options = ["English", "Russian", "Chinese"]
    language_menu = ctk.CTkOptionMenu(
        content_frame,
        variable=language_var,
        values=language_options,
        command=set_language,
    )
    language_menu.pack(pady=5)


def display_run_analysis(user):
    clear_frame(content_frame)
    try:
        current_results = pd.read_csv("plagiarism_results.csv")
        current_overall_results = pd.read_csv("plagiarism_overall_results.csv").to_dict(
            "records"
        )[0]
        display_results(current_results, current_overall_results, user)
    except Exception as e:
        print("Error loading new analysis data:", e)
        display_default_run_analysis_ui(content_frame, user)


def display_default_run_analysis_ui(frame, user):
    label = ctk.CTkLabel(frame, text=translate("run_analysis"), font=("Arial", 18))
    label.pack(pady=20)
    button = ctk.CTkButton(
        frame,
        text=translate("select_files_and_run_analysis"),
        command=lambda: on_run(user),
        font=("Arial", 14),
    )
    button.pack(pady=10)


def on_run(user):
    global current_results, current_overall_results, query_file_name

    query_file_path = select_file()
    folder_path = select_folder()
    if not query_file_path or not folder_path:
        messagebox.showwarning(
            translate("input_error"), translate("select_query_and_folder")
        )
        return
    results, overall_results = run_analysis(query_file_path, folder_path, user)
    display_results(results, overall_results, user)


def save_current_analysis_if_needed(user):
    if (
        current_results is not None
        and current_overall_results is not None
        and not analysis_saved
    ):
        save_history(user, query_file_name, current_overall_results)


def reset_analysis(user):
    global current_results, current_overall_results, query_file_name, analysis_saved
    current_results = None
    current_overall_results = None
    query_file_name = None
    analysis_saved = False

    # Удаление файлов с результатами анализа
    try:
        os.remove("plagiarism_results.csv")
        os.remove("plagiarism_overall_results.csv")
    except FileNotFoundError:
        print("No temporary files to delete.")

    # Очистка интерфейса
    clear_frame(content_frame)
    display_run_analysis(user)


def set_mode(new_mode):
    global current_mode
    current_mode = new_mode
    ctk.set_appearance_mode(new_mode)
    update_menu_color()
    save_settings()  # Сохранение настроек


def set_theme(new_theme):
    global current_theme
    current_theme = new_theme
    ctk.set_default_color_theme(new_theme)
    update_menu_color()
    save_settings()  # Сохранение настроек


def set_language(new_language):
    global current_language
    current_language = new_language
    update_texts()
    save_settings()  # Сохранение настроек


def update_texts():
    run_button.configure(text=translate("run_analysis"))
    history_button.configure(text=translate("history"))
    settings_button.configure(text=translate("settings"))
    menu_label.configure(text=translate("menu"))
    logout_button.configure(
        text=translate("logout_button")
    )  # Обновление текста кнопки выхода


def update_menu_color():
    menu_colors = {
        "blue": ("#1f6aa5", "#fafafa"),
        "green": ("#2cc985", "#fafafa"),
    }
    if current_theme in menu_colors:
        color, hover_color = menu_colors[current_theme]
        run_button.configure(fg_color=color, hover_color=hover_color)
        history_button.configure(fg_color=color, hover_color=hover_color)
        settings_button.configure(fg_color=color, hover_color=hover_color)
        logout_button.configure(
            fg_color=color, hover_color=hover_color
        )  # Применение цвета к кнопке выхода


def apply_settings():
    ctk.set_appearance_mode(current_mode)  # Применение темы и режима
    ctk.set_default_color_theme(current_theme)  # Применение цветовой темы
    update_menu_color()  # Обновление цветов


def display_main_window(user):
    load_settings()  # Загрузка сохраненных настроек
    global root, main_frame, content_frame, run_button, history_button, settings_button, logout_button, menu_label

    root = ctk.CTk()
    root.title("Plagiarism Detection Tool")
    root.geometry("800x600")

    main_frame = ctk.CTkFrame(root)
    main_frame.pack(side="left", fill="y", padx=10, pady=10)

    content_frame = ctk.CTkFrame(root)
    content_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    menu_label = ctk.CTkLabel(main_frame, text=translate("menu"), font=("Arial", 18))
    menu_label.pack(pady=10)

    run_button = ctk.CTkButton(
        main_frame,
        text=translate("run_analysis"),
        command=lambda: display_run_analysis(user),
        font=("Arial", 14),
    )
    run_button.pack(pady=10)

    history_button = ctk.CTkButton(
        main_frame,
        text=translate("history"),
        command=lambda: display_history(user),
        font=("Arial", 14),
    )
    history_button.pack(pady=10)

    settings_button = ctk.CTkButton(
        main_frame,
        text=translate("settings"),
        command=lambda: display_settings(user),
        font=("Arial", 14),
    )
    settings_button.pack(pady=10)

    logout_button = ctk.CTkButton(
        main_frame,
        text=translate("logout_button"),
        command=lambda: logout(user),
        font=("Arial", 14),
    )
    logout_button.pack(side="bottom", pady=10)

    update_menu_color()

    root.mainloop()
