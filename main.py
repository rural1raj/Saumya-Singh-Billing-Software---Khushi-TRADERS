import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, datetime, os, platform, subprocess
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# DATABASE 
db = sqlite3.connect("billing.db")
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT,password TEXT)")
cur.execute("""CREATE TABLE IF NOT EXISTS invoices(
invoice_no INTEGER PRIMARY KEY,
date TEXT, customer TEXT, total REAL)""")

cur.execute("SELECT * FROM users")
if not cur.fetchone():
    cur.execute("INSERT INTO users VALUES('admin','1234')")
    db.commit()

# MAIN WINDOW 
root = tk.Tk()
root.title("Saumya Singh Billing Software - Khushi TRADERS")
root.geometry("950x600")
root.config(bg="#2aff16")


title_label= tk.Label(
    root,
    text= (" SAUMYA SIN ,GH BILLING SYSTEM"),
    font= ("Helvetica",18,"bold"),
    bg="#000000",
    fg= "#18E5F8",
    padx=10,
    pady=15,
)
title_label.pack(fill="x")

# ================= LOGIN =================
def login():
    cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                (user_e.get(), pass_e.get()))
    if cur.fetchone():
        login_f.pack_forget()
        dash.pack(fill="both", expand=True)
    else:
        messagebox.showerror("Error","Invalid Login")

login_f = tk.Frame(root, bg="#04F9F5", padx=40, pady=40)
login_f.pack(expand=True)

tk.Label(login_f, text="USER LOGIN",font=("Arial",16,"bold"),bg="green",fg="white").pack(pady=10 ,fill="x")

tk.Label(login_f, text="Username",bg="#1DFAE0").pack(anchor="center")
user_e = tk.Entry(login_f, width=30)
user_e.pack()

tk.Label(login_f, text="Password",background="#1DFAE0").pack(anchor="center")
pass_e = tk.Entry(login_f, width=30, show="*")
pass_e.pack()

tk.Button(login_f, text="LOGIN",font= ("Helvetica",13,"bold"),
          bg="#0A1E13", fg="#35F320",
          command=login).pack(pady=15,fill="x")

# ================= DASHBOARD =================
dash=tk.Frame(root,bg="#35fefe")
tk.Label(dash,text="KHUSHI TRADERS – GST BILLING SOFTWARE",
         bg="#1F618D",fg="white",
         font=("Arial",18,"bold"),pady=10).pack(fill="x")

btn_f=tk.Frame(dash,bg="#a97fe9")
btn_f.pack(pady=40)

# ================= PDF =================
def generate_pdf(inv,cust,items,sub,cgst,sgst,total):
    file=f"Invoice_{inv}.pdf"
    pdf=SimpleDocTemplate(file,pagesize=A4)
    styles=getSampleStyleSheet()

    data=[["Product/Item","Qty","Price","Total"]]+items

    pdf.build([
        Paragraph("<b>KHUSHI TRADERS</b>",styles["Title"]),
        Paragraph("GSTIN: 08ABCDE1234F1Z5",styles["Normal"]),
        Paragraph(f"Invoice No: {inv}",styles["Normal"]),
        Paragraph(f"Customer: {cust}",styles["Normal"]),
        Table(data),
        Paragraph(f"Subtotal: ₹{sub:.2f}",styles["Normal"]),
        Paragraph(f"CGST 5%: ₹{cgst:.2f}",styles["Normal"]),
        Paragraph(f"SGST 5%: ₹{sgst:.2f}",styles["Normal"]),
        Paragraph(f"<b>Grand Total: ₹{total:.2f}</b>",styles["Heading2"])
    ])

    # Cross-platform open
    if platform.system() == "Windows":
        os.startfile(file)
    elif platform.system() == "Darwin":
        subprocess.call(["open", file])
    else:
        subprocess.call(["xdg-open", file])

# ================= NEW INVOICE =================
def new_invoice(edit_data=None):
    win=tk.Toplevel(root)
    win.title("New Invoice")
    win.geometry("900x550")
    win.config(bg="#106D43")

    items=[]

    # Auto Invoice Number
    if edit_data:
        inv = edit_data
    else:
        cur.execute("SELECT MAX(invoice_no) FROM invoices")
        last = cur.fetchone()[0]
        inv = 1001 if not last else last + 1

    tk.Label(win,text="KHUSHI BILLING SYSTEM",
             font=("Arial",16,"bold"),
             bg="cyan").pack(fill="x")

    tk.Label(win,text=f"Invoice No: {inv}",
             font=("Arial",12,"bold"),
             bg="red",fg="white").pack()

    tk.Label(win,text="Customer Name",
             font=("Arial",12,"bold"),
             bg="#C3F846").pack(anchor="w",padx=20)

    cust=tk.Entry(win,width=40)
    cust.pack(padx=20)

    table=ttk.Treeview(win,
                       columns=("Product/Item Name","Qty","Price","Total"),
                       show="headings")
    for c in ("Product/Item Name","Qty","Price","Total"):
        table.heading(c,text=c)
    table.pack(expand=True,fill="both",padx=20,pady=10)

    form=tk.Frame(win); form.pack()

    tk.Label(form,text="Product/Item",bg="#F8852D").grid(row=0,column=0)
    tk.Label(form,text="Qty",bg="#F3F5F0",).grid(row=0,column=1)
    tk.Label(form,text="Price",bg="#1DF316").grid(row=0,column=2)

    item=tk.Entry(form,width=20)
    qty=tk.Entry(form,width=8)
    price=tk.Entry(form,width=10)

    item.grid(row=1,column=0)
    qty.grid(row=1,column=1)
    price.grid(row=1,column=2)

    sub=tk.StringVar(value="0")
    cg=tk.StringVar(value="0")
    sg=tk.StringVar(value="0")
    gt=tk.StringVar(value="0")

    def update():
        s=sum(i[3] for i in items)
        c=s*0.05
        g=s*0.05
        t=s+c+g
        sub.set(f"{s:.2f}")
        cg.set(f"{c:.2f}")
        sg.set(f"{g:.2f}")
        gt.set(f"{t:.2f}")

    def add():
        try:
            q=int(qty.get())
            p=float(price.get())
        except:
            messagebox.showerror("Error","Invalid Qty or Price")
            return

        if not item.get():
            return

        t=q*p
        items.append([item.get(),q,p,t])
        table.insert("", "end", values=items[-1])
        item.delete(0,"end")
        qty.delete(0,"end")
        price.delete(0,"end")
        update()

    def delete():
        s=table.selection()
        if not s: return
        i=table.index(s[0])
        table.delete(s[0])
        items.pop(i)
        update()

    tk.Button(form,text="Add",bg="#0DD906",command=add).grid(row=1,column=3)
    tk.Button(form,text="Delete",bg="#E1110A",command=delete).grid(row=1,column=4)

    tf=tk.Frame(win); tf.pack(anchor="e",padx=20)
    tk.Label(tf,text="Grand Total").grid(row=0,column=0)
    tk.Label(tf,textvariable=gt,
             font=("Arial",11,"bold")).grid(row=0,column=1)

    def save():
        if not cust.get() or not items:
            messagebox.showerror("Error","Fill details first")
            return

        total=float(gt.get())

        if edit_data:
            cur.execute("UPDATE invoices SET customer=?, total=? WHERE invoice_no=?",
                        (cust.get(), total, inv))
        else:
            cur.execute("INSERT INTO invoices VALUES(?,?,?,?)",
                        (inv,datetime.date.today(),cust.get(),total))

        db.commit()

        generate_pdf(inv,cust.get(),items,
                     float(sub.get()),
                     float(cg.get()),
                     float(sg.get()),
                     total)

        win.destroy()

    tk.Button(win,text="Save & PDF",
              bg="#3EE985",fg="#030401",
              command=save).pack(pady=5)

    tk.Button(win,text="⬅ Back",bg="#C3F846",
              command=win.destroy).pack()

# ================= SEARCH =================
def search_invoice():
    win=tk.Toplevel(root)
    win.title("Search Invoice")
    win.geometry("650x400")
    win.config(background="#15EA75")

    tk.Label(win,text="Search Invoice").pack()

    se=tk.Entry(win,width=30)
    se.pack()

    tree=ttk.Treeview(win,
                      columns=("Invoice No","Date","Customer","Total"),
                      show="headings")
    r= 1
    for c in ("Invoice No","Date","Customer","Total"):
        tree.heading(c,text=c)


    tree.pack(expand=True,fill="both")

    def load(q=""):
        tree.delete(*tree.get_children())
        if q:
            cur.execute("""SELECT * FROM invoices
                        WHERE invoice_no LIKE ?
                        OR customer LIKE ?""",
                        (f"%{q}%",f"%{q}%"))
        else:
            cur.execute("SELECT * FROM invoices")

        for r in cur.fetchall():
            tree.insert("", "end", values=r)

    def delete_inv():
        s=tree.selection()
        if not s: return
        inv=tree.item(s[0])["values"][0]

        if messagebox.askyesno("Confirm","Delete invoice?"):
            cur.execute("DELETE FROM invoices WHERE invoice_no=?", (inv,))
            db.commit()
            load()

    def edit_inv():
        s=tree.selection()
        if not s: return
        inv=tree.item(s[0])["values"][0]
        new_invoice(inv)

    load()
    se.bind("<KeyRelease>",lambda e: load(se.get()))

    bf=tk.Frame(win); bf.pack(pady=5)
    tk.Button(bf,text="Delete Invoice",
              bg="#C0392B",fg="white",
              command=delete_inv).grid(row=0,column=0,padx=5)

    tk.Button(bf,text="Edit",
              bg="#F126E3",
              command=edit_inv).grid(row=0,column=1,padx=5)

    tk.Button(bf,text="⬅ Back",bg="#C3F846",
              command=win.destroy).grid(row=0,column=2,padx=5)

# ================= DASH BUTTONS =================
tk.Button(btn_f,text="New Invoice",
          width=25,height=2,
          command=new_invoice).grid(row=0,column=0,padx=10)

tk.Button(btn_f,text="Search Invoice",
          width=25,height=2,
          command=search_invoice).grid(row=0,column=1,padx=10)

tk.Button(btn_f,text="Exit",
          width=25,height=2,
          command=root.destroy).grid(row=0,column=2,padx=10)

root.mainloop()

