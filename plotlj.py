import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot

from labjack import ljm

import pyqtgraph as pg
import numpy as np
import queue
import time

class PLOT(QtWidgets.QMainWindow):
  def __init__(self, setting, labjack):
    QtWidgets.QMainWindow.__init__(self)

    self.setting = setting
    self.labjack = labjack

    uic.loadUi('tab.ui',self)
    
    self.gains = ['1', '10', '100', '1000']
    self.threadpool = QtCore.QThreadPool()
    self.q = queue.Queue(maxsize=20)
    self.STREAM = False

    self.comboBoxGainC1.addItems(self.gains)
    self.comboBoxGainC2.addItems(self.gains)
    self.comboBoxGainC3.addItems(self.gains)
    self.comboBoxGainC4.addItems(self.gains)
    self.comboBoxGainC5.addItems(self.gains)
    self.comboBoxGainC6.addItems(self.gains)
    self.comboBoxGainC7.addItems(self.gains)
    self.comboBoxGainC8.addItems(self.gains)
    self.comboBoxGainC9.addItems(self.gains)
    self.comboBoxGainC10.addItems(self.gains)
    self.comboBoxGainC11.addItems(self.gains)
    self.comboBoxGainC12.addItems(self.gains)
    self.comboBoxGainC13.addItems(self.gains)
    self.comboBoxGainC14.addItems(self.gains)
    self.comboBoxGainC1.currentIndexChanged['QString'].connect(self.event_GainC1)
    self.comboBoxGainC2.currentIndexChanged['QString'].connect(self.event_GainC2)
    self.comboBoxGainC3.currentIndexChanged['QString'].connect(self.event_GainC3)
    self.comboBoxGainC4.currentIndexChanged['QString'].connect(self.event_GainC4)
    self.comboBoxGainC5.currentIndexChanged['QString'].connect(self.event_GainC5)
    self.comboBoxGainC6.currentIndexChanged['QString'].connect(self.event_GainC6)
    self.comboBoxGainC7.currentIndexChanged['QString'].connect(self.event_GainC7)
    self.comboBoxGainC8.currentIndexChanged['QString'].connect(self.event_GainC8)
    self.comboBoxGainC9.currentIndexChanged['QString'].connect(self.event_GainC9)
    self.comboBoxGainC10.currentIndexChanged['QString'].connect(self.event_GainC10)
    self.comboBoxGainC11.currentIndexChanged['QString'].connect(self.event_GainC11)
    self.comboBoxGainC12.currentIndexChanged['QString'].connect(self.event_GainC12)
    self.comboBoxGainC13.currentIndexChanged['QString'].connect(self.event_GainC13)
    self.comboBoxGainC14.currentIndexChanged['QString'].connect(self.event_GainC14)

    self.tabWidget.currentChanged['int'].connect(self.event_Tabs)

    self.pushButtonSettingWrite.clicked.connect(self.event_SettingWrite)
    self.pushButtonSettingDefault.clicked.connect(self.event_SettingDefault)
    
    self.pushButtonXYplotStart.clicked.connect(self.start_xyplot)
    self.pushButtonXYplotStop.clicked.connect(self.stop_xyplot)
    
    #self.lineEditSampling.setText(str(self.setting.SAMPLING))
    #self.lineEditWindow.setText(str(self.setting.WINDOW))
    self.lineEditSampling.textChanged['QString'].connect(self.event_SamplingChanged)
    self.lineEditWindow.textChanged['QString'].connect(self.event_WindowChanged)

    # Graph-1
    self.pushButton_Graph1.clicked.connect(self.event_Graph1)
    self.pushButton_Graph2.clicked.connect(self.event_Graph2)
    self.pushButton_Graph3.clicked.connect(self.event_Graph3)
    self.pushButton_Graph4.clicked.connect(self.event_Graph4)
    # Graph-2
    self.pushButton_Graph5.clicked.connect(self.event_Graph5)
    self.pushButton_Graph6.clicked.connect(self.event_Graph6)
    self.pushButton_Graph7.clicked.connect(self.event_Graph7)
    self.pushButton_Graph8.clicked.connect(self.event_Graph8)
    # Graph-3
    self.pushButton_Graph9.clicked.connect(self.event_Graph9)
    self.pushButton_Graph10.clicked.connect(self.event_Graph10)
    self.pushButton_Graph11.clicked.connect(self.event_Graph11)
    self.pushButton_Graph12.clicked.connect(self.event_Graph12)
    # Graph-4
    self.pushButton_Graph13.clicked.connect(self.event_Graph13)
    self.pushButton_Graph14.clicked.connect(self.event_Graph14)
    self.pushButton_Graph15.clicked.connect(self.event_Graph15)
    self.pushButton_Graph16.clicked.connect(self.event_Graph16)
        
    # Time Plots - CheckBox
    self.checkBoxTC1.stateChanged['int'].connect(self.event_checkTC1)
    self.checkBoxTC2.stateChanged['int'].connect(self.event_checkTC2)
    self.checkBoxTC3.stateChanged['int'].connect(self.event_checkTC3)
    self.checkBoxTC4.stateChanged['int'].connect(self.event_checkTC4)
    self.checkBoxTC5.stateChanged['int'].connect(self.event_checkTC5)
    self.checkBoxTC6.stateChanged['int'].connect(self.event_checkTC6)
    self.checkBoxTC7.stateChanged['int'].connect(self.event_checkTC7)
    self.checkBoxTC8.stateChanged['int'].connect(self.event_checkTC8)
    self.checkBoxTC9.stateChanged['int'].connect(self.event_checkTC9)
    self.checkBoxTC10.stateChanged['int'].connect(self.event_checkTC10)
    self.checkBoxTC11.stateChanged['int'].connect(self.event_checkTC11)
    self.checkBoxTC12.stateChanged['int'].connect(self.event_checkTC12)
    self.checkBoxTC13.stateChanged['int'].connect(self.event_checkTC13)
    self.checkBoxTC14.stateChanged['int'].connect(self.event_checkTC14)
    # Time Plots - Label Click
    self.labelTC1.mousePressEvent = self.event_labelTC1
    self.labelTC2.mousePressEvent = self.event_labelTC2
    self.labelTC3.mousePressEvent = self.event_labelTC3
    self.labelTC4.mousePressEvent = self.event_labelTC4
    self.labelTC5.mousePressEvent = self.event_labelTC5
    self.labelTC6.mousePressEvent = self.event_labelTC6
    self.labelTC7.mousePressEvent = self.event_labelTC7
    self.labelTC8.mousePressEvent = self.event_labelTC8
    self.labelTC9.mousePressEvent = self.event_labelTC9
    self.labelTC10.mousePressEvent = self.event_labelTC10
    self.labelTC11.mousePressEvent = self.event_labelTC11
    self.labelTC12.mousePressEvent = self.event_labelTC12
    self.labelTC13.mousePressEvent = self.event_labelTC13
    self.labelTC14.mousePressEvent = self.event_labelTC14
    # Time Plots - LineEdit Change
    self.lineEditTC1.textChanged['QString'].connect(self.event_lineEditTC1)
    self.lineEditTC2.textChanged['QString'].connect(self.event_lineEditTC2)
    self.lineEditTC3.textChanged['QString'].connect(self.event_lineEditTC3)
    self.lineEditTC4.textChanged['QString'].connect(self.event_lineEditTC4)
    self.lineEditTC5.textChanged['QString'].connect(self.event_lineEditTC5)
    self.lineEditTC6.textChanged['QString'].connect(self.event_lineEditTC6)
    self.lineEditTC7.textChanged['QString'].connect(self.event_lineEditTC7)
    self.lineEditTC8.textChanged['QString'].connect(self.event_lineEditTC8)
    self.lineEditTC9.textChanged['QString'].connect(self.event_lineEditTC9)
    self.lineEditTC10.textChanged['QString'].connect(self.event_lineEditTC10)
    self.lineEditTC11.textChanged['QString'].connect(self.event_lineEditTC11)
    self.lineEditTC12.textChanged['QString'].connect(self.event_lineEditTC12)
    self.lineEditTC13.textChanged['QString'].connect(self.event_lineEditTC13)
    self.lineEditTC14.textChanged['QString'].connect(self.event_lineEditTC14)

    # XYplotDialog
    self.xyplotDialog = XYplotDialog()
    self.xyplotDialog.comboBoxX.addItems(self.setting.ALIAS)
    self.xyplotDialog.comboBoxY.addItems(self.setting.ALIAS)
    self.xyplotDialog.buttonBox.accepted.connect(self.xyplotDialogReturnOK)

    # XYplot - GraphicsLayout
    self.xyplotpg = pg.GraphicsLayoutWidget()
    self.xyplotpg.setBackground('b')

    self.xyplotItem1 = self.xyplotpg.addPlot(0,0)
    self.xyplotItem2 = self.xyplotpg.addPlot(0,1)
    self.xyplotItem3 = self.xyplotpg.addPlot(1,0)
    self.xyplotItem4 = self.xyplotpg.addPlot(1,1)

    #self.xyplotItem1.disableAutoRange()
    #self.xyplotItem2.disableAutoRange()
    #self.xyplotItem3.disableAutoRange()
    #self.xyplotItem4.disableAutoRange()

    self.TplotItem = pg.PlotWidget()
    self.TplotItem.setBackground('w')
    
    self.xyplot_ref = None
    self.Tplot_ref = None
    self.updateSetting()

    # Menu Items
    self.actionNewSession.triggered.connect(self.event_NewSession)
    self.actionSettings.triggered.connect(self.event_MenuSettings)
    self.actionTimePlot.triggered.connect(self.event_TimePlot)
    
    # File Setting
    self.FILE = False

    self.st = time.time()

    self.interval = 30
    self.timer = QtCore.QTimer()
    self.timer.setInterval(self.interval)
    self.timer.timeout.connect(self.update_plot)
    self.timer.start()

  def event_GainC1(self,value):
    print(value)

  def event_GainC2(self,value):
    print(value)

  def event_GainC3(self,value):
    print(value)

  def event_GainC4(self,value):
    print(value)

  def event_GainC5(self,value):
    print(value)

  def event_GainC6(self,value):
    print(value)

  def event_GainC7(self,value):
    print(value)

  def event_GainC8(self,value):
    print(value)

  def event_GainC9(self,value):
    print(value)

  def event_GainC10(self,value):
    print(value)

  def event_GainC11(self,value):
    print(value)

  def event_GainC12(self,value):
    print(value)

  def event_GainC13(self,value):
    print(value)

  def event_GainC14(self,value):
    print(value)

  def event_SamplingChanged(self,value):
    self.setting.setSampling(int(value))

  def event_WindowChanged(self,value):
    self.setting.setWindow(int(value))

  # Graph-1
  def event_Graph1(self):
    self.xyplotDialog.labelTitle.setText('Graph-1')
    self.xyplotDialog.labelGraphIndex.setText('0')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[0]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[0]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[0]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[0]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[0])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[0])
    self.xyplotDialog.exec()

  def event_Graph2(self):
    self.xyplotDialog.labelTitle.setText('Graph-2')
    self.xyplotDialog.labelGraphIndex.setText('1')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[1]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[1]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[1]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[1]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[1])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[1])
    self.xyplotDialog.exec()

  def event_Graph3(self):
    self.xyplotDialog.labelTitle.setText('Graph-3')
    self.xyplotDialog.labelGraphIndex.setText('2')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[2]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[2]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[2]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[2]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[2])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[2])
    self.xyplotDialog.exec()

  def event_Graph4(self):
    self.xyplotDialog.labelTitle.setText('Graph-4')
    self.xyplotDialog.labelGraphIndex.setText('3')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[3]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[3]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[3]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[3]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[3])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[3])
    self.xyplotDialog.exec()

  # Graph-2
  def event_Graph5(self):
    self.xyplotDialog.labelTitle.setText('Graph-5')
    self.xyplotDialog.labelGraphIndex.setText('4')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[4]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[4]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[4]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[4]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[4])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[4])
    self.xyplotDialog.exec()

  def event_Graph6(self):
    self.xyplotDialog.labelTitle.setText('Graph-6')
    self.xyplotDialog.labelGraphIndex.setText('5')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[5]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[5]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[5]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[5]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[5])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[5])
    self.xyplotDialog.exec()

  def event_Graph7(self):
    self.xyplotDialog.labelTitle.setText('Graph-7')
    self.xyplotDialog.labelGraphIndex.setText('6')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[6]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[6]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[6]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[6]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[6])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[6])
    self.xyplotDialog.exec()

  def event_Graph8(self):
    self.xyplotDialog.labelTitle.setText('Graph-8')
    self.xyplotDialog.labelGraphIndex.setText('7')
    self.xyplotDialog.labelGraphIndex.setHidden(True)
    self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[7]))
    self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[7]))
    self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[7]))
    self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[7]))
    self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[7])
    self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[7])
    self.xyplotDialog.exec()

  # Graph-3
  def event_Graph9(self,value):
    self.setting.setXYplotItem3X(value)

  def event_Graph10(self,value):
    self.setting.setXYplotItem3Y(value)

  def event_Graph11(self,value):
    self.setting.setXYplotItem3Xmin(float(value))

  def event_Graph12(self,value):
    self.setting.setXYplotItem3Xmax(float(value))

  # Graph-4
  def event_Graph13(self,value):
    self.setting.setXYplotItem4X(value)

  def event_Graph14(self,value):
    self.setting.setXYplotItem4Y(value)

  def event_Graph15(self):
    self.setting.setXYplotItem4Xmin(float(value))

  def event_Graph16(self):
    self.setting.setXYplotItem4Xmax(float(value))

  # Time Plot - CheckBox Events
  def event_checkTC1(self,value):
    self.setting.setTimePlotEnable(0,value)

  def event_checkTC2(self,value):
    self.setting.setTimePlotEnable(1,value)

  def event_checkTC3(self,value):
    self.setting.setTimePlotEnable(2,value)

  def event_checkTC4(self,value):
    self.setting.setTimePlotEnable(3,value)

  def event_checkTC5(self,value):
    self.setting.setTimePlotEnable(4,value)

  def event_checkTC6(self,value):
    self.setting.setTimePlotEnable(5,value)

  def event_checkTC7(self,value):
    self.setting.setTimePlotEnable(6,value)

  def event_checkTC8(self,value):
    self.setting.setTimePlotEnable(7,value)

  def event_checkTC9(self,value):
    self.setting.setTimePlotEnable(8,value)

  def event_checkTC10(self,value):
    self.setting.setTimePlotEnable(9,value)

  def event_checkTC11(self,value):
    self.setting.setTimePlotEnable(10,value)

  def event_checkTC12(self,value):
    self.setting.setTimePlotEnable(11,value)

  def event_checkTC13(self,value):
    self.setting.setTimePlotEnable(12,value)

  def event_checkTC14(self,value):
    self.setting.setTimePlotEnable(13,value)

  # Time Plot - Label Events
  def event_labelTC1(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(0, color_hex)

  def event_labelTC2(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(1, color_hex)

  def event_labelTC3(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(2, color_hex)

  def event_labelTC4(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(3, color_hex)

  def event_labelTC5(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(4, color_hex)

  def event_labelTC6(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(5, color_hex)

  def event_labelTC7(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(6, color_hex)

  def event_labelTC8(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(7, color_hex)

  def event_labelTC9(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(8, color_hex)

  def event_labelTC10(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(9, color_hex)

  def event_labelTC11(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(10, color_hex)

  def event_labelTC12(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(11, color_hex)

  def event_labelTC13(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(12, color_hex)

  def event_labelTC14(self, event):
    color = QtWidgets.QColorDialog.getColor()
    color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(color.getRgb()[2], '02x')
    self.setting.setTimePlotColor(13, color_hex)

  # Time Plots - LineEdit Events
  def event_lineEditTC1(self,value):
    self.setting.setTimePlotOffset(0, float(value))

  def event_lineEditTC2(self,value):
    self.setting.setTimePlotOffset(1, float(value))

  def event_lineEditTC3(self,value):
    self.setting.setTimePlotOffset(2, float(value))

  def event_lineEditTC4(self,value):
    self.setting.setTimePlotOffset(3, float(value))

  def event_lineEditTC5(self,value):
    self.setting.setTimePlotOffset(4, float(value))

  def event_lineEditTC6(self,value):
    self.setting.setTimePlotOffset(5, float(value))

  def event_lineEditTC7(self,value):
    self.setting.setTimePlotOffset(6, float(value))

  def event_lineEditTC8(self,value):
    self.setting.setTimePlotOffset(7, float(value))

  def event_lineEditTC9(self,value):
    self.setting.setTimePlotOffset(8, float(value))

  def event_lineEditTC10(self,value):
    self.setting.setTimePlotOffset(9, float(value))

  def event_lineEditTC11(self,value):
    self.setting.setTimePlotOffset(10, float(value))

  def event_lineEditTC12(self,value):
    self.setting.setTimePlotOffset(11, float(value))

  def event_lineEditTC13(self,value):
    self.setting.setTimePlotOffset(12, float(value))

  def event_lineEditTC14(self,value):
    self.setting.setTimePlotOffset(13, float(value))


  def event_Tabs(self,value):
    if value == 1:
      self.XYplotUI()
    elif value == 2:
      self.TplotUI()

  def event_NewSession(self, test):
    if self.FILE == False:
      self.FILE = True
      self.stackedWidget.setCurrentIndex(1)

  def event_MenuSettings(self):
    if self.FILE == True and self.STREAM == False:
      self.stackedWidget.setCurrentIndex(1)

  def event_TimePlot(self):
    if self.FILE == True:
      self.stackedWidget.setCurrentIndex(2)


  def XYplotUI(self):
    # Graph-1
    xyplotItem1LabelX = self.setting.ALIAS[self.setting.XYPLOT_X[0]]
    xyplotItem1LabelY = self.setting.ALIAS[self.setting.XYPLOT_Y[0]]
    self.xyplotItem1.setLabels(title='Graph-1', bottom=xyplotItem1LabelX, left=xyplotItem1LabelY)
    self.xyplotItem1.setXRange(min=self.setting.XYPLOT_XMIN[0], max=self.setting.XYPLOT_XMAX[0])
    self.xyplotItem1.setYRange(min=self.setting.XYPLOT_YMIN[0], max=self.setting.XYPLOT_YMAX[0])
    # Graph-2
    xyplotItem2LabelX = self.setting.ALIAS[self.setting.XYPLOT_X[1]]
    xyplotItem2LabelY = self.setting.ALIAS[self.setting.XYPLOT_Y[1]]
    self.xyplotItem2.setLabels(title='Graph-2', bottom=xyplotItem2LabelX, left=xyplotItem2LabelY)
    self.xyplotItem2.setXRange(min=self.setting.XYPLOT_XMIN[1], max=self.setting.XYPLOT_XMAX[1])
    self.xyplotItem2.setYRange(min=self.setting.XYPLOT_YMIN[1], max=self.setting.XYPLOT_YMAX[1])
    # Graph-3
    xyplotItem3LabelX = self.setting.ALIAS[self.setting.XYPLOT_X[2]]
    xyplotItem3LabelY = self.setting.ALIAS[self.setting.XYPLOT_Y[2]]
    self.xyplotItem3.setLabels(title='Graph-3', bottom=xyplotItem3LabelX, left=xyplotItem3LabelY)
    self.xyplotItem3.setXRange(min=self.setting.XYPLOT_XMIN[2], max=self.setting.XYPLOT_XMAX[2])
    self.xyplotItem3.setYRange(min=self.setting.XYPLOT_YMIN[2], max=self.setting.XYPLOT_YMAX[2])
    # Graph-4
    xyplotItem4LabelX = self.setting.ALIAS[self.setting.XYPLOT_X[3]]
    xyplotItem4LabelY = self.setting.ALIAS[self.setting.XYPLOT_Y[3]]
    self.xyplotItem4.setLabels(title='Graph-4', bottom=xyplotItem4LabelX, left=xyplotItem4LabelY)
    self.xyplotItem4.setXRange(min=self.setting.XYPLOT_XMIN[3], max=self.setting.XYPLOT_XMAX[3])
    self.xyplotItem4.setYRange(min=self.setting.XYPLOT_YMIN[3], max=self.setting.XYPLOT_YMAX[3])

    self.verticalLayoutXYplot.addWidget(self.xyplotpg) # CHECK - MULTIPLE

  def TplotUI(self):
    self.verticalLayoutTplot.addWidget(self.TplotItem) # CHECK - MULTIPLE
    for i in range(self.setting.CHANNEL):
      label_name = getattr(self, "labelTC%d" % (i+1))
      label_name.setText(self.setting.ALIAS[i])
      checkBox_name = getattr(self, "checkBoxTC%d" % (i+1))
      if self.setting.timePlotEnable[i] == None:
        checkBox_name.setChecked(False)
      else:
        checkBox_name.setChecked(True)

  def stop_xyplot(self):
    self.STREAM = False
    #ljm.eStreamStop(self.labjack.handle)

  def xyplotDialogReturnOK(self):
    graphIndex = int(self.xyplotDialog.labelGraphIndex.text())
    x = self.xyplotDialog.comboBoxX.currentIndex()
    y = self.xyplotDialog.comboBoxY.currentIndex()
    xmin = float(self.xyplotDialog.lineEditXmin.text())
    xmax = float(self.xyplotDialog.lineEditXmax.text())
    ymin = float(self.xyplotDialog.lineEditYmin.text())
    ymax = float(self.xyplotDialog.lineEditYmax.text())

    self.setting.setXYplotX(x, graphIndex)
    self.setting.setXYplotY(y, graphIndex)
    self.setting.setXYplotXmin(xmin, graphIndex)
    self.setting.setXYplotXmax(xmax, graphIndex)
    self.setting.setXYplotYmin(ymin, graphIndex)
    self.setting.setXYplotYmax(ymax, graphIndex)

  def start_xyplot(self):
    self.STREAM = True
    self.plotdata =  np.zeros((self.setting.WINDOW,self.setting.CHANNEL))
    self.worker = Worker(self.stream_xyplot, )
    self.threadpool.start(self.worker)

  def stream_xyplot(self):
    self.getStream()

  def getStream(self):
    scanRate = self.setting.SAMPLING
    scansPerRead = int(scanRate / 20)
    numAddresses = self.setting.CHANNEL
    scanList = ljm.namesToAddresses(numAddresses, self.labjack.AIN_NAMES)[0]
    try:
      def myStreamReadCallback(arg):
        st = time.time()
        ret = ljm.eStreamRead(self.labjack.handle)
        result = ret[0]
        #print("Device %d" % ret[1])    #deviceScanBacklog
        #print("Ljm Lib %d" % ret[2])    #ljmScanBackLog
        #print(len(result))
        #print("-------------------")
        x = np.column_stack((result[::14], result[1::14], result[2::14], result[3::14], result[4::14], result[5::14], result[6::14], result[7::14], result[8::14], result[9::14], result[10::14], result[11::14], result[12::14], result[13::14]))
        #x = x.reshape(-1, 10, 14).mean(1)
        self.q.put(x)
        if not self.STREAM:
          ljm.eStreamStop(self.labjack.handle)
      stream = ljm.eStreamStart(self.labjack.handle, scansPerRead, numAddresses, scanList, scanRate)
      ljm.setStreamCallback(self.labjack.handle, myStreamReadCallback)
      while self.STREAM:
        time.sleep(0.01)
    except ljm.LJMError as e:
      print("ERROR: ",e)

  def update_plot(self):
    #print(self.threadpool.activeThreadCount())
    try:
      data=[0]
      plot_type = self.tabWidget.currentIndex()
      while True:
        try:
          data = self.q.get_nowait()
        except queue.Empty:
          break

        shift = len(data)
        self.plotdata = np.roll(self.plotdata, -shift,axis = 0)
        self.plotdata[-shift:,:] = data
        
        if plot_type == 1:
            self.xyplot1DataX = self.plotdata[:,self.setting.XYPLOT_X[0]]
            self.xyplot1DataY = self.plotdata[:,self.setting.XYPLOT_Y[0]]
            self.xyplot2DataX = self.plotdata[:,self.setting.XYPLOT_X[1]]
            self.xyplot2DataY = self.plotdata[:,self.setting.XYPLOT_Y[1]]
            self.xyplot3DataX = self.plotdata[:,self.setting.XYPLOT_X[2]]
            self.xyplot3DataY = self.plotdata[:,self.setting.XYPLOT_Y[2]]
            self.xyplot4DataX = self.plotdata[:,self.setting.XYPLOT_X[3]]
            self.xyplot4DataY = self.plotdata[:,self.setting.XYPLOT_Y[3]]

            if self.xyplot_ref is None:
              self.xyplot_ref = True
              self.xyplotLineRef1 = self.xyplotItem1.plot(self.xyplot1DataX, self.xyplot1DataY)
              self.xyplotLineRef2 = self.xyplotItem2.plot(self.xyplot2DataX, self.xyplot2DataY)
              self.xyplotLineRef3 = self.xyplotItem3.plot(self.xyplot3DataX, self.xyplot3DataY)
              self.xyplotLineRef4 = self.xyplotItem4.plot(self.xyplot4DataX, self.xyplot4DataY)
            else:
              self.xyplotLineRef1.setData(self.xyplot1DataX, self.xyplot1DataY)
              self.xyplotLineRef2.setData(self.xyplot2DataX, self.xyplot2DataY)
              self.xyplotLineRef3.setData(self.xyplot3DataX, self.xyplot3DataY)
              self.xyplotLineRef4.setData(self.xyplot4DataX, self.xyplot4DataY)
        elif plot_type == 2:
            self.TplotData1 = self.plotdata[:,0]
            self.TplotData2 = self.plotdata[:,1]
            self.TplotData3 = self.plotdata[:,2]
            self.TplotData4 = self.plotdata[:,3]
            self.TplotData5 = self.plotdata[:,4]
            self.TplotData6 = self.plotdata[:,5]
            self.TplotData7 = self.plotdata[:,6]
            self.TplotData8 = self.plotdata[:,7]
            self.TplotData9 = self.plotdata[:,8]
            self.TplotData10 = self.plotdata[:,9]
            self.TplotData11 = self.plotdata[:,10]
            self.TplotData12 = self.plotdata[:,11]
            self.TplotData13 = self.plotdata[:,12]
            self.TplotData14 = self.plotdata[:,13]
            
            self.TplotData1[-shift:] = self.TplotData1[-shift:] + self.setting.timePlotOffset[0]
            self.TplotData2[-shift:] = self.TplotData2[-shift:] + self.setting.timePlotOffset[1]
            self.TplotData3[-shift:] = self.TplotData3[-shift:] + self.setting.timePlotOffset[2]
            self.TplotData4[-shift:] = self.TplotData4[-shift:] + self.setting.timePlotOffset[3]
            self.TplotData5[-shift:] = self.TplotData5[-shift:] + self.setting.timePlotOffset[4]
            self.TplotData6[-shift:] = self.TplotData6[-shift:] + self.setting.timePlotOffset[5]
            self.TplotData7[-shift:] = self.TplotData7[-shift:] + self.setting.timePlotOffset[6]
            self.TplotData8[-shift:] = self.TplotData8[-shift:] + self.setting.timePlotOffset[7]
            self.TplotData9[-shift:] = self.TplotData9[-shift:] + self.setting.timePlotOffset[8]
            self.TplotData10[-shift:] = self.TplotData10[-shift:] + self.setting.timePlotOffset[9]
            self.TplotData11[-shift:] = self.TplotData11[-shift:] + self.setting.timePlotOffset[10]
            self.TplotData12[-shift:] = self.TplotData12[-shift:] + self.setting.timePlotOffset[11]
            self.TplotData13[-shift:] = self.TplotData13[-shift:] + self.setting.timePlotOffset[12]
            self.TplotData14[-shift:] = self.TplotData14[-shift:] + self.setting.timePlotOffset[13]

            if self.Tplot_ref is None:
                self.Tplot_ref = True
                self.TplotLineRef1 = self.TplotItem.plot()
                self.TplotLineRef2 = self.TplotItem.plot()
                self.TplotLineRef3 = self.TplotItem.plot()
                self.TplotLineRef4 = self.TplotItem.plot()
                self.TplotLineRef5 = self.TplotItem.plot()
                self.TplotLineRef6 = self.TplotItem.plot()
                self.TplotLineRef7 = self.TplotItem.plot()
                self.TplotLineRef8 = self.TplotItem.plot()
                self.TplotLineRef9 = self.TplotItem.plot()
                self.TplotLineRef10 = self.TplotItem.plot()
                self.TplotLineRef11 = self.TplotItem.plot()
                self.TplotLineRef12 = self.TplotItem.plot()
                self.TplotLineRef13 = self.TplotItem.plot()
                self.TplotLineRef14 = self.TplotItem.plot()
            else:
                self.TplotLineRef1.setData(self.TplotData1, pen=self.setting.timePlotEnable[0])
                self.TplotLineRef2.setData(self.TplotData2, pen=self.setting.timePlotEnable[1])
                self.TplotLineRef3.setData(self.TplotData3, pen=self.setting.timePlotEnable[2])
                self.TplotLineRef4.setData(self.TplotData4, pen=self.setting.timePlotEnable[3])
                self.TplotLineRef5.setData(self.TplotData5, pen=self.setting.timePlotEnable[4])
                self.TplotLineRef6.setData(self.TplotData6, pen=self.setting.timePlotEnable[5])
                self.TplotLineRef7.setData(self.TplotData7, pen=self.setting.timePlotEnable[6])
                self.TplotLineRef8.setData(self.TplotData8, pen=self.setting.timePlotEnable[7])
                self.TplotLineRef9.setData(self.TplotData9, pen=self.setting.timePlotEnable[8])
                self.TplotLineRef10.setData(self.TplotData10, pen=self.setting.timePlotEnable[9])
                self.TplotLineRef11.setData(self.TplotData11, pen=self.setting.timePlotEnable[10])
                self.TplotLineRef12.setData(self.TplotData12, pen=self.setting.timePlotEnable[11])
                self.TplotLineRef13.setData(self.TplotData13, pen=self.setting.timePlotEnable[12])
                self.TplotLineRef14.setData(self.TplotData14, pen=self.setting.timePlotEnable[13])
    except:
      pass


  def event_SettingWrite(self):
    gains = []
    alias = []
    sampling = self.lineEditSampling.text()
    window = self.lineEditWindow.text()

    for i in range(self.setting.CHANNEL):
      comboWidget_name = getattr(self, "comboBoxGainC%d" % (i+1))
      gains.append(comboWidget_name.currentIndex())
      lineWidget_name = getattr(self, "lineEditAliasC%d" % (i+1))
      alias.append(lineWidget_name.text())

    self.setting.setValues(gains,alias,sampling,window)
    self.labjack.writeGain(self.setting.GAINS)

  def event_SettingDefault(self):
    self.setting.setDefault()
    for i in range(self.setting.CHANNEL):
      comboWidget_name = getattr(self, "comboBoxGainC%d" % (i+1))
      comboWidget_name.setCurrentIndex(self.setting.GAINS[i])
      lineWidget_name = getattr(self, "lineEditAliasC%d" % (i+1))
      lineWidget_name.setText(self.setting.ALIAS[i])
      self.lineEditSampling.setText(str(self.setting.SAMPLING))
      self.lineEditWindow.setText(str(self.setting.WINDOW))

  def updateSetting(self):
    for i in range(self.setting.CHANNEL):
      comboWidget_name = getattr(self, "comboBoxGainC%d" % (i+1))
      comboWidget_name.setCurrentIndex(self.setting.GAINS[i])
      lineWidget_name = getattr(self, "lineEditAliasC%d" % (i+1))
      lineWidget_name.setText(self.setting.ALIAS[i])

    self.lineEditSampling.setText(str(self.setting.SAMPLING))
    self.lineEditWindow.setText(str(self.setting.WINDOW))

    '''
    for i in range(4):
      comboBoxXYplotItemX = getattr(self, "comboBoxXYplotItem%dX" % (i+1))
      comboBoxXYplotItemY = getattr(self, "comboBoxXYplotItem%dY" % (i+1))
      lineEditXYplotItemXmin = getattr(self, "lineEditXYplotItem%dXmin" % (i+1))
      lineEditXYplotItemXmax = getattr(self, "lineEditXYplotItem%dXmax" % (i+1))
      lineEditXYplotItemYmin = getattr(self, "lineEditXYplotItem%dYmin" % (i+1))
      lineEditXYplotItemYmax = getattr(self, "lineEditXYplotItem%dYmax" % (i+1))
      comboBoxXYplotItemX.setCurrentIndex(getattr(self.setting, "XYPLOTITEM%dX" % (i+1)))
      comboBoxXYplotItemY.setCurrentIndex(getattr(self.setting, "XYPLOTITEM%dY" % (i+1)))
      lineEditXYplotItemXmin.setText(str(getattr(self.setting, "XYPLOTITEM%dXMIN" % (i+1))))
      lineEditXYplotItemXmax.setText(str(getattr(self.setting, "XYPLOTITEM%dXMAX" % (i+1))))
      lineEditXYplotItemYmin.setText(str(getattr(self.setting, "XYPLOTITEM%dYMIN" % (i+1))))
      lineEditXYplotItemYmax.setText(str(getattr(self.setting, "XYPLOTITEM%dYMAX" % (i+1))))
    '''


class Setting:
  def __init__(self):
    self.GAINS = []
    self.ALIAS = []
    self.SAMPLING = 0
    self.WINDOW = 0
    self.CHANNEL = 14
    self.XYPLOTITEM1X = 0
    self.XYPLOTITEM1Y = 0
    self.XYPLOTITEM1XMIN = 0
    self.XYPLOTITEM1XMAX = 0
    self.XYPLOTITEM1YMIN = 0
    self.XYPLOTITEM1YMAX = 0
    self.XYPLOTITEM2X = 0
    self.XYPLOTITEM2Y = 0
    self.XYPLOTITEM2XMIN = 0
    self.XYPLOTITEM2XMAX = 0
    self.XYPLOTITEM2YMIN = 0
    self.XYPLOTITEM2YMAX = 0
    self.XYPLOTITEM3X = 0
    self.XYPLOTITEM3Y = 0
    self.XYPLOTITEM3XMIN = 0
    self.XYPLOTITEM3XMAX = 0
    self.XYPLOTITEM3YMIN = 0
    self.XYPLOTITEM3YMAX = 0
    self.XYPLOTITEM4X = 0
    self.XYPLOTITEM4Y = 0
    self.XYPLOTITEM4XMIN = 0
    self.XYPLOTITEM4XMAX = 0
    self.XYPLOTITEM4YMIN = 0
    self.XYPLOTITEM4YMAX = 0
    self.XYPLOT_X = []
    self.XYPLOT_Y = []
    self.XYPLOT_XMIN = []
    self.XYPLOT_XMAX = []
    self.XYPLOT_YMIN = []
    self.XYPLOT_YMAX = []
    self.setDefault() # Remove LATER
    self.timePlotColors = ['#000', '#F00', '#0F0', '#00F', '#FF0', '#0FF', '#F0F', '#500', '#050', '#005', '#550', '#055', '#505', '#555']
    self.timePlotEnable = ['#000', '#F00', '#0F0', '#00F', '#FF0', '#0FF', '#F0F', '#500', '#050', '#005', '#550', '#055', '#505', '#555']
    self.timePlotOffset = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

  def setDefault(self):
    self.GAINS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #index to "self.gains". Not Actual values
    self.ALIAS = ['Channel 01', 'Channel 02', 'Channel 03', 'Channel 04', 'Channel 05', 'Channel 06', 'Channel 07', 'Channel 08', 'Channel 09', 'Channel 10', 'Channel 11', 'Channel 12', 'Channel 13', 'Channel 14']
    self.SAMPLING = 100
    self.WINDOW = 1000
    self.CHANNEL = 14
    self.XYPLOTITEM1X = 0
    self.XYPLOTITEM1Y = 1
    self.XYPLOTITEM1XMIN = -1
    self.XYPLOTITEM1XMAX = 1
    self.XYPLOTITEM1YMIN = -10
    self.XYPLOTITEM1YMAX = 10
    self.XYPLOTITEM2X = 2
    self.XYPLOTITEM2Y = 3
    self.XYPLOTITEM2XMIN = -2
    self.XYPLOTITEM2XMAX = 2
    self.XYPLOTITEM2YMIN = -20
    self.XYPLOTITEM2YMAX = 20
    self.XYPLOTITEM3X = 4
    self.XYPLOTITEM3Y = 5
    self.XYPLOTITEM3XMIN = -3
    self.XYPLOTITEM3XMAX = 3
    self.XYPLOTITEM3YMIN = -30
    self.XYPLOTITEM3YMAX = 30
    self.XYPLOTITEM4X = 6
    self.XYPLOTITEM4Y = 7
    self.XYPLOTITEM4XMIN = -4
    self.XYPLOTITEM4XMAX = 4
    self.XYPLOTITEM4YMIN = -40
    self.XYPLOTITEM4YMAX = 40
    self.XYPLOT_X = [0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #index to "self.setting.ALIAS-CHANNEL Number 0..". Not Actual values
    self.XYPLOT_Y = [10, 11, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #index to "self.setting.ALIAS-CHANNEL Number 0..". Not Actual values
    self.XYPLOT_XMIN = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]
    self.XYPLOT_XMAX = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    self.XYPLOT_YMIN = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]
    self.XYPLOT_YMAX = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

  def setValues(self,gains,alias,sampling,window):
    self.GAINS = gains
    self.ALIAS = alias
    self.SAMPLING = sampling
    self.WINDOW = window

  def setSampling(self, sampling):
    self.SAMPLING = sampling

  def setWindow(self, window):
    self.WINDOW = window

  # XYlot - X/Y min/max
  def setXYplotX(self, channel, graph):
    self.XYPLOT_X[graph] = channel

  def setXYplotY(self, channel, graph):
    self.XYPLOT_Y[graph] = channel

  def setXYplotXmin(self, min_value, graph):
    self.XYPLOT_XMIN[graph] = min_value

  def setXYplotXmax(self, max_value, graph):
    self.XYPLOT_XMAX[graph] = max_value

  def setXYplotYmin(self, min_value, graph):
    self.XYPLOT_YMIN[graph] = min_value

  def setXYplotYmax(self, max_value, graph):
    self.XYPLOT_YMAX[graph] = max_value
  
  # Time Plot - Enable
  def setTimePlotEnable(self, channel, chk):
    if chk == 0:
      self.timePlotEnable[channel] = None
    elif chk == 2:
      self.timePlotEnable[channel] = self.timePlotColors[channel]

  # Time Plot - Colors
  def setTimePlotColor(self, channel, value):
    self.timePlotColors[channel] = value
    if self.timePlotEnable[channel] != None:
      self.timePlotEnable[channel] = self.timePlotColors[channel]

  # Time Plot - Offset
  def setTimePlotOffset(self, channel, value):
    self.timePlotOffset[channel] = value
    #print("Channel:%d Value:%f" %(channel, value))


class Labjack:
  def __init__(self):
    self.RANGE_NAMES = ["AIN0_RANGE", "AIN1_RANGE", "AIN2_RANGE", "AIN3_RANGE", "AIN4_RANGE", "AIN5_RANGE", "AIN6_RANGE", "AIN7_RANGE", "AIN8_RANGE", "AIN9_RANGE", "AIN10_RANGE", "AIN11_RANGE", "AIN12_RANGE", "AIN13_RANGE"]
    self.RANGE_VALUES = [10.0, 1.0, 0.1, 0.01] # Map to "self.gains". Actual values
    self.AIN_NAMES = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6", "AIN7", "AIN8", "AIN9", "AIN10", "AIN11", "AIN12", "AIN13"]

    self.handle = ljm.openS("ANY", "ANY", "ANY")
    self.info = ljm.getHandleInfo(self.handle)
    print(self.info)

  def writeGain(self,gainIndex):
    gainIndex_range = []
    numNames = len(self.RANGE_NAMES)
    [gainIndex_range.append(self.RANGE_VALUES[i]) for i in gainIndex]
    ljm.eWriteNames(self.handle, numNames, self.RANGE_NAMES, gainIndex_range)
    print("Wrote Gains")

  def readGain(self):
    ranges = []
    numNames = len(self.RANGE_NAMES)
    results = ljm.eReadNames(self.handle, numNames, self.RANGE_NAMES)
    [ranges.append(round(i,2)) for i in results]
    print(ranges)

class Worker(QtCore.QRunnable):
  def __init__(self, function, *args, **kwargs):
    super(Worker, self).__init__()
    self.function = function
    self.args = args
    self.kwargs = kwargs

  @pyqtSlot()
  def run(self):
    self.function(*self.args, **self.kwargs)

class XYplotDialog(QtWidgets.QDialog):
  def __init__(self):
    super().__init__()
    uic.loadUi('plot_dlg.ui', self)
    #print(dir(self.buttonBox.accepted))

class PlotItem(pg.PlotItem):
  def __init__(self, *args, **kwargs):
    pg.PlotItem.__init__(self, *args, **kwargs)

  def mouseDoubleClickEvent(self, e):
    print(self.getLabel('title'))


app = QtWidgets.QApplication(sys.argv)
setting = Setting()
labjack = Labjack()
labjack .readGain()
window = PLOT(setting,labjack)
window.show()
sys.exit(app.exec_())