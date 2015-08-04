#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import subprocess
import sys

import analogclock


class Fatherland_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.s_hour = 0
        self.s_min = 0
        self.sliders_text_value = '00m'
        self.stored_alarms = []
        self.running_alarms = []
        self.tick_tock_timer = QTimer()
        self.model = QStandardItemModel()
        self.countdown_is_running = False
        self.initUI()

    def initUI(self):
        father_grid = QGridLayout()
        father_grid.setSpacing(10)

        self.left = Left_Widget()
        self.right_clock = Right_widget_top()
        self.low_alarms = Down_right_widget()

        father_grid.addWidget(self.left, 0, 0, 2, 2)
        father_grid.addWidget(self.right_clock, 0, 3, 1, 1)
        father_grid.addWidget(self.low_alarms, 1, 3, 1, 1)
        self.setLayout(father_grid)

        # LOGIC
        self.left.slider_hours.valueChanged[int].connect(self.value_changed)
        self.left.slider_minutes.valueChanged[int].connect(self.value_changed)

        self.left.button_start.clicked.connect(self.add_new_alarm)
        self.left.button_clear.clicked.connect(self.clear_all_countdowns)

    def value_changed(self, value):
        self.get_current_value()
        self.left.the_time_label.setText(self.sliders_text_value)

    def get_current_value(self):
        self.s_hour = self.left.slider_hours.value()
        self.s_min = self.left.slider_minutes.value()

        if self.s_hour < 1:
            self.sliders_text_value = '{:02}m'.format(self.s_min)
        else:
            self.sliders_text_value = '{}h : {:02}m'.format(
                self.s_hour, self.s_min)

    def add_new_alarm(self):
        print('single click')
        current_time = int(time.time())
        seconds_lasting = self.s_hour*3600 + self.s_min*60

        item = QStandardItem(self.digits_from_seconds(seconds_lasting))
        item.alarm = {
            'start_time': current_time,
            'end_time': current_time + seconds_lasting,
            'length': seconds_lasting,
            'word_length': self.sliders_text_value,
            'q_timer': QTimer()
        }
        item.alarm['q_timer'].timeout.connect(self.alarm_ended)
        item.alarm['q_timer'].setSingleShot(True)
        item.alarm['q_timer'].start(seconds_lasting*1000)
        self.model.appendRow(item)
        self.low_alarms.running_list.setModel(self.model)

        self.countdown_is_running = True

        self.tick_tock_timer.timeout.connect(self.tick_tock)
        self.tick_tock_timer.setSingleShot(False)
        self.tick_tock_timer.start(1000)

    def tick_tock(self):
        print('ticking')
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            remaining = round(item.alarm['q_timer'].remainingTime() / 1000)
            item.setText(self.digits_from_seconds(remaining))

    def alarm_ended(self):
        s = ['play', '/usr/share/sounds/KDE-Im-Contact-Out.ogg']
        subprocess.Popen(s)

        now = int(time.time())
        zero_alarms_runing = True
        print(dir(self.model))
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            if item.alarm['end_time'] > now:
                zero_alarms_runing = False
            else:
                t = '{} ALARM ENDED'.format(item.alarm['word_length'])
                item.setText(t)
                item.alarm['q_timer'].stop()
                item.alarm['q_timer'].timeout.connect(self.alarm_ended_cleanup)
                item.alarm['q_timer'].setSingleShot(True)
                item.alarm['q_timer'].start(5000)

        if zero_alarms_runing:
            self.tick_tock_timer.stop()
            self.countdown_is_running = False

    def alarm_ended_cleanup(self):
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            if item.alarm['end_time'] < now:
                self.model.removeRow(item.row())


    def digits_from_seconds(self, secs):
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        if h == 0:
            return '{:02}:{:02}'.format(m, s)
        return '{:02}:{:02}:{:02}'.format(h, m, s)

    def clear_all_countdowns(self):
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            item.alarm['q_timer'].stop()
        self.model.clear()
        self.tick_tock_timer.stop()
        self.countdown_is_running = False


class Left_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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


class Right_widget_top(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.the_clock = analogclock.AnalogClock()
        self.the_clock.show()

        self.rgrid = QGridLayout()
        self.rgrid.setSpacing(10)

        self.rgrid.addWidget(self.the_clock, 1, 1, 25, 25)
        self.setLayout(self.rgrid)


class Down_right_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.running_list = QListView(self)


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
