#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request
import webbrowser
import os
import sys
import socket
import gettext

APPNAME = 'streamradios'
LOCALE = os.path.abspath('/usr/share/locale')

gettext.bindtextdomain(APPNAME, LOCALE)
gettext.textdomain(APPNAME)
_ = gettext.gettext

strangeCharRadios = ['Transamérica 100.1 FM', '105 FM', 'Band FM 96.1', 'Rádio Mix FM 106.3']

radiosDir = os.path.expanduser('~/.config/streamradios/file/')


def audioInfo(name, url, label):
    try:
        r = urllib.request.Request(url)
        r.add_header('Icy-MetaData', 1)
        res = urllib.request.urlopen(r)
        icy_metaint = res.headers.get('icy-metaint')
        if icy_metaint is not None:
            metaint = int(icy_metaint)
            read_buffer = metaint + 255
            content = res.read(read_buffer)
            title = content[metaint:].split(b"'")[1]
            title_e = str(title).replace("b'", '').replace("'", '')
            
        if len(title_e) > 100 or len(title_e) <= 0:
            label.setText(name)
        elif name in strangeCharRadios:
            label.setText(name)
        else:
            label.setText(title_e)
    except IndexError:
        pass
        label.setText(name)


def browserOnGoogle(music_name):
    if music_name == _('Nothing is playing') or music_name in strangeCharRadios:
        pass
    else:
        webbrowser.open(f'https://google.com/search?q={music_name}')


def updateRadioList():
    if not os.path.exists(radiosDir):
        os.makedirs(radiosDir)
    else:
        url = 'https://tinyurl.com/RadiosAP'
        urllib.request.urlretrieve(url, f'{radiosDir}/radios.m3u8')

        python = sys.executable
        os.execl(python, python, *sys.argv)


# Checks if there's a new software's version
def check_for_updates(popup):
    __version__ = 0.3
    try:
        new_version = urllib.request.urlopen(
            'https://raw.githubusercontent.com/Alexsussa/streamradios/master/version').read()
        if float(new_version) > float(__version__):
            popup.setWindowTitle(_('New software version'))
            popup.setIcon(popup.Information)
            popup.setText(_("There's a new software version to download.\n\nDownload it now!"))
            popup.show()
            popup.buttonClicked.connect(lambda: webbrowser.open('https://github.com/Alexsussa/streamradios/releases/'))
                
        if float(new_version) <= float(__version__):
            popup.setWindowTitle(_('Updated'))
            popup.setIcon(popup.Information)
            popup.setText(_('Software has the last version installed.'))
            popup.show()

    except socket.error:
        popup.setWindowTitle(_('Connection error'))
        popup.setText(_('No internet connection.'))
        popup.show()
