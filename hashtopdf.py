import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from os import path
import sys
import hashlib
import fpdf

# create the root window
root = tk.Tk()
root.title('DXF Hash to PDF')
root.resizable(False, False)
root.geometry('300x150')


thefile = ""
def select_file():
    global thefile
    filetypes = (
        ('dxf files', '*.dxf'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Επιλογή αρχείου',
        initialdir='/',
        filetypes=filetypes)

    thefile = filename
    labelBox.config(text=path.basename(filename))

def hash_file():
    global thefile
    #thefile = "C:\Intel\Logs\IntelGFX.log"
    sha512 = hashlib.sha512()
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    with open(thefile, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha512.update(data)
    #labelBox.config(text="SHA512: {0}".format(sha512.hexdigest()))
    hashtext="{0}".format(sha512.hexdigest())
    pdf = fpdf.FPDF(format='letter') #pdf format
    pdf.add_page() #create new page
    pdf.set_font("Arial", size=12) # font and textsize
    pdf.multi_cell(200, 10, txt=hashtext, align="L")
    pdf.output(thefile+"_hash.pdf")
    showinfo(title="Έτοιμο",message="Το αρχείο\n"+path.basename(thefile)+"_hash.pdf"+"\nδημιουργήθηκε.")


def showabout():
    showinfo(title="About",message="dnikolos@gmail.com")

# open button
open_button = ttk.Button(
    root,
    text="Επιλογή αρχείου",
    command=select_file
)

#hash file
hash_button = ttk.Button(
    root,
    text='Hash',
    command=hash_file
)

#about
about_button=ttk.Button(
    root,
    text='About',
    command=showabout
)

#label
labelBox = ttk.Label(root, text='File')

open_button.pack()
labelBox.pack()
hash_button.pack()
about_button.pack()

# run the application
root.mainloop()

