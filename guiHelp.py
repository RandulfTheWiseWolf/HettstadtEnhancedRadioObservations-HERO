import tkinter as tk

class tEntry(tk.Entry):

    def __init__(self, parent, std_text, *args, **kwargs):

        keys = kwargs.keys()
        if "fg" in keys:
            self.text_color = kwargs["fg"]
        else:
            self.text_color = "#000000"
        if "pfg" in keys:
            self.std_text_color = kwargs["pfg"]
            del kwargs["pfg"]
        else:
            self.std_text_color = "#BDBDBD"

        self.parent = parent
        self.std_text = std_text

        tk.Entry.__init__(self, parent, *args, **kwargs)
        self.bind("<FocusIn>", self.__active_mode)
        self.bind("<FocusOut>", self.__passive_mode)
        self.bind("<Return>", self.__update)

        self.__passive_mode("a")
        
    def __update(self, event):
        if self.get() != "":
            #self.parent.update_spdms()
            pass

    def __passive_mode(self, event):
        if self.get() == "":
            self.config(fg=self.std_text_color)
            self.insert(0, self.std_text)
        else:
            #self.parent.update_spdms()
            pass
            
    def __active_mode(self, event):
        if self.get() == self.std_text:
            self.delete(0, tk.END)
            self.config(fg=self.text_color)