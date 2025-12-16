import re
import tkinter as tk
from tkinter import ttk
from sympy import (
    sympify, Symbol, diff,
    simplify, expand, factor,
    sin, cos, tan, cot, log, exp, pi, E
)
from sympy.printing.latex import latex


SAFE = {
    "sin": sin, "cos": cos, "tan": tan, "cot": cot,
    "log": log, "exp": exp,
    "pi": pi, "E": E
}

_deg = re.compile(r"\b(sin|cos|tan|cot)\(\s*([+-]?\d+(?:\.\d+)?)\s*\)")

def normalize(s: str) -> str:
    s = s.strip().replace("^", "**")
    s = re.sub(r"\bln\s*\(", "log(", s)
    return _deg.sub(r"\1(pi*(\2)/180)", s)

def parse(expr: str, ans=None):
    expr = normalize(expr)

    loc = dict(SAFE)
    if ans is not None:
        loc["Ans"] = ans

    for name in set(re.findall(r"[A-Za-z_]\w*", expr)) - set(loc):
        loc[name] = Symbol(name)

    return sympify(expr, locals=loc)


class MiniCalc(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Аналитический калькулятор")
        self.geometry("720x420")

        self.ans = None
        self.expr = tk.StringVar()
        self.result = tk.StringVar()

        ttk.Entry(self, textvariable=self.expr, font=("Segoe UI", 14)).pack(fill="x", padx=10, pady=10)

        btns = ttk.Frame(self)
        btns.pack(padx=10)

        #режимы работы
        self.ops = {
            "=": ("eval", None),
            "d/dx": ("diff", None),
            "упростить": ("op", simplify),
            "раскрыть": ("op", expand),
            "разложить": ("op", factor),
            "очистить": ("clear", None),
        }

        for text in self.ops:
            ttk.Button(btns, text=text, command=lambda t=text: self.apply(t)).pack(side="left", padx=4)

        ttk.Label(self, textvariable=self.result, wraplength=690).pack(padx=10, pady=10)

        self.steps = tk.Text(self, height=6, font=("Consolas", 11))
        self.steps.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def set_steps(self, s=""):
        self.steps.delete("1.0", tk.END)
        if s:
            self.steps.insert("1.0", s)

    def apply(self, key: str):
        kind, fn = self.ops[key]

        if kind == "clear":
            self.expr.set("")
            self.result.set("")
            self.set_steps("")
            return

        expr = parse(self.expr.get(), self.ans)

        if kind == "eval":
            out = expr
            self.set_steps("")

        elif kind == "diff":
            x = Symbol("x")
            out = diff(expr, x)
            self.set_steps(rf"\frac{{d}}{{dx}}\left({latex(expr)}\right) = {latex(out)}")

        else:
            out = fn(expr)
            self.set_steps("")

        self.ans = out
        self.result.set(str(out))


if __name__ == "__main__":
    MiniCalc().mainloop()
