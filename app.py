#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from functools import partial
from common import audioInfo, browserOnGoogle, check_for_updates, updateRadioList
import sys
import os
import socket
import vlc
import webbrowser
import gettext

APPNAME = 'streamradios'
LOCALE = os.path.abspath('/usr/share/locale')

gettext.bindtextdomain(APPNAME, LOCALE)
gettext.textdomain(APPNAME)
_ = gettext.gettext


radios_buttons = []
radios = {}
links = []
names = []


class Interface(QMainWindow):
    def __init__(self):
        super().__init__()

        # App's images
        self.logoBg = QPixmap('/opt/streamradios/images/logo.png')
        self.playIcon = QIcon('/opt/streamradios/images/play.png')
        self.stopIcon = QIcon('/opt/streamradios/images/stop.png')
        self.winIcon = QIcon('/opt/streamradios/images/streamradios.png')
        self.css = open('/usr/share/doc/streamradios/sr.css', 'r').read()

        self.popup = QMessageBox()

        self.vlcInstance = vlc.Instance()
        self.mp = self.vlcInstance.media_player_new()

        self.mainMenu = QMenuBar()
        self.mainMenu.setFont(QFont('Helvetica', 11))

        self.fileMenu = QMenu(_('File'))
        self.fileMenu.addAction(_('Update radios list...'), updateRadioList, 'Ctrl+R')
        self.fileMenu.addAction(_('Check for software updates'), lambda: check_for_updates(self.popup), 'Ctrl+U')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(_('Quit'), sys.exit, 'Ctrl+Q')

        self.helpMenu = QMenu(_('Help'))
        self.helpMenu.addAction(_('Documentation'), lambda: webbrowser.open('https://github.com/Alexsussa/streamradios#streamradios'), 'Ctrl+D')
        self.helpMenu.addAction(_('License'), lambda: webbrowser.open('https://github.com/Alexsussa/streamradios/blob/master/docs/COPYING'), 'Ctrl+L')
        self.helpMenu.addAction('GitHub', lambda: webbrowser.open('https://github.com/Alexsussa/streamradios'), 'Ctrl+G')
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(_('About'), self.about, 'Ctrl+H')

        self.mainMenu.addMenu(self.fileMenu)
        self.mainMenu.addMenu(self.helpMenu)
        self.setMenuBar(self.mainMenu)

        self.cw = QWidget()

        self.central = QWidget()

        self.vlayoutMain = QHBoxLayout()

        self.vlayoutLeft = QVBoxLayout()
        self.vlayoutLeft.setAlignment(Qt.AlignLeft)

        self.vlayoutRight = QVBoxLayout()
        self.vlayoutRight.setAlignment(Qt.AlignRight)

        self.vlayoutCenter = QVBoxLayout()
        self.vlayoutCenter.setAlignment(Qt.AlignCenter)

        self.cw.setLayout(self.vlayoutMain)
        self.setCentralWidget(self.cw)
        
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setAlignment(Qt.AlignLeft)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.central)

        self.vlayoutMain.addWidget(self.scrollArea)

        self.vlayoutLeft = QVBoxLayout(self.central)
        self.vlayoutLeft.setAlignment(Qt.AlignLeft)

        self.vlayoutMain.addLayout(self.vlayoutRight)

        self.labelLogo = QLabel()
        self.labelLogo.setPixmap(self.logoBg)

        self.lbPlaying = QLabel(_('Nothing is playing'))
        self.lbPlaying.setFont(QFont('Helvetica', 14))
        self.lbPlaying.setAlignment(Qt.AlignCenter)

        self.btnPlayStop = QPushButton()
        self.btnPlayStop.setObjectName('PlayPause')
        self.btnPlayStop.setFixedSize(150, 150)
        self.btnPlayStop.setIcon(self.playIcon)
        self.btnPlayStop.setIconSize(QSize(180, 180))
        self.btnPlayStop.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnPlayStop.clicked.connect(self.stopRadio)

        self.vlayoutRight.addWidget(self.labelLogo)
        self.vlayoutRight.addStretch()
        self.vlayoutRight.addWidget(self.lbPlaying)
        self.vlayoutRight.addStretch()
        self.vlayoutRight.addWidget(self.btnPlayStop, alignment=Qt.AlignCenter)
        self.vlayoutRight.addStretch()

        self.setStyleSheet(self.css)

        # Funções que iniciam com o programa
        self.addButtons()

        # Atalhos do teclado
        self.lbPlaying.mousePressEvent = lambda event: browserOnGoogle(self.lbPlaying.text())

    
    def addButtons(self):
        radiosDir = os.path.expanduser('~/.config/streamradios/file/')
        if not os.path.exists(radiosDir):
            os.makedirs(radiosDir)
        else:
            file = open(radiosDir + 'radios.m3u8', 'r')
            for item in file:
                if str(item).startswith('#EXTINF:-1,'):
                    names.append(str(item).replace('#EXTINF:-1,', '').replace('\n', ''))
                if str(item).startswith('https://') or str(item).startswith('http://'):
                    links.append(str(item).replace('\n', ''))

                for name in names:
                    radios.setdefault(name)
                for link in links:
                    radios[name] = link

            for i in radios.keys():
                self.radioButton = QPushButton(i, self.central)
                self.radioButton.clicked.connect(partial(self.playRadio, i, radios[i]))
                self.radioButton.setFixedHeight(26)
                self.vlayoutLeft.addWidget(self.radioButton)
                radios_buttons.append(self.radioButton)


    def playRadio(self, name, url):
        try:
            media = vlc.Media(url)
            self.mp.set_media(media)
            self.mp.play()
            #print(f'TOCANDO AGORA {name}\n{url}')
            self.btnPlayStop.setIcon(self.stopIcon)
            #self.lbPlaying.setText(name)
            self.lbPlaying.setCursor(QCursor(Qt.PointingHandCursor))
            self.lbPlaying.setStyleSheet('QLabel:hover { color: blue; }')
            window.setWindowTitle(name)
            audioInfo(name, url, self.lbPlaying)
            for button in radios_buttons:
                button.setDisabled(True)
        except socket.error:
            self.btnPlayStop.setIcon(self.playIcon)
            self.lbPlaying.setText(_('Nothing is playing'))
            self.lbPlaying.setCursor(QCursor(Qt.ArrowCursor))
            self.lbPlaying.setStyleSheet('QLabel:hover { color: black; }')
            window.setWindowTitle('Stream Radios')
            for button in radios_buttons:
                button.setDisabled(False)

    
    def stopRadio(self):
        try:
            if self.mp.is_playing() == 1:
                self.mp.stop()
                self.btnPlayStop.setIcon(self.playIcon)
                self.lbPlaying.setText(_('Nothing is playing'))
                self.lbPlaying.setCursor(QCursor(Qt.ArrowCursor))
                self.lbPlaying.setStyleSheet('QLabel:hover { color: black; }')
                window.setWindowTitle('Stream Radios')
                for button in radios_buttons:
                    button.setDisabled(False)

        except socket.error:
            self.mp.stop()

    
    def about(self):
        logo = QLabel('')
        logo.setStyleSheet('background-image: url(images/streamradios.png); background-repeat: no-repeat; width: 100%; height: 100%;')
        logo.setWindowIcon(QIcon(self.winIcon))
        logo.setFixedSize(256, 256)
        name = QLabel('Stream Radios')
        name.setFixedHeight(20)
        version = QLabel('v0.3')
        version.setFixedHeight(10)

        license_file = open('doc/COPYING', 'r').read()
        licen = QTextEdit()
        licen.setReadOnly(True)
        licen.setText(license_file)

        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addWidget(name)
        layout.addWidget(version)
        layout.addWidget(licen)

        layout.setAlignment(logo, Qt.AlignHCenter)
        layout.setAlignment(name, Qt.AlignHCenter)
        layout.setAlignment(version, Qt.AlignHCenter)

        about = QDialog()
        about.setWindowTitle(_('About Stream Radios'))
        about.setWindowIcon(self.winIcon)
        about.setFixedSize(450, 500)
        about.setLayout(layout)
        about.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    systemLocale = QLocale().system().name()
    library = QLibraryInfo.location(QLibraryInfo.LibraryLocation.TranslationsPath)
    translator.load('qt_' + systemLocale, library)
    window = Interface()
    window.setWindowTitle('Stream Radios')
    window.setFixedSize(800, 600)
    window.setWindowIcon(QIcon('images/streamradios.png'))
    window.show()
    app.installTranslator(translator)
    sys.exit(app.exec_())
