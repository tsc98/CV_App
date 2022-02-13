#!/usr/bin/env python
import random
import sys
import tkinter as tk
from tkinter import *

root = tk.Tk()
root.geometry("600x400")
root.title("CV Developer")
global label
label = Label(root)

def launch():
        list = ['work', 'work', 'work', 'phys', 'sleep']
        output = random.choice(list)
        label.config(bg='gray', text='It is time to '+output)
        label.pack(pady =15)

tk.Button(root, text="Test my CV", command=launch).pack(pady=40)
tk.mainloop()