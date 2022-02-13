import csv
import os
from os import path

import pypandoc
import sys
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import tkinter.font as tkFont
from tkinter import filedialog
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
import string
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image, ImageTk

matplotlib.use("TkAgg")
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
import pypandoc

# BACKEND
global data
data = 'output_data.csv'

def clean_text(doc):
    name, form = path.splitext(doc)
    if form == '.doc' or form == '.docx':
        text = pypandoc.convert_file(doc, 'plain')
    else:
        filename = doc
        file = open(filename, 'rt', encoding='latin-1')
        text = file.read()
        file.close()
    tokens = word_tokenize(text)
    tokens = [w.lower() for w in tokens]
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    global data
    data = words
    return words


def count_text(text, title):
    input_df_x = pd.DataFrame(text)
    Count = input_df_x.pivot_table(index=[0], aggfunc='size')
    df1x = pd.DataFrame(Count)
    df1x.columns = ['count' + title]
    df1x = df1x.sort_values(by=['count' + title], ascending=False)
    return df1x


def run_analysis(JS, CV):
    Jobspec = clean_text(JS)
    CircV = clean_text(CV)
    Count_JS = count_text(Jobspec, 'JS')
    Count_Cv = count_text(CircV, 'CV')
    data = [Count_JS["countJS"], Count_Cv["countCV"]]
    headers = ["job_spec", "cv"]
    combined = pd.concat(data, axis=1, keys=headers)
    combined1 = combined.sort_values(["job_spec"], ascending=False)
    combined2 = combined1.fillna(0)
    return combined2


def run_model(JS, CV):
    Output = run_analysis(JS, CV)
    # create_T50_graph(Output)
    return Output

def create_list(JS, CV):
    output = run_analysis(JS, CV)
    not_men = output[output['cv']==0]
    return not_men

def create_add_list(JS, CV):
    not_men = create_list(JS, CV)
    need_add = not_men[not_men.loc[:, 'job_spec'] > 1]
    need_add = need_add.loc[:, 'job_spec']
    return need_add

def create_add_whitespace(JS, CV):
    b = create_list(JS, CV)
    ws = b[b.loc[:,'job_spec']==1]
    ws = ws.loc[:,'job_spec']
    return ws

def remove_words(JS, CV):
    output = run_analysis(JS, CV)
    df = output[(output.cv != 0) & (output.job_spec != 0)]
    too_many = df[df.cv >= (df.job_spec * 2)]
    return too_many

def good_balance(JS, CV):
    df = create_list(JS, CV)
    s1 = df.job_spec / df.cv
    balance = s1.where((s1 > 0.5) & (s1 < 1.5)).dropna()
    return balance


# output = run_model(JS, CV)

##############################
# GUI

myfont = ('Arial', 11)
font = FontProperties()
font.set_family('serif')
font.set_name('Arial')
font.set_weight('bold')
font.set_size('9')

font2 = FontProperties()
font2.set_family('serif')
font2.set_name('Arial')
font2.set_weight('bold')
font2.set_size('14')

# baseline just to add pages
class CVApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "CV Hack App")
        tk.Tk.maxsize(self, 1000,1000)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(3, weight=1)
        container.grid_columnconfigure(5, weight=1)
        self.frames = {}
        for F in (StartPage, Top50, Lists):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=3, column=5, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Select the variables.
# TODO update the label text with a brief on how to use the systems
# TODO Change the order of the buttons
class StartPage(tk.Frame):
    CV = None
    JS = None

    @classmethod
    def update_cv(cls, value):
        cls.CV = value

    @classmethod
    def update_JS(cls, value):
        cls.JS = value

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="                          Define what the App does                           ",
                         font='myfont').place(x=300, y = 100)
        button1 = ttk.Button(
            self, text='Show the top 50 Jobspec words',
            command=lambda: controller.show_frame(Top50), width=40).place(x=300, y = 250)
        button3 = ttk.Button(self, text='Upload the JobSpec doc',
                             command=lambda: self.open_file_JS(), width=40).place(x=300, y = 150)
        button4 = ttk.Button(self, text='Upload your CV',
                             command=lambda: self.open_file_CV(), width=40).place(x=300, y = 200)



    # TODO: link these two to the input class
    def open_file_CV(self):
        entry1 = ttk.Label(self, width=40).place(x=350, y=225)
        filename = filedialog.askopenfilename(parent=self, title='Open file to load')
        head, tail = os.path.split(str(filename))
        print(tail)
        entry1 = ttk.Label(self, text=tail, width=40).place(x=350, y=225)
        self.update_cv(filename)
        print(StartPage.CV)
        return filename

    def open_file_JS(self):
        entry2 = ttk.Label(self).place(x=350, y=175)
        filename1 = filedialog.askopenfilename(parent=self, title='Open file to load')
        head, tail = os.path.split(str(filename1))
        print(tail)
        entry2 = ttk.Label(self, text=tail).place(x=350, y=175)
        self.update_JS(filename1)
        print(StartPage.JS)
        return filename1

class Top50(tk.Frame):

    field = None
    @classmethod
    def update_field(cls, value):
        cls.field = value

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One", font='myfont')
        label.pack()
        button1 = ttk.Button(self, text='back to home', command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = ttk.Button(self, text='Show graph', command=lambda: self.calculate())
        button2.pack()
        button3 = ttk.Button(self, text='Show not mentioned list', command=lambda: controller.show_frame(Lists))
        button3.pack()
        self.field_var = StringVar()


    def calculate(self):
        print(StartPage.JS)
        print(StartPage.CV)
        a_cv = StartPage.CV
        a_js = StartPage.JS
        output = run_model(str(a_js), str(a_cv))
        print(output)
        f = Figure(figsize=(10, 9), dpi=100)
        a = f.add_subplot(111)
        chosen = output.head(n=50)
        index = chosen.index
        index1 = index
        app_data = self.field_var.get()
        app_data1 = index1.insert(0, app_data)
        print(app_data1)
        with open('output_data.csv', 'a+', newline='') as file:
            mywriter = csv.writer(file, delimiter=',')
            mywriter.writerow(app_data1)
        a.hlines(y=index, xmin=chosen['job_spec'], xmax=chosen['cv'], color='grey', alpha=0.4)
        a.scatter(chosen['job_spec'], index, color='skyblue', alpha=1, label='Job Spec')
        a.scatter(chosen['cv'], index, color='green', alpha=0.4, label='CV')
        a.legend()
        a.set_yticks(index)
        a.set_yticklabels(index, fontproperties=font)
        a.set_xticks(np.arange(0, 25, step=1))
        a.set_title("Comparison of the Top 50 words in the JobSpec and the CV", loc='left', fontproperties=font2)
        a.set_xlabel('Value of the variables', fontproperties=font2)
        a.set_ylabel('Index', fontproperties=font2)
        a.grid(True, alpha=0.4)
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack()
        canvas.get_tk_widget().pack()

class Lists(tk.Frame):

    @classmethod
    def update_field(cls, value):
        cls.field = value

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        button1 = ttk.Button(self, text='back to home', command=lambda: controller.show_frame(StartPage))
        button1.grid(row = 2, column = 1, columnspan =4, sticky = "nsew", pady = 2,)
        button2 = ttk.Button(self, text='Show List', command=lambda: self.list1())
        button2.grid(row = 3, column = 1, columnspan =4, sticky = "nsew", pady = 2,)



    def list1(self):
        T = Text(self)
        a_cv = StartPage.CV
        a_js = StartPage.JS
        output = create_add_list(str(a_js), str(a_cv))
        T.insert(INSERT, output)
        T.grid(row=5, column=1, columnspan=1, sticky="nsew", pady=2)
        T2 = Text(self)
        output = remove_words(str(a_js), str(a_cv))
        T2.insert(INSERT, output)
        T2.grid(row=5, column=2, columnspan=1, sticky="nsew", pady=2)
        T3 = Text(self)
        output = create_list(str(a_js), str(a_cv))
        T3.insert(INSERT, output)
        T3.grid(row=7, column=1, columnspan=1, sticky="nsew", pady=2)
        T4 = Text(self, )
        output = good_balance(str(a_js), str(a_cv))
        T4.insert(INSERT, output)
        T4.grid(row=7, column=2, columnspan=1, sticky="nsew", pady=2)
        label1 = tk.Label(self, text="Words that need adding", font='myfont')
        label1.grid(row=4, column=1, columnspan=1, sticky="nsew", pady=2)
        label2 = tk.Label(self, text="Words to reduce", font='myfont')
        label2.grid(row=4, column=2, columnspan=1, sticky="nsew", pady=2)
        label3 = tk.Label(self, text="Words that haven't been mentioned", font='myfont')
        label3.grid(row=6, column=1, columnspan=1, sticky="nsew", pady=2)
        label4 = tk.Label(self, text="Words with good balance", font='myfont')
        label4.grid(row=6, column=2, columnspan=1, sticky="nsew", pady=2)








# TODO: Beautify the start page
# TODO: Create a top 100
# TODO: Create the function for the key words to add.
# TODO: Generate two word clouds
# TODO: create a much wider dataset of different areas and then use Spaced to analyse:https://kanoki.org/2019/03/17/text-data-visualization-in-python/


app = CVApp()
app.geometry("1000x1000")
app.mainloop()
'''
#Create two lists, words to add it to CV adn the words to whitespace
not_mentioned = combined[combined['CV'] == 0]
critical = not_mentioned[not_mentioned['Job Spec']>1]
Add_words = critical.index
Add_words = Add_words.tolist()
combined_yes = combined[combined['CV']> 0]
combined_yes = combined_yes[combined_yes['Job Spec']> 0]
not_enough = combined_yes[combined_yes['CV'].values <= (combined_yes['Job Spec'].values/2)]
not_enough_val = not_enough.index
not_enough_val = not_enough_val.tolist()
Add_words = Add_words + not_enough_val
print(Add_words)

plt.plot(index, top_50['Job Spec'], 'b:', label='Job Spec')
plt.plot(index, top_50['CV'], 'r:', label='CV')
plt.xlabel('index',)
plt.grid(True, alpha = 0.4)
plt.show()'''

# root.mainloop()
