import os
from tkinter import *
SOURCE = "ast2code.py"
NAME = "ast2code"
win = Tk()
y = dict(expand=YES)
x = dict(fill=X)
yb = dict(fill=BOTH,**y)
tyb = dict(side=TOP,**yb)
libp = next(i for i in sys.path if "lib" in i)
def clr():
    win.geometry("=300x300+200+200")
    l = list(win.children.values())
    for x in l:
        x.destroy()
def page1():
    clr()
    win.title("CompactInstaller 1.0")
    Message(win,text=f"You are about to install {NAME}.").pack(tyb)
    f = Frame(win)
    Button(f,text="Quit",command=exit).pack(x,**y,side=LEFT)
    Button(f,text="Continue",command=page2).pack(x,**y,side=RIGHT)
    f.pack(x)
def page2():
    global ent
    clr()
    win.title("Select path")
    Label(win,text=f"Installing {SOURCE} to:").pack(tyb)
    ent = Entry(win)
    ent.insert(END,libp)
    ent.pack(side=TOP,fill=X)
    f = Frame(win)
    Button(f,text="Back",command=page1).pack(x,**y,side=LEFT)
    Button(f,text="Install",command=page3).pack(x,**y,side=RIGHT)
    f.pack(x)
def error(tex):
    clr()
    win.title("Error")
    Message(win,text=f"Error installing:{tex}.").pack(tyb)
    f = Frame(win)
    Button(f,text="Quit",command=exit).pack(x,**y,side=LEFT)
    Button(f,text="Continue",state=DISABLED).pack(x,**y,side=RIGHT)
    f.pack(x)
def page3():
    tex = ent.get()
    clr()
    win.title("Installing")
    msg = Message(win,text=f"Installing {NAME}...")
    msg.pack(tyb)
    f = Frame(win)
    bb = Button(f,text="Quit",command=exit)
    bb.pack(x,**y,side=LEFT)
    b = Button(f,text="Continue",command=exit,state=DISABLED)
    b.pack(x,**y,side=RIGHT)
    f.pack(x)
    tex = os.path.join(tex,SOURCE)
    try:
        open(tex,"w").write(open(SOURCE).read())
    except Exception as e:
        error(str(e))
        return
    bb.destroy()
    b.config(state=NORMAL,text="Finish")
    msg.config(text="Installed")
page1()
mainloop()
