import tkinter as tk
from tkinter import messagebox
from database import add_customer
def show_add_customer(content):
    for w in content.winfo_children(): w.destroy()
    frm = tk.Frame(content, padx=10, pady=10)
    frm.pack(anchor='nw')

    tk.Label(frm, text="Add Customer", font=('Helvetica',14)).grid(row=0,column=0,columnspan=2,pady=8)
    tk.Label(frm, text="Company Name").grid(row=1,column=0,sticky='e')
    e_name = tk.Entry(frm,width=40); e_name.grid(row=1,column=1)
    tk.Label(frm, text="Address").grid(row=2,column=0,sticky='e')
    e_addr = tk.Text(frm,width=30,height=3); e_addr.grid(row=2,column=1)
    tk.Label(frm, text="Email").grid(row=3,column=0,sticky='e')
    e_email = tk.Entry(frm,width=40); e_email.grid(row=3,column=1)
    tk.Label(frm, text="Phone").grid(row=4,column=0,sticky='e')
    e_phone = tk.Entry(frm,width=40); e_phone.grid(row=4,column=1)

    def save():
        add_customer(e_name.get(), e_addr.get("1.0","end").strip(), e_email.get(), e_phone.get())
        messagebox.showinfo("Saved","Customer added successfully.")
        e_name.delete(0,"end"); e_addr.delete("1.0","end"); e_email.delete(0,"end"); e_phone.delete(0,"end")

    tk.Button(frm,text="Save Customer",command=save).grid(row=5,column=1,sticky='e',pady=8)
