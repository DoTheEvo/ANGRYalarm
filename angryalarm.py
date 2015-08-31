#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import json
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import subprocess
import sys

import analogclock


class Fatherland_widget(QWidget):
    def __init__(self, settings=None, set=None):
        super().__init__()
        self.settings = settings
        self.set = set
        self.s_hour = 0
        self.s_min = 0
        self.sliders_text_value = ''
        self.stored_alarms = []
        self.running_alarms = []
        self.tick_tock_timer = QTimer()
        self.end_notice_timer = QTimer()
        self.model = QStandardItemModel()
        self.countdown_is_running = False
        self.initUI()

    def initUI(self):
        father_grid = QGridLayout()
        father_grid.setSpacing(10)

        self.left = Left_Widget()
        self.running_list = QListView()

        self.the_clock = analogclock.AnalogClock()

        self.running_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        father_grid.addWidget(self.left.tabWidget, 0, 0, 2, 2)
        father_grid.addWidget(self.the_clock, 0, 3, 1, 1)
        father_grid.addWidget(self.running_list, 1, 3, 1, 1)
        self.setLayout(father_grid)

        # LOGIC
        self.left.slider_hours.setValue(int(self.set['hours']))
        self.left.slider_minutes.setValue(int(self.set['minutes']))
        self.get_current_value()
        self.left.slider_hours.valueChanged[int].connect(self.get_current_value)
        self.left.slider_minutes.valueChanged[int].connect(self.get_current_value)

        self.left.button_start.clicked.connect(self.initial_alarm_data)
        self.left.button_clear.clicked.connect(self.clear_all_countdowns)

    def get_current_value(self, value=None):
        self.s_hour = self.left.slider_hours.value()
        self.s_min = self.left.slider_minutes.value()

        self.settings.setValue('hours', str(self.s_hour))
        self.settings.setValue('minutes', str(self.s_min))
        if self.s_hour < 1:
            self.sliders_text_value = '{:02}m'.format(self.s_min)
        else:
            self.sliders_text_value = '{}h : {:02}m'.format(
                self.s_hour, self.s_min)

        self.left.the_time_label.setText(self.sliders_text_value)

    def tick_tock(self):
        print('ticking')
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            remaining = round(item.alarm['q_timer'].remainingTime() / 1000)
            if remaining > 0:
                item.setText(self.digits_from_seconds(remaining))
            else:
                t = '{} ALARM ENDED'.format(item.alarm['word_length'])
                item.setText(t)


    def initial_alarm_data(self):
        now = int(time.time())
        seconds_lasting = self.s_hour * 3600 + self.s_min * 60

        alarm = {
            'start_time': now,
            'end_time': now + seconds_lasting,
            'length': seconds_lasting,
            'word_length': self.sliders_text_value
        }

        if seconds_lasting > 0:
            setting_name =  'Countdowns/{}'.format(alarm['end_time'])
            self.settings.setValue(setting_name, json.dumps(alarm))

        self.add_new_alarm(alarm)

    def add_new_alarm(self, alarm_data):
        now = int(time.time())
        seconds_left = alarm_data['end_time'] - now

        if seconds_left > 0:
            item = QStandardItem(self.digits_from_seconds(seconds_left))
        else:
            item = QStandardItem('{} ALARM ENDED'.format(alarm_data['word_length']))

        item.alarm = alarm_data

        item.alarm['q_timer'] = QTimer()
        item.alarm['q_timer'].timeout.connect(self.alarm_ended)
        item.alarm['q_timer'].setSingleShot(True)
        if seconds_left > 0:
            item.alarm['q_timer'].start(seconds_left * 1000)
        else:
            item.alarm['q_timer'].start(500)


        where = self.position_in_model(item)
        self.model.insertRow(where, item)
        self.running_list.setModel(self.model)

        # ONLY NEED SINGLE tick_tock_timer RUNNING
        if self.countdown_is_running is False:
            self.tick_tock_timer = QTimer()
            self.tick_tock_timer.timeout.connect(self.tick_tock)
            self.tick_tock_timer.setSingleShot(False)
            self.tick_tock_timer.start(1000)
            self.countdown_is_running = True

    def alarm_ended(self):
        s = ['play', '/usr/share/sounds/KDE-Im-Contact-Out.ogg']
        subprocess.Popen(s)
        print('asas')
        now = int(time.time())
        zero_alarms_runing = True
        for x in range(self.model.rowCount()):
            print('zzzzzzzzzzzzzz')
            item = self.model.item(x)
            if item.alarm['end_time'] > now:
                zero_alarms_runing = False
            else:
                name_in_settings = 'Countdowns/{}'.format(item.alarm['end_time'])
                self.settings.remove(name_in_settings)

        if zero_alarms_runing:
            self.tick_tock_timer.stop()
            self.countdown_is_running = False

        self.end_notice_timer.timeout.connect(self.alarm_ended_cleanup)
        self.end_notice_timer.setSingleShot(True)
        self.end_notice_timer.start(5000)

    def alarm_ended_cleanup(self):
        now = int(time.time())
        marked_for_removal = []
        for x in range(self.model.rowCount()):
            item = self.model.item(x)
            if item.alarm['end_time'] <= now:
                marked_for_removal.append(item)

        for z in marked_for_removal:
            self.model.removeRow(z.row())

    def position_in_model(self, item):
        count = 0
        numb_of_items = self.model.rowCount()

        if numb_of_items == 0:
            return 0

        for x in range(numb_of_items):
            count += 1
            prev = self.model.item(x)
            if item.alarm['end_time'] <= prev.alarm['end_time']:
                return x

        return count

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

        self.settings.remove('Countdowns')

class Left_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.tabWidget = QTabWidget()
        self.tab_1 = QWidget()
        self.tab_2 = QWidget()
        self.tabWidget.addTab(self.tab_1, 'Countdown')
        self.tabWidget.addTab(self.tab_2, 'Longterm')
        self.tabWidget.setCurrentIndex(0)

        self.slider_hours = QSlider(Qt.Horizontal, self)
        self.slider_minutes = QSlider(Qt.Horizontal, self)

        self.slider_minutes.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.slider_hours.setMinimum(0)
        self.slider_hours.setMaximum(24)
        self.slider_hours.setTickPosition(2)

        self.slider_minutes.setMinimum(0)
        self.slider_minutes.setMaximum(60)
        self.slider_minutes.setTickPosition(2)
        self.slider_minutes.setTickInterval(10)

        font = QFont()
        font.setPointSize(15)

        self.button_start = QPushButton("START")
        self.button_clear = QPushButton("Clear All")
        self.button_start.setFont(font)
        self.button_clear.setFont(font)

        self.button_start.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.button_clear.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)

        self.the_time_label = QLabel()
        self.the_time_label.setAlignment(Qt.AlignHCenter)
        self.the_time_label.setStyleSheet("QLabel { color: #ffc100 }")

        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        font.setWeight(75)
        self.the_time_label.setFont(font)

        grid_layout = QGridLayout(self.tab_1)
        grid_layout.addWidget(self.slider_hours, 0, 0, 1, 3)
        grid_layout.addWidget(self.slider_minutes, 2, 0, 2, 3)
        grid_layout.addWidget(self.the_time_label, 4, 0, 1, 3)
        grid_layout.addWidget(self.button_clear, 5, 0, 2, 1)
        grid_layout.addWidget(self.button_start, 5, 1, 2, 2)


# THE MAIN APPLICATION WINDOW WITH THE STATUS BAR AND LOGIC
class Gui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.settings = QSettings('angryalarm', 'angryalarm')
        self.set = {'hours': '0',
                    'minutes': '10',
                    'previous_alarms': []}
        self.read_settings()

        self.style_data = ''
        f = open('stylesheet.qss', 'r')
        self.style_data = f.read()
        f.close()

        self.init_GUI()

    def init_GUI(self):
        self.icon = self.get_tray_icon()
        self.setWindowIcon(self.icon)

        self.center = Fatherland_widget(self.settings, self.set)
        self.setCentralWidget(self.center)
        self.setStyleSheet(self.style_data)

        self.setWindowTitle('ANGRYalarm')
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.show()
        self.make_sys_tray()

        for z in self.set['previous_alarms']:
            self.center.add_new_alarm(z)
        print(self.set)

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
        base64_data = '''iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAALGPC/xhBQAAAAlwSF
                      lzAAAOwgAADsIBFShKgAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAAC5El
                      EQVQ4T61Ta0iTYRj1h5WVEUEQM9N5JTXDqDSFtIu1yktTU6wkE3SFIYmXoDItzMzbZl7m1DnzOv38
                      tulsTqcuN3fT5aWfYkS/NIyMAv1Ryen9JIRh0Z9eeODwnPOd97zPx2Nn979OTnZuhC7pSpGFE7r0L
                      jnh7WJ6ihNF0S40LXNdSE9hzSfHz05wTn7SXYsrys3OjbK5dy71uuPCg6xRlR8bg6S+Pbm/unT7xr
                      kCHi8vn8fL/8hLOvu14N6KmnCMZvFhjnYuNWnXhsl0zIVHA/7uELF2o8nLebXL00k7dNRnuTfoMHq
                      D/DF0zGeZ9EYJt8JoVIfcMc3lPN4wsEaFp3a47Vvj790pLWOzlmt93FEVH4vajDuou5uBaoKFpFfO
                      Zn1hNO1EOxl5hrdhMHuVa6857usn9XCSlcdw8bK5FTq9ATqdHq9UAzAaLeu9yrhYSD1YCpLIbybxs
                      r3NHGg/94SyWC6oHgU0Gi20Wj2U/SrQtBxSKQW5Qkk4OfhxMejxZSdu+nmNR3wnmholGB83Q60eRn
                      +/GgaDmSQxgs9/AdWAhiQyQtwghjjgoNXGwBAeslUYdfGnwWjG1PQsDCSysK6B3NqP6moh+vpUMJk
                      m8GZqhpiaIIrkrOnCAh02TPSnAncIoiNQWyuCoLKKiCwwkg8YLJG0wGyeXDeVNLegokIAYUw0XocE
                      ONqkqDl/+r1MroTZYkV3N43CwiJ0dFLoITMZHByBiZgwHC3rRXMk58OmGYi9XfKqip5jiAywrU2KX
                      hJ7eGQMw8NjoCjF+nPUxEhYXAqJ94H8TQaU136HmtBgK79UQBIo0KdUo6W1A9IuGkqCOztp8Ev4qA
                      8LmerycNr+xxUqCQtxKb3E+f40jYeq6nqI6sVoaGwmWIRnabdQEcH5URwa7PrX/cvMzDrh6enVFuB
                      gL7vJdp7PCg76zFQKwQEOW+Rstlt7Tk5u8L8WeBsR7CHlTMrrdzGY6TGczfkFSv+cb9Ll4CsAAAAA
                      SUVORK5CYII='''

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

        if self.settings.value('hours'):
                    self.set['hours'] = self.settings.value('hours')
        if self.settings.value('minutes'):
                    self.set['minutes'] = self.settings.value('minutes')

        self.settings.beginGroup('Countdowns')
        previous_alarms = self.settings.allKeys()
        for x in previous_alarms:
            self.set['previous_alarms'].append(json.loads(self.settings.value(x)))
        self.settings.endGroup()

    def closeEvent(self, event):
        self.settings.setValue('Last_Run/geometry', self.saveGeometry())
        self.settings.setValue('Last_Run/window_state', self.saveState())

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Gui_MainWindow()
    sys.exit(app.exec_())
