# -*- coding:utf-8 -*-

import ctypes
import time
import sys
from PyQt4 import QtGui, QtCore
import json

def lock(duration, check_period):
	if check_period > 0:
		times = int(duration/check_period) + 1 # in case time is zero
	else:
		times = 1
	for i in xrange(times):
		lock_one_time()
		time.sleep(check_period)

def lock_one_time():
	ctypes.windll.user32.LockWorkStation()

class TimeLabel(QtGui.QLabel):

	def __init__(self, parent, callback):
		super(TimeLabel, self).__init__(parent)
		self.callback = callback

	def setTime(self, time_val):
		time_val = int(time_val)
		seconds = time_val % 60
		minutes = time_val / 60
		self.setText('<font size=20><b>%02d:%02d</b></font>' % (minutes, seconds))

	def mouseMoveEvent(self, event):
		if event.buttons() & QtCore.Qt.LeftButton:
			self.callback(event.globalPos())

class MyWindow(QtGui.QMainWindow):
	def __init__(self):
		super(MyWindow, self).__init__(flags=QtCore.Qt.WindowStaysOnTopHint \
			| QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint \
			| QtCore.Qt.Dialog | QtCore.Qt.Tool)

		self.time_label = TimeLabel(self, self.onMouseMove)
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

		# set context menu
		self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)

		# load configuration
		try:
			f = open('config.json')
			config = json.load(f)
			f.close()
		except:
			config = {}
		self.work_time = config.get('work_time', 30)
		self.relax_time = config.get('relax_time', 3)
		self.check_period = config.get('check_period', 0.1)
		self.lock_one_time = config.get('lock_one_time', False)
		self.beep_start_time = config.get('beep_start_time', 30)
		self.beep_end_time = self.beep_start_time - config.get('beep_times', 10)
		self.work()

	def work(self):
		QtCore.QTimer.singleShot(self.work_time*1000, self.relax)
		self.count_down(self.work_time)

	def count_down(self, time_val):
		if time_val < 0:
			return

		if time_val <= self.beep_start_time and time_val > self.beep_end_time:
			QtGui.QApplication.beep()

		self.time_label.setTime(time_val)
		QtCore.QTimer.singleShot(1000, lambda: self.count_down(time_val-1))

	def relax(self):
		QtCore.QTimer.singleShot(self.relax_time*1000, self.work)
		if self.lock_one_time:
			lock_one_time()
		else:
			lock(self.relax_time, self.check_period)

	def onMouseMove(self, pos):
		self.setGeometry(pos.x(), pos.y(), self.size.width(), self.size.height())

	def contextMenuEvent(self, event):
		menu = QtGui.QMenu(self)
		menu.addAction(self.exitAction);
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