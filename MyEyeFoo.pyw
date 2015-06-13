# -*- coding:utf-8 -*-

import ctypes
import time
import sys
from PyQt4 import QtGui, QtCore
import json

def lock_one_time():
	ctypes.windll.user32.LockWorkStation()

class TimeLabel(QtGui.QLabel, QtCore.QTimer):

	def __init__(self, parent, config, move_callback):
		super(TimeLabel, self).__init__(parent)

		self.beep_start_time = config.get('beep_start_time', 30)
		self.beep_end_time = self.beep_start_time - config.get('beep_times', 10)

		self.move_callback = move_callback
		self.time = 0
		self.timer = QtCore.QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self._count)

	def countDown(self, time):
		self.time = time
		self.setTime(time)
		self.timer.start()

	def _count(self):
		self.time -= 1
		self.setTime(self.time)
		if self.time <= self.beep_start_time and self.time >= self.beep_end_time:
			QtGui.QApplication.beep()

		if self.time <= 0:
			self.timer.stop()

	def setTime(self, time_val):
		time_val = int(time_val)
		seconds = time_val % 60
		minutes = time_val / 60
		self.setText('<font size=6><b>%02d:%02d</b></font>' % (minutes, seconds))

	def mouseMoveEvent(self, event):
		if event.buttons() & QtCore.Qt.LeftButton:
			self.move_callback(event.globalPos())

class MyWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__(flags=QtCore.Qt.WindowStaysOnTopHint \
			| QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint \
			| QtCore.Qt.Dialog | QtCore.Qt.Tool)

		# load configuration
		try:
			f = open('config.json')
			config = json.load(f)
			f.close()
		except Exception as e:
			print e
			config = {}
		self.work_time = config.get('work_time', 30)
		self.relax_time = config.get('relax_time', 3)
		self.check_period = config.get('check_period', 0.1)
		if self.check_period <=0:
			self.check_period = 0.1
		self.lock_one_time = config.get('lock_one_time', False)

		self.time_label = TimeLabel(self, config, self.onMouseMove)
		self.time_label.setTime(0)

		# set geometry
		self.settings = QtCore.QSettings("MyEyeFoo", "MyEyeFoo")
		pos = self.settings.value('pos', QtCore.QPoint(100, 100)).toPoint()
		self.size = self.time_label.sizeHint()
		self.setGeometry(pos.x(), pos.y(), self.size.width(), self.size.height())
		self.setFixedSize(self.size)

		# create close action
		self.exitAction = QtGui.QAction('Exit', self)
		self.exitAction.triggered.connect(QtGui.QApplication.quit)
		self.resetAction = QtGui.QAction('Reset', self)
		self.resetAction.triggered.connect(self.reset)

		# set context menu
		self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

		# setup timer
		self.work_timer = QtCore.QTimer()
		self.work_timer.setInterval(self.work_time*1000)
		self.work_timer.setSingleShot(True)
		self.work_timer.timeout.connect(self.relax)

		self.relax_timer = QtCore.QTimer()
		self.relax_timer.setInterval(self.relax_time*1000)
		self.relax_timer.setSingleShot(True)
		self.relax_timer.timeout.connect(self.work)

		self.work()

	def reset(self):
		self.work()

	def lock(self):
		if not self.working:
			lock_one_time()
			QtCore.QTimer.singleShot(self.check_period*1000, self.lock)

	def work(self):
		self.working = True
		self.relax_timer.stop()
		self.work_timer.start()
		self.time_label.countDown(self.work_time)

	def relax(self):
		self.working = False
		self.work_timer.stop()
		self.relax_timer.start()
		self.time_label.countDown(self.relax_time)
		if self.lock_one_time:
			lock_one_time()
		else:
			self.lock()

	def onMouseMove(self, pos):
		self.setGeometry(pos.x(), pos.y(), self.size.width(), self.size.height())

	def contextMenuEvent(self, event):
		menu = QtGui.QMenu(self)
		menu.addAction(self.exitAction)
		menu.addAction(self.resetAction)
		menu.exec_(event.globalPos())

	def closeEvent(self, event):
		geometry = self.geometry()
		pos = QtCore.QPoint(geometry.x(), geometry.y())
		self.settings.setValue('pos', pos)
		event.accept()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = MyWindow()
	window.show()
	sys.exit(app.exec_())