__author__ = 'kenneche'

from tkinter import *
from MyParser import *


class MyApp():

    def get_text(self):
        num = self.search_num.get()
        p = MyParser()
        if not (num is ""):
            p.main(num)
#        self.label_3.config(text=num)

    def __init__(self):
        self.root = Tk()
        self.top_frame = Frame(self.root)
        self.bot_frame = Frame(self.root)

        self.search_num = StringVar()

        self.label_1 = Label(self.top_frame, text="CIS-")
        self.label_2 = Label(self.top_frame, text="Output")
        self.out_label_hd_0 = Label(self.bot_frame, text="Cisco Equipment Number")
        self.out_label_hd_1 = Label(self.bot_frame, text="Manufacturer")
        self.out_label_hd_2 = Label(self.bot_frame, text="Model")
        self.out_label_hd_3 = Label(self.bot_frame, text="Description")
        self.out_label_hd_4 = Label(self.bot_frame, text="Cal Date")
        self.out_label_hd_5 = Label(self.bot_frame, text="Cal Due Date")

        self.entry_1 = Entry(self.top_frame, textvariable=self.search_num)
        self.button_1 = Button(self.top_frame, text="Search", command=self.get_text)

    def gui(self):
        self.top_frame.pack(side=TOP)
        self.bot_frame.pack(side=BOTTOM)
        self.label_1.grid(row=0, column=0, sticky=E)
        self.entry_1.grid(row=0, column=1, columnspan=2)
        self.button_1.grid(row=1, column=1)
        self.label_2.grid(row=2, sticky=(W, E))
        self.out_label_hd_0.grid(row=3, column=0)
        self.out_label_hd_1.grid(row=3, column=1)
        self.out_label_hd_2.grid(row=3, column=2)
        self.out_label_hd_3.grid(row=3, column=3)
        self.out_label_hd_4.grid(row=3, column=4)
        self.out_label_hd_5.grid(row=3, column=5)

        self.entry_1.focus()
        self.root.bind('<Return>', self.get_text())

        self.root.mainloop()




if __name__ == '__main__':
    app = MyApp()
    app.gui()
