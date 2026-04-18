import tkinter as tk
import os
from tkinter import ttk, messagebox
from datetime import datetime
from database import get_customers, get_items
from database import save_quotation
from database import get_quotation_history
from database import get_latest_quotation
from pdf_generator import generate_pdf

def show_create_quote(content, company_info, my_name):
    for w in content.winfo_children(): w.destroy()
    main = tk.Frame(content, padx=10, pady=10)
    main.pack(fill='both', expand=True)

    # -------------------- Quotation header form --------------------
    top = tk.Frame(main); top.pack(anchor='nw', fill='x')
    tk.Label(top, text="Create Quotation", font=('Helvetica',14)).grid(row=0,column=0,columnspan=4,pady=8,sticky='w')

    tk.Label(top,text="Quotation No").grid(row=1,column=0,sticky='e')
    qno_ent = tk.Entry(top); qno_ent.grid(row=1,column=1,padx=6)
    tk.Label(top,text="Quotation Date").grid(row=1,column=2,sticky='e')
    qdate_ent = tk.Entry(top); qdate_ent.grid(row=1,column=3,padx=6)
    qdate_ent.insert(0, datetime.now().strftime("%d-%m-%Y"))

    
    # Customer dropdown
    tk.Label(top,text="Select Customer").grid(row=3,column=0,sticky='e')
    customers = get_customers()
    cust_map = {r[1]: r for r in customers}
    cust_var = tk.StringVar()
    cb_cust = ttk.Combobox(top,textvariable=cust_var,values=list(cust_map.keys()),state="readonly",width=40)
    cb_cust.grid(row=3,column=1,columnspan=3,sticky='w',padx=6)
    if customers: cb_cust.current(0)

    # -------------------- Middle section --------------------
    mid = tk.Frame(main); mid.pack(fill='both',expand=True,pady=8)

    # Left: Item search
    left = tk.Frame(mid,bd=1,relief='sunken',padx=6,pady=6)
    left.pack(side='left',fill='y')
    tk.Label(left,text="Search Items").pack(anchor='w')
    search_var = tk.StringVar()
    e_search = tk.Entry(left,textvariable=search_var,width=30); e_search.pack(pady=4)
    lb = tk.Listbox(left,width=40,height=18); lb.pack()
    items_cache = []

    def populate_items(search=""):
        lb.delete(0,'end'); items_cache.clear()
        rows = get_items(search)
        for r in rows:
            items_cache.append(r)
            lb.insert('end', f"{r[1]} | HSN:{r[2]} | {r[3]} | ₹{r[4]:.2f}")

    def on_search(*_): populate_items(search_var.get().strip())
    search_var.trace_add('write', on_search)
    populate_items()

    # Center: item details + add button
    center = tk.Frame(mid,padx=6,pady=6); center.pack(side='left')
    sel_lbl = tk.Label(center,text="No item selected",wraplength=200,justify='left')
    sel_lbl.pack(pady=6)
    tk.Label(center,text="Quantity").pack(anchor='w')
    qty_spin = tk.Spinbox(center,from_=1,to=10000,width=8); qty_spin.pack()
    tk.Label(center,text="UOM").pack(anchor='w')
    uom_var = tk.StringVar(value="Nos")
    cb_uom = ttk.Combobox(center,textvariable=uom_var,values=["Nos","Mtr","Set","Joints"],state="readonly",width=10)
    cb_uom.pack()
    tk.Label(center,text="Price").pack(anchor='w')
    price_ent = tk.Entry(center,width=12); price_ent.pack()

    selected_item = {"data": None}

    def on_select(evt=None):
        sel = lb.curselection()
        if not sel: return
        it = items_cache[sel[0]]
        selected_item["data"] = it
        sel_lbl.config(text=f"{it[1]} | HSN:{it[2]} | {it[3]}")
        qty_spin.delete(0,'end'); qty_spin.insert(0,"1")
        uom_var.set("Nos")
        price_ent.delete(0,'end'); price_ent.insert(0,f"{it[4]:.2f}")
        if cust_var.get():
            cust_row = cust_map[cust_var.get()]
            latest = get_latest_quotation(cust_row[0], it[0])  # customer_id, item_id

            if latest:
                sel_lbl.config(
                text=(f"{it[1]} | HSN:{it[2]} | {it[3]}\n"
                  f"Latest Quote → No:{latest[0]} Date:{latest[1]} | "
                  f"Qty:{latest[6]} {latest[7]} | Price:₹{latest[8]:.2f}")
                )
            else:
                sel_lbl.config(
                text=f"{it[1]} | HSN:{it[2]} | {it[3]}\nNo previous quotations for this customer."
                )
            #if history:
                #hist_text = "\n".join([f"No:{h[0]} Date:{h[1]}" for h in history[:5]])
                #sel_lbl.config(text=f"{it[1]} | HSN:{it[2]} | {it[3]}\nPrevious Quotes:\n{hist_text}")



    lb.bind("<<ListboxSelect>>", on_select)

    # Right: Treeview of added items
    right = tk.Frame(mid,bd=1,relief='sunken',padx=6,pady=6)
    right.pack(side='left',fill='both',expand=True)
    #tv = ttk.Treeview(right,columns=("SNo","Item","HSN","Make","Qty","UOM","Price"),show='headings')
    tv = ttk.Treeview(right,columns=("SNo","Item","HSN","Make","Qty","UOM","Price","ItemID"),show='headings')
    tv.heading("ItemID", text="ItemID")
    tv.column("ItemID", width=0, stretch=False)  # invisible

    for col,wid in zip(("SNo","Item","HSN","Make","Qty","UOM","Price"),(40,180,60,70,50,60,70)):
        tv.heading(col,text=col); tv.column(col,width=wid,anchor='center')
    tv.pack(fill='both',expand=True)

    # Add to quote
    def add_item():
        if not selected_item["data"]:
            messagebox.showwarning("Select","Please select an item"); return
        try:
            qty = float(qty_spin.get()); price = float(price_ent.get())
        except: 
            messagebox.showerror("Error","Enter valid qty/price"); return
        it = selected_item["data"]
        idx = len(tv.get_children())+1
        tv.insert('', 'end', values=(idx,it[1],it[2],it[3],qty,uom_var.get(),price,it[0]))
        update_total()

    tk.Button(center,text="Add →",command=add_item).pack(pady=6)

    # Buttons to remove/clear
    btns = tk.Frame(right); btns.pack(fill='x')
    def remove():
        for s in tv.selection(): tv.delete(s)
        reindex(); update_total()
    def clear():
        for i in tv.get_children(): tv.delete(i)
        update_total()
    tk.Button(btns,text="Remove Selected",command=remove).pack(side='left',padx=4)
    tk.Button(btns,text="Clear All",command=clear).pack(side='left',padx=4)

    #-------------------Intro Line------------------------------------------
    tk.Label(content, text="Intro Line").pack(anchor='w', pady=4)
    intro_text = tk.Text(content, width=50, height=4)
    intro_text.insert("1.0", "We give below our lowest quotation for Timing belts.")
    intro_text.pack(fill='x', pady=4)

    # -------------------- Terms & Conditions (editable) --------------------
    tc_frame = tk.Frame(main, bd=1, relief='sunken', padx=6, pady=6)
    tc_frame.pack(fill='x', pady=8)
    tk.Label(tc_frame, text="Terms & Conditions (edit as needed):", font=('Helvetica',12,'bold')).pack(anchor='w')
    tc_text = tk.Text(tc_frame, width=100, height=8)
    tc_text.pack()

    # Default terms
    default_terms = [
        "Discount: 10% on the above price.",
        "Freight: Extra.",
        "Taxes: GST 18% Extra.",
        "Delivery: Ready stock.",
        "Transport: Courier/ APSRTC Cargo/ Lorry service.",
        "Payment: Against Delivery.",
        "Insurance: On your own agreement.",
        "Validity: Prices are subjected to change without any notice."
    ]
    for t in default_terms:
        tc_text.insert("end", t + "\n")

    # -------------------- Bottom section --------------------
    bottom = tk.Frame(main); bottom.pack(fill='x',pady=8)
    total_lbl = tk.Label(bottom,text="Total: 0.00",font=('Helvetica',12,'bold'))
    total_lbl.pack(side='left',padx=12)

    def reindex():
        for i,it in enumerate(tv.get_children(),start=1):
            vals = list(tv.item(it,'values')); vals[0]=i; tv.item(it,values=vals)

    def update_total():
        total=0
        for iid in tv.get_children():
            vals = tv.item(iid,'values')
            total += float(vals[4])*float(vals[6])
        total_lbl.config(text=f"Total: {total:.2f}")

    def reset_form():
        qno_ent.delete(0,"end")
        qdate_ent.delete(0,"end"); qdate_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        cb_cust.set("")
        for i in tv.get_children(): tv.delete(i)
        tc_text.delete("1.0","end")
        for t in default_terms: tc_text.insert("end", t + "\n")
        total_lbl.config(text="Total: 0.00")



    def create_pdf():
        if not tv.get_children():
            messagebox.showwarning("Empty","No items added"); return

        cust_row = cust_map[cust_var.get()]
        customer = {"company_name":cust_row[1],"address":cust_row[2] or "",
                    "email":cust_row[3] or "","phone":cust_row[4] or ""}

        # ✅ Initialize items list here
        items = []

        for iid in tv.get_children():
            v = tv.item(iid,'values')
            items.append({
                "id": int(v[7]),   # hidden ItemID column
                "name": v[1],
                "hsn": v[2],
                "make": v[3],
                "qty": float(v[4]),
                "uom": v[5],
                "price": float(v[6])
            })

        intro_line = intro_text.get("1.0", "end").strip()
        # Read terms from text box
        terms = [line.strip() for line in tc_text.get("1.0","end").splitlines() if line.strip()]
        meta = {"quotation_no":qno_ent.get(),"quotation_date":qdate_ent.get()}
        fname = f"Quotation_{qno_ent.get()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        customer_name = customer["company_name"]
        folder_path = os.path.join("Quotations", customer_name)
        os.makedirs(folder_path, exist_ok=True)
        fname = os.path.join(folder_path, f"Quotation_{meta['quotation_no']}.pdf")


        generate_pdf(fname, company_info, meta, customer, items, terms, my_name, intro_line)
        #generate_pdf(fname, company_info, meta, customer, items, terms, my_name)
        save_quotation(meta, cust_row[0], items)
        messagebox.showinfo("PDF Created", f"Saved as {fname}")
        
    tk.Button(bottom,text="Create PDF",command=create_pdf,font=('Helvetica',12)).pack(side='right',padx=12)
    tk.Button(bottom,text="New Quotation",command=reset_form,font=('Helvetica',12)).pack(side='right',padx=12)
