import tkinter as tk
from tkinter import ttk
from database import get_customers, get_items, get_quotation_history

def show_history(content):
    for w in content.winfo_children(): w.destroy()
    frm = tk.Frame(content, padx=10, pady=10)
    frm.pack(fill='both', expand=True)

    tk.Label(frm, text="Quotation History", font=('Helvetica',14)).pack(pady=8)

    # Filters
    filter_frame = tk.Frame(frm); filter_frame.pack(fill='x', pady=6)
    tk.Label(filter_frame, text="Customer:").grid(row=0,column=0,sticky='e')
    customers = get_customers()
    cust_map = {r[1]: r[0] for r in customers}
    cust_var = tk.StringVar()
    cb_cust = ttk.Combobox(filter_frame,textvariable=cust_var,values=list(cust_map.keys()),state="readonly",width=30)
    cb_cust.grid(row=0,column=1,padx=6)

    tk.Label(filter_frame, text="Item:").grid(row=0,column=2,sticky='e')
    items = get_items()
    item_map = {r[1]: r[0] for r in items}
    item_var = tk.StringVar()
    cb_item = ttk.Combobox(filter_frame,textvariable=item_var,values=list(item_map.keys()),state="readonly",width=30)
    cb_item.grid(row=0,column=3,padx=6)

    # Treeview
    tv = ttk.Treeview(frm,columns=("QuotationNo","Date","Customer","Item"),show='headings')
    for col,wid in zip(("QuotationNo","Date","Customer","Item"),(120,100,200,200)):
        tv.heading(col,text=col); tv.column(col,width=wid,anchor='center')
    tv.pack(fill='both',expand=True,pady=8)

    def load_history():
        cust_id = cust_map.get(cust_var.get()) if cust_var.get() else None
        item_id = item_map.get(item_var.get()) if item_var.get() else None
        rows = get_quotation_history(cust_id,item_id)
        for i in tv.get_children(): tv.delete(i)
        for r in rows:
            tv.insert('', 'end', values=r)

    tk.Button(frm,text="Load History",command=load_history).pack(pady=6)