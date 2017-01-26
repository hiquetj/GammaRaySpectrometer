#!/usr/bin/env python

import matplotlib
matplotlib.use("WxAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import linspace, array, random, where, zeros
from numpy.random import random as rand
import sys
import traceback
import pdb

from threading import RLock
from GammaParticleReader import MonitorThread

import wx

IS_GTK = 'wxGTK' in wx.PlatformInfo
IS_WIN = 'wxMSW' in wx.PlatformInfo
IS_MAC = 'wxMac' in wx.PlatformInfo

NUMCHANNELS=1024

class CanvasFrame(wx.Frame):
	def __init__(self, parent, title):
		self.lock = RLock()
		wx.Frame.__init__(self, parent, -1, title, size=(550, 350))
		self.SetBackgroundColour(wx.NamedColour("WHITE"))

		self.figure = Figure()

		self.axes = self.figure.add_subplot(111)
		
		self.data = zeros(NUMCHANNELS)
		self.total = []
		
		self.canvas = FigureCanvas(self, -1, self.figure)

		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.vbox.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
		
		self.commandLine = wx.TextCtrl(self, size=(800, -1))
		self.txtDisplay = wx.TextCtrl(self, size=(800,150), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		self.hbox = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox.Add(self.commandLine, 0)
		
		self.clearButton = wx.Button(self, label="Clear")
		self.saveButton = wx.Button(self, label="Save Data")
		self.hbox.Add(self.clearButton, 0)
		self.hbox.Add(self.saveButton, 20)
		
		self.vbox.Add(self.hbox, 0, wx.LEFT | wx.BOTTOM)
		

		menuBar = wx.MenuBar()
		self.labels = []  # top row of data labels
		self.rows = zeros(NUMCHANNELS, int)	   # list of lists of elements.

		self.update_plot()

		self.clearButton.Bind(wx.EVT_BUTTON, self.OnClear)
		self.saveButton.Bind(wx.EVT_BUTTON, self.OnSave)

		self.SetSizer(self.vbox)
		self.Fit()

		TIMER_ID = 1

		self.timer = wx.Timer(self, TIMER_ID)
		self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
		self.timer.Start(1000)
		
		if 'noserial' not in sys.argv:
			self.mon = MonitorThread(callback=self.dataCallback, nc=NUMCHANNELS)
		else:
			self.mon = MonitorThread(callback=self.dataCallback, fr=1)
			
		self.mon.start()
			
	def OnClear(self, evt):
		self.data = zeros(NUMCHANNELS)
		
	def OnSave(self, evt):
		self.lock.acquire()
		resultFile = open('Unknown_Data.csv', 'wb')
		resultFile.write('\n'.join([`x` for x in self.data]))
		resultFile.close()
		self.lock.release()
		
		
	def ontimer(self, evt):
		self.update_plot()
		self.canvas.draw()
		
		
	def dataCallback(self, items):
		self.lock.acquire()
		self.data += array(items[0])
		
		#To check and see why data is wrong or out of place
		#self.total = self.data 
		#print self.total
		
		
		self.lock.release()
		
	def update_plot(self):
		self.lock.acquire()
		self.axes.clear()
		self.axes.plot(range(NUMCHANNELS), self.data, 'b-', label='A')
		self.axes.set_ylabel("# of counts")
		self.axes.set_xlabel("Volts (in 1023 terms)")
		self.lock.release()

	def OnPaint(self, event):
		self.update_plot()
		self.canvas.draw()
		

class MyApp(wx.App):
	def OnInit(self):
		frame = CanvasFrame(None, "Gamma Particle Spectrum")
		self.SetTopWindow(frame)
		frame.Show(True)
		return True

import os
print "Here now:", os.getcwd()
app = MyApp()
#pdb.set_trace()
app.MainLoop()