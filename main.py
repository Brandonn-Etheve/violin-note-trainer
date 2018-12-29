import random
import threading
from tkinter import ttk

import Dsp
import time
import tkinter as tk
from synthesizer import Player, Synthesizer, Waveform

dsp = Dsp.Dsp()

player = Player()
player.open_stream()
synthesizer = Synthesizer(osc1_waveform=Waveform.sine, osc1_volume=0.6, use_osc2=False)
window = tk.Tk()

mode = tk.IntVar()
mode.set(0)

auto_play_sound = tk.BooleanVar()
auto_play_sound.set(False)

modes = [
    ("Libre", 0),
    ("Entrainement aléatoire", 1),
]

keys = ["do", "do#", "dob", "fa", "fa#", "la", "lab", "mi", "mib", "ré", "réb", "si", "sib", "sol", "solb"]
key_imgs = []

for key in keys:
    key_imgs.append(tk.PhotoImage(file="./img/key_signature/"+key+".png"))

possible_key_signature = (0,)

window.title("Brandonn music app")
ws = window.winfo_screenwidth()  # width of the screen
hs = window.winfo_screenheight()  # height of the screen
w = 800  # width for the Tk root
h = 600  # height for the Tk root
# calculate x and y coordinates for the Tk root window
x = (ws / 2) - (w / 2)
y = (hs / 2) - (h / 2)
window.geometry('%dx%d+%d+%d' % (w, h, x, y))
window.resizable(False, False)


canvas = tk.Canvas(window, width=750, height=850)
canvas.place(y=150, x=-390, relx=0.5)
canvas_key_img = canvas.create_image(20, 20, anchor=tk.NW)


barre_img = tk.PhotoImage(file="./img/barre.png")
canvas_b1_img = canvas.create_image(480, 310, anchor=tk.NW, image=barre_img)
canvas_b2_img = canvas.create_image(480, 345, anchor=tk.NW, image=barre_img)

note_img = tk.PhotoImage(file="./img/note.png")
canvas_note_img = canvas.create_image(500, 257, anchor=tk.NW, image=note_img)

# on place la note en fonction de son nom au bon endroit. ensuite on regarde si cette note est shap flat ou normale.
#ensuite on regarde si l'armature est censse modifer cette note, et si besoin on ajoute un bemol # ou becare

#35 pix
# 17.5 pix height

def getRandomTargetNoteIndex():
    return random.randint(31, 60)


target_note_index = getRandomTargetNoteIndex()

def playTune():
    player.play_wave(synthesizer.generate_constant_wave(dsp.notes_frequency[target_note_index], 20.0))

def repeat_btn_clicked():
    threading.Thread(target=playTune, args=()).start()

def next_btn_clicked():
    global target_note_index
    if auto_play_sound.get():
        threading.Thread(target=playTune, args=()).start()
    target_note_index = getRandomTargetNoteIndex()
    index = -1
    if len(possible_key_signature) > 0 :
        while index not in possible_key_signature:
            index = random.randint(0, len(keys))
    else:
        index = 0
    # im = tk.PhotoImage(file="./img/key_signature/"+keys[index]+".png")
    canvas.itemconfig(canvas_key_img, image=key_imgs[index])


def open_setting():
    setting_window = tk.Toplevel(window)
    setting_window.title("Brandonn music app -> Réglage")
    # get screen width and height

    ws = window.winfo_screenwidth()  # width of the screen
    hs = window.winfo_screenheight()  # height of the screen
    w = 400  # width for the Tk root
    h = 400  # height for the Tk root
    # calculate x and y coordinates for the Tk root window
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    setting_window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    setting_window.resizable(False, False)

    mode_lbl = tk.Label(setting_window, text="Séléction du mode :", font=("Arial Bold", 15))
    mode_lbl.pack()

    for text, value in modes:
        b = tk.Radiobutton(setting_window, text=text, variable=mode, value=value)
        b.pack(anchor=tk.W)

    key_lbl = tk.Label(setting_window, wraplength=300, text="Séléction des armatures pour l'entrainement aléatoires :", font=("Arial Bold", 15))
    key_lbl.pack()

    listbox = tk.Listbox(setting_window, selectmode=tk.MULTIPLE)
    listbox.pack()

    def key_signature_select(event):
        global possible_key_signature
        possible_key_signature = listbox.curselection()

    listbox.bind("<<ListboxSelect>>", key_signature_select)
    for item in keys:
        listbox.insert(tk.END, item)
    for selected_key in possible_key_signature:
        listbox.selection_set(selected_key)


    auto_play_sound_checkbox = tk.Checkbutton(setting_window,wraplength=300, text="Jouer automatiquement une tonalité de référence au changement de note en entrainement aléatoire :", variable=auto_play_sound)
    auto_play_sound_checkbox.pack()


menubar= tk.Menu(window)
window.config(menu=menubar)
menubar.add_command(label="Réglages", command=open_setting)




lbl = tk.Label(window, text="Music app", font=("Arial Bold", 25))
lbl.place(relx=0.5, x=-85, rely=0)


scale = tk.Scale(window, from_=-100, to=100, orient=tk.HORIZONTAL, width=50, length=450)
scale.place(y=50, relx=0.15, relwidth=0.7)

lbl_note_left = tk.Label(window, text="do", font=("Arial Bold", 15))
lbl_note_left.place(y=125, relx=0.15)

lbl_note = tk.Label(window, text="re", font=("Arial Bold", 15))
lbl_note.place(y=125, x=-18, relx=0.5)
#
lbl_note_right = tk.Label(window, text="mi", font=("Arial Bold", 15))
lbl_note_right.place(y=125, x=-30, relx=0.85)





repeat_btn = tk.Button(window, text="Rejouer", command=repeat_btn_clicked)
repeat_btn.place(y=565, x=-150, relx=0.5)

next_btn = tk.Button(window, text="Suivant", command=next_btn_clicked)
next_btn.place(y=565, x=90, relx=0.5)



def mainLoop():
    num_notes = len(dsp.notes_name)

    while True:
        if mode.get() == 0:

            lbl_note_left.configure(text=dsp.note_left)
            lbl_note_right.configure(text=dsp.note_right)
            lbl_note.configure(text=dsp.note)
            closeness = dsp.closeness
            scale.set(closeness)
        else:
            if target_note_index > 0:
                lbl_note_left.configure(text=dsp.notes_name[target_note_index-1])
            else:
                lbl_note_left.configure(text="--")

            if target_note_index < num_notes-1:
                lbl_note_right.configure(text=dsp.notes_name[target_note_index+1])
            else:
                lbl_note_right.configure(text="--")

            # print(dsp.notes_name[target_note_index-1],dsp.notes_name[target_note_index],dsp.notes_name[target_note_index+1])
            lbl_note.configure(text=dsp.notes_name[target_note_index])

            # lbl_note_left.pack(side="left", padx=120, pady=0)
            # lbl_note.pack(side="left", padx=50, pady=0)
            # lbl_note_right.pack(side="left", padx=30, pady=0)


            closeness = 0
            if dsp.note_index > target_note_index:
                closeness = 100
            elif dsp.note_index < target_note_index:
                closeness = -100
            else:
                closeness = dsp.closeness
            scale.set(closeness)
            # print(dsp.strongestFrequency)
        time.sleep(0.1)

thread1 = threading.Thread(target=mainLoop, args=())
thread1.setDaemon(False)
thread1.start()


window.mainloop()

#
# while True:
#     print(dsp.note, dsp.closeness, dsp.strongestFrequency)
#     time.sleep(0.1)
#
