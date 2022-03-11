# encoding: utf-8
import heapq
import math
import os
import tkinter as tk
from tkinter import *
from tkinter.filedialog import asksaveasfile
from PIL import ImageTk, Image
from tkinter import filedialog as fd
import codecs

NUMBER_OF_SENTENCES = 5
MINIMUM_SENTENCE_LENGTH = 10
MINIMUM_NUMBER_OF_CHARACTERS = 666
SUMMARY = ""
article = ""


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def TFIDF(call_method_button):
    global NUMBER_OF_SENTENCES
    global MINIMUM_NUMBER_OF_CHARACTERS
    global MINIMUM_SENTENCE_LENGTH
    global SUMMARY
    global article
    SUMMARY = ""

    # if there is no enough sentences then create new sentences by turning the arabic "Fasila" to dot
    dot_word_ratio = article.count(".") / (article.count(" ") + 1)
    if dot_word_ratio < 0.03:
        article = article.replace("،", ".")

    # remove any new line symbols
    article = article.replace("\n", ".")

    # sentences is a list which contains each sentence in the article.
    sentences = article.split(".")

    # documents is a list which contains each sentence in the article with length larger than MINIMUM_SENTENCE_LENGTH.
    documents = [sentence for sentence in sentences if len(sentence) > MINIMUM_SENTENCE_LENGTH]

    # docs_tf is a dictionary of lists of (term, term count) in each document.
    # docs_tf[0] = [(مشروع", 3"), (مشروع", 3"), (عربي", 6"), ...]    which represents doc0
    # docs_tf[0][0] = (مشروع", 3")
    docs_tf = dict(enumerate([[(word, document.split(" ").count(word)) for word in document.split(" ")] for document in documents]))

    # TF is same as docs_tf but with no duplicates in the one document.
    # TF[0] = [(مشروع", 3"), (جديد", 4"), (عربي", 6"), ...]    which represents doc0
    # TF[0][0] = (مشروع", 3")
    TF = {}
    for i in docs_tf : TF[i] = list(dict.fromkeys(docs_tf[i]))

    # NTF is same as TF but with normalized term frequencies.
    # NTF[0] = [(مشروع", 0.45"), (جديد", 0.56"), (عربي", 0.78"), ...]    which represents doc0
    # NTF[0][0] = (مشروع", 0.45")
    NTF = {k: [] for k in TF}
    [NTF[i].append((t_tf_pair[0], t_tf_pair[1] / len(docs_tf[i]))) for i in TF for t_tf_pair in TF[i]]

    # terms is a set of all words inside the original article.
    # terms = {"جميل","عربي","خط" ...}
    # terms[0] = "خط"
    terms = set(article.replace(".", " ").split(" "))

    # DF is a dictionary of (term: document_frequency for that term)
    # DF["بيرزيت"] = 5
    DF = {}
    for i, term in enumerate(terms):
        DF[term] = 0
        for sentence in documents: DF[term] += 1 if term in sentence else 0

    # IDF is dictionary of lists of (term: normalized document_frequency for that term) tuples
    # IDF[0] = [('مع', 0.47), ('إيران', 0.87) ...] which represents doc0
    # IDF[0][0] = ('مع', 0.47)
    number_of_docs = len(NTF)
    IDF = {k : [] for k in range(number_of_docs)}
    {IDF[i].append((word_NTF_tuple[0], math.log(len(documents) / DF[word_NTF_tuple[0]]))) for i in range(number_of_docs) for word_NTF_tuple in TF[i]}

    NTF_IDF = {}
    for i in range(len(NTF)):
        NTF_IDF_COLLECTION = []
        [NTF_IDF_COLLECTION.append((NTF[i][x][0], NTF[i][x][1] * IDF[i][x][1])) for x in range(0, len(NTF[i]))]
        NTF_IDF[i] = NTF_IDF_COLLECTION

    if call_method_button:
        NUMBER_OF_SENTENCES = 3
        # top_sentences is just the index of the sentences with the largest TF_IDF
        while len(SUMMARY) < MINIMUM_NUMBER_OF_CHARACTERS and NUMBER_OF_SENTENCES < 9:
            top_sentences = sorted(heapq.nlargest(NUMBER_OF_SENTENCES, NTF_IDF, key=NTF_IDF.get))
            SUMMARY = ''.join((documents[i].strip() + ". ") for i in top_sentences)
            NUMBER_OF_SENTENCES += 1
        NUMBER_OF_SENTENCES -= 1

    else:
        top_sentences = sorted(heapq.nlargest(NUMBER_OF_SENTENCES, NTF_IDF, key=NTF_IDF.get))
        SUMMARY = ''.join((documents[i].strip() + ". ") for i in top_sentences)

    input.config(text=str(NUMBER_OF_SENTENCES))
    return SUMMARY


def summarize(e):
    clear(e)
    text.insert("1.0", TFIDF(True), "end")
    return


def increment(e):
    global NUMBER_OF_SENTENCES

    if NUMBER_OF_SENTENCES < 9:
        NUMBER_OF_SENTENCES += 1
        clear(e)
        text.insert("1.0", TFIDF(False), "end")
        input.config(text=str(NUMBER_OF_SENTENCES))
    return


def clear(e):
    text.config(state='normal')
    text.delete(1.0,END)
    return


def save(e):
    global SUMMARY
    file = asksaveasfile(filetypes=[('Text Document', '*.txt')], defaultextension=[('Text Document', '*.txt')])
    if file:
        path = str(file).split("'")[1]
        file.close()
        file = codecs.open(path, "w", "utf-8")
        file.write(SUMMARY)
        file.close()
    return


def decrement(e):
    global NUMBER_OF_SENTENCES

    if NUMBER_OF_SENTENCES > 1:
        NUMBER_OF_SENTENCES -= 1
        clear(e)
        text.insert("1.0", TFIDF(False), "end")
        input.config(text=str(NUMBER_OF_SENTENCES))
    return


def select_file(e):
    global article

    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    new_label = filename.split('/')[-1][0:28]
    input_file.config(text=new_label)

    if new_label:
        with open(filename, encoding="utf_8") as f:
            file_text = f.read().replace("\n", "")

        with open(filename, encoding="utf_8") as f:
            article = f.read()


window = tk.Tk()
window.title('Arabic Text Summarizer')
window.geometry('1300x705')
window.resizable(False, False)

font_size = round(21.0 - window.winfo_fpixels('1i')/12.0)
box_width = round(152 - 0.458333333 * window.winfo_fpixels('1i'))

mapBG = Image.open(resource_path("images/bg.png")).convert("RGBA")
combined = ImageTk.PhotoImage(mapBG)
label = Label(image=combined)
label.place(x=0, y=-2)

Frame1 = Frame(window)
Frame1.place(x=20, y=20)

button_summa_img = Image.open(resource_path("images/button.png"))
button_summa = ImageTk.PhotoImage(button_summa_img)
buttonLabel = tk.Label(window, image=button_summa, bd=0)
buttonLabel.pack()
buttonLabel.place(x=961,y=547)
buttonLabel.bind('<Button-1>', summarize)

button_file_img = Image.open(resource_path("images/file.png"))
button_file = ImageTk.PhotoImage(button_file_img)
button_label_file = tk.Label(window, image=button_file, bd=0)
button_label_file.pack()
button_label_file.place(x=108,y=220)
button_label_file.bind('<Button-1>', select_file)

input_file = Message(window, text="", bg='white', width=220)
input_file.place(x=148,y=219)

input = Message(window, justify='right', text=str(NUMBER_OF_SENTENCES), bg='white', width=1080, font=("Arial", font_size, "normal"))
input.place(x=1134,y=219)

window.iconphoto(False, tk.PhotoImage(file=resource_path("images/ico.png")))

text = Text()
text.tag_configure('tag-center', justify='right')
text.insert('end', '.هنا سيظهر النص المختصر', 'tag-center')
text.config(state='normal', font=("Courier New", font_size))
scrollbar = Scrollbar(window)
scrollbar.pack(side=RIGHT, fill=Y, pady=(313,196), padx=95)
text.config(width=box_width, height=8)
text.place(x=100, y=331)
scrollbar.config(command=text.yview)
text.config(yscrollcommand=scrollbar.set)

hider_img = Image.open(resource_path("images/hider.png"))
hider_imgtk = ImageTk.PhotoImage(hider_img)
hider = tk.Label(window, image=hider_imgtk, bd=0)
hider.pack()
hider.place(x=100,y=331)

hider_img2 = Image.open(resource_path("images/hider2.png"))
hider_imgtk2 = ImageTk.PhotoImage(hider_img2)
hider2 = tk.Label(window, image=hider_imgtk2, bd=0)
hider2.pack()
hider2.place(x=99,y=331)

hider_img3 = Image.open(resource_path("images/hider3.png"))
hider_imgtk3 = ImageTk.PhotoImage(hider_img3)
hider3 = tk.Label(window, image=hider_imgtk3, bd=0)
hider3.pack()
hider3.place(x=1185,y=308)

hider_img4 = Image.open(resource_path("images/hider4.png"))
hider_imgtk4 = ImageTk.PhotoImage(hider_img4)
hider4 = tk.Label(window, image=hider_imgtk4, bd=0)
hider4.pack()
hider4.place(x=1185,y=495)

hider_img5 = Image.open(resource_path("images/hider5.png"))
hider_imgtk5 = ImageTk.PhotoImage(hider_img5)
hider5 = tk.Label(window, image=hider_imgtk5, bd=0)
hider5.pack()
hider5.place(x=1173,y=199)
hider5.bind('<Button-1>', increment)

hider_img6 = Image.open(resource_path("images/hider6.png"))
hider_imgtk6 = ImageTk.PhotoImage(hider_img6)
hider6 = tk.Label(window, image=hider_imgtk6, bd=0)
hider6.pack()
hider6.place(x=1173,y=235)
hider6.bind('<Button-1>', decrement)

button_clear_img = Image.open(resource_path("images/button_clear.png"))
button_clear_label = ImageTk.PhotoImage(button_clear_img)
button_clear = tk.Label(window, image=button_clear_label, bd=0)
button_clear.pack()
button_clear.place(x=87,y=547)
button_clear.bind('<Button-1>', clear)

button_save_img = Image.open(resource_path("images/button_save.png"))
button_save_label = ImageTk.PhotoImage(button_save_img)
button_save = tk.Label(window, image=button_save_label, bd=0)
button_save.pack()
button_save.place(x=438,y=201)
button_save.bind('<Button-1>', save)

window.mainloop()