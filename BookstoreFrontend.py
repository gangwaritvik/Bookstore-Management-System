import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG

# ---------- Database ----------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------- Neon Button ----------
class NeonButton(tk.Canvas):
    def __init__(self, parent, text, icon="", command=None,
                 base="#0b69ff", hover="#44a0ff", fg="#ffffff",
                 width=180, height=60, radius=18):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.text = text
        self.icon = icon
        self.base = base
        self.hover = hover
        self.fg = fg
        self.radius = radius
        self.width = width
        self.height = height
        self.bind("<Enter>", self._hover)
        self.bind("<Leave>", self._normal)
        self.bind("<Button-1>", self._click)
        self._draw(base)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2, x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self, color):
        self.delete("all")
        self._rounded_rect(0, 0, self.width, self.height, self.radius, fill=color, outline="")
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        self.create_text(self.width/2, self.height/2, text=label, fill=self.fg, font=("Segoe UI Semibold", 12))

    def _hover(self, e): self._draw(self.hover)
    def _normal(self, e): self._draw(self.base)
    def _click(self, e):
        if self.command:
            self.command()

# ---------- Main App ----------
class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Bookstore Management — Dark Neon")
        self.root.state("zoomed")
        self.root.configure(bg="#0d1117")
        self.create_login_screen()

    # ---------- LOGIN ----------
    def create_login_screen(self):
        self.clear_root()
        frame = tk.Frame(self.root, bg="#0f1720")
        frame.place(relx=0.5, rely=0.5, anchor="center", width=480, height=360)

        tk.Label(frame, text="Bookstore Login", bg="#0f1720", fg="#e6eefc",
                 font=("Segoe UI Semibold", 22)).pack(pady=(25, 10))
        tk.Label(frame, text="Username", bg="#0f1720", fg="#9fb6ff").pack()
        self.user = tk.Entry(frame, bg="#111421", fg="white", relief="flat", font=("Segoe UI", 12))
        self.user.pack(pady=5, ipady=6)
        tk.Label(frame, text="Password", bg="#0f1720", fg="#9fb6ff").pack()
        self.passw = tk.Entry(frame, show="*", bg="#111421", fg="white", relief="flat", font=("Segoe UI", 12))
        self.passw.pack(pady=5, ipady=6)
        NeonButton(frame, text="Login", icon="🔒", base="#0b69ff",
                   hover="#44a0ff", command=self.login).pack(pady=15)
        tk.Label(frame, text="Default: admin / admin", bg="#0f1720", fg="#6f8fbf").pack()

    def login(self):
        u, p = self.user.get(), self.passw.get()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM admin WHERE Username=%s AND Password=%s", (u, p))
            if cur.fetchone():
                self.create_dashboard()
            else:
                messagebox.showerror("Error", "Invalid Credentials")
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ---------- DASHBOARD ----------
    def create_dashboard(self):
        self.clear_root()
        tk.Label(self.root, text="📘 Bookstore Dashboard", bg="#0d1117",
                 fg="#e6eefc", font=("Segoe UI Semibold", 26)).pack(pady=20)

        grid = tk.Frame(self.root, bg="#0d1117")
        grid.pack(expand=True)

        buttons = [
            ("Admin", "🧑‍💼"), ("Staff", "👩‍💻"), ("Supplier", "🚚"), ("Book", "📚"),
            ("Customer", "🧍"), ("Orders", "🧾"), ("OrderDetails", "📦"), ("Supply", "🔗")
        ]

        for i, (name, icon) in enumerate(buttons):
            NeonButton(grid, text=name, icon=icon, width=220, height=70, radius=18,
                       base="#0b69ff", hover="#44a0ff",
                       command=lambda n=name.lower(): self.open_table_window(n)
                       ).grid(row=i//4, column=i%4, padx=30, pady=25)

    # ---------- TABLE WINDOW ----------
    def open_table_window(self, table):
        win = tk.Toplevel(self.root)
        win.title(f"{table.capitalize()} Records")
        win.geometry("1200x750")
        win.configure(bg="#0d1117")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Neon.Treeview", background="#0f1720", foreground="#e6eefc",
                        fieldbackground="#0f1720", rowheight=28, font=("Segoe UI", 10))
        style.configure("Neon.Treeview.Heading", background="#0b69ff", foreground="white",
                        font=("Segoe UI Semibold", 11))
        style.map("Neon.Treeview", background=[('selected', '#44a0ff')])

        tk.Label(win, text=f"{table.capitalize()} Management", bg="#0d1117", fg="#e6eefc",
                 font=("Segoe UI Semibold", 18)).pack(pady=10)

        frame = tk.Frame(win, bg="#0d1117")
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        tree = ttk.Treeview(frame, show="headings", style="Neon.Treeview")
        tree.pack(fill="both", expand=True)
        ttk.Scrollbar(frame, orient="vertical", command=tree.yview).pack(side="right", fill="y")
        ttk.Scrollbar(frame, orient="horizontal", command=tree.xview).pack(side="bottom", fill="x")
        tree.configure(yscrollcommand=lambda f,l: None, xscrollcommand=lambda f,l: None)

        btns = tk.Frame(win, bg="#0d1117")
        btns.pack(pady=12)
        NeonButton(btns, text="Add", icon="➕", base="#00c853", hover="#52e089",
                   command=lambda: self.add_record(table, tree)).grid(row=0, column=0, padx=10)
        NeonButton(btns, text="Edit", icon="✏️", base="#ffb300", hover="#ffd46a",
                   command=lambda: self.edit_record(table, tree)).grid(row=0, column=1, padx=10)
        NeonButton(btns, text="Delete", icon="🗑️", base="#ff3b30", hover="#ff6b6b",
                   command=lambda: self.delete_record(table, tree)).grid(row=0, column=2, padx=10)
        NeonButton(btns, text="Refresh", icon="🔄", base="#0b69ff", hover="#44a0ff",
                   command=lambda: self.load_data(table, tree)).grid(row=0, column=3, padx=10)

        self.load_data(table, tree)

    # ---------- DATA OPS ----------
    def load_data(self, table, tree):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table}")
        cols = [c[0] for c in cur.fetchall()]
        tree["columns"] = cols
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor="center")
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        tree.delete(*tree.get_children())
        for r in rows:
            tree.insert("", "end", values=r)
        conn.close()

    def add_record(self, table, tree):
        form = tk.Toplevel(self.root)
        form.title(f"Add {table.capitalize()}")
        form.geometry("520x520")
        form.configure(bg="#0f1720")

        tk.Label(form, text=f"Add New {table.capitalize()} Record", bg="#0f1720",
                 fg="#e6eefc", font=("Segoe UI Semibold", 14)).pack(pady=10)

        frm = tk.Frame(form, bg="#0f1720")
        frm.pack(pady=10)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table}")
        cols = [c[0] for c in cur.fetchall()][1:]
        conn.close()

        entries = {}

        for i, col in enumerate(cols):
            tk.Label(frm, text=col, bg="#0f1720", fg="#9fb6ff").grid(row=i, column=0, padx=6, pady=6)
            # special dropdowns
            if table == "orders" and col in ["Customer_ID", "Staff_ID"]:
                values = self.fetch_dropdown(col.split('_')[0].lower())
                cb = ttk.Combobox(frm, values=values, font=("Segoe UI", 10))
                cb.grid(row=i, column=1, padx=6, pady=6)
                entries[col] = cb
            elif table == "orderdetails" and col in ["Order_ID", "Book_ID"]:
                values = self.fetch_dropdown(col.split('_')[0].lower())
                cb = ttk.Combobox(frm, values=values, font=("Segoe UI", 10))
                cb.grid(row=i, column=1, padx=6, pady=6)
                entries[col] = cb
            elif table == "supply" and col in ["Supplier_ID", "Book_ID"]:
                values = self.fetch_dropdown(col.split('_')[0].lower())
                cb = ttk.Combobox(frm, values=values, font=("Segoe UI", 10))
                cb.grid(row=i, column=1, padx=6, pady=6)
                entries[col] = cb
            else:
                e = tk.Entry(frm, bg="#111421", fg="white", relief="flat")
                e.grid(row=i, column=1, padx=6, pady=6)
                entries[col] = e

        def save():
            vals = [entries[c].get() for c in cols]
            if not all(vals):
                messagebox.showwarning("Missing", "All fields required.")
                return
            conn = get_connection()
            cur = conn.cursor()
            placeholders = ",".join(["%s"] * len(vals))
            cur.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", vals)
            conn.commit()
            conn.close()
            form.destroy()
            self.load_data(table, tree)

        NeonButton(form, text="Save", icon="💾", base="#00c853", hover="#52e089",
                   command=save).pack(pady=15)

    def fetch_dropdown(self, tab):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT {tab.capitalize()}_ID FROM {tab}")
            vals = [str(x[0]) for x in cur.fetchall()]
            conn.close()
            return vals
        except:
            return []

    def edit_record(self, table, tree):
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Select a record to edit.")
            return
        vals = tree.item(sel, "values")
        form = tk.Toplevel(self.root)
        form.title(f"Edit {table.capitalize()}")
        form.geometry("520x520")
        form.configure(bg="#0f1720")

        tk.Label(form, text=f"Edit {table.capitalize()} Record", bg="#0f1720",
                 fg="#e6eefc", font=("Segoe UI Semibold", 14)).pack(pady=10)

        frm = tk.Frame(form, bg="#0f1720")
        frm.pack(pady=10)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table}")
        cols = [c[0] for c in cur.fetchall()]
        conn.close()
        id_col = cols[0]

        entries = {}
        for i, col in enumerate(cols[1:]):
            tk.Label(frm, text=col, bg="#0f1720", fg="#9fb6ff").grid(row=i, column=0, padx=6, pady=6)
            e = tk.Entry(frm, bg="#111421", fg="white", relief="flat")
            e.grid(row=i, column=1, padx=6, pady=6)
            e.insert(0, vals[i+1])
            entries[col] = e

        def update():
            new_vals = [entries[c].get() for c in cols[1:]]
            conn = get_connection()
            cur = conn.cursor()
            set_clause = ", ".join([f"{c}=%s" for c in cols[1:]])
            cur.execute(f"UPDATE {table} SET {set_clause} WHERE {id_col}=%s", (*new_vals, vals[0]))
            conn.commit()
            conn.close()
            form.destroy()
            self.load_data(table, tree)

        NeonButton(form, text="Update", icon="✅", base="#ffb300", hover="#ffd46a",
                   command=update).pack(pady=15)

    def delete_record(self, table, tree):
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Please select a record.")
            return
        vals = tree.item(sel, "values")
        if not messagebox.askyesno("Delete", f"Delete record {vals[0]}?"):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table}")
        id_col = cur.fetchone()[0]
        cur.execute(f"DELETE FROM {table} WHERE {id_col}=%s", (vals[0],))
        conn.commit()
        conn.close()
        self.load_data(table, tree)

    def clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()
