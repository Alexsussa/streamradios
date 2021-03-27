#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from tkinter.ttk import *
from tkinter.messagebox import *
from tkinter import *
from threading import Thread, Timer
from playsound import playsound
import urllib.request
import webbrowser
import socket
import os
import multiprocessing
import gettext

__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]

__title__ = "StreamRadios"
__summary__ = "Core utilities for Python packages"
__uri__ = "https://github.com/Alexsussa/streamradios"

__version__ = "0.2"

__author__ = "Alex Pinheiro"
__email__ = "alexsussa2@gmail.com"

__license__ = "GPL v3.0"
__copyright__ = "2021 %s" % __author__

appname = 'streamradios'
ldir = '/usr/share/locale/'
gettext.bindtextdomain(appname, ldir)
gettext.textdomain(appname)
_ = gettext.gettext

buttons_radios = []
namelist = []
linklist = []
dictname = {}
strangercharradios = ['Transamérica', '105 FM']


def check_for_updates():
    try:
        new_version = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Alexsussa/streamradios/master/version').read()
        if float(new_version) > float(__version__):
            showinfo(title=_('New software version'),
                     message=_("There's a new software version to download.\n\nDownload it now!"))
            webbrowser.open('doc/index.html')
        if float(new_version) <= float(__version__):
            showinfo(title=_('Updated'), message=_('Software has the last version installed.'))
    except socket.error:
        showerror(title=_('Connection error'), message=_('No internet connection.'))


class Application:
    def __init__(self, master=None):
        self.menubar = Menu(window, bd=0, bg='#d9d9d9')
        file = Menu(self.menubar, tearoff=0, bd=0)
        # file.add_command(label=_('Search radios...'), command=lambda: Thread(target=self.search_radios).start(), accelerator='Ctrl+F')
        file.add_command(label=_('Update radios'),
                         command=lambda: [Thread(target=self.create_buttons, daemon=True).start(),
                                          Thread(target=self.update_radios, daemon=True).start()], accelerator='Ctrl+R')
        file.add_separator()
        file.add_command(label=_('Quit'), command=window.quit, accelerator='Ctrl+Q')
        self.menubar.add_cascade(label=_('File'), menu=file)

        help = Menu(self.menubar, tearoff=0, bd=0)
        help.add_command(label=_('Check for updates...'),
                         command=lambda: Thread(target=check_for_updates, daemon=True).start(),
                         accelerator='Ctrl+U')
        help.add_separator()
        help.add_command(label=_('About'), command=self.about, accelerator='Ctrl+H')
        self.menubar.add_cascade(label=_('Help'), menu=help)

        window.config(menu=self.menubar)

        s = Style()
        s.configure('TPanedwindow', background='#f0f0f0')
        self.c1 = Panedwindow(master)
        self.c1.pack(side=LEFT, fill='both', expand=True, anchor='nw')

        self.c2 = Panedwindow(master, style='TPanedwindow')
        self.c2.pack(side=LEFT, fill='both', expand=True, anchor='center')

        self.c3 = Frame(master)
        self.c3.pack()

        self.logo = PhotoImage(file='/usr/share/icons/hicolor/256x256/apps/logo.png')
        self.bg = Label(self.c2, image=self.logo, height=400, width=-500)
        self.bg.image = self.logo
        self.bg.pack(fill='both')

        self.playing = Label(self.c2, text=_('Nothing is playing'), anchor='center', font=('Arial', 12))
        self.playing.pack(fill='x', expand=False)

        self.textview = Text(self.c1, width=30)
        self.textview.pack(side=LEFT, fill='both', expand=True)
        self.vb = Scrollbar(self.c1, command=self.textview.yview)
        self.vb.pack(side=RIGHT, fill='y')
        self.textview.config(yscrollcommand=self.vb.set)

        """self.imgprev = PhotoImage(file='images/prev.png')
        self.btnprev = Button(self.c2, image=self.imgprev, cursor='hand2', relief='flat')
        self.btnprev.image = self.imgprev
        self.btnprev.pack(side=LEFT, fill='both', expand='yes')"""

        self.imgstop = PhotoImage(file='/usr/share/icons/hicolor/256x256/apps/stop.png')
        self.imgplay = PhotoImage(file='/usr/share/icons/hicolor/256x256/apps/play.png')
        self.btnplaypause = Button(self.c2, image=self.imgplay, cursor='hand2', relief='flat',
                                   activebackground='#f0f0f0')
        self.btnplaypause.image = self.imgplay
        self.btnplaypause.pack(side=BOTTOM, expand=True, anchor='center')

        """self.imgnext = PhotoImage(file='images/next.png')
        self.btnnext = Button(self.c2, image=self.imgnext, cursor='hand2', relief='flat')
        self.btnnext.image = self.imgnext
        self.btnnext.pack(side=LEFT, fill='both', expand='yes')"""

        # binds
        window.bind('<Control-R>', lambda e: [Thread(target=self.create_buttons, daemon=True).start(),
                                              Thread(target=self.update_radios, daemon=True).start()])
        window.bind('<Control-r>', lambda e: [Thread(target=self.create_buttons, daemon=True).start(),
                                              Thread(target=self.update_radios, daemon=True).start()])
        window.bind('<Control-H>', lambda e: Thread(target=self.about, daemon=True).start())
        window.bind('<Control-h>', lambda e: Thread(target=self.about, daemon=True).start())
        window.bind('<Control-U>', lambda e: Thread(target=self.about, daemon=True).start())
        window.bind('<Control-u>', lambda e: Thread(target=check_for_updates, daemon=True).start())
        window.bind('<Control-Q>', lambda e: window.quit())
        window.bind('<Control-q>', lambda e: window.quit())

        # Functions are running when software starts
        Thread(target=self.create_buttons, daemon=True).start()
        # Thread(target=self.update_radios, daemon=True).start()

    def about(self, event=None):
        popup = Toplevel()
        popup.title(_('About Stream Radios'))
        popup.geometry('400x450')
        imgbg = PhotoImage(file='/usr/share/icons/hicolor/256x256/apps/streamradios.png')
        bg = Label(popup, image=imgbg)
        bg.image = imgbg
        bg.pack()
        version = Label(popup, text='Version 0.2', fg='black')
        version.pack()
        gh = Label(popup, text='Stream Radios GitHub', cursor='hand2', underline=14, fg='blue')
        gh.pack(pady=10)
        gh.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/Alexsussa/streamradios/'))
        license = Label(popup, text='Stream Radios License', cursor='hand2', underline=14, fg='blue')
        license.pack(pady=10)
        license.bind('<Button-1>',
                     lambda e: webbrowser.open('https://github.com/Alexsussa/streamradios/blob/master/LICENSE/'))
        dev = Label(popup, text=_('Developed by: Alex Pinheiro'), cursor='hand2', fg='gray')
        dev.pack(side=LEFT, anchor='sw')
        dev.bind('<Button-1>', lambda e: webbrowser.open('https://github.com/Alexsussa/'))
        copy = Label(popup, text='© Alex Pinheiro - 2021', fg='gray')
        copy.pack(side=RIGHT, anchor='se')
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus_force()
        popup.transient(window)

    def restart(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def active_buttons_again(self):
        for button in buttons_radios:
            button.config(state='normal')

    def update_radios(self):
        self.textview.config(state='normal')
        self.textview.delete(1.0, END)
        url = 'https://bit.ly/RadiosAP'
        urllib.request.urlretrieve(url, '/opt/streamradios/file/radios.m3u8')
        self.textview.config(state='disable')
        showinfo(title=_('Update complete'), message=_('Radios list update completed.\nSoftware will restart now.'))
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def create_buttons(self):
        name = ''
        m3u8 = open('/opt/streamradios/file/radios.m3u8', 'r')
        ext = '#EXTINF:-1,'
        prefixs = ('http://', 'https://')
        # namelist = []
        # linklist = []
        # dictname = {}
        for linha in m3u8:
            if linha.startswith(ext):
                namelist.append(linha.replace(ext, '').replace('\n', ''))
            if linha.startswith(prefixs):
                linklist.append(linha)
            for name in namelist:
                dictname.setdefault(name)
            for link in linklist:
                dictname[name] = link

        for i in dictname.keys():
            self.btnradio = Button(self.textview, text=i, relief='solid', cursor='hand2', anchor='center', width=41,
                                   height=2)
            self.btnradio.config(command=lambda i=i: [Thread(target=self.play(name=i, url=dictname[i])).start()])
            self.btnradio.pack(side=TOP, fill='both')

            self.textview.window_create('end', window=self.btnradio)
            self.textview.insert('end', '\n')
            self.textview.config(state='disable')
            buttons_radios.append(self.btnradio)

    def play(self, name, url):
        try:
            multiprocessing.Queue()
            p = multiprocessing.Process(target=playsound, args=(url,), daemon=True)
            Thread(target=self.audioinfo, args=(name, url,)).start()
            if len(multiprocessing.active_children()) <= 0:
                p.start()
                for button in buttons_radios:
                    button.config(state='disable')
                    window.title(name)
                    self.btnplaypause.config(image=self.imgstop)
                    self.btnplaypause.config(command=lambda: [p.terminate(), self.restart(), self.active_buttons_again(),
                                                              self.btnplaypause.config(image=self.imgplay),
                                                              self.playing.config(text=_('Nothing is playing'),
                                                                                  cursor='arrow'),
                                                              self.playing.unbind('<Enter>'),
                                                              self.playing.unbind('<Button-1>'),
                                                              window.title('Stream Radios')])

            elif len(multiprocessing.active_children()) > 0:
                for p in multiprocessing.active_children():
                    p.terminate()
                    self.btnplaypause.config(image=self.imgplay)
                    self.btnplaypause.config(command=lambda: [p.start()])
                    self.playing.config(text=_('Nothing is playing'))
                    window.title('Stream Radios')

            elif window.destroy():
                for p in multiprocessing.active_children():
                    p.terminate()

            elif window.quit():
                for p in multiprocessing.active_children():
                    p.terminate()

        except socket.error:
            showerror(title=_('Error'),
                      message=_('Failed to connect the radio.\nCheck your internet connection or radio url.'))

    def audioinfo(self, name, url):
        r = urllib.request.Request(url)
        r.add_header('Icy-MetaData', 1)
        res = urllib.request.urlopen(r)
        icy_metaint = res.headers.get('icy-metaint')
        # print(icy_metaint)
        if icy_metaint is not None:
            metaint = int(icy_metaint)
            # print(metaint)
            read_buffer = metaint + 255
            content = res.read(read_buffer)
            # print(content)
            title = content[metaint:].split(b"'")[1]
            title_list = []
            if len(title) > 100 or len(title) <= 0:
                self.playing.config(text=name)
            elif name in strangercharradios:
                self.playing.config(text=name)
            else:
                self.playing.config(text=title, cursor='hand2')
                window.title(name)
                musicname = str(title).replace("b'", '').replace("'", '')
                self.playing.bind('<Enter>', lambda e: self.playing.config(fg='blue', font=('Arial', 12, 'underline')))
                self.playing.bind('<Leave>', lambda e: self.playing.config(fg='black', font=('Arial', 12)))
                self.playing.bind('<Button-1>',
                                  lambda e: webbrowser.open(f"https://www.google.com/search?q={musicname}"))

                if __name__ == '__main__':
                    self.audioinfo(name, url)


window = Tk()
Application(window)
logo = PhotoImage(file='/usr/share/icons/hicolor/256x256/apps/streamradios.png')
window.tk.call('wm', 'iconphoto', window._w, logo)
window.title('Stream Radios')
window.geometry('1000x600')
window.resizable(False, False)
window.update()
window.mainloop()
