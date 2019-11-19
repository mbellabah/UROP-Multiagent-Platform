import threading
import tkinter as tk
from tkinter import ttk


# MARK: Threading
def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper


class Application(tk.Frame):
    def __init__(self, name, agent_object, master=None):
        super().__init__(master)
        self.master = master
        self.agent_object = agent_object
        self.name = name
        self.master.geometry('700x220')
        self.master.title(f'Agent: {self.name}')

        self.my_notebook = None
        self.my_maintab = None
        self.my_licensetab = None
        self.quit = None

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.quit = tk.Button(self, text='QUIT', fg='red', command=self.master.destroy)
        self.quit.pack(side='bottom')

        self.my_notebook = Notebook(self.master)
        self.my_maintab = MainTab(self.my_notebook.master_main, agent_object=self.agent_object)
        self.my_licensetab = LicenseTab(self.my_notebook.master_license)


class Notebook:
    def __init__(self, master):
        self.master = master
        self.note_book = ttk.Notebook(master)
        self.note_book.pack(fill=tk.BOTH)

        # Main tab - self.master_main
        self.master_main = tk.Frame(self.note_book)
        self.note_book.add(self.master_main, text='Main')

        # License and Details tab - self.master_license
        self.master_license = tk.Frame(self.note_book)
        self.note_book.add(self.master_license, text='License')


class MainTab:
    def __init__(self, master, agent_object):
        self.master = master
        self.agent_object = agent_object
        self.agent_name = self.agent_object.name
        ttk.Separator(self.master, orient=tk.HORIZONTAL).grid(row=0, sticky="ew", columnspan=5, pady=5)

        # Initialization
        self.all_offers_button = ttk.Button(self.master, text='Get all Completed Transactions', command=self.get_all_offers_func)
        self.all_offers_label = ttk.Label(self.master, text='')
        self.initial_offer_button = ttk.Button(self.master, text='Get initial offer', command=self.get_initial_offer_func)
        self.initial_offer_label_2 = ttk.Label(self.master, text=self.agent_object.my_current_offer)

        # Deployment
        self.all_offers_button.grid(row=1, column=1)
        self.initial_offer_button.grid(row=2, column=1)
        self.initial_offer_label_2.grid(row=2, column=2)
        self.all_offers_label.grid(row=1, column=2)

    def get_all_offers_func(self):
        adjust = self.agent_object.transaction_log
        if len(adjust) == 0:
            self.all_offers_label.config(text='No completed transactions at the time')
        else:
            self.all_offers_label.config(text=adjust)

    def get_initial_offer_func(self):
        pass


class LicenseTab:
    def __init__(self, master):
        self.master = master
        ttk.Separator(self.master, orient=tk.HORIZONTAL).grid(row=0, sticky="ew", columnspan=5, pady=5)

        tk.Label(self.master, text="""
                Program Name: Project Auxo MAS
                Version: 1.0\n
                Copyright: Project Auxo\n
                Creator: Mohamadou Bella Bah
                """).grid(row=1, padx=5, pady=5)


# MARK: Main GUI container - places everything in App into agent container
class GUI:
    def __init__(self, name, agent_object):
        self.name = name
        self.agent_object = agent_object
        self.app = None
        self.root = None

    @threaded
    def run(self):
        self.root = tk.Tk()
        self.app = Application(master=self.root, name=self.name, agent_object=self.agent_object)
        self.app.mainloop()
