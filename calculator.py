"""
Минималистичный GUI-калькулятор на Tkinter.

Логика вычислений сохранена из исходного консольного скрипта,
но обёрнута в аккуратный графический интерфейс:
- поддержка +, -, *, /
- защита от деления на ноль
- очистка (C) и удаление последнего символа (⌫)
- ввод с клавиатуры (цифры, операторы, Enter, Backspace, Esc)
- аккуратное форматирование результата (без лишних .0 и хвостов float)
"""

import tkinter as tk


# ---------- Цветовая схема (минимализм: чёрно-белый + один акцент) ----------
BG_MAIN = "#1e1e1e"
BG_DISPLAY = "#1e1e1e"
FG_DISPLAY = "#ffffff"
BG_BTN = "#2b2b2b"
BG_BTN_HOVER = "#3a3a3a"
BG_OP = "#3a3a3a"
BG_OP_HOVER = "#4a4a4a"
BG_ACCENT = "#ff9f0a"
BG_ACCENT_HOVER = "#ffb84d"
FG_BTN = "#ffffff"
FG_ACCENT = "#1e1e1e"
FONT_DISPLAY = ("Helvetica Neue", 40, "normal")
FONT_BTN = ("Helvetica Neue", 18, "normal")


def format_result(value: float) -> str:
    """Убирает лишние нули и превращает 3.0 в 3."""
    if isinstance(value, str):
        return value
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор")
        self.configure(bg=BG_MAIN)
        self.resizable(False, False)

        self.expression = ""      # то, что видно на экране
        self.first_operand = None
        self.operation = None
        self.reset_next_input = False

        self._build_display()
        self._build_buttons()
        self._bind_keys()

    # ---------------------------------------------------------------- UI --
    def _build_display(self):
        frame = tk.Frame(self, bg=BG_DISPLAY)
        frame.pack(fill="both", padx=12, pady=(18, 6))

        self.display_var = tk.StringVar(value="0")
        label = tk.Label(
            frame,
            textvariable=self.display_var,
            anchor="e",
            bg=BG_DISPLAY,
            fg=FG_DISPLAY,
            font=FONT_DISPLAY,
            padx=10,
        )
        label.pack(fill="both")

    def _build_buttons(self):
        grid = tk.Frame(self, bg=BG_MAIN)
        grid.pack(padx=12, pady=(0, 12))

        layout = [
            [("C", "func"), ("⌫", "func"), ("%", "op"), ("÷", "op")],
            [("7", "num"), ("8", "num"), ("9", "num"), ("×", "op")],
            [("4", "num"), ("5", "num"), ("6", "num"), ("-", "op")],
            [("1", "num"), ("2", "num"), ("3", "num"), ("+", "op")],
            [("0", "num_wide"), (".", "num"), ("=", "eq")],
        ]

        for row_values in layout:
            row = tk.Frame(grid, bg=BG_MAIN)
            row.pack(fill="x", pady=4)
            for text, kind in row_values:
                self._make_button(row, text, kind)

    def _make_button(self, parent, text, kind):
        colors = {
            "num": (BG_BTN, BG_BTN_HOVER, FG_BTN),
            "num_wide": (BG_BTN, BG_BTN_HOVER, FG_BTN),
            "func": (BG_OP, BG_OP_HOVER, FG_BTN),
            "op": (BG_OP, BG_OP_HOVER, FG_BTN),
            "eq": (BG_ACCENT, BG_ACCENT_HOVER, FG_ACCENT),
        }
        bg, hover, fg = colors[kind]
        width = 2 if kind == "num_wide" else 1

        btn = tk.Button(
            parent,
            text=text,
            font=FONT_BTN,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground=fg,
            bd=0,
            relief="flat",
            width=8 * width,
            height=2,
            command=lambda t=text: self._on_button(t),
        )
        btn.pack(side="left", padx=4, expand=(kind == "num_wide"), fill="x" if kind == "num_wide" else None)
        btn.bind("<Enter>", lambda e, b=btn, c=hover: b.config(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))

    # ------------------------------------------------------------- логика --
    def _on_button(self, text):
        if text.isdigit() or text == ".":
            self._input_digit(text)
        elif text == "C":
            self._clear()
        elif text == "⌫":
            self._backspace()
        elif text in ("+", "-", "×", "÷", "%"):
            self._set_operation(text)
        elif text == "=":
            self._calculate()
        self._refresh()

    def _input_digit(self, digit):
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
        self.expression = ""
        self.first_operand = None
        self.operation = None
        self.reset_next_input = False

    def _backspace(self):
        self.expression = self.expression[:-1]

    def _set_operation(self, op):
        if not self.expression and self.first_operand is None:
            return
        if self.expression:
            if self.first_operand is not None and self.operation:
                self._calculate()
            else:
                self.first_operand = float(self.expression)
        self.operation = op
        self.reset_next_input = True

    def _calculate(self):
        if self.first_operand is None or not self.expression or not self.operation:
            return
        second_operand = float(self.expression)
        result = self._apply(self.first_operand, second_operand, self.operation)

        if result == "Ошибка: на ноль делить нельзя!":
            self.expression = result
            self.first_operand = None
        else:
            self.expression = format_result(result)
            self.first_operand = result

        self.operation = None
        self.reset_next_input = True

    @staticmethod
    def _apply(a, b, op):
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
        if op == "%":
            return a % b if b != 0 else "Ошибка: на ноль делить нельзя!"
        return b

    def _refresh(self):
        self.display_var.set(self.expression if self.expression else "0")

    # ------------------------------------------------------------ клавиши --
    def _bind_keys(self):
        for digit in "0123456789.":
            self.bind(digit, lambda e, d=digit: self._on_button(d))
        self.bind("+", lambda e: self._on_button("+"))
        self.bind("-", lambda e: self._on_button("-"))
        self.bind("*", lambda e: self._on_button("×"))
        self.bind("/", lambda e: self._on_button("÷"))
        self.bind("%", lambda e: self._on_button("%"))
        self.bind("<Return>", lambda e: self._on_button("="))
        self.bind("<KP_Enter>", lambda e: self._on_button("="))
        self.bind("<BackSpace>", lambda e: self._on_button("⌫"))
        self.bind("<Escape>", lambda e: self._on_button("C"))


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
