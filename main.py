import tkinter as tk
from database import init_db, validate_user
from ui_customer import show_add_customer
from ui_items import show_add_item
from ui_quote import show_create_quote
from ui_history import show_history


class QuotationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quotation App")
        #self.geometry("1024x700")
        self.state('zoomed')
        #self.attributes('-fullscreen', True)
        init_db()
        self.company_info = {
            "name": "BALAJI BELTINGS",
            "address": "7-3-41, JAKKAVARI STREET, PERALA, CHIRALA-523157, BAPATLA DIST.(A.P.)",
            "email": "Email: balajibeltingscrl@beltsmail.com",
            "phone": "Mobile: +91-9346238595"
        }
        self.my_name = "D Srinivisa Rao"
        self.show_login()

    def show_login(self):
        frm = tk.Frame(self); frm.pack(expand=True)
        tk.Label(frm,text="Login",font=('Helvetica',18)).pack(pady=8)
        e_user = tk.Entry(frm); e_user.pack(pady=4)
        e_pass = tk.Entry(frm,show="*"); e_pass.pack(pady=4)

        def attempt():
            if validate_user(e_user.get(), e_pass.get()):
                frm.destroy(); self.show_main()
            else:
                tk.messagebox.showerror("Login","Invalid credentials")
        tk.Button(frm,text="Login",command=attempt).pack(pady=8)
        tk.Label(frm,text="Default: admin/admin").pack()

    def show_main(self):
        menu = tk.Frame(self,width=200,bd=2,relief="ridge"); menu.pack(side="left",fill="y")
        content = tk.Frame(self); content.pack(side="right",fill="both",expand=True)
        tk.Button(menu,text="Add Customer",width=20,
                  command=lambda: show_add_customer(content)).pack(pady=6)
        tk.Button(menu,text="Add Item",width=20,
                  command=lambda: show_add_item(content)).pack(pady=6)
        tk.Button(menu,text="Create Quotation",width=20,
                  command=lambda: show_create_quote(content,self.company_info,self.my_name)).pack(pady=6)
        tk.Button(menu,text="Quotation History",width=20,
          command=lambda: show_history(content)).pack(pady=6)
        tk.Button(menu,text="Exit",width=20,command=self.quit).pack(side="bottom",pady=6)

if __name__ == "__main__":
    app = QuotationApp()
    app.mainloop()
