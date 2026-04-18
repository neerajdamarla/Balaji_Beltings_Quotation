import tkinter as tk
from tkinter import ttk, messagebox
from database import add_item

def show_add_item(content):
    for w in content.winfo_children(): w.destroy()
    frm = tk.Frame(content, padx=10, pady=10); frm.pack(anchor='nw')

    tk.Label(frm, text="Add Item", font=('Helvetica',14)).grid(row=0,column=0,columnspan=2,pady=8)
    tk.Label(frm, text="Name").grid(row=1,column=0,sticky='e')
    e_name = tk.Entry(frm,width=40); e_name.grid(row=1,column=1)
    tk.Label(frm, text="HSN").grid(row=2,column=0,sticky='e')
    e_hsn = tk.Entry(frm,width=40); e_hsn.grid(row=2,column=1)
    tk.Label(frm, text="Make").grid(row=3,column=0,sticky='e')
    tk.Label(frm, text="Make").grid(row=3,column=0,sticky='e')
    e_make = tk.Entry(frm, width=40)
    e_make.grid(row=3,column=1)
    tk.Label(frm, text="Price").grid(row=4,column=0,sticky='e')
    e_price = tk.Entry(frm,width=40); e_price.grid(row=4,column=1)

    def save():
        try:
            price = float(e_price.get())
        except:
            messagebox.showerror("Error","Enter valid price"); return
        add_item(e_name.get(), e_hsn.get(), e_make.get(), price)
        messagebox.showinfo("Saved","Item added successfully.")
        e_name.delete(0,"end"); e_hsn.delete(0,"end"); e_price.delete(0,"end"); e_make.delete(0,"end")

    tk.Button(frm,text="Save Item",command=save).grid(row=5,column=1,sticky='e',pady=8)
