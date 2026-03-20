import tkinter as tk
from tkinter import ttk, filedialog as fd
from tkinter.messagebox import showinfo, showerror
from os import path
import hashlib
import fpdf
import threading

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#1e1e2e"   # main background
BG2      = "#2a2a3e"   # card / frame background
ACCENT   = "#7c6af7"   # purple accent
ACCENT2  = "#a89cfa"   # lighter accent for hover
FG       = "#cdd6f4"   # primary text
FG_DIM   = "#6c7086"   # muted text
SUCCESS  = "#a6e3a1"   # green
ERROR    = "#f38ba8"   # red
RADIUS   = 8

# ── Root window ───────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("DXF Hash → PDF")
root.resizable(False, False)
root.geometry("480x320")
root.configure(bg=BG)

# ── ttk style ─────────────────────────────────────────────────────────────────
style = ttk.Style(root)
style.theme_use("clam")

style.configure("TFrame",        background=BG)
style.configure("Card.TFrame",   background=BG2)
style.configure("TLabel",        background=BG,  foreground=FG,
                                 font=("Segoe UI", 10))
style.configure("Dim.TLabel",    background=BG,  foreground=FG_DIM,
                                 font=("Segoe UI", 9))
style.configure("Title.TLabel",  background=BG,  foreground=FG,
                                 font=("Segoe UI", 13, "bold"))
style.configure("File.TLabel",   background=BG2, foreground=FG,
                                 font=("Segoe UI", 9),
                                 padding=(8, 6))

# Primary button
style.configure("Accent.TButton",
                background=ACCENT, foreground="#ffffff",
                font=("Segoe UI", 10, "bold"),
                borderwidth=0, focusthickness=0,
                padding=(14, 8))
style.map("Accent.TButton",
          background=[("active", ACCENT2), ("pressed", "#5a4ed4")],
          foreground=[("active", "#ffffff")])

# Secondary (ghost) button
style.configure("Ghost.TButton",
                background=BG2, foreground=FG,
                font=("Segoe UI", 10),
                borderwidth=0, focusthickness=0,
                padding=(14, 8))
style.map("Ghost.TButton",
          background=[("active", "#353550"), ("pressed", "#2a2a3e")],
          foreground=[("active", FG)])

# Progress bar
style.configure("Accent.Horizontal.TProgressbar",
                troughcolor=BG2, background=ACCENT,
                borderwidth=0, thickness=5)

# ── State ──────────────────────────────────────────────────────────────────────
thefile = ""

# ── Helpers ────────────────────────────────────────────────────────────────────
def select_file():
    global thefile
    filename = fd.askopenfilename(
        title="Επιλογή αρχείου",
        initialdir="/",
        filetypes=[("DXF files", "*.dxf"), ("All files", "*.*")]
    )
    if filename:
        thefile = filename
        short = path.basename(filename)
        file_label.config(text=f"📄  {short}")
        hash_btn.config(state="normal")
        set_status("Αρχείο επιλέχθηκε — πατήστε «Δημιουργία PDF»", FG_DIM)
        progress["value"] = 0

def set_status(msg, colour=FG_DIM):
    status_label.config(text=msg, foreground=colour)

def _do_hash():
    """Runs in a background thread so the UI stays responsive."""
    try:
        sha512   = hashlib.sha512()
        BUF_SIZE = 65536
        size     = path.getsize(thefile)
        done     = 0
        with open(thefile, "rb") as f:
            while chunk := f.read(BUF_SIZE):
                sha512.update(chunk)
                done += len(chunk)
                pct = done / size * 100
                root.after(0, lambda v=pct: progress.__setitem__("value", v))

        hashtext = sha512.hexdigest()
        pdf = fpdf.FPDF(format="letter")
        pdf.add_page()
        pdf.set_font("Arial", size=11)
        pdf.set_text_color(30, 30, 50)
        pdf.multi_cell(0, 8, txt=f"SHA-512\n\n{hashtext}", align="L")
        outfile = thefile + "_hash.pdf"
        pdf.output(outfile)

        root.after(0, lambda: [
            set_status(f"✓  {path.basename(outfile)}  δημιουργήθηκε", SUCCESS),
            progress.__setitem__("value", 100),
            hash_btn.config(state="normal"),
        ])
    except Exception as exc:
        root.after(0, lambda: [
            set_status(f"✗  Σφάλμα: {exc}", ERROR),
            hash_btn.config(state="normal"),
            progress.__setitem__("value", 0),
        ])

def hash_file():
    if not thefile:
        return
    hash_btn.config(state="disabled")
    set_status("Υπολογισμός hash…", FG_DIM)
    progress["value"] = 0
    threading.Thread(target=_do_hash, daemon=True).start()

def show_about():
    showinfo("About", "DXF Hash → PDF\n\ndnikolos@gmail.com")

# ── Layout ─────────────────────────────────────────────────────────────────────
# Header
header = ttk.Frame(root, style="TFrame")
header.pack(fill="x", padx=20, pady=(18, 6))
ttk.Label(header, text="DXF Hash → PDF", style="Title.TLabel").pack(side="left")
ttk.Button(header, text="About", style="Ghost.TButton",
           command=show_about).pack(side="right")

# Separator (hand-drawn, no ttk.Separator quirks)
sep = tk.Frame(root, bg=BG2, height=1)
sep.pack(fill="x", padx=20, pady=4)

# File card
card = ttk.Frame(root, style="Card.TFrame", padding=12)
card.pack(fill="x", padx=20, pady=8)

file_label = ttk.Label(card, text="📂  Κανένα αρχείο επιλεγμένο",
                        style="File.TLabel")
file_label.pack(fill="x")

# Buttons row
btn_row = ttk.Frame(root, style="TFrame")
btn_row.pack(fill="x", padx=20, pady=(4, 0))

open_btn = ttk.Button(btn_row, text="Επιλογή αρχείου",
                       style="Ghost.TButton", command=select_file)
open_btn.pack(side="left", padx=(0, 8))

hash_btn = ttk.Button(btn_row, text="Δημιουργία PDF",
                       style="Accent.TButton", command=hash_file,
                       state="disabled")
hash_btn.pack(side="left")

# Progress bar
progress = ttk.Progressbar(root, style="Accent.Horizontal.TProgressbar",
                            orient="horizontal", maximum=100, value=0)
progress.pack(fill="x", padx=20, pady=(12, 4))

# Status bar
status_label = ttk.Label(root, text="Επιλέξτε ένα αρχείο DXF για να ξεκινήσετε.",
                          style="Dim.TLabel")
status_label.pack(padx=20, pady=(0, 14), anchor="w")

# ── Run ────────────────────────────────────────────────────────────────────────
root.mainloop()
