import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from config import DB_CONFIG

# ---------------- Database Helper -----------------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ---------------- Utility: Neon Button -----------------
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
        self._draw_static()
        self.bind("<Enter>", lambda e: self._draw_hover())
        self.bind("<Leave>", lambda e: self._draw_static())
        self.bind("<Button-1>", self._on_click)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1,
            x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2,
            x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw_static(self):
        self.delete("all")
        self._rounded_rect(6, 6, self.width - 6, self.height - 6, self.radius, fill=self.base, outline="")
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        self.create_text(self.width/2, self.height/2, text=label, fill=self.fg, font=("Segoe UI Semibold", 12))

    def _draw_hover(self):
        self.delete("all")
        self._rounded_rect(6, 6, self.width - 6, self.height - 6, self.radius, fill=self.hover, outline="")
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        self.create_text(self.width/2, self.height/2, text=label, fill=self.fg, font=("Segoe UI Semibold", 12))

    def _on_click(self, _):
        if callable(self.command):
            try:
                self.command()
            except Exception as e:
                messagebox.showerror("Error", str(e))

# ---------------- Main App -----------------
class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Bookstore Management")
        self.root.state("zoomed")
        self.root.configure(bg="#0d1117")
        self.create_login_screen()

    # ---------- LOGIN ----------
    def create_login_screen(self):
        self._clear_root()
        center = tk.Frame(self.root, bg="#0d1117")
        center.pack(expand=True, fill="both")

        card = tk.Frame(center, bg="#0f1720")
        card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=380)

        tk.Label(card, text="Bookstore Admin Login", bg="#0f1720", fg="#e6eefc", font=("Segoe UI Semibold", 22)).pack(pady=(30,12))
        tk.Label(card, text="Username", bg="#0f1720", fg="#9fb6ff", font=("Segoe UI", 10)).pack(anchor="w", padx=36)
        self.entry_user = tk.Entry(card, bg="#111421", fg="#dbe9ff", relief="flat", font=("Segoe UI", 11))
        self.entry_user.pack(fill="x", padx=36, pady=(6,10), ipady=8)
        tk.Label(card, text="Password", bg="#0f1720", fg="#9fb6ff", font=("Segoe UI", 10)).pack(anchor="w", padx=36)
        self.entry_pwd = tk.Entry(card, show="*", bg="#111421", fg="#dbe9ff", relief="flat", font=("Segoe UI", 11))
        self.entry_pwd.pack(fill="x", padx=36, pady=(6,20), ipady=8)

        NeonButton(card, text="Login", icon="🔒", command=self._attempt_login,
                   base="#0b69ff", hover="#44a0ff", width=220, height=56, radius=14).pack(pady=(6,20))
        tk.Label(card, text="Default: admin / admin", bg="#0f1720", fg="#6f8fbf", font=("Segoe UI", 9)).pack()

    def _attempt_login(self):
        user, pwd = self.entry_user.get().strip(), self.entry_pwd.get().strip()
        if not user or not pwd:
            messagebox.showwarning("Login", "Enter username and password.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor(buffered=True)
            cur.execute("SELECT * FROM admin WHERE Username=%s AND Password=%s", (user, pwd))
            if cur.fetchone():
                self.create_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid credentials.")
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ---------- DASHBOARD ----------
    def create_dashboard(self):
        self._clear_root()
        tk.Label(self.root, text="📘 Bookstore Dashboard", bg="#0d1117", fg="#dbe9ff",
                 font=("Segoe UI Semibold", 28)).pack(pady=20)
        container = tk.Frame(self.root, bg="#0d1117")
        container.pack(expand=True, fill="both")

        buttons = [
            ("Admin", "🧑‍💼", "#0b69ff"), ("Staff", "👩‍💻", "#1666ff"),
            ("Supplier", "🚚", "#1e90ff"), ("Book", "📚", "#3aa6ff"),
            ("Customer", "🧍", "#0b69ff"), ("Orders", "🧾", "#1666ff"),
            ("OrderDetails", "📦", "#1e90ff"), ("Supply", "🔗", "#3aa6ff")
        ]
        grid = tk.Frame(container, bg="#0d1117")
        grid.place(relx=0.5, rely=0.5, anchor="center")

        for i, (name, icon, color) in enumerate(buttons):
            NeonButton(grid, text=name, icon=icon,
                       command=lambda n=name.lower(): self.open_table_window(n),
                       base=color, hover="#69b8ff", width=220, height=70, radius=20).grid(
                row=i//4, column=i%4, padx=28, pady=22
            )

    # ---------- TABLE WINDOW ----------
    def open_table_window(self, table_name):
        win = tk.Toplevel(self.root)
        win.title(f"{table_name.capitalize()} Management")
        win.geometry("1200x760")
        win.configure(bg="#0d1117")

        tk.Label(win, text=f"{table_name.capitalize()} Records", bg="#0d1117", fg="#e6eefc",
                 font=("Segoe UI Semibold", 18)).pack(pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0f1720", fieldbackground="#0f1720",
                        foreground="#e6eefc", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#0b69ff", foreground="white", font=("Segoe UI Semibold", 11))

        frame = tk.Frame(win, bg="#0d1117")
        frame.pack(fill="both", expand=True, padx=14, pady=10)
        tree = ttk.Treeview(frame, show="headings")
        tree.pack(fill="both", expand=True)
        ttk.Scrollbar(frame, orient="vertical", command=tree.yview).pack(side="right", fill="y")

        ctrl = tk.Frame(win, bg="#0d1117")
        ctrl.pack(pady=12)
        NeonButton(ctrl, text="Add", icon="➕", base="#00c853", hover="#52e089",
                   width=160, command=lambda: self._open_add_form(table_name, tree)).grid(row=0, column=0, padx=10)
        NeonButton(ctrl, text="Delete", icon="🗑️", base="#ff3b30", hover="#ff6b6b",
                   width=160, command=lambda: self._delete_record(table_name, tree)).grid(row=0, column=1, padx=10)
        NeonButton(ctrl, text="Refresh", icon="🔄", base="#0b69ff", hover="#44a0ff",
                   width=160, command=lambda: self._load_table_data(table_name, tree)).grid(row=0, column=2, padx=10)

        self._load_table_data(table_name, tree)

    # ---------- Load Table ----------
    def _load_table_data(self, table_name, tree):
        try:
            conn = get_connection()
            cur = conn.cursor(buffered=True)
            cur.execute(f"SHOW COLUMNS FROM {table_name}")
            cols = [r[0] for r in cur.fetchall()]
            tree["columns"] = cols
            for c in cols:
                tree.heading(c, text=c)
                tree.column(c, width=140)
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert("", "end", values=r)
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    # ---------- Add Form ----------
    def _open_add_form(self, table_name, tree):
        try:
            conn = get_connection()
            cur = conn.cursor(buffered=True)
            cur.execute(f"SHOW COLUMNS FROM {table_name}")
            cols = [r[0] for r in cur.fetchall()][1:]
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return

        form = tk.Toplevel(self.root)
        form.title(f"Add to {table_name.capitalize()}")
        form.geometry("520x520")
        form.configure(bg="#0f1720")
        tk.Label(form, text=f"Add New {table_name.capitalize()} Record", bg="#0f1720", fg="#dbe9ff",
                 font=("Segoe UI Semibold", 14)).pack(pady=12)
        canvas = tk.Frame(form, bg="#0f1720")
        canvas.pack(padx=14, pady=6, fill="both", expand=True)
        entries = {}

        # --- Foreign Key Dropdown Logic ---
        conn = get_connection()
        cur = conn.cursor(buffered=True)

        if table_name.lower() == "orders":
            cur.execute("SELECT Customer_ID FROM customer")
            cust_ids = [str(x[0]) for x in cur.fetchall()]
            cur.execute("SELECT Staff_ID FROM staff")
            staff_ids = [str(x[0]) for x in cur.fetchall()]
            fields = [("Customer_ID", cust_ids), ("Staff_ID", staff_ids), ("Order_Date (YYYY-MM-DD)", None), ("Order_Amount", None)]

        elif table_name.lower() == "orderdetails":
            cur.execute("SELECT Order_ID FROM orders")
            order_ids = [str(x[0]) for x in cur.fetchall()]
            cur.execute("SELECT Book_ID FROM book")
            book_ids = [str(x[0]) for x in cur.fetchall()]
            fields = [("Order_ID", order_ids), ("Book_ID", book_ids), ("Quantity", None), ("Subtotal", None)]

        elif table_name.lower() == "supply":
            cur.execute("SELECT Supplier_ID FROM supplier")
            supp_ids = [str(x[0]) for x in cur.fetchall()]
            cur.execute("SELECT Book_ID FROM book")
            book_ids = [str(x[0]) for x in cur.fetchall()]
            fields = [("Supplier_ID", supp_ids), ("Book_ID", book_ids), ("Quantity", None), ("Supply_Date (YYYY-MM-DD)", None)]

        else:
            fields = [(c, None) for c in cols]

        conn.close()

        for i, (name, options) in enumerate(fields):
            tk.Label(canvas, text=name, bg="#0f1720", fg="#9fb6ff").grid(row=i, column=0, padx=8, pady=6, sticky="e")
            if options:
                cb = ttk.Combobox(canvas, values=options, state="readonly", width=32)
                cb.grid(row=i, column=1, padx=8, pady=6)
                entries[name.split()[0]] = cb
            else:
                ent = tk.Entry(canvas, bg="#111421", fg="#e6eefc", relief="flat", width=34)
                ent.grid(row=i, column=1, padx=8, pady=6)
                entries[name.split()[0]] = ent

        def save():
            vals = [entries[c].get().strip() for c in entries]
            if not all(vals):
                messagebox.showwarning("Input required", "Please fill all fields.")
                return
            try:
                conn = get_connection()
                cur = conn.cursor(buffered=True)
                placeholders = ",".join(["%s"] * len(vals))
                cur.execute(f"INSERT INTO {table_name} ({','.join(entries.keys())}) VALUES ({placeholders})", vals)
                conn.commit()
                conn.close()
                form.destroy()
                self._load_table_data(table_name, tree)
            except Exception as e:
                messagebox.showerror("DB Error", str(e))

        NeonButton(form, text="Save", icon="💾", base="#00c853", hover="#52e089", width=160, command=save).pack(pady=14)

    # ---------- Delete ----------
    def _delete_record(self, table_name, tree):
        sel = tree.focus()
        if not sel:
            messagebox.showwarning("Select", "Please select a record.")
            return
        vals = tree.item(sel, "values")
        if not messagebox.askyesno("Delete", f"Delete record {vals[0]}?"):
            return
        try:
            conn = get_connection()
            cur = conn.cursor(buffered=True)
            cur.execute(f"SHOW COLUMNS FROM {table_name}")
            id_col = cur.fetchone()[0]
            cur.execute(f"DELETE FROM {table_name} WHERE {id_col}=%s", (vals[0],))
            conn.commit()
            conn.close()
            self._load_table_data(table_name, tree)
        except Exception as e:
            messagebox.showerror("DB Error", str(e))

    def _clear_root(self):
        for w in self.root.winfo_children():
            w.destroy()

# ---------------- Run ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()
