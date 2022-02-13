#import the data
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
import openpyxl


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

def create_T50_graph(data):
    chosen = data.head(n=50)
    index = chosen.index
    plt.rcParams["figure.figsize"] = (8, 9)
    plt.hlines(y=index, xmin=chosen['job_spec'], xmax=chosen['cv'], color='grey', alpha=0.4)
    plt.scatter(chosen['job_spec'], index, color='skyblue', alpha=1, label='job_spec')
    plt.scatter(chosen['cv'], index, color='green', alpha=0.4, label='cv')
    plt.legend()
    plt.yticks(index, fontsize=7)
    plt.xticks(np.arange(0, 25, step=1), fontsize=6)
    plt.title("Comparison of the Top 50 words in the JobSpec and the CV", loc='left')
    plt.xlabel('Value of the variables')
    plt.ylabel('Index')
    plt.grid(True, alpha=0.4)
    plt.show()


def run_model(JS, CV):
    Output = run_analysis(JS, CV)
    # create_T50_graph(Output)
    return Output

JS = 'jsr.txt'
CV = 'Rosanna Hithersay.docx'

output = run_model(JS,CV)
create_T50_graph(output)
not_men = output[output['cv']==0]
need_add = not_men[not_men.loc[:,'job_spec']>1]
need_add = need_add.loc[:,'job_spec']

#build the whitespace
ws = not_men[not_men.loc[:,'job_spec']==1]
ws = ws.loc[:,'job_spec']

#build the words to reduce
df = output[(output.cv != 0) & (output.job_spec != 0)]
too_many = df[df.cv >= (df.job_spec * 2)]

#good balance words
s1 = df.job_spec/df.cv
balance = s1.where((s1 > 0.5) & (s1 < 1.5)).dropna()


with pd.ExcelWriter('jobspec_cv-summary.xlsx') as writer:
    need_add.to_excel(writer, sheet_name='Words that need adding')
    ws.to_excel(writer, sheet_name='Words that should be added')
    too_many.to_excel(writer, sheet_name='Words that could be minimised')
    balance.to_excel(writer, sheet_name='Words that have a good ratio')

'''
#TODO: define a class for the input variables
class Inputs:
    CV = None
    JS = None

#TODO: find a way to remove this!! Maybe through the use of another App window?



#baseline just to add pages
class CVApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "CV Hack App")
        container = tk.Frame(self)
        container.pack(side="top", fill="both",expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, Display):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


#Select the variables.
#TODO update the label text with a brief on how to use the systems
#TODO Change the order of the buttons
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = "Define what the App does")
        label.pack(pady = 20,padx = 20)
        button3 = ttk.Button(self, text='Upload the JobSpec doc', command=lambda: self.open_file_JS())
        button3.pack()
        button4 = ttk.Button(self, text='Upload your CV', command=lambda: self.open_file_CV())
        button4.pack()
        button1 = ttk.Button(self, text='Show CV', command=lambda: controller.show_frame(Display))
        button1.pack()

    def open_file_CV(self):
        entry1 = ttk.Label(self).place(x=160, y=43)
        filename = filedialog.askopenfilename(parent=self, title='Open file to load')
        head, tail = os.path.split(filename)
        print(tail)
        entry1 = ttk.Label(self, text=tail).place(x=160, y=43)
        Inputs.CV = filename
        print(Inputs.CV)
        return filename

    def open_file_JS(self):
        entry2 = ttk.Label(self).place(x=160, y=70)
        filename1 = filedialog.askopenfilename(parent=self, title='Open file to load')
        head, tail = os.path.split(filename1)
        print(tail)
        entry2 = ttk.Label(self, text=tail).place(x=160, y=70)
        Inputs.JS = filename1
        print(Inputs.JS)
        return filename1

class Display(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = "Define what the App does")
        label.pack(pady = 20,padx = 20)
        button1 = ttk.Button(self, text = 'Show CV', command = lambda:controller.show_frame(StartPage))
        button1.pack()
        label1 = tk.Label(self, text=Inputs.CV)
        label2 = tk.Label(self, text=Inputs.JS)
        label1.pack()
        label2.pack()


app = CVApp()
app.mainloop()

global data
data = pd.DataFrame()

def clean_text(doc):
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
    headers = ["Job Spec", "CV"]
    combined = pd.concat(data, axis=1, keys=headers)
    combined1 = combined.sort_values(["Job Spec"], ascending=False)
    combined2 = combined1.fillna(0)
    return combined2


def create_T50_graph(data):
    chosen = data.head(n=50)
    index = chosen.index
    plt.rcParams["figure.figsize"] = (8, 9)
    plt.hlines(y=index, xmin=chosen['Job Spec'], xmax=chosen['CV'], color='grey', alpha=0.4)
    plt.scatter(chosen['Job Spec'], index, color='skyblue', alpha=1, label='Job Spec')
    plt.scatter(chosen['CV'], index, color='green', alpha=0.4, label='CV')
    plt.legend()
    plt.yticks(index, fontsize=7)
    plt.xticks(np.arange(0, 25, step=1), fontsize=6)
    plt.title("Comparison of the Top 50 words in the JobSpec and the CV", loc='left')
    plt.xlabel('Value of the variables')
    plt.ylabel('Index')
    plt.grid(True, alpha=0.4)
    plt.show()


def run_model(JS, CV):
    Output = run_analysis(JS,CV)
    create_T50_graph(Output)
    return Output

JS = 'CV_data-input.txt'gu1ws1ye

CV = 'CV_Tom-Scott-Alg_test.txt'
output = run_model(JS, CV)



# Add title and axis names
plt.yticks(index, fontsize= 4)
plt.xticks(np.arange(0,25, step = 1), fontsize = 6)
plt.title("Comparison of the JobSpec and the CV", loc='left')
plt.xlabel('Value of the variables')
plt.ylabel('index')
plt.grid(True, alpha = 0.4)

# Show the graph
plt.show()

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