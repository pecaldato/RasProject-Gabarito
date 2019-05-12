from tkinter import *
from tkinter import ttk
import time

MAX = 30

root = Tk()
root.geometry('{}x{}'.format(400, 100))
progress_var = DoubleVar() #here you have ints but when calc. %'s usually floats
theLabel = Label(root, text="Sample text to show")
theLabel.pack()
progressbar = ttk.Progressbar(root, variable=progress_var, maximum=MAX)
progressbar.pack(fill=X, expand=1)


def loop_function():

    k = 0
    while k <= MAX:
    ### some work to be done
        progress_var.set(k)
        k += 1
        time.sleep(0.02)
        root.update_idletasks()
    root.after(100, loop_function)

loop_function()
root.mainloop()