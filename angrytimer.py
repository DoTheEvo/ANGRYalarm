#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
from datetime import datetime
import locale
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import subprocess
import sys

import analogclock


class Fatherland_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        h_box = QHBoxLayout()
        h_box.setSpacing(10)

        self.left = Left_Widget()
        self.right = Right_widget()

        h_box.addWidget(self.left)
        h_box.addWidget(self.right)
        self.setLayout(h_box)


class Left_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sliders_value = [0, 0]
        self.sliders_text_value = '00m'
        self.running_countdowns = []

    def get_current_value(self):
        h = self.slider_hours.value()
        m = self.slider_minutes.value()
        self.sliders_value = [h, m]

        if h < 1:
            self.sliders_text_value = '{:02}m'.format(m)
        else:
            self.sliders_text_value = '{}h : {:02}m'.format(h, m)

    def changeValue(self, value):
        self.get_current_value()
        self.the_time_label.setText(self.sliders_text_value)

    def start_countdown_btn_press(self):
        print(self.sliders_value)
        #self.current_timer.timeout.connect(self.print_hello)
        #self.current_timer.setSingleShot(True)
        #self.current_timer.start(3000)
        q = QTimer()
        q.timeout.connect(self.print_hello)
        q.setSingleShot(True)
        q.start(3000)
        self.running_countdowns.append({'text': self.sliders_text_value,
                                        'qtimer': q,
                                        'end_time': 'fuck'
                                       })

    def clear_all_countdowns(self):
        print('clear')
        for x in self.running_countdowns:
            x['qtimer'].stop()
        self.running_countdowns = []
        print(self.running_countdowns)

    def print_hello(self):
        print('zz')
        s = ['play', '/usr/share/sounds/KDE-Im-Contact-Out.ogg']
        subprocess.Popen(s)

    def initUI(self):
        # ITEMS

        left_right_layout = QHBoxLayout()
        left_right_layout.setSpacing(10)

        self.slider_hours = QSlider(Qt.Horizontal, self)
        self.slider_minutes = QSlider(Qt.Horizontal, self)

        self.slider_hours.setMinimum(0)
        self.slider_hours.setMaximum(24)
        self.slider_hours.setTickPosition(2)

        self.slider_minutes.setMinimum(0)
        self.slider_minutes.setMaximum(60)
        self.slider_minutes.setTickPosition(2)
        self.slider_minutes.setTickInterval(10)

        self.tabWidget = QTabWidget()
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_1, 'Countdown')
        self.tabWidget.addTab(self.tab_2, 'Longterm')
        self.tabWidget.setCurrentIndex(0)

        self.button_start = QPushButton("Start the Countdown")
        self.button_clear = QPushButton("Clear All")
        self.the_time_label = QLabel('15m')

        grid_layout = QGridLayout(self.tab_1)
        grid_layout.addWidget(self.slider_hours, 0, 0, 1, 3)
        grid_layout.addWidget(self.slider_minutes, 1, 0, 1, 3)
        grid_layout.addWidget(self.the_time_label, 2, 1, 1, 1)
        grid_layout.addWidget(self.button_clear, 2, 0)
        grid_layout.addWidget(self.button_start, 2, 2)

        left_right_layout.addWidget(self.tabWidget)
        self.setLayout(left_right_layout)

        # LOGIC

        self.slider_hours.valueChanged[int].connect(self.changeValue)
        self.slider_minutes.valueChanged[int].connect(self.changeValue)

        self.button_start.clicked.connect(self.start_countdown_btn_press)
        self.button_clear.clicked.connect(self.clear_all_countdowns)



class Right_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.the_clock = analogclock.AnalogClock()
        self.the_clock.show()

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.the_clock, 1, 1, 25, 25)
        self.setLayout(grid)


# THE MAIN APPLICATION WINDOW WITH THE STATUS BAR AND LOGIC
class Gui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.settings = QSettings('angrytimer', 'angrytimer')
        self.set = {}
        self.read_settings()
        self.init_GUI()

    def init_GUI(self):
        self.icon = self.get_tray_icon()
        self.setWindowIcon(self.icon)

        self.center = Fatherland_widget()
        self.setCentralWidget(self.center)

        self.setWindowTitle('ANGRYtimer')
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.show()
        self.make_sys_tray()

    def make_sys_tray(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            menu = QMenu()
            menu.addAction('v0.0.1')
            menu.addSeparator()
            exitAction = menu.addAction('Quit')
            exitAction.triggered.connect(sys.exit)

            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(self.icon)
            self.tray_icon.setContextMenu(menu)
            self.tray_icon.show()
            self.tray_icon.setToolTip('ANGRYtimer')
            self.tray_icon.activated.connect(self.sys_tray_clicking)

    def sys_tray_clicking(self, reason):
        if (reason == QSystemTrayIcon.DoubleClick or
                reason == QSystemTrayIcon.Trigger):
            self.show()
        elif (reason == QSystemTrayIcon.MiddleClick):
            QCoreApplication.instance().quit()

    def get_tray_icon(self):
        base64_data = '''iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHN
                         CSVQICAgIfAhkiAAAAQNJREFUOI3t1M9KAlEcxfHPmP0xU6Ogo
                         G0teoCiHjAIfIOIepvKRUE9R0G0KNApfy0c8hqKKUMrD9zVGc4
                         9nPtlsgp5n6qSVSk7cBG8CJ6sEX63UEcXz4jE20YNPbygPy25Q
                         o6oE+fEPXFF7A5yA9Eg2sQDcU3sJd6k89O4iiMcYKVol3rH2Mc
                         a1meZ4hMdNPCIj+SjHHfFZU94/0Nwlv4rWoY7vhrdeLNoO86bG
                         lym/ge3lsHDdI2fojbBG6sUtzOiQ1wQOwk6GwWKHeJyHtxOcFi
                         0TpFaxmnhNcyIW45bQ6RS3Hq4MeB7Ltyahki9Gd2xidWiwG9va
                         nCZqi7xlZGVHfwN6+5nU/ccBUYAAAAASUVORK5CYII='''

        pm = QPixmap()
        pm.loadFromData(base64.b64decode(base64_data))
        i = QIcon()
        i.addPixmap(pm)
        return i

    def read_settings(self):
        if self.settings.value('Last_Run/geometry'):
            self.restoreGeometry(self.settings.value('Last_Run/geometry'))
        else:
            self.resize(640, 480)
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

    def closeEvent(self, event):
        self.settings.setValue('Last_Run/geometry', self.saveGeometry())
        self.settings.setValue('Last_Run/window_state', self.saveState())
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Gui_MainWindow()
    sys.exit(app.exec_())