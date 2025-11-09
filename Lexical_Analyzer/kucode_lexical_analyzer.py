#!/usr/bin/env python3


import os
import re
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import namedtuple

# -----------------------------
# rules
# -----------------------------
KEYWORDS = {
    'start', 'finish', 'define', 'give', 'worldwide', 'fixed',
    'num', 'decimal', 'bigdecimal', 'text', 'letter', 'bool', 'empty', 'list', 'group',
    'check', 'otherwise', 'otherwise check', 'select', 'option', 'stop', 'fallback',
    'each', 'during', 'skip', 'show', 'read', 'from', 'to', 'step', 'none'
}
BOOL_LITERALS = {'Yes', 'No'}

TOKEN_SPECIFICATION = [
    ('MULTICOMMENT', r'~~.*?~~'),
    ('SINGLECOMMENT', r'~[^\n]*'),
    ('STRING', r'"(?:\\.|[^"\\])*"'),
    ('CHAR', r"'(?:\\.|[^'\\])'"),
    ('NUMBER', r'\b\d+(?:\.\d+)?\b'),
    ('IDENT', r'\b[A-Za-z_][A-Za-z0-9_]*\b'),
    ('OP', r'\*\*|==|!=|<=|>=|\+\+|--|&&|\|\||->|\+=|-=|\*=|/=|%=|[+\-*/%<>=&|^~!:?]'),
    ('DELIM', r'[;,()\{\}\[\]\.]'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t\r]+'),
    ('MISMATCH', r'.'),
]
master_re = re.compile('|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION), re.DOTALL | re.MULTILINE)
Token = namedtuple('Token', ['type', 'lexeme', 'line', 'col'])


def is_valid_identifier(name: str):
    if len(name) > 20:
        return False, "identifier exceeds 20 characters"
    if name[0].isdigit():
        return False, "identifier starts with a digit"
    if name[0] == '_':
        return False, "identifier starts with an underscore"
    if name in KEYWORDS:
        return False, "identifier is a reserved keyword"
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', name):
        return False, "contains invalid characters"
    return True, ""


def classify_ident(lexeme: str):
    if lexeme in BOOL_LITERALS:
        return 'BOOL_LITERAL'
    if lexeme in KEYWORDS:
        return 'KEYWORD'
    return 'IDENTIFIER'


def tokenize(code: str):
    line_num = 1
    line_start = 0
    tokens = []
    errors = []

    for mo in master_re.finditer(code):
        kind = mo.lastgroup
        lexeme = mo.group()
        start = mo.start()
        col = start - line_start + 1

        # --- NEW: keep track of newline as token ---
        if kind == 'NEWLINE':
            tokens.append(Token('NEWLINE', '\\n', line_num, col))
            line_num += 1
            line_start = mo.end()
            continue

        # --- NEW: keep whitespace instead of skipping ---
        if kind == 'SKIP':
            # Represent visible symbols for clarity
            display_lex = lexeme.replace(' ', '␣').replace('\t', '⇥')
            tokens.append(Token('WHITESPACE', display_lex, line_num, col))
            continue

        # Comments
        if kind in ('MULTICOMMENT', 'SINGLECOMMENT'):
            tokens.append(Token('COMMENT', lexeme, line_num, col))
            if kind == 'MULTICOMMENT':
                nlcount = lexeme.count('\n')
                if nlcount:
                    line_num += nlcount
                    last_nl = lexeme.rfind('\n')
                    line_start = mo.start() + last_nl + 1
            continue

        # Strings, chars, numbers, identifiers, etc.
        if kind == 'STRING':
            tokens.append(Token('STRING', lexeme, line_num, col))
            continue
        if kind == 'CHAR':
            tokens.append(Token('CHAR', lexeme, line_num, col))
            continue
        if kind == 'NUMBER':
            tokens.append(Token('NUMBER', lexeme, line_num, col))
            continue
        if kind == 'IDENT':
            typ = classify_ident(lexeme)
            if typ == 'IDENTIFIER':
                valid, reason = is_valid_identifier(lexeme)
                if not valid:
                    tokens.append(Token('INVALID_IDENTIFIER', lexeme, line_num, col))
                    errors.append((line_num, col, f"Invalid identifier '{lexeme}': {reason}"))
                else:
                    tokens.append(Token('IDENTIFIER', lexeme, line_num, col))
            else:
                tokens.append(Token(typ, lexeme, line_num, col))
            continue
        if kind == 'OP':
            tokens.append(Token('OPERATOR', lexeme, line_num, col))
            continue
        if kind == 'DELIM':
            tokens.append(Token('DELIMITER', lexeme, line_num, col))
            continue
        if kind == 'MISMATCH':
            tokens.append(Token('UNKNOWN', lexeme, line_num, col))
            errors.append((line_num, col, f"Unknown token '{lexeme}'"))
            continue

    return tokens, errors



# -----------------------------
# gui
# -----------------------------
class ModernKuCodeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KuCode Lexical Analyzer")
        self.geometry("1100x680")
        self.minsize(900, 520)
        self.configure(bg="#eaf2fb")  # subtle pale background for contrast

        # Colors (shades of blue)
        self.header_bg = "#1b6fa8"     # chosen bright royal blue
        self.header_fg = "#ffffff"
        self.panel_bg = "#f3f8fc"
        self.card_bg = "#e0eefc"
        self.editor_bg = "#021826"     # dark editor background
        self.editor_fg = "#dff6ff"     # code text
        self.line_fg = "#6fb5e0"       # line numbers
        self.token_bg = "#ffffff"
        self.terminal_bg = "#00171a"
        self.terminal_fg = "#6fff9c"
        self.btn_bg = "#145c8a"
        self.btn_fg = "#ffffff"

        self.logo_img = None
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=self.panel_bg)
        style.configure('Card.TFrame', background=self.card_bg)
        style.configure('TLabel', background=self.panel_bg, foreground='#0b2b45', font=('Segoe UI', 10))
        style.configure('Header.TLabel', background=self.header_bg, foreground=self.header_fg, font=('Segoe UI', 12, 'bold'))
        style.configure('TButton', background=self.btn_bg, foreground=self.btn_fg, font=('Segoe UI', 10, 'bold'))
        style.map('TButton', background=[('active', '#2a85c4')])

    def _build_ui(self):
        # HEADER: single horizontal bar
        header = tk.Frame(self, bg=self.header_bg, height=64)
        header.pack(side=tk.TOP, fill=tk.X)

        # Left: logo + title
        left_h = tk.Frame(header, bg=self.header_bg)
        left_h.pack(side=tk.LEFT, padx=12, pady=8)
        logo_path = os.path.join(os.getcwd(), "logo.png")
        if os.path.exists(logo_path):
            try:
                img = tk.PhotoImage(file=logo_path)
                # subsample if too large
                max_h = 48
                if img.height() > max_h or img.width() > max_h:
                    factor = max(1, int(max(img.width(), img.height()) / max_h))
                    img = img.subsample(factor, factor)
                self.logo_img = img
                lbl_logo = tk.Label(left_h, image=self.logo_img, bg=self.header_bg)
                lbl_logo.pack(side=tk.LEFT)
            except Exception:
                lbl_logo = tk.Label(left_h, text="KuCode", bg=self.header_bg, fg=self.header_fg, font=('Segoe UI', 14, 'bold'))
                lbl_logo.pack(side=tk.LEFT)
        else:
            lbl_logo = tk.Label(left_h, text="KuCode", bg=self.header_bg, fg=self.header_fg, font=('Segoe UI', 14, 'bold'))
            lbl_logo.pack(side=tk.LEFT)

        lbl_title = tk.Label(left_h, text="KuCode Lexical Analyzer", bg=self.header_bg, fg=self.header_fg, font=('Segoe UI', 14, 'bold'))
        lbl_title.pack(side=tk.LEFT, padx=(10, 0))

        # Right: three buttons
        right_h = tk.Frame(header, bg=self.header_bg)
        right_h.pack(side=tk.RIGHT, padx=12, pady=8)
        btn_save = tk.Button(right_h, text="Save", command=self.save_tokens, bg=self.btn_bg, fg=self.btn_fg, bd=0, padx=12, pady=6)
        btn_save.pack(side=tk.RIGHT, padx=(8, 0))
        btn_analyze = tk.Button(right_h, text="Analyze", command=self.analyze_code, bg="#0f7cc0", fg=self.btn_fg, bd=0, padx=12, pady=6)
        btn_analyze.pack(side=tk.RIGHT, padx=(8, 0))
        btn_clear = tk.Button(right_h, text="Clear", command=self.clear_all, bg=self.btn_bg, fg=self.btn_fg, bd=0, padx=12, pady=6)
        btn_clear.pack(side=tk.RIGHT, padx=(8, 0))

        # MAIN AREA: editor (left 70%) and token pane (right 30%)
        main_frame = tk.Frame(self, bg=self.panel_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(12, 8))

        main_frame.columnconfigure(0, weight=7)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=0)

        # Editor Card (left)
        editor_card = tk.Frame(main_frame, bg=self.card_bg, bd=0)
        editor_card.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

        lbl_src = tk.Label(editor_card, text="Source Code", bg=self.card_bg, fg='#073a5a', font=('Segoe UI', 10, 'bold'))
        lbl_src.pack(anchor='w', padx=8, pady=(8, 4))

        # Editor inner frame: line numbers canvas + text widget
        editor_inner = tk.Frame(editor_card, bg=self.card_bg)
        editor_inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Canvas for line numbers (will draw text so it's aligned)
        self.lnum_canvas = tk.Canvas(editor_inner, width=56, bg="#e6f3ff", highlightthickness=0)
        self.lnum_canvas.pack(side=tk.LEFT, fill=tk.Y)

        # Text widget for source code
        self.editor = tk.Text(editor_inner, wrap='none', undo=True, bg=self.editor_bg, fg=self.editor_fg,
                              insertbackground=self.editor_fg, font=('Consolas', 12), relief='flat', bd=0)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars (vertical sync both widgets, horizontal for editor)
        self.vscroll = ttk.Scrollbar(editor_inner, orient='vertical', command=self._on_vscroll)
        self.vscroll.pack(side=tk.LEFT, fill=tk.Y)
        self.editor.configure(yscrollcommand=self._on_editor_yscroll)
        self.hscroll = ttk.Scrollbar(editor_card, orient='horizontal', command=self.editor.xview)
        self.hscroll.pack(fill=tk.X, padx=8, pady=(0, 8))
        self.editor.configure(xscrollcommand=self.hscroll.set)

        # Bind events to update line numbers
        self.editor.bind("<<Modified>>", self._on_change)
        self.editor.bind("<KeyRelease>", self._on_change)
        self.editor.bind("<MouseWheel>", self._on_change)       # Windows scroll
        self.editor.bind("<Button-4>", self._on_change)         # Linux scroll up
        self.editor.bind("<Button-5>", self._on_change)         # Linux scroll down
        self.editor.bind("<Configure>", self._on_change)
        self.lnum_canvas.bind("<Button-1>", lambda e: self.editor.focus_set())

        # Terminal (bottom-left)
        terminal_card = tk.Frame(main_frame, bg=self.card_bg, bd=0)
        terminal_card.grid(row=1, column=0, sticky='nsew', padx=(0, 8), pady=(0, 8))
        lbl_term = tk.Label(terminal_card, text="Terminal", bg=self.card_bg, fg='#073a5a', font=('Segoe UI', 10, 'bold'))
        lbl_term.pack(anchor='w', padx=8, pady=(6, 0))
        self.terminal = tk.Text(terminal_card, height=8, bg=self.terminal_bg, fg=self.terminal_fg, font=('Consolas', 11), state='disabled', bd=0)
        self.terminal.pack(fill=tk.BOTH, expand=False, padx=8, pady=(4, 8))

        # Tokens Card (right)
        tokens_card = tk.Frame(main_frame, bg=self.card_bg, bd=0)
        tokens_card.grid(row=0, column=1, rowspan=2, sticky='nsew')

        lbl_tokens = tk.Label(tokens_card, text="Tokens", bg=self.card_bg, fg='#073a5a', font=('Segoe UI', 10, 'bold'))
        lbl_tokens.pack(anchor='w', padx=8, pady=(8, 4))

        # Treeview for tokens
        cols = ('Type', 'Lexeme', 'Line', 'Col')
        self.tree = ttk.Treeview(tokens_card, columns=cols, show='headings', height=20)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.column('Type', width=110, anchor='w')
        self.tree.column('Lexeme', width=260, anchor='w')
        self.tree.column('Line', width=60, anchor='center')
        self.tree.column('Col', width=60, anchor='center')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        tree_scroll = ttk.Scrollbar(tokens_card, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8))
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # Insert starter sample
        sample = (
            "~ Sample KuCode program\n"
            "fixed num PI = 3.1416;\n"
            "num x = 10;\n"
            "decimal y = 2.5;\n"
            "text name = \"Axel\";\n"
            "start {\n"
            "    show(\"Hello, KuCode\");\n"
            "    check (x > 0) {\n"
            "        show(\"Positive\");\n"
            "    }\n"
            "}\n"
            "finish\n"
        )
        self.editor.insert("1.0", sample)
        # Initial draw of line numbers
        self.after(100, self._draw_line_numbers)

    # -------------------------
    # Scroll & line number sync
    # -------------------------
    def _on_vscroll(self, *args):
        """Scroll both editor and line numbers canvas."""
        self.editor.yview(*args)
        self._draw_line_numbers()

    def _on_editor_yscroll(self, *args):
        """Called by editor yscrollcommand — we attach scrollbar and update canvas."""
        self.vscroll.set(*args)
        self._draw_line_numbers()

    def _on_change(self, event=None):
        """Event handler for changes/scrolling to redraw line numbers."""
        try:
            self.editor.edit_modified(False)
        except Exception:
            pass
        self._draw_line_numbers()

    def _draw_line_numbers(self):
        """Draw static line numbers aligned with editor lines (no jump when typing)."""
        self.lnum_canvas.delete("all")

        # Get total number of lines
        total_lines = int(self.editor.index('end-1c').split('.')[0])

        # Compute line height based on font metrics (fixed height)
        try:
            font_metrics = self.editor.dlineinfo("1.0")
            line_height = font_metrics[3] if font_metrics else 20
        except Exception:
            line_height = 20

        # Scroll offset: how far the first visible line is scrolled
        first_visible_index = self.editor.index("@0,0")
        first_line = int(first_visible_index.split('.')[0])
        y_offset = -int(self.editor.dlineinfo(f"{first_line}.0")[1]) if self.editor.dlineinfo(f"{first_line}.0") else 0

        # Canvas height
        canvas_h = self.lnum_canvas.winfo_height()
        if canvas_h <= 0:
            return

        # Draw visible range only
        visible_lines = int(canvas_h / line_height) + 2
        for i in range(visible_lines):
            line_num = first_line + i
            if line_num > total_lines:
                break
            y = y_offset + i * line_height + line_height / 2
            self.lnum_canvas.create_text(
                50, y, text=str(line_num), anchor="e",
                fill=self.line_fg, font=("Consolas", 11)
            )


    # -------------------------
    # Terminal helpers
    # -------------------------
    def _write_terminal(self, text: str, error=False):
        self.terminal.configure(state='normal')
        self.terminal.delete('1.0', tk.END)
        self.terminal.insert('1.0', text)
        if error:
            self.terminal.tag_config('err', foreground='#ff6b6b')
            self.terminal.tag_add('err', '1.0', tk.END)
        else:
            self.terminal.tag_config('ok', foreground=self.terminal_fg)
            self.terminal.tag_add('ok', '1.0', tk.END)
        self.terminal.configure(state='disabled')

    # -------------------------
    # Actions
    # -------------------------
    def analyze_code(self):
        code = self.editor.get("1.0", "end-1c")
        tokens, errors = tokenize(code)
        # clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        for t in tokens:
            lex = t.lexeme
            if len(lex) > 180:
                lex = lex[:177] + "..."
            self.tree.insert('', 'end', values=(t.type, lex, t.line, t.col))
        if not errors:
            self._write_terminal("✅ Lexically correct — no lexical errors detected.\n", error=False)
        else:
            out = "❌ Lexical errors found:\n"
            for ln, col, msg in errors:
                out += f"Line {ln}, Col {col}: {msg}\n"
            self._write_terminal(out, error=True)

    def save_tokens(self):
        items = [self.tree.item(iid)['values'] for iid in self.tree.get_children()]
        if not items:
            messagebox.showinfo("No tokens", "No tokens to save. Run Analyze first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Lexeme', 'Line', 'Col'])
                for r in items:
                    writer.writerow(r)
            self._write_terminal(f"Tokens saved to: {path}\n", error=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tokens:\n{e}")

    def clear_all(self):
        self.editor.delete("1.0", "end")
        for i in self.tree.get_children():
            self.tree.delete(i)
        self._write_terminal("Cleared. Ready.\n", error=False)
        self._draw_line_numbers()


if __name__ == "__main__":
    app = ModernKuCodeApp()
    app.mainloop()
