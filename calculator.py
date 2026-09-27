"""
Минималистичный GUI-калькулятор на Tkinter (расширенная версия).

Возможности:
    - Базовые операции: +, -, ×, ÷
    - Дополнительные функции: √ (корень), x² (квадрат), ± (смена знака)
    - Память: M+, M-, MR, MC
    - История вычислений (боковая панель, можно скрыть/показать)
    - Переключение тёмной/светлой темы
    - Копирование результата в буфер обмена (Ctrl+C)
    - Управление с клавиатуры (цифры, операторы, Enter, Backspace, Esc, t, h)
    - Аккуратное форматирование чисел

Запуск:
    python calculator.py
"""

import tkinter as tk


# ============================================================================
#  Темы оформления
# ============================================================================
THEMES = {
    "dark": {
        "bg_main": "#1e1e1e",
        "bg_display": "#1e1e1e",
        "fg_display": "#ffffff",
        "fg_sub": "#8a8a8a",
        "bg_btn": "#2b2b2b",
        "bg_btn_hover": "#3a3a3a",
        "bg_op": "#3a3a3a",
        "bg_op_hover": "#4a4a4a",
        "bg_accent": "#ff9f0a",
        "bg_accent_hover": "#ffb84d",
        "fg_btn": "#ffffff",
        "fg_accent": "#1e1e1e",
        "bg_history": "#151515",
        "fg_history": "#c9c9c9",
    },
    "light": {
        "bg_main": "#f2f2f2",
        "bg_display": "#f2f2f2",
        "fg_display": "#1e1e1e",
        "fg_sub": "#6a6a6a",
        "bg_btn": "#ffffff",
        "bg_btn_hover": "#e6e6e6",
        "bg_op": "#e0e0e0",
        "bg_op_hover": "#cfcfcf",
        "bg_accent": "#ff9500",
        "bg_accent_hover": "#ffb04d",
        "fg_btn": "#1e1e1e",
        "fg_accent": "#ffffff",
        "bg_history": "#e9e9e9",
        "fg_history": "#3a3a3a",
    },
}

FONT_DISPLAY = ("Helvetica Neue", 38, "normal")
FONT_SUB = ("Helvetica Neue", 12, "normal")
FONT_BTN = ("Helvetica Neue", 16, "normal")
FONT_HISTORY_TITLE = ("Helvetica Neue", 13, "bold")
FONT_HISTORY = ("Helvetica Neue", 11, "normal")


# ============================================================================
#  Вспомогательные функции
# ============================================================================
def format_result(value) -> str:
    """Приводит число к удобному для чтения виду.

    - Строка (например, сообщение об ошибке) возвращается без изменений.
    - Целое значение (3.0) отображается без дробной части ("3").
    - Иначе обрезаются хвостовые нули дробной части (0.500000 -> 0.5).
    """
    if isinstance(value, str):
        return value
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text


# ============================================================================
#  Класс Calculator
# ============================================================================
class Calculator(tk.Tk):
    """Окно приложения и хранилище всего состояния вычислений."""

    def __init__(self):
        super().__init__()
        self.title("Калькулятор")
        self.resizable(False, False)

        self.theme_name = "dark"
        self.theme = THEMES[self.theme_name]

        self.expression = ""
        self.first_operand = None
        self.operation = None
        self.reset_next_input = False
        self.memory = 0.0
        self.history = []          # список строк вида "a + b = c"
        self.history_visible = True

        self.body = tk.Frame(self, bg=self.theme["bg_main"])
        self.body.pack(fill="both", expand=True)

        self._build_topbar()
        self._build_display()
        self._build_buttons()
        self._build_history_panel()
        self._bind_keys()
        self._apply_theme()

    # ------------------------------------------------------------------ #
    #  Построение интерфейса
    # ------------------------------------------------------------------ #
    def _build_topbar(self):
        """Верхняя панель: смена темы, показ/скрытие истории, метка памяти."""
        bar = tk.Frame(self.body, bg=self.theme["bg_main"])
        bar.pack(fill="x", padx=12, pady=(10, 0))
        self.bar = bar

        self.theme_btn = tk.Button(
            bar, text="☾", command=self._toggle_theme,
            bd=0, relief="flat", font=("Helvetica Neue", 12),
            width=3, cursor="hand2",
        )
        self.theme_btn.pack(side="left")

        self.history_btn = tk.Button(
            bar, text="🕘", command=self._toggle_history,
            bd=0, relief="flat", font=("Helvetica Neue", 12),
            width=3, cursor="hand2",
        )
        self.history_btn.pack(side="left", padx=(6, 0))

        self.memory_label = tk.Label(
            bar, text="", font=FONT_SUB, bg=self.theme["bg_main"],
        )
        self.memory_label.pack(side="right")

    def _build_display(self):
        """Область экрана: промежуточное выражение и текущий ввод/результат."""
        frame = tk.Frame(self.body, bg=self.theme["bg_display"])
        frame.pack(fill="both", padx=12, pady=(4, 6))
        self.display_frame = frame

        self.sub_var = tk.StringVar(value="")
        self.sub_label = tk.Label(
            frame, textvariable=self.sub_var, anchor="e",
            font=FONT_SUB, padx=10,
        )
        self.sub_label.pack(fill="x")

        self.display_var = tk.StringVar(value="0")
        self.display_label = tk.Label(
            frame, textvariable=self.display_var, anchor="e",
            font=FONT_DISPLAY, padx=10,
        )
        self.display_label.pack(fill="both")

    def _build_buttons(self):
        """Сетка кнопок: память, очистка, операции, цифры, функции, "=" ."""
        grid = tk.Frame(self.body, bg=self.theme["bg_main"])
        grid.pack(padx=12, pady=(0, 12))
        self.grid_frame = grid

        layout = [
            [("MC", "func"), ("MR", "func"), ("M-", "func"), ("M+", "func")],
            [("C", "func"), ("⌫", "func"), ("√", "op"), ("÷", "op")],
            [("7", "num"), ("8", "num"), ("9", "num"), ("×", "op")],
            [("4", "num"), ("5", "num"), ("6", "num"), ("-", "op")],
            [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
            [("±", "op"), ("0", "num"), (".", "num"), ("x²", "op")],
            [("=", "eq")],
        ]

        self.buttons = []
        for row_values in layout:
            row = tk.Frame(grid, bg=self.theme["bg_main"])
            row.pack(fill="x", pady=3)
            for text, kind in row_values:
                self._make_button(row, text, kind, full_width=(text == "="))

    def _make_button(self, parent, text, kind, full_width=False):
        """Создаёт одну кнопку и регистрирует её для последующей темизации."""
        btn = tk.Button(
            parent, text=text, font=FONT_BTN, bd=0, relief="flat",
            width=8 if not full_width else 36, height=2,
            cursor="hand2",
            command=lambda t=text: self._on_button(t),
        )
        btn.pack(side="left", padx=4, fill="x", expand=full_width)
        self.buttons.append((btn, kind))
        return btn

    def _build_history_panel(self):
        """Боковая панель истории вычислений (Listbox + кнопка очистки)."""
        panel = tk.Frame(self.body, width=200)
        self.history_panel = panel

        title = tk.Label(panel, text="История", font=FONT_HISTORY_TITLE)
        title.pack(anchor="w", padx=10, pady=(10, 4))
        self.history_title = title

        clear_btn = tk.Button(
            panel, text="Очистить историю", bd=0, relief="flat",
            font=("Helvetica Neue", 10), cursor="hand2",
            command=self._clear_history,
        )
        clear_btn.pack(anchor="w", padx=10, pady=(0, 6))
        self.history_clear_btn = clear_btn

        self.history_list = tk.Listbox(
            panel, bd=0, highlightthickness=0, font=FONT_HISTORY,
            activestyle="none",
        )
        self.history_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.history_list.bind("<<ListboxSelect>>", self._recall_history)

        panel.pack(side="right", fill="y")

    # ------------------------------------------------------------------ #
    #  Тема оформления
    # ------------------------------------------------------------------ #
    def _apply_theme(self):
        """Перекрашивает все виджеты в цвета текущей темы (self.theme)."""
        t = self.theme
        self.configure(bg=t["bg_main"])
        self.body.configure(bg=t["bg_main"])
        self.bar.configure(bg=t["bg_main"])
        self.theme_btn.configure(
            text="☀" if self.theme_name == "dark" else "☾",
            bg=t["bg_main"], fg=t["fg_display"],
            activebackground=t["bg_main"], activeforeground=t["fg_display"],
        )
        self.history_btn.configure(
            bg=t["bg_main"], fg=t["fg_display"],
            activebackground=t["bg_main"], activeforeground=t["fg_display"],
        )
        self.memory_label.configure(bg=t["bg_main"], fg=t["fg_sub"])

        self.display_frame.configure(bg=t["bg_display"])
        self.sub_label.configure(bg=t["bg_display"], fg=t["fg_sub"])
        self.display_label.configure(bg=t["bg_display"], fg=t["fg_display"])

        self.grid_frame.configure(bg=t["bg_main"])
        for child in self.grid_frame.winfo_children():
            child.configure(bg=t["bg_main"])

        for btn, kind in self.buttons:
            if kind == "eq":
                bg, hover, fg = t["bg_accent"], t["bg_accent_hover"], t["fg_accent"]
            elif kind in ("func", "op"):
                bg, hover, fg = t["bg_op"], t["bg_op_hover"], t["fg_btn"]
            else:
                bg, hover, fg = t["bg_btn"], t["bg_btn_hover"], t["fg_btn"]
            btn.configure(bg=bg, fg=fg, activebackground=hover, activeforeground=fg)
            btn.bind("<Enter>", lambda e, b=btn, c=hover: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))

        self.history_panel.configure(bg=t["bg_history"])
        self.history_title.configure(bg=t["bg_history"], fg=t["fg_history"])
        self.history_clear_btn.configure(
            bg=t["bg_history"], fg=t["fg_sub"],
            activebackground=t["bg_history"], activeforeground=t["fg_history"],
        )
        self.history_list.configure(
            bg=t["bg_history"], fg=t["fg_history"],
            selectbackground=t["bg_accent"], selectforeground=t["fg_accent"],
        )

    def _toggle_theme(self):
        """Переключает self.theme_name между "dark" и "light"."""
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.theme = THEMES[self.theme_name]
        self._apply_theme()

    def _toggle_history(self):
        """Показывает или скрывает боковую панель истории."""
        self.history_visible = not self.history_visible
        if self.history_visible:
            self.history_panel.pack(side="right", fill="y")
        else:
            self.history_panel.pack_forget()

    # ------------------------------------------------------------------ #
    #  Основная логика вычислений
    # ------------------------------------------------------------------ #
    def _on_button(self, text):
        """Главный диспетчер: определяет тип нажатой кнопки и вызывает нужный метод."""
        if text.isdigit() or text == ".":
            self._input_digit(text)
        elif text == "C":
            self._clear()
        elif text == "⌫":
            self._backspace()
        elif text in ("+", "-", "×", "÷"):
            self._set_operation(text)
        elif text == "=":
            self._calculate()
        elif text == "√":
            self._unary(lambda a: a ** 0.5 if a >= 0 else "Ошибка: корень из отрицательного числа")
        elif text == "x²":
            self._unary(lambda a: a * a)
        elif text == "±":
            self._toggle_sign()
        elif text == "M+":
            self._memory_add()
        elif text == "M-":
            self._memory_subtract()
        elif text == "MR":
            self._memory_recall()
        elif text == "MC":
            self._memory_clear()
        self._refresh()

    def _input_digit(self, digit):
        """Добавляет цифру/точку к выражению; не допускает вторую точку и лишние нули."""
        if self.reset_next_input:
            self.expression = ""
            self.reset_next_input = False
        if digit == "." and "." in self.expression:
            return
        if self.expression == "0" and digit != ".":
            self.expression = digit
        else:
            self.expression += digit

    def _clear(self):
        """Полностью сбрасывает выражение, операнды и операцию."""
        self.expression = ""
        self.first_operand = None
        self.operation = None
        self.reset_next_input = False
        self.sub_var.set("")

    def _backspace(self):
        """Удаляет последний введённый символ."""
        self.expression = self.expression[:-1]

    def _set_operation(self, op):
        """Фиксирует первый операнд и операцию; поддерживает цепочки вида 2 + 3 + 4."""
        if not self.expression and self.first_operand is None:
            return
        if self.expression:
            if self.first_operand is not None and self.operation:
                self._calculate(silent=True)
            else:
                self.first_operand = float(self.expression)
        self.operation = op
        self.sub_var.set(f"{format_result(self.first_operand)} {op}")
        self.reset_next_input = True

    def _calculate(self, silent=False):
        """Выполняет вычисление, форматирует результат и пишет запись в историю."""
        if self.first_operand is None or not self.expression or not self.operation:
            return
        second_operand = float(self.expression)
        result = self._apply(self.first_operand, second_operand, self.operation)

        entry = (
            f"{format_result(self.first_operand)} {self.operation} "
            f"{format_result(second_operand)} = {format_result(result)}"
        )

        if isinstance(result, str):
            self.expression = result
            self.first_operand = None
        else:
            self.expression = format_result(result)
            self.first_operand = result
            if not silent:
                self._add_history(entry)

        self.operation = None
        self.reset_next_input = True
        self.sub_var.set("")

    def _unary(self, fn):
        """Применяет одноместную функцию (√ или x²) к текущему числу."""
        if not self.expression:
            return
        value = float(self.expression)
        result = fn(value)
        if isinstance(result, str):
            self.expression = result
        else:
            self.expression = format_result(result)
            self._add_history(f"{format_result(value)} → {format_result(result)}")
        self.reset_next_input = True

    def _toggle_sign(self):
        """Меняет знак текущего введённого числа на противоположный."""
        if not self.expression or self.expression == "0":
            return
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression

    @staticmethod
    def _apply(a, b, op):
        """Выполняет арифметическую операцию над двумя числами."""
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "×":
            return a * b
        if op == "÷":
            if b == 0:
                return "Ошибка: на ноль делить нельзя!"
            return a / b
        return b

    # ------------------------------------------------------------------ #
    #  Память калькулятора
    # ------------------------------------------------------------------ #
    def _memory_add(self):
        """M+: прибавляет текущее число к значению памяти."""
        if self.expression:
            self.memory += float(self.expression)
            self._update_memory_label()

    def _memory_subtract(self):
        """M-: вычитает текущее число из значения памяти."""
        if self.expression:
            self.memory -= float(self.expression)
            self._update_memory_label()

    def _memory_recall(self):
        """MR: подставляет значение памяти в поле ввода."""
        self.expression = format_result(self.memory)
        self.reset_next_input = True

    def _memory_clear(self):
        """MC: обнуляет память."""
        self.memory = 0.0
        self._update_memory_label()

    def _update_memory_label(self):
        """Обновляет метку памяти в верхней панели (например "M: 42")."""
        self.memory_label.configure(
            text=f"M: {format_result(self.memory)}" if self.memory else ""
        )

    # ------------------------------------------------------------------ #
    #  История вычислений
    # ------------------------------------------------------------------ #
    def _add_history(self, entry):
        """Добавляет строку вычисления в self.history и в виджет Listbox."""
        self.history.append(entry)
        self.history_list.insert(tk.END, entry)
        self.history_list.see(tk.END)

    def _clear_history(self):
        """Полностью очищает историю."""
        self.history.clear()
        self.history_list.delete(0, tk.END)

    def _recall_history(self, _event):
        """Клик по записи истории: подставляет итоговое число в поле ввода."""
        selection = self.history_list.curselection()
        if not selection:
            return
        entry = self.history[selection[0]]
        result = entry.split("=")[-1].split("→")[-1].strip()
        self.expression = result
        self.reset_next_input = True
        self._refresh()

    # ------------------------------------------------------------------ #
    #  Вывод и буфер обмена
    # ------------------------------------------------------------------ #
    def _refresh(self):
        """Обновляет отображаемый текст (display_var) по текущему expression."""
        self.display_var.set(self.expression if self.expression else "0")

    def _copy_to_clipboard(self, _event=None):
        """Копирует текущее значение экрана в системный буфер обмена (Ctrl+C)."""
        self.clipboard_clear()
        self.clipboard_append(self.display_var.get())

    # ------------------------------------------------------------------ #
    #  Управление с клавиатуры
    # ------------------------------------------------------------------ #
    def _bind_keys(self):
        """Привязывает клавиши клавиатуры к тем же обработчикам, что и кнопки мыши."""
        for digit in "0123456789.":
            self.bind(digit, lambda e, d=digit: self._on_button(d))
        self.bind("+", lambda e: self._on_button("+"))
        self.bind("-", lambda e: self._on_button("-"))
        self.bind("*", lambda e: self._on_button("×"))
        self.bind("/", lambda e: self._on_button("÷"))
        self.bind("<Return>", lambda e: self._on_button("="))
        self.bind("<KP_Enter>", lambda e: self._on_button("="))
        self.bind("<BackSpace>", lambda e: self._on_button("⌫"))
        self.bind("<Escape>", lambda e: self._on_button("C"))
        self.bind("<Control-c>", self._copy_to_clipboard)
        self.bind("t", lambda e: self._toggle_theme())
        self.bind("h", lambda e: self._toggle_history())


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
