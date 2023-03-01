import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
#from labjack import ljm
import u3
import pyqtgraph as pg
import numpy as np
import queue
import time
import scipy.signal
import serial.tools.list_ports
import pandas as pd

d = u3.U3()


d.streamConfig(NumChannels=1, SamplesPerPacket=25, ScanFrequency=1000)

try:
    d.streamStart()

except:
    d.streamStop()
    d.streamStart()

class PLOT(QtWidgets.QMainWindow):
    def __init__(self, setting, labjack):
        QtWidgets.QMainWindow.__init__(self)

        self.setting = setting
        self.labjack = labjack

        uic.loadUi('images/tab.ui', self)

        self.gains = ['1', '10', '100', '1000']
        self.threadpool = QtCore.QThreadPool()
        self.q = queue.Queue(maxsize=40)
        self.f = queue.Queue(maxsize=2)
        self.STREAM = False
        self.TEAR_AVG = None
        self.input_mean = None
        self.OFFLINE = False
        self.TEAR_FILE = False
        #self.FFT_DATA = np.zeros((self.setting.FFTbins,self.setting.CHANNEL))
        self.LOG_DATA = {}
        self.LOG_MAN = {}
        self.LOG_MAN_vel = {}
        self.LOG_MAN_acc = {}
        self.LOCALS_ZO = None
        self.LOCALS_vZO = None
        self.LOCALS_dZO = None

        # GAIN Combos
        self.comboBoxGainC1.addItems(self.gains)
        self.comboBoxGainC2.addItems(self.gains)
        self.comboBoxGainC3.addItems(self.gains)
        self.comboBoxGainC4.addItems(self.gains)
        self.comboBoxGainC5.addItems(self.gains)
        self.comboBoxGainC6.addItems(self.gains)
        self.comboBoxGainC7.addItems(self.gains)
        self.comboBoxGainC8.addItems(self.gains)
        # self.comboBoxGainC9.addItems(self.gains)
        # self.comboBoxGainC10.addItems(self.gains)
        # self.comboBoxGainC11.addItems(self.gains)
        # self.comboBoxGainC12.addItems(self.gains)
        # self.comboBoxGainC13.addItems(self.gains)
        # self.comboBoxGainC14.addItems(self.gains)
        self.comboBoxGainC1.currentIndexChanged['QString'].connect(self.event_GainC1)
        self.comboBoxGainC2.currentIndexChanged['QString'].connect(self.event_GainC2)
        self.comboBoxGainC3.currentIndexChanged['QString'].connect(self.event_GainC3)
        self.comboBoxGainC4.currentIndexChanged['QString'].connect(self.event_GainC4)
        self.comboBoxGainC5.currentIndexChanged['QString'].connect(self.event_GainC5)
        self.comboBoxGainC6.currentIndexChanged['QString'].connect(self.event_GainC6)
        self.comboBoxGainC7.currentIndexChanged['QString'].connect(self.event_GainC7)
        # self.comboBoxGainC8.currentIndexChanged['QString'].connect(self.event_GainC8)
        # self.comboBoxGainC9.currentIndexChanged['QString'].connect(self.event_GainC9)
        # self.comboBoxGainC10.currentIndexChanged['QString'].connect(self.event_GainC10)
        # self.comboBoxGainC11.currentIndexChanged['QString'].connect(self.event_GainC11)
        # self.comboBoxGainC12.currentIndexChanged['QString'].connect(self.event_GainC12)
        # self.comboBoxGainC13.currentIndexChanged['QString'].connect(self.event_GainC13)
        # self.comboBoxGainC14.currentIndexChanged['QString'].connect(self.event_GainC14)

        self.tabWidget.currentChanged['int'].connect(self.event_Tabs)

        # Setting - Write & Default
        self.pushButtonSettingWrite.clicked.connect(self.event_SettingWrite)
        self.pushButtonSettingDefault.clicked.connect(self.event_SettingDefault)
        # XY plot Color
        #self.pushButtonXYcolor.clicked.connect(self.event_SettingXYcolor)
        # XY Pen Color
        #self.pushButtonXYpen.clicked.connect(self.event_SettingXYpen)

        # PLOT - Start, Stop & TEAR
        self.pushButtonXYplotStart.clicked.connect(self.start_xyplot)
        self.pushButtonXYplotStop.clicked.connect(self.stop_xyplot)
        self.pushButtonTEAR.clicked.connect(self.tear_xyplot)

        # DAQ Setting
        self.lineEditSampling.textChanged['QString'].connect(self.event_SamplingChanged)
        self.lineEditWindow.textChanged['QString'].connect(self.event_WindowChanged)
        self.lineEditAvg.textChanged['QString'].connect(self.event_AvgChanged)
        self.lineEditSampling.editingFinished.connect(self.event_SamplingFinished)

        # Multiplier Setting
        self.lineEditMultiC1.textChanged['QString'].connect(self.event_MultiC1)
        self.lineEditMultiC2.textChanged['QString'].connect(self.event_MultiC2)
        self.lineEditMultiC3.textChanged['QString'].connect(self.event_MultiC3)
        self.lineEditMultiC4.textChanged['QString'].connect(self.event_MultiC4)
        self.lineEditMultiC5.textChanged['QString'].connect(self.event_MultiC5)
        self.lineEditMultiC6.textChanged['QString'].connect(self.event_MultiC6)
        self.lineEditMultiC7.textChanged['QString'].connect(self.event_MultiC7)
        self.lineEditMultiC8.textChanged['QString'].connect(self.event_MultiC8)
        # self.lineEditMultiC9.textChanged['QString'].connect(self.event_MultiC9)
        # self.lineEditMultiC10.textChanged['QString'].connect(self.event_MultiC10)
        # self.lineEditMultiC11.textChanged['QString'].connect(self.event_MultiC11)
        # self.lineEditMultiC12.textChanged['QString'].connect(self.event_MultiC12)
        # self.lineEditMultiC13.textChanged['QString'].connect(self.event_MultiC13)
        # self.lineEditMultiC14.textChanged['QString'].connect(self.event_MultiC14)

        # Graph-1
        # self.pushButton_Graph1.clicked.connect(self.event_Graph1)
        # self.pushButton_Graph2.clicked.connect(self.event_Graph2)
        # self.pushButton_Graph3.clicked.connect(self.event_Graph3)
        # self.pushButton_Graph4.clicked.connect(self.event_Graph4)
        # Graph-2
        # self.pushButton_Graph5.clicked.connect(self.event_Graph5)
        # self.pushButton_Graph6.clicked.connect(self.event_Graph6)
        # self.pushButton_Graph7.clicked.connect(self.event_Graph7)
        # self.pushButton_Graph8.clicked.connect(self.event_Graph8)
        # Graph-3
        # self.pushButton_Graph9.clicked.connect(self.event_Graph9)
        # self.pushButton_Graph10.clicked.connect(self.event_Graph10)
        # self.pushButton_Graph11.clicked.connect(self.event_Graph11)
        # self.pushButton_Graph12.clicked.connect(self.event_Graph12)
        # Graph-4
        # self.pushButton_Graph13.clicked.connect(self.event_Graph13)
        # self.pushButton_Graph14.clicked.connect(self.event_Graph14)
        # self.pushButton_Graph15.clicked.connect(self.event_Graph15)
        # self.pushButton_Graph16.clicked.connect(self.event_Graph16)

        # Time Plots - CheckBox
        self.checkBoxTC1.stateChanged['int'].connect(self.event_checkTC1)
        self.checkBoxTC2.stateChanged['int'].connect(self.event_checkTC2)
        self.checkBoxTC3.stateChanged['int'].connect(self.event_checkTC3)
        self.checkBoxTC4.stateChanged['int'].connect(self.event_checkTC4)
        self.checkBoxTC5.stateChanged['int'].connect(self.event_checkTC5)
        self.checkBoxTC6.stateChanged['int'].connect(self.event_checkTC6)
        self.checkBoxTC7.stateChanged['int'].connect(self.event_checkTC7)
        self.checkBoxTC8.stateChanged['int'].connect(self.event_checkTC8)

        # ALL Plots - CheckBox
        self.checkBoxC1A.stateChanged['int'].connect(self.event_checkC1A)
        self.checkBoxC1V.stateChanged['int'].connect(self.event_checkC1V)
        self.checkBoxC1D.stateChanged['int'].connect(self.event_checkC1D)
        self.checkBoxC2A.stateChanged['int'].connect(self.event_checkC2A)
        self.checkBoxC2V.stateChanged['int'].connect(self.event_checkC2V)
        self.checkBoxC2D.stateChanged['int'].connect(self.event_checkC2D)
        self.checkBoxC3A.stateChanged['int'].connect(self.event_checkC3A)
        self.checkBoxC3V.stateChanged['int'].connect(self.event_checkC3V)
        self.checkBoxC3D.stateChanged['int'].connect(self.event_checkC3D)
        self.checkBoxC4A.stateChanged['int'].connect(self.event_checkC4A)
        self.checkBoxC4V.stateChanged['int'].connect(self.event_checkC4V)
        self.checkBoxC4D.stateChanged['int'].connect(self.event_checkC4D)
        self.checkBoxC5A.stateChanged['int'].connect(self.event_checkC5A)
        self.checkBoxC5V.stateChanged['int'].connect(self.event_checkC5V)
        self.checkBoxC5D.stateChanged['int'].connect(self.event_checkC5D)
        self.checkBoxC6A.stateChanged['int'].connect(self.event_checkC6A)
        self.checkBoxC6V.stateChanged['int'].connect(self.event_checkC6V)
        self.checkBoxC6D.stateChanged['int'].connect(self.event_checkC6D)
        self.checkBoxC7A.stateChanged['int'].connect(self.event_checkC7A)
        self.checkBoxC7V.stateChanged['int'].connect(self.event_checkC7V)
        self.checkBoxC7D.stateChanged['int'].connect(self.event_checkC7D)
        self.checkBoxC8A.stateChanged['int'].connect(self.event_checkC8A)
        self.checkBoxC8V.stateChanged['int'].connect(self.event_checkC8V)
        self.checkBoxC8D.stateChanged['int'].connect(self.event_checkC8D)

        self.checkBox_Filter.stateChanged['int'].connect(self.event_Filter)

        # Time Plots - Label Click
        self.labelTC1.mousePressEvent = self.event_labelTC1
        self.labelTC2.mousePressEvent = self.event_labelTC2
        self.labelTC3.mousePressEvent = self.event_labelTC3
        self.labelTC4.mousePressEvent = self.event_labelTC4
        self.labelTC5.mousePressEvent = self.event_labelTC5
        self.labelTC6.mousePressEvent = self.event_labelTC6
        self.labelTC7.mousePressEvent = self.event_labelTC7
        self.labelTC8.mousePressEvent = self.event_labelTC8

        # Time Plots - LineEdit Change
        self.lineEditTC1.textChanged['QString'].connect(self.event_lineEditTC1)
        self.lineEditTC2.textChanged['QString'].connect(self.event_lineEditTC2)
        self.lineEditTC3.textChanged['QString'].connect(self.event_lineEditTC3)
        self.lineEditTC4.textChanged['QString'].connect(self.event_lineEditTC4)
        self.lineEditTC5.textChanged['QString'].connect(self.event_lineEditTC5)
        self.lineEditTC6.textChanged['QString'].connect(self.event_lineEditTC6)
        self.lineEditTC7.textChanged['QString'].connect(self.event_lineEditTC7)
        self.lineEditTC8.textChanged['QString'].connect(self.event_lineEditTC8)

        # XYplotDialog
        self.xyplotDialog = XYplotDialog()
        self.xyplotDialog.comboBoxX.addItems(self.setting.ALIAS)
        self.xyplotDialog.comboBoxY.addItems(self.setting.ALIAS)
        self.xyplotDialog.buttonBox.accepted.connect(self.xyplotDialogReturnOK)

        # NewSessionDialog
        self.newSessionDialog = NewSessionDialog()
        self.newSessionDialog.buttonBox.accepted.connect(self.newSessionDialogReturnOK)

        # FilterDialog
        self.filterDialog = FilterDialog()
        self.filterDialog.buttonBox.accepted.connect(self.filterDialogReturnOK)

        # LogManualDialog
        self.logManualDialog = LogManualDialog()
        self.logManualDialog.buttonBox.accepted.connect(self.logManualDialogReturnOK)

        # Safety Warning Checkbox
        self.checkBoxEnsure.stateChanged['int'].connect(self.event_checkEnsure)

        # XY-Plot Buffer
        self.xyplotData = np.empty((0, 14))

        # pyqtgraph - setting
        pg.setConfigOption('foreground', 'k')

        # XYplot-1 - GraphicsLayout
        self.xyplotpg_1 = pg.GraphicsLayoutWidget()
        self.xyplotpg_1.setBackground('w')
        self.xyplotpg_1.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.xyplotpg_1.ci.layout.setSpacing(0)

        self.xyplotItem1 = self.xyplotpg_1.addPlot(0, 0)
        self.xyplotItem2 = self.xyplotpg_1.addPlot(0, 1)
        self.xyplotItem3 = self.xyplotpg_1.addPlot(1, 0)
        self.xyplotItem4 = self.xyplotpg_1.addPlot(1, 1)

        # self.xyplotItem1.disableAutoRange()
        # self.xyplotItem2.disableAutoRange()
        # self.xyplotItem3.disableAutoRange()
        # self.xyplotItem4.disableAutoRange()

        # XYplot-2 - GraphicsLayout
        self.xyplotpg_2 = pg.GraphicsLayoutWidget()
        self.xyplotpg_2.setBackground('w')
        self.xyplotpg_2.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.xyplotpg_2.ci.layout.setSpacing(0)

        self.xyplotItem5 = self.xyplotpg_2.addPlot(0, 0)
        self.xyplotItem6 = self.xyplotpg_2.addPlot(0, 1)
        self.xyplotItem7 = self.xyplotpg_2.addPlot(1, 0)
        self.xyplotItem8 = self.xyplotpg_2.addPlot(1, 1)

        # self.xyplotItem5.disableAutoRange()
        # self.xyplotItem6.disableAutoRange()
        # self.xyplotItem7.disableAutoRange()
        # self.xyplotItem8.disableAutoRange()

        # XYplot-3 - GraphicsLayout
        self.xyplotpg_3 = pg.GraphicsLayoutWidget()
        self.xyplotpg_3.setBackground('w')
        self.xyplotpg_3.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.xyplotpg_3.ci.layout.setSpacing(0)

        self.xyplotItem9 = self.xyplotpg_3.addPlot(0, 0)
        self.xyplotItem10 = self.xyplotpg_3.addPlot(0, 1)
        self.xyplotItem11 = self.xyplotpg_3.addPlot(1, 0)
        self.xyplotItem12 = self.xyplotpg_3.addPlot(1, 1)

        # self.xyplotItem9.disableAutoRange()
        # self.xyplotItem10.disableAutoRange()
        # self.xyplotItem11.disableAutoRange()
        # self.xyplotItem12.disableAutoRange()

        # XYplot-4 - GraphicsLayout
        self.xyplotpg_4 = pg.GraphicsLayoutWidget()
        self.xyplotpg_4.setBackground('w')
        self.xyplotpg_4.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.xyplotpg_4.ci.layout.setSpacing(0)

        self.xyplotItem13 = self.xyplotpg_4.addPlot(0, 0)
        self.xyplotItem14 = self.xyplotpg_4.addPlot(0, 1)
        self.xyplotItem15 = self.xyplotpg_4.addPlot(1, 0)
        self.xyplotItem16 = self.xyplotpg_4.addPlot(1, 1)

        # self.xyplotItem13.disableAutoRange()
        # self.xyplotItem14.disableAutoRange()
        # self.xyplotItem15.disableAutoRange()
        # self.xyplotItem16.disableAutoRange()

        self.TplotItem = pg.PlotWidget()
        self.TplotItem.setBackground('w')
        
        self.W1C1Layout = pg.GraphicsLayoutWidget()
        self.W1C1Layout.setBackground('w')
        self.W1C1Plot = pg.PlotItem()
        self.W1C1AxisA = self.W1C1Plot.getAxis("left")
        self.W1C1AxisV = pg.AxisItem("left")
        self.W1C1AxisD = pg.AxisItem("left")
        self.W1C1ViewA = self.W1C1Plot.vb
        self.W1C1ViewV = pg.ViewBox()
        self.W1C1ViewD = pg.ViewBox()
        self.W1C1Layout.addItem(self.W1C1Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W1C1Layout.addItem(self.W1C1AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W1C1Layout.addItem(self.W1C1AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W1C1Layout.scene().addItem(self.W1C1ViewV)
        self.W1C1Layout.scene().addItem(self.W1C1ViewD)
        self.W1C1AxisV.linkToView(self.W1C1ViewV)
        self.W1C1AxisD.linkToView(self.W1C1ViewD)
        self.W1C1ViewV.setXLink(self.W1C1ViewA)
        self.W1C1ViewD.setXLink(self.W1C1ViewV)
        self.W1C1ViewV.setGeometry(self.W1C1ViewA.sceneBoundingRect())
        self.W1C1ViewD.setGeometry(self.W1C1ViewA.sceneBoundingRect())
        self.W1C1ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W1C1ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W1C1AxisA.setLabel('Acc', color='#000')
        self.W1C1AxisV.setLabel('Vel', color='#F00')
        self.W1C1AxisD.setLabel('Disp', color='#00F')
        self.C1plotLineRefA = pg.PlotDataItem()
        self.C1plotLineRefV = pg.PlotDataItem()
        self.C1plotLineRefD = pg.PlotDataItem()
        self.W1C1ViewA.addItem(self.C1plotLineRefA)
        self.W1C1ViewV.addItem(self.C1plotLineRefV)
        self.W1C1ViewD.addItem(self.C1plotLineRefD)
        self.W1C1ViewA.sigResized.connect(self.updateW1C1Views)

        self.W1C2Layout = pg.GraphicsLayoutWidget()
        self.W1C2Layout.setBackground('w')
        self.W1C2Plot = pg.PlotItem()
        self.W1C2AxisA = self.W1C2Plot.getAxis("left")
        self.W1C2AxisV = pg.AxisItem("left")
        self.W1C2AxisD = pg.AxisItem("left")
        self.W1C2ViewA = self.W1C2Plot.vb
        self.W1C2ViewV = pg.ViewBox()
        self.W1C2ViewD = pg.ViewBox()
        self.W1C2Layout.addItem(self.W1C2Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W1C2Layout.addItem(self.W1C2AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W1C2Layout.addItem(self.W1C2AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W1C2Layout.scene().addItem(self.W1C2ViewV)
        self.W1C2Layout.scene().addItem(self.W1C2ViewD)
        self.W1C2AxisV.linkToView(self.W1C2ViewV)
        self.W1C2AxisD.linkToView(self.W1C2ViewD)
        self.W1C2ViewV.setXLink(self.W1C2ViewA)
        self.W1C2ViewD.setXLink(self.W1C2ViewV)
        self.W1C2ViewV.setGeometry(self.W1C2ViewA.sceneBoundingRect())
        self.W1C2ViewD.setGeometry(self.W1C2ViewA.sceneBoundingRect())
        self.W1C2ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W1C2ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W1C2AxisA.setLabel('Acc', color='#000')
        self.W1C2AxisV.setLabel('Vel', color='#F00')
        self.W1C2AxisD.setLabel('Disp', color='#00F')
        self.C2plotLineRefA = pg.PlotDataItem()
        self.C2plotLineRefV = pg.PlotDataItem()
        self.C2plotLineRefD = pg.PlotDataItem()
        self.W1C2ViewA.addItem(self.C2plotLineRefA)
        self.W1C2ViewV.addItem(self.C2plotLineRefV)
        self.W1C2ViewD.addItem(self.C2plotLineRefD)
        self.W1C2ViewA.sigResized.connect(self.updateW1C2Views)
        
        self.W2C3Layout = pg.GraphicsLayoutWidget()
        self.W2C3Layout.setBackground('w')
        self.W2C3Plot = pg.PlotItem()
        self.W2C3AxisA = self.W2C3Plot.getAxis("left")
        self.W2C3AxisV = pg.AxisItem("left")
        self.W2C3AxisD = pg.AxisItem("left")
        self.W2C3ViewA = self.W2C3Plot.vb
        self.W2C3ViewV = pg.ViewBox()
        self.W2C3ViewD = pg.ViewBox()
        self.W2C3Layout.addItem(self.W2C3Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W2C3Layout.addItem(self.W2C3AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W2C3Layout.addItem(self.W2C3AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W2C3Layout.scene().addItem(self.W2C3ViewV)
        self.W2C3Layout.scene().addItem(self.W2C3ViewD)
        self.W2C3AxisV.linkToView(self.W2C3ViewV)
        self.W2C3AxisD.linkToView(self.W2C3ViewD)
        self.W2C3ViewV.setXLink(self.W2C3ViewA)
        self.W2C3ViewD.setXLink(self.W2C3ViewV)
        self.W2C3ViewV.setGeometry(self.W2C3ViewA.sceneBoundingRect())
        self.W2C3ViewD.setGeometry(self.W2C3ViewA.sceneBoundingRect())
        self.W2C3ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W2C3ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W2C3AxisA.setLabel('Acc', color='#000')
        self.W2C3AxisV.setLabel('Vel', color='#F00')
        self.W2C3AxisD.setLabel('Disp', color='#00F')
        self.C3plotLineRefA = pg.PlotDataItem()
        self.C3plotLineRefV = pg.PlotDataItem()
        self.C3plotLineRefD = pg.PlotDataItem()
        self.W2C3ViewA.addItem(self.C3plotLineRefA)
        self.W2C3ViewV.addItem(self.C3plotLineRefV)
        self.W2C3ViewD.addItem(self.C3plotLineRefD)
        self.W2C3ViewA.sigResized.connect(self.updateW2C3Views)
        
        self.W2C4Layout = pg.GraphicsLayoutWidget()
        self.W2C4Layout.setBackground('w')
        self.W2C4Plot = pg.PlotItem()
        self.W2C4AxisA = self.W2C4Plot.getAxis("left")
        self.W2C4AxisV = pg.AxisItem("left")
        self.W2C4AxisD = pg.AxisItem("left")
        self.W2C4ViewA = self.W2C4Plot.vb
        self.W2C4ViewV = pg.ViewBox()
        self.W2C4ViewD = pg.ViewBox()
        self.W2C4Layout.addItem(self.W2C4Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W2C4Layout.addItem(self.W2C4AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W2C4Layout.addItem(self.W2C4AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W2C4Layout.scene().addItem(self.W2C4ViewV)
        self.W2C4Layout.scene().addItem(self.W2C4ViewD)
        self.W2C4AxisV.linkToView(self.W2C4ViewV)
        self.W2C4AxisD.linkToView(self.W2C4ViewD)
        self.W2C4ViewV.setXLink(self.W2C4ViewA)
        self.W2C4ViewD.setXLink(self.W2C4ViewV)
        self.W2C4ViewV.setGeometry(self.W2C4ViewA.sceneBoundingRect())
        self.W2C4ViewD.setGeometry(self.W2C4ViewA.sceneBoundingRect())
        self.W2C4ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W2C4ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W2C4AxisA.setLabel('Acc', color='#000')
        self.W2C4AxisV.setLabel('Vel', color='#F00')
        self.W2C4AxisD.setLabel('Disp', color='#00F')
        self.C4plotLineRefA = pg.PlotDataItem()
        self.C4plotLineRefV = pg.PlotDataItem()
        self.C4plotLineRefD = pg.PlotDataItem()
        self.W2C4ViewA.addItem(self.C4plotLineRefA)
        self.W2C4ViewV.addItem(self.C4plotLineRefV)
        self.W2C4ViewD.addItem(self.C4plotLineRefD)
        self.W2C4ViewA.sigResized.connect(self.updateW2C4Views)
        
        self.W3C5Layout = pg.GraphicsLayoutWidget()
        self.W3C5Layout.setBackground('w')
        self.W3C5Plot = pg.PlotItem()
        self.W3C5AxisA = self.W3C5Plot.getAxis("left")
        self.W3C5AxisV = pg.AxisItem("left")
        self.W3C5AxisD = pg.AxisItem("left")
        self.W3C5ViewA = self.W3C5Plot.vb
        self.W3C5ViewV = pg.ViewBox()
        self.W3C5ViewD = pg.ViewBox()
        self.W3C5Layout.addItem(self.W3C5Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W3C5Layout.addItem(self.W3C5AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W3C5Layout.addItem(self.W3C5AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W3C5Layout.scene().addItem(self.W3C5ViewV)
        self.W3C5Layout.scene().addItem(self.W3C5ViewD)
        self.W3C5AxisV.linkToView(self.W3C5ViewV)
        self.W3C5AxisD.linkToView(self.W3C5ViewD)
        self.W3C5ViewV.setXLink(self.W3C5ViewA)
        self.W3C5ViewD.setXLink(self.W3C5ViewV)
        self.W3C5ViewV.setGeometry(self.W3C5ViewA.sceneBoundingRect())
        self.W3C5ViewD.setGeometry(self.W3C5ViewA.sceneBoundingRect())
        self.W3C5ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W3C5ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W3C5AxisA.setLabel('Acc', color='#000')
        self.W3C5AxisV.setLabel('Vel', color='#F00')
        self.W3C5AxisD.setLabel('Disp', color='#00F')
        self.C5plotLineRefA = pg.PlotDataItem()
        self.C5plotLineRefV = pg.PlotDataItem()
        self.C5plotLineRefD = pg.PlotDataItem()
        self.W3C5ViewA.addItem(self.C5plotLineRefA)
        self.W3C5ViewV.addItem(self.C5plotLineRefV)
        self.W3C5ViewD.addItem(self.C5plotLineRefD)
        self.W3C5ViewA.sigResized.connect(self.updateW3C5Views)
        
        self.W3C6Layout = pg.GraphicsLayoutWidget()
        self.W3C6Layout.setBackground('w')
        self.W3C6Plot = pg.PlotItem()
        self.W3C6AxisA = self.W3C6Plot.getAxis("left")
        self.W3C6AxisV = pg.AxisItem("left")
        self.W3C6AxisD = pg.AxisItem("left")
        self.W3C6ViewA = self.W3C6Plot.vb
        self.W3C6ViewV = pg.ViewBox()
        self.W3C6ViewD = pg.ViewBox()
        self.W3C6Layout.addItem(self.W3C6Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W3C6Layout.addItem(self.W3C6AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W3C6Layout.addItem(self.W3C6AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W3C6Layout.scene().addItem(self.W3C6ViewV)
        self.W3C6Layout.scene().addItem(self.W3C6ViewD)
        self.W3C6AxisV.linkToView(self.W3C6ViewV)
        self.W3C6AxisD.linkToView(self.W3C6ViewD)
        self.W3C6ViewV.setXLink(self.W3C6ViewA)
        self.W3C6ViewD.setXLink(self.W3C6ViewV)
        self.W3C6ViewV.setGeometry(self.W3C6ViewA.sceneBoundingRect())
        self.W3C6ViewD.setGeometry(self.W3C6ViewA.sceneBoundingRect())
        self.W3C6ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W3C6ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W3C6AxisA.setLabel('Acc', color='#000')
        self.W3C6AxisV.setLabel('Vel', color='#F00')
        self.W3C6AxisD.setLabel('Disp', color='#00F')
        self.C6plotLineRefA = pg.PlotDataItem()
        self.C6plotLineRefV = pg.PlotDataItem()
        self.C6plotLineRefD = pg.PlotDataItem()
        self.W3C6ViewA.addItem(self.C6plotLineRefA)
        self.W3C6ViewV.addItem(self.C6plotLineRefV)
        self.W3C6ViewD.addItem(self.C6plotLineRefD)
        self.W3C6ViewA.sigResized.connect(self.updateW3C6Views)
        
        self.W4C7Layout = pg.GraphicsLayoutWidget()
        self.W4C7Layout.setBackground('w')
        self.W4C7Plot = pg.PlotItem()
        self.W4C7AxisA = self.W4C7Plot.getAxis("left")
        self.W4C7AxisV = pg.AxisItem("left")
        self.W4C7AxisD = pg.AxisItem("left")
        self.W4C7ViewA = self.W4C7Plot.vb
        self.W4C7ViewV = pg.ViewBox()
        self.W4C7ViewD = pg.ViewBox()
        self.W4C7Layout.addItem(self.W4C7Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W4C7Layout.addItem(self.W4C7AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W4C7Layout.addItem(self.W4C7AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W4C7Layout.scene().addItem(self.W4C7ViewV)
        self.W4C7Layout.scene().addItem(self.W4C7ViewD)
        self.W4C7AxisV.linkToView(self.W4C7ViewV)
        self.W4C7AxisD.linkToView(self.W4C7ViewD)
        self.W4C7ViewV.setXLink(self.W4C7ViewA)
        self.W4C7ViewD.setXLink(self.W4C7ViewV)
        self.W4C7ViewV.setGeometry(self.W4C7ViewA.sceneBoundingRect())
        self.W4C7ViewD.setGeometry(self.W4C7ViewA.sceneBoundingRect())
        self.W4C7ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W4C7ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W4C7AxisA.setLabel('Acc', color='#000')
        self.W4C7AxisV.setLabel('Vel', color='#F00')
        self.W4C7AxisD.setLabel('Disp', color='#00F')
        self.C7plotLineRefA = pg.PlotDataItem()
        self.C7plotLineRefV = pg.PlotDataItem()
        self.C7plotLineRefD = pg.PlotDataItem()
        self.W4C7ViewA.addItem(self.C7plotLineRefA)
        self.W4C7ViewV.addItem(self.C7plotLineRefV)
        self.W4C7ViewD.addItem(self.C7plotLineRefD)
        self.W4C7ViewA.sigResized.connect(self.updateW4C7Views)
        
        self.W4C8Layout = pg.GraphicsLayoutWidget()
        self.W4C8Layout.setBackground('w')
        self.W4C8Plot = pg.PlotItem()
        self.W4C8AxisA = self.W4C8Plot.getAxis("left")
        self.W4C8AxisV = pg.AxisItem("left")
        self.W4C8AxisD = pg.AxisItem("left")
        self.W4C8ViewA = self.W4C8Plot.vb
        self.W4C8ViewV = pg.ViewBox()
        self.W4C8ViewD = pg.ViewBox()
        self.W4C8Layout.addItem(self.W4C8Plot, row = 2, col = 3,  rowspan=1, colspan=1)
        self.W4C8Layout.addItem(self.W4C8AxisV, row = 2, col = 2,  rowspan=1, colspan=1)
        self.W4C8Layout.addItem(self.W4C8AxisD, row = 2, col = 1,  rowspan=1, colspan=1)
        self.W4C8Layout.scene().addItem(self.W4C8ViewV)
        self.W4C8Layout.scene().addItem(self.W4C8ViewD)
        self.W4C8AxisV.linkToView(self.W4C8ViewV)
        self.W4C8AxisD.linkToView(self.W4C8ViewD)
        self.W4C8ViewV.setXLink(self.W4C8ViewA)
        self.W4C8ViewD.setXLink(self.W4C8ViewV)
        self.W4C8ViewV.setGeometry(self.W4C8ViewA.sceneBoundingRect())
        self.W4C8ViewD.setGeometry(self.W4C8ViewA.sceneBoundingRect())
        self.W4C8ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W4C8ViewV.enableAutoRange(axis= pg.ViewBox.XYAxes, enable=True)
        self.W4C8AxisA.setLabel('Acc', color='#000')
        self.W4C8AxisV.setLabel('Vel', color='#F00')
        self.W4C8AxisD.setLabel('Disp', color='#00F')
        self.C8plotLineRefA = pg.PlotDataItem()
        self.C8plotLineRefV = pg.PlotDataItem()
        self.C8plotLineRefD = pg.PlotDataItem()
        self.W4C8ViewA.addItem(self.C8plotLineRefA)
        self.W4C8ViewV.addItem(self.C8plotLineRefV)
        self.W4C8ViewD.addItem(self.C8plotLineRefD)
        self.W4C8ViewA.sigResized.connect(self.updateW4C8Views)

        self.Tplot_ref = None
        self.Aplot_ref = True
        self.W1plot_ref = True
        self.W2plot_ref = True
        self.W3plot_ref = True
        self.W4plot_ref = True


        self.pushButton_FilterSetting.clicked.connect(self.event_FilterSetting)
        self.pushButton_LogManual.clicked.connect(self.event_LogManual)

        self.event_start()
        self.updateSetting()

        # Menu Items
        self.actionNewSession.triggered.connect(self.event_NewSession)
        self.actionSettings.triggered.connect(self.event_MenuSettings)
        self.actionTimePlot.triggered.connect(self.event_TimePlot)
        self.actionOpenSession.triggered.connect(self.event_OpenSession)

        # File Setting
        self.FILE = False

        self.st = time.time()

        self.interval = 50
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def updateW1C1Views(self):
        self.W1C1ViewV.setGeometry(self.W1C1ViewA.sceneBoundingRect())
        self.W1C1ViewD.setGeometry(self.W1C1ViewA.sceneBoundingRect())

    def updateW1C2Views(self):
        self.W1C2ViewV.setGeometry(self.W1C2ViewA.sceneBoundingRect())
        self.W1C2ViewD.setGeometry(self.W1C2ViewA.sceneBoundingRect())

    def updateW2C3Views(self):
        self.W2C3ViewV.setGeometry(self.W2C3ViewA.sceneBoundingRect())
        self.W2C3ViewD.setGeometry(self.W2C3ViewA.sceneBoundingRect())

    def updateW2C4Views(self):
        self.W2C4ViewV.setGeometry(self.W2C4ViewA.sceneBoundingRect())
        self.W2C4ViewD.setGeometry(self.W2C4ViewA.sceneBoundingRect())

    def updateW3C5Views(self):
        self.W3C5ViewV.setGeometry(self.W3C5ViewA.sceneBoundingRect())
        self.W3C5ViewD.setGeometry(self.W3C5ViewA.sceneBoundingRect())

    def updateW3C6Views(self):
        self.W3C6ViewV.setGeometry(self.W3C6ViewA.sceneBoundingRect())
        self.W3C6ViewD.setGeometry(self.W3C6ViewA.sceneBoundingRect())

    def updateW4C7Views(self):
        self.W4C7ViewV.setGeometry(self.W4C7ViewA.sceneBoundingRect())
        self.W4C7ViewD.setGeometry(self.W4C7ViewA.sceneBoundingRect())

    def updateW4C8Views(self):
        self.W4C8ViewV.setGeometry(self.W4C8ViewA.sceneBoundingRect())
        self.W4C8ViewD.setGeometry(self.W4C8ViewA.sceneBoundingRect())

    # GAIN Events
    def event_GainC1(self, value):
        print(value)

    def event_GainC2(self, value):
        print(value)

    def event_GainC3(self, value):
        print(value)

    def event_GainC4(self, value):
        print(value)

    def event_GainC5(self, value):
        print(value)

    def event_GainC6(self, value):
        print(value)

    def event_GainC7(self, value):
        print(value)

    def event_GainC8(self, value):
        print(value)

    def event_GainC9(self, value):
        print(value)

    def event_GainC10(self, value):
        print(value)

    def event_GainC11(self, value):
        print(value)

    def event_GainC12(self, value):
        print(value)

    def event_GainC13(self, value):
        print(value)

    def event_GainC14(self, value):
        print(value)

    # Multiplier Events
    def event_MultiC1(self, value):
        self.setting.setMultiplier(0, float(value))

    def event_MultiC2(self, value):
        self.setting.setMultiplier(1, float(value))

    def event_MultiC3(self, value):
        self.setting.setMultiplier(2, float(value))

    def event_MultiC4(self, value):
        self.setting.setMultiplier(3, float(value))

    def event_MultiC5(self, value):
        self.setting.setMultiplier(4, float(value))

    def event_MultiC6(self, value):
        self.setting.setMultiplier(5, float(value))

    def event_MultiC7(self, value):
        self.setting.setMultiplier(6, float(value))

    def event_MultiC8(self, value):
        self.setting.setMultiplier(7, float(value))

    def event_MultiC9(self, value):
        self.setting.setMultiplier(8, float(value))

    def event_MultiC10(self, value):
        self.setting.setMultiplier(9, float(value))

    def event_MultiC11(self, value):
        self.setting.setMultiplier(10, float(value))

    def event_MultiC12(self, value):
        self.setting.setMultiplier(11, float(value))

    def event_MultiC13(self, value):
        self.setting.setMultiplier(12, float(value))

    def event_MultiC14(self, value):
        self.setting.setMultiplier(13, float(value))

    def event_SamplingChanged(self, value):
        self.setting.setSampling(int(value))

    def event_SamplingFinished(self):
        if int(self.lineEditSampling.text()) % 10 != 0:
            error_dialog = QtWidgets.QErrorMessage(self)
            error_dialog.setWindowModality(QtCore.Qt.WindowModal)
            error_dialog.showMessage("Sampling must be multiple of 10")

    def event_WindowChanged(self, value):
        self.setting.setWindow(int(value))

    def event_AvgChanged(self, value):
        self.setting.setAvg(int(value))

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
    def event_Graph9(self):
        self.xyplotDialog.labelTitle.setText('Graph-9')
        self.xyplotDialog.labelGraphIndex.setText('8')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[8]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[8]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[8]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[8]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[8])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[8])
        self.xyplotDialog.exec()

    def event_Graph10(self):
        self.xyplotDialog.labelTitle.setText('Graph-10')
        self.xyplotDialog.labelGraphIndex.setText('9')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[9]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[9]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[9]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[9]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[9])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[9])
        self.xyplotDialog.exec()

    def event_Graph11(self):
        self.xyplotDialog.labelTitle.setText('Graph-11')
        self.xyplotDialog.labelGraphIndex.setText('10')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[10]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[10]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[10]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[10]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[10])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[10])
        self.xyplotDialog.exec()

    def event_Graph12(self):
        self.xyplotDialog.labelTitle.setText('Graph-12')
        self.xyplotDialog.labelGraphIndex.setText('11')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[11]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[11]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[11]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[11]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[11])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[11])
        self.xyplotDialog.exec()

    # Graph-4
    def event_Graph13(self):
        self.xyplotDialog.labelTitle.setText('Graph-13')
        self.xyplotDialog.labelGraphIndex.setText('12')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[12]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[12]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[12]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[12]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[12])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[12])
        self.xyplotDialog.exec()

    def event_Graph14(self):
        self.xyplotDialog.labelTitle.setText('Graph-14')
        self.xyplotDialog.labelGraphIndex.setText('13')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[13]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[13]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[13]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[13]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[13])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[13])
        self.xyplotDialog.exec()

    def event_Graph15(self):
        self.xyplotDialog.labelTitle.setText('Graph-15')
        self.xyplotDialog.labelGraphIndex.setText('14')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[14]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[14]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[14]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[14]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[14])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[14])
        self.xyplotDialog.exec()

    def event_Graph16(self):
        self.xyplotDialog.labelTitle.setText('Graph-16')
        self.xyplotDialog.labelGraphIndex.setText('15')
        self.xyplotDialog.labelGraphIndex.setHidden(True)
        self.xyplotDialog.lineEditXmin.setText(str(self.setting.XYPLOT_XMIN[15]))
        self.xyplotDialog.lineEditXmax.setText(str(self.setting.XYPLOT_XMAX[15]))
        self.xyplotDialog.lineEditYmin.setText(str(self.setting.XYPLOT_YMIN[15]))
        self.xyplotDialog.lineEditYmax.setText(str(self.setting.XYPLOT_YMAX[15]))
        self.xyplotDialog.comboBoxX.setCurrentIndex(self.setting.XYPLOT_X[15])
        self.xyplotDialog.comboBoxY.setCurrentIndex(self.setting.XYPLOT_Y[15])
        self.xyplotDialog.exec()

    # Time Plot - CheckBox Events
    def event_checkTC1(self, value):
        self.setting.setTimePlotEnable(0, value)

    def event_checkTC2(self, value):
        self.setting.setTimePlotEnable(1, value)

    def event_checkTC3(self, value):
        self.setting.setTimePlotEnable(2, value)

    def event_checkTC4(self, value):
        self.setting.setTimePlotEnable(3, value)

    def event_checkTC5(self, value):
        self.setting.setTimePlotEnable(4, value)

    def event_checkTC6(self, value):
        self.setting.setTimePlotEnable(5, value)

    def event_checkTC7(self, value):
        self.setting.setTimePlotEnable(6, value)

    def event_checkTC8(self, value):
        self.setting.setTimePlotEnable(7, value)

    def event_checkTC9(self, value):
        self.setting.setTimePlotEnable(8, value)

    def event_checkTC10(self, value):
        self.setting.setTimePlotEnable(9, value)

    def event_checkTC11(self, value):
        self.setting.setTimePlotEnable(10, value)

    def event_checkTC12(self, value):
        self.setting.setTimePlotEnable(11, value)

    def event_checkTC13(self, value):
        self.setting.setTimePlotEnable(12, value)

    def event_checkTC14(self, value):
        self.setting.setTimePlotEnable(13, value)

    def event_Filter(self, value):
        if value == 0:
            self.setting.FilterEnable = False
        elif value == 2:
            self.setting.FilterEnable = True

    # ALL Plot - CheckBox Events
    def event_checkC1A(self, value):
        self.setting.setAllPlotEnable('C1A', value)

    def event_checkC1V(self, value):
        self.setting.setAllPlotEnable('C1V', value)

    def event_checkC1D(self, value):
        self.setting.setAllPlotEnable('C1D', value)
        
    def event_checkC2A(self, value):
        self.setting.setAllPlotEnable('C2A', value)

    def event_checkC2V(self, value):
        self.setting.setAllPlotEnable('C2V', value)

    def event_checkC2D(self, value):
        self.setting.setAllPlotEnable('C2D', value)
        
    def event_checkC3A(self, value):
        self.setting.setAllPlotEnable('C3A', value)

    def event_checkC3V(self, value):
        self.setting.setAllPlotEnable('C3V', value)

    def event_checkC3D(self, value):
        self.setting.setAllPlotEnable('C3D', value)
        
    def event_checkC4A(self, value):
        self.setting.setAllPlotEnable('C4A', value)

    def event_checkC4V(self, value):
        self.setting.setAllPlotEnable('C4V', value)

    def event_checkC4D(self, value):
        self.setting.setAllPlotEnable('C4D', value)
        
    def event_checkC5A(self, value):
        self.setting.setAllPlotEnable('C5A', value)

    def event_checkC5V(self, value):
        self.setting.setAllPlotEnable('C5V', value)

    def event_checkC5D(self, value):
        self.setting.setAllPlotEnable('C5D', value)
        
    def event_checkC6A(self, value):
        self.setting.setAllPlotEnable('C6A', value)

    def event_checkC6V(self, value):
        self.setting.setAllPlotEnable('C6V', value)

    def event_checkC6D(self, value):
        self.setting.setAllPlotEnable('C6D', value)
        
    def event_checkC7A(self, value):
        self.setting.setAllPlotEnable('C7A', value)

    def event_checkC7V(self, value):
        self.setting.setAllPlotEnable('C7V', value)

    def event_checkC7D(self, value):
        self.setting.setAllPlotEnable('C7D', value)
        
    def event_checkC8A(self, value):
        self.setting.setAllPlotEnable('C8A', value)

    def event_checkC8V(self, value):
        self.setting.setAllPlotEnable('C8V', value)

    def event_checkC8D(self, value):
        self.setting.setAllPlotEnable('C8D', value)

    # Safety Ensure - CheckBox Event
    def event_checkEnsure(self, value):
        if value == 0:
            self.labjack.lowDAC0()
        elif value == 2:
            self.labjack.highDAC0()

    # Time Plot - Label Events
    def event_labelTC1(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(0, color_hex)
        self.labelTC1.setStyleSheet("color:"+color_hex)

    def event_labelTC2(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(1, color_hex)
        self.labelTC2.setStyleSheet("color:"+color_hex)

    def event_labelTC3(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(2, color_hex)
        self.labelTC3.setStyleSheet("color:"+color_hex)

    def event_labelTC4(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(3, color_hex)
        self.labelTC4.setStyleSheet("color:"+color_hex)

    def event_labelTC5(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(4, color_hex)
        self.labelTC5.setStyleSheet("color:"+color_hex)

    def event_labelTC6(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(5, color_hex)
        self.labelTC6.setStyleSheet("color:"+color_hex)

    def event_labelTC7(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(6, color_hex)
        self.labelTC7.setStyleSheet("color:"+color_hex)

    def event_labelTC8(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(7, color_hex)
        self.labelTC8.setStyleSheet("color:"+color_hex)

    def event_labelTC9(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(8, color_hex)

    def event_labelTC10(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(9, color_hex)

    def event_labelTC11(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(10, color_hex)

    def event_labelTC12(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(11, color_hex)

    def event_labelTC13(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(12, color_hex)

    def event_labelTC14(self, event):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.setTimePlotColor(13, color_hex)

    # Time Plots - LineEdit Events
    def event_lineEditTC1(self, value):
        self.setting.setTimePlotOffset(0, float(value))

    def event_lineEditTC2(self, value):
        self.setting.setTimePlotOffset(1, float(value))

    def event_lineEditTC3(self, value):
        self.setting.setTimePlotOffset(2, float(value))

    def event_lineEditTC4(self, value):
        self.setting.setTimePlotOffset(3, float(value))

    def event_lineEditTC5(self, value):
        self.setting.setTimePlotOffset(4, float(value))

    def event_lineEditTC6(self, value):
        self.setting.setTimePlotOffset(5, float(value))

    def event_lineEditTC7(self, value):
        self.setting.setTimePlotOffset(6, float(value))

    def event_lineEditTC8(self, value):
        self.setting.setTimePlotOffset(7, float(value))

    def event_lineEditTC9(self, value):
        self.setting.setTimePlotOffset(8, float(value))

    def event_lineEditTC10(self, value):
        self.setting.setTimePlotOffset(9, float(value))

    def event_lineEditTC11(self, value):
        self.setting.setTimePlotOffset(10, float(value))

    def event_lineEditTC12(self, value):
        self.setting.setTimePlotOffset(11, float(value))

    def event_lineEditTC13(self, value):
        self.setting.setTimePlotOffset(12, float(value))

    def event_lineEditTC14(self, value):
        self.setting.setTimePlotOffset(13, float(value))

    def event_Tabs(self, value):
        if value == 1:
            self.XYplotUI_2()
        elif value == 2:
            self.XYplotUI_1()
        elif value == 3:
            self.XYplotUI_4()
        elif value == 4:
            self.TplotUI()

    def event_NewSession(self, test):
        if self.FILE == True and self.STREAM == False:
            self.FILE = False

        if self.FILE == False:
            self.newSessionDialog.exec()

    def event_FilterSetting(self):
        self.filterDialog.exec()

    def event_LogManual(self):
        self.logManualDialog.label_C1.setText(self.setting.ALIAS[0])
        self.logManualDialog.label_C2.setText(self.setting.ALIAS[1])
        self.logManualDialog.label_C3.setText(self.setting.ALIAS[2])
        self.logManualDialog.label_C4.setText(self.setting.ALIAS[3])
        self.logManualDialog.label_C5.setText(self.setting.ALIAS[4])
        self.logManualDialog.label_C6.setText(self.setting.ALIAS[5])
        self.logManualDialog.label_C7.setText(self.setting.ALIAS[6])
        self.logManualDialog.label_C8.setText(self.setting.ALIAS[7])

        self.logManualDialog.lineEdit_C1F.setText("{:.3f}".format(self.fft_peak[0]))
        self.logManualDialog.lineEdit_C2F.setText("{:.3f}".format(self.fft_peak[1]))
        self.logManualDialog.lineEdit_C3F.setText("{:.3f}".format(self.fft_peak[2]))
        self.logManualDialog.lineEdit_C4F.setText("{:.3f}".format(self.fft_peak[3]))
        self.logManualDialog.lineEdit_C5F.setText("{:.3f}".format(self.fft_peak[4]))
        self.logManualDialog.lineEdit_C6F.setText("{:.3f}".format(self.fft_peak[5]))
        self.logManualDialog.lineEdit_C7F.setText("{:.3f}".format(self.fft_peak[6]))
        self.logManualDialog.lineEdit_C8F.setText("{:.3f}".format(self.fft_peak[7]))

        self.logManualDialog.lineEdit_C1D.setText("{:.3f}".format(self.displacementPeak[0]))
        self.logManualDialog.lineEdit_C2D.setText("{:.3f}".format(self.displacementPeak[1]))
        self.logManualDialog.lineEdit_C3D.setText("{:.3f}".format(self.displacementPeak[2]))
        self.logManualDialog.lineEdit_C4D.setText("{:.3f}".format(self.displacementPeak[3]))
        self.logManualDialog.lineEdit_C5D.setText("{:.3f}".format(self.displacementPeak[4]))
        self.logManualDialog.lineEdit_C6D.setText("{:.3f}".format(self.displacementPeak[5]))
        self.logManualDialog.lineEdit_C7D.setText("{:.3f}".format(self.displacementPeak[6]))
        self.logManualDialog.lineEdit_C8D.setText("{:.3f}".format(self.displacementPeak[7]))

        self.logManualDialog.exec()

    def event_OpenSession(self):
        if self.STREAM == True:
            return

        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Session', '', "Text files (*.csv)")
        if fname[0] != '':
            fHandle = open(fname[0], 'r')
            config_str = fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline() + fHandle.readline()
            self.readHeader(config_str)
            fHandle.close()
            self.offlinedata = np.genfromtxt(fname[0], delimiter=',', skip_header=10)
            # print(self.offlinedata.shape)
            self.OFFLINE = True
            self.FILE = False
            self.stackedWidget.setCurrentIndex(2)

    def event_MenuSettings(self):
        # if self.FILE == True and self.STREAM == False:
        if self.STREAM == False:
            self.stackedWidget.setCurrentIndex(1)

    def event_TimePlot(self):
        if self.FILE == True or self.OFFLINE == True:
            self.stackedWidget.setCurrentIndex(2)

    def XYplotUI_1(self):
        W1C1Plot_Title = self.setting.ALIAS[0]
        self.W1C1Plot.setLabels(title=W1C1Plot_Title)
        W1C2Plot_Title = self.setting.ALIAS[1]
        self.W1C2Plot.setLabels(title=W1C2Plot_Title)
        W2C3Plot_Title = self.setting.ALIAS[2]
        self.W2C3Plot.setLabels(title=W2C3Plot_Title)

        self.plot_C1.addWidget(self.W1C1Layout)
        self.plot_C2.addWidget(self.W1C2Layout)
        self.plot_C3.addWidget(self.W2C3Layout)

    def XYplotUI_2(self):
        W2C4Plot_Title = self.setting.ALIAS[3]
        self.W2C4Plot.setLabels(title=W2C4Plot_Title)
        W3C5Plot_Title = self.setting.ALIAS[4]
        self.W3C5Plot.setLabels(title=W3C5Plot_Title)
        W3C6Plot_Title = self.setting.ALIAS[5]
        self.W3C6Plot.setLabels(title=W3C6Plot_Title)
        
        self.plot_C4.addWidget(self.W2C4Layout)
        self.plot_C5.addWidget(self.W3C5Layout)
        self.plot_C6.addWidget(self.W3C6Layout)

    def XYplotUI_3(self):
        pass

    def XYplotUI_4(self):
        W4C7Plot_Title = self.setting.ALIAS[6]
        self.W4C7Plot.setLabels(title=W4C7Plot_Title)
        W4C8Plot_Title = self.setting.ALIAS[7]
        self.W4C8Plot.setLabels(title=W4C8Plot_Title)
    
        self.plot_C7.addWidget(self.W4C7Layout)
        self.plot_C8.addWidget(self.W4C8Layout)

    def TplotUI(self):
        self.verticalLayoutTplot.addWidget(self.TplotItem)  # CHECK - MULTIPLE
        for i in range(self.setting.CHANNEL):
            label_name = getattr(self, "labelTC%d" % (i + 1))
            label_name.setText(self.setting.ALIAS[i])
            label_name.setStyleSheet("color:"+self.setting.timePlotColors[i])
            checkBox_name = getattr(self, "checkBoxTC%d" % (i + 1))
            if self.setting.timePlotEnable[i] == None:
                checkBox_name.setChecked(False)
            else:
                checkBox_name.setChecked(True)

    def AplotUI(self):
        self.plot_C1.addWidget(self.W1C1Layout)
        self.plot_C2.addWidget(self.C2plotItem)
        self.plot_C3.addWidget(self.C3plotItem)
        self.plot_C4.addWidget(self.C4plotItem)

    def stop_xyplot(self):
        #self.d2= u3.U3()
        if self.OFFLINE == True:
            offline_dialog = QtWidgets.QErrorMessage(self)
            offline_dialog.setWindowModality(QtCore.Qt.WindowModal)
            offline_dialog.setWindowTitle("Offline Mode")
            offline_dialog.showMessage("Offline Mode. Please start \"New Session\"")
            

        self.pushButtonXYplotStart.setStyleSheet("background-color:none;")
        self.pushButtonXYplotStop.setStyleSheet("background-color:rgb(250,0,0);")
        self.STREAM = False
        self.d2.ACQ = False
        # self.d2.writeCal(b"<T,8,0000,5>")

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

    def newSessionDialogReturnOK(self):
        file = self.newSessionDialog.lineEditFile.text()
        auth = self.newSessionDialog.lineEditAuthor.text()
        desc = self.newSessionDialog.textEditDescription.toPlainText()

        self.setting.setSession(file, auth, desc)
        self.FILE = True
        self.OFFLINE = False
        self.plotdata = np.zeros((self.setting.WINDOW, self.setting.CHANNEL*3))
        self.xyplotData = np.empty((0, 14))
        self.q.put(np.zeros((1, 14)))
        self.stackedWidget.setCurrentIndex(2)

    def filterDialogReturnOK(self):
        lc = self.filterDialog.lineEdit_LC.text()
        hc = self.filterDialog.lineEdit_HC.text()
        o = self.filterDialog.lineEdit_O.text()

        self.setting.setFilter(float(lc), float(hc), float(o))

    def logManualDialogReturnOK(self):
        c1f = self.logManualDialog.lineEdit_C1F.text()
        c2f = self.logManualDialog.lineEdit_C2F.text()
        c3f = self.logManualDialog.lineEdit_C3F.text()
        c4f = self.logManualDialog.lineEdit_C4F.text()
        c5f = self.logManualDialog.lineEdit_C5F.text()
        c6f = self.logManualDialog.lineEdit_C6F.text()
        c7f = self.logManualDialog.lineEdit_C7F.text()
        c8f = self.logManualDialog.lineEdit_C8F.text()
        c1d = self.logManualDialog.lineEdit_C1D.text()
        c2d = self.logManualDialog.lineEdit_C2D.text()
        c3d = self.logManualDialog.lineEdit_C3D.text()
        c4d = self.logManualDialog.lineEdit_C4D.text()
        c5d = self.logManualDialog.lineEdit_C5D.text()
        c6d = self.logManualDialog.lineEdit_C6D.text()
        c7d = self.logManualDialog.lineEdit_C7D.text()
        c8d = self.logManualDialog.lineEdit_C8D.text()

        if c1f in self.LOG_MAN:
            self.LOG_MAN[c1f][0] = c1d
            self.LOG_MAN_vel[c1f][0] = "{:.3f}".format(self.velocityPeak[0])
            self.LOG_MAN_acc[c1f][0] = "{:.3f}".format(self.accelerationPeak[0])
        else:
            self.LOG_MAN[c1f] = {}
            self.LOG_MAN_vel[c1f] = {}
            self.LOG_MAN_acc[c1f] = {}
            self.LOG_MAN[c1f][0] = c1d
            self.LOG_MAN_vel[c1f][0] = "{:.3f}".format(self.velocityPeak[0])
            self.LOG_MAN_acc[c1f][0] = "{:.3f}".format(self.accelerationPeak[0])
        if c2f in self.LOG_MAN:
            self.LOG_MAN[c2f][1] = c2d
            self.LOG_MAN_vel[c2f][1] = "{:.3f}".format(self.velocityPeak[1])
            self.LOG_MAN_acc[c2f][1] = "{:.3f}".format(self.accelerationPeak[1])
        else:
            self.LOG_MAN[c2f] = {}
            self.LOG_MAN_vel[c2f] = {}
            self.LOG_MAN_acc[c2f] = {}
            self.LOG_MAN[c2f][1] = c2d
            self.LOG_MAN_vel[c2f][1] = "{:.3f}".format(self.velocityPeak[1])
            self.LOG_MAN_acc[c2f][1] = "{:.3f}".format(self.accelerationPeak[1])
        if c3f in self.LOG_MAN:
            self.LOG_MAN[c3f][2] = c3d
            self.LOG_MAN_vel[c3f][2] = "{:.3f}".format(self.velocityPeak[2])
            self.LOG_MAN_acc[c3f][2] = "{:.3f}".format(self.accelerationPeak[2])
        else:
            self.LOG_MAN[c3f] = {}
            self.LOG_MAN_vel[c3f] = {}
            self.LOG_MAN_acc[c3f] = {}
            self.LOG_MAN[c3f][2] = c3d
            self.LOG_MAN_vel[c3f][2] = "{:.3f}".format(self.velocityPeak[2])
            self.LOG_MAN_acc[c3f][2] = "{:.3f}".format(self.accelerationPeak[2])
        if c4f in self.LOG_MAN:
            self.LOG_MAN[c4f][3] = c4d
            self.LOG_MAN_vel[c4f][3] = "{:.3f}".format(self.velocityPeak[3])
            self.LOG_MAN_acc[c4f][3] = "{:.3f}".format(self.accelerationPeak[3])
        else:
            self.LOG_MAN[c4f] = {}
            self.LOG_MAN_vel[c4f] = {}
            self.LOG_MAN_acc[c4f] = {}
            self.LOG_MAN[c4f][3] = c4d
            self.LOG_MAN_vel[c4f][3] = "{:.3f}".format(self.velocityPeak[3])
            self.LOG_MAN_acc[c4f][3] = "{:.3f}".format(self.accelerationPeak[3])
        if c5f in self.LOG_MAN:
            self.LOG_MAN[c5f][4] = c5d
            self.LOG_MAN_vel[c5f][4] = "{:.3f}".format(self.velocityPeak[4])
            self.LOG_MAN_acc[c5f][4] = "{:.3f}".format(self.accelerationPeak[4])
        else:
            self.LOG_MAN[c5f] = {}
            self.LOG_MAN_vel[c5f] = {}
            self.LOG_MAN_acc[c5f] = {}
            self.LOG_MAN[c5f][4] = c5d
            self.LOG_MAN_vel[c5f][4] = "{:.3f}".format(self.velocityPeak[4])
            self.LOG_MAN_acc[c5f][4] = "{:.3f}".format(self.accelerationPeak[4])
        if c6f in self.LOG_MAN:
            self.LOG_MAN[c6f][5] = c6d
            self.LOG_MAN_vel[c6f][5] = "{:.3f}".format(self.velocityPeak[5])
            self.LOG_MAN_acc[c6f][5] = "{:.3f}".format(self.accelerationPeak[5])
        else:
            self.LOG_MAN[c6f] = {}
            self.LOG_MAN_vel[c6f] = {}
            self.LOG_MAN_acc[c6f] = {}
            self.LOG_MAN[c6f][5] = c6d
            self.LOG_MAN_vel[c6f][5] = "{:.3f}".format(self.velocityPeak[5])
            self.LOG_MAN_acc[c6f][5] = "{:.3f}".format(self.accelerationPeak[5])
        if c7f in self.LOG_MAN:
            self.LOG_MAN[c7f][6] = c7d
            self.LOG_MAN_vel[c7f][6] = "{:.3f}".format(self.velocityPeak[6])
            self.LOG_MAN_acc[c7f][6] = "{:.3f}".format(self.accelerationPeak[6])
        else:
            self.LOG_MAN[c7f] = {}
            self.LOG_MAN_vel[c7f] = {}
            self.LOG_MAN_acc[c7f] = {}
            self.LOG_MAN[c7f][6] = c7d
            self.LOG_MAN_vel[c7f][6] = "{:.3f}".format(self.velocityPeak[6])
            self.LOG_MAN_acc[c7f][6] = "{:.3f}".format(self.accelerationPeak[6])
        if c8f in self.LOG_MAN:
            self.LOG_MAN[c8f][7] = c8d
            self.LOG_MAN_vel[c8f][7] = "{:.3f}".format(self.velocityPeak[7])
            self.LOG_MAN_acc[c8f][7] = "{:.3f}".format(self.accelerationPeak[7])
        else:
            self.LOG_MAN[c8f] = {}
            self.LOG_MAN_vel[c8f] = {}
            self.LOG_MAN_acc[c8f] = {}
            self.LOG_MAN[c8f][7] = c8d
            self.LOG_MAN_vel[c8f][7] = "{:.3f}".format(self.velocityPeak[7])
            self.LOG_MAN_acc[c8f][7] = "{:.3f}".format(self.accelerationPeak[7])

    def start_xyplot(self):
        if self.OFFLINE == True:
            offline_dialog = QtWidgets.QErrorMessage(self)
            offline_dialog.setWindowModality(QtCore.Qt.WindowModal)
            offline_dialog.setWindowTitle("Offline Mode")
            offline_dialog.showMessage("Offline Mode. Please start \"New Session\"")
            return

        self.pushButtonXYplotStart.setStyleSheet("background-color:rgb(0,255,0);")
        self.pushButtonXYplotStop.setStyleSheet("background-color:none;")
        f = open(str(self.setting.FILENAME) + '_' + str(self.setting.SAMPLING) + '.csv', 'w')
        self.writeHeader(f)
        f.close()

        self.STREAM = True
        self.plotdata = np.zeros((self.setting.WINDOW, self.setting.CHANNEL*3))
        self.worker_stream = Worker(self.stream_plot, )
        self.worker_file = Worker(self.write_plot, )
        self.threadpool.start(self.worker_stream)
        self.threadpool.start(self.worker_file)

    def tear_xyplot(self):
        if self.STREAM == True:
            self.q.queue.clear()
            self.f.queue.clear()
            self.plotdata = np.zeros((self.setting.WINDOW, self.setting.CHANNEL*3))
            self.xyplotData = np.empty((0, 14))
            self.TEAR_AVG = False
            self.TEAR_FILE = True

    def stream_plot(self):
        self.getStream()

    def write_plot(self):
        while self.STREAM:
            data = [0]

            while True:
                try:
                    data = self.f.get_nowait()
                except queue.Empty:
                    break

                f = open(str(self.setting.FILENAME) + '_' + str(self.setting.SAMPLING) + '.csv', 'a')
                np.savetxt(f, data, fmt='%1.3f', delimiter=',')
                f.close()

                if self.TEAR_FILE == True:
                    f = open(str(self.setting.FILENAME) + '_' + str(self.setting.SAMPLING) + '.csv', 'w')
                    self.writeHeader(f)
                    f.close()
                    self.TEAR_FILE = False

            time.sleep(0.001)

    def filter_data2(self, array, fs, state, cutoff=[1.,2000], axis=-1,filt_order=3):
        if self.setting.FilterEnable == False:
            return array, None

        if cutoff[1]>=fs/2:
            cutoff[1]=fs/2.1
        if cutoff[0]==0:
            return array

        array = np.moveaxis(array, axis, -1)

        sos_coeffs = scipy.signal.butter(N=filt_order, Wn=cutoff, btype='bandpass', fs=fs, output='sos',)

        init_state = scipy.signal.sosfilt_zi(sos_coeffs)
    
        for _ in range(1):
            init_fwd = init_state * array[(Ellipsis, 0) + ((None,)*init_state.ndim)]
            init_fwd = np.moveaxis(init_fwd, array.ndim-1, 0)
            if type(state) == type(array):
                array, _zo = scipy.signal.sosfilt(sos_coeffs, array, axis=-1, zi=state)
            else:
                array, _zo = scipy.signal.sosfilt(sos_coeffs, array, axis=-1, zi=init_fwd)
            array = array[..., ::-1]

        return np.moveaxis(array, -1, axis), _zo

    def filter_data(self, array, fs, state, cutoff=[1.,2000], axis=-1,filt_order=3):
        if self.setting.FilterEnable == False:
            return array, None

        if cutoff[1]>=fs/2:
            cutoff[1]=fs/2.1
        if cutoff[0]==0:
            return array

        sos_coeffs = scipy.signal.butter(N=filt_order, Wn=cutoff, btype='bandpass', fs=fs, output='sos',)
        init_state = scipy.signal.sosfilt_zi(sos_coeffs)
    
        for _ in range(1):
            if type(state) == type(array) and state.shape[0] == filt_order:
                array, _zo = scipy.signal.sosfilt(sos_coeffs, array, axis=0, zi=state)
            else:
                init_fwd = init_state * array[(0, Ellipsis) + ((None,)*init_state.ndim)]
                init_fwd = np.moveaxis(init_fwd, array.ndim-2, 2)
                array, _zo = scipy.signal.sosfilt(sos_coeffs, array, axis=0, zi=init_fwd)

        return array, _zo

    def integrate(self, array, fs, state, axis=-1, cutoff=[1.,2000],filt_order=3,alpha=1):
        #window = scipy.signal.tukey(len(array),alpha=alpha)
        #array = np.transpose(window*np.transpose(array))
    
        result = scipy.integrate.cumtrapz(array, dx=1/fs, initial=0, axis=axis)
        result = result - result.mean(axis=0)

        result, zf = self.filter_data(result, fs, state, cutoff=cutoff, axis=axis,filt_order=filt_order)
    
        return result, zf

    def fft(self, array, fs):
        N = array.shape[0]
        x_plot= scipy.fft.fftfreq(N, 1/fs)[:N//2]
    
        yf = scipy.fft.fft(array,axis=0) 
        y_plot= 2.0/N * np.abs(yf[0:N//2])
        
        return x_plot,y_plot

    # def getStream(self):
    #     scanRate = self.setting.SAMPLING
    #     avg = self.setting.AVG
    #     numAddresses = self.setting.CHANNEL
    #     mul = np.array(self.setting.MULTIPLIER)
    #     unit = np.array([3.334,3.334,3.334,3.334,3.334,3.334,35.72,35.72])
    #     unit2 = np.array([9810,9810,9810,9810,9810,9810,1,1])

    #     effective_sampling = scanRate / avg
    #     index_multiplier = int(effective_sampling / 20)
    #     index = np.arange(20)
    #     index = index * index_multiplier
    #     index = index + [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9]
        
    #     self.FFT_DATA = np.zeros(((self.setting.SAMPLING*5),self.setting.CHANNEL))
    #     self.labjack.LENGTH = self.setting.SAMPLING
    #     self.labjack.ACQ = True
    #     #self.labjack.send_message("<S,8,10000,5>")
    #     self.labjack.send_message("<S,8,"+str(self.setting.SAMPLING)+",5>")

    #     try:
    #         while self.STREAM:
    #             ts = time.time()
    #             #print("                              STREM qsize:",self.labjack.sec.qsize())
    #             time.sleep(0.001)
    #             x = np.empty((0, self.setting.CHANNEL))
    #             serialBuffer_length = self.labjack.sec.qsize()
    #             while (serialBuffer_length) > 0:
    #                 tmp = self.labjack.sec.get_nowait()
    #                 x = np.append(x, np.array(tmp, dtype='float64'), axis=0)
    #                 serialBuffer_length = serialBuffer_length - 1
    #             #print("                              STREM DATA",x.shape)
    #             #print("                              STREM pend:",self.labjack.sec.qsize())

    #             #x = np.random.random((100,8))
    #             if x.shape[0] == 0:
    #                 continue

    #             x = x * unit
    #             # Multiply
    #             x = x * mul

    #             if self.TEAR_AVG == False:
    #                 self.input_mean = x.mean(0)
    #                 self.TEAR_AVG = True

    #             if self.TEAR_AVG == True:
    #                 x = x - self.input_mean

    #             #FFT Was Here

    #             x, self.LOCALS_ZO = self.filter_data(x, effective_sampling, self.LOCALS_ZO, cutoff=[self.setting.LowerCutoff,self.setting.HigherCutoff], axis=0, filt_order=self.setting.Order)
    #             v, self.LOCALS_vZO = self.integrate(x, effective_sampling, self.LOCALS_vZO, axis=0, cutoff=[self.setting.LowerCutoff,self.setting.HigherCutoff],filt_order=self.setting.Order,alpha=1)
    #             d, self.LOCALS_dZO = self.integrate(v, effective_sampling, self.LOCALS_dZO, axis=0, cutoff=[self.setting.LowerCutoff,self.setting.HigherCutoff],filt_order=self.setting.Order,alpha=1)
    #             diff = np.diff(x,axis=0,prepend=0)
    #             d[:,6:8] = v[:,6:8]
    #             v[:,6:8] = x[:,6:8]
    #             x[:,6:8] = diff[:,6:8]

    #             shift = len(x)
    #             self.FFT_DATA = np.roll(self.FFT_DATA, -shift, axis=0)
    #             self.FFT_DATA[-shift:, :] = x

    #             fft_x,fft_y = self.fft(self.FFT_DATA,effective_sampling)
    #             fft_x = fft_x[1::]
    #             fft_y = fft_y[1::]
    #             fft_argmax = np.argmax(fft_y,axis=0)
    #             self.fft_peak = fft_x[fft_argmax]
    #             #print("                              STREM self.fft_peak",self.fft_peak)

    #             self.lineEdit_C1_F.setText("{:.3f}".format(self.fft_peak[0]))
    #             self.lineEdit_C2_F.setText("{:.3f}".format(self.fft_peak[1]))
    #             self.lineEdit_C3_F.setText("{:.3f}".format(self.fft_peak[2]))
    #             self.lineEdit_C4_F.setText("{:.3f}".format(self.fft_peak[3]))
    #             self.lineEdit_C5_F.setText("{:.3f}".format(self.fft_peak[4]))
    #             self.lineEdit_C6_F.setText("{:.3f}".format(self.fft_peak[5]))
    #             self.lineEdit_C7_F.setText("{:.3f}".format(self.fft_peak[6]))
    #             self.lineEdit_C8_F.setText("{:.3f}".format(self.fft_peak[7]))

    #             v = v * unit2
    #             d = d * unit2

    #             self.accelerationPeak = np.amax(x,axis=0)
    #             self.velocityPeak = np.amax(v,axis=0)
    #             self.displacementPeak = np.amax(d,axis=0)
    #             #print("                                  INDICATORS Peak",np.amax(x,axis=0))

    #             #self.accelerationPeak[0] = 89.888
    #             #self.velocityPeak[0] = 329.897
    #             #self.displacementPeak[0] = 98.789
    #             self.lineEdit_C1_A.setText("{:.3f}".format(self.accelerationPeak[0]))
    #             self.lineEdit_C1_V.setText("{:.3f}".format(self.velocityPeak[0]))
    #             self.lineEdit_C1_D.setText("{:.3f}".format(self.displacementPeak[0]))
    #             self.lineEdit_C2_A.setText("{:.3f}".format(self.accelerationPeak[1]))
    #             self.lineEdit_C2_V.setText("{:.3f}".format(self.velocityPeak[1]))
    #             self.lineEdit_C2_D.setText("{:.3f}".format(self.displacementPeak[1]))
    #             self.lineEdit_C3_A.setText("{:.3f}".format(self.accelerationPeak[2]))
    #             self.lineEdit_C3_V.setText("{:.3f}".format(self.velocityPeak[2]))
    #             self.lineEdit_C3_D.setText("{:.3f}".format(self.displacementPeak[2]))
    #             self.lineEdit_C4_A.setText("{:.3f}".format(self.accelerationPeak[3]))
    #             self.lineEdit_C4_V.setText("{:.3f}".format(self.velocityPeak[3]))
    #             self.lineEdit_C4_D.setText("{:.3f}".format(self.displacementPeak[3]))
    #             self.lineEdit_C5_A.setText("{:.3f}".format(self.accelerationPeak[4]))
    #             self.lineEdit_C5_V.setText("{:.3f}".format(self.velocityPeak[4]))
    #             self.lineEdit_C5_D.setText("{:.3f}".format(self.displacementPeak[4]))
    #             self.lineEdit_C6_A.setText("{:.3f}".format(self.accelerationPeak[5]))
    #             self.lineEdit_C6_V.setText("{:.3f}".format(self.velocityPeak[5]))
    #             self.lineEdit_C6_D.setText("{:.3f}".format(self.displacementPeak[5]))
    #             self.lineEdit_C7_A.setText("{:.3f}".format(self.accelerationPeak[6]))
    #             self.lineEdit_C7_V.setText("{:.3f}".format(self.velocityPeak[6]))
    #             self.lineEdit_C7_D.setText("{:.3f}".format(self.displacementPeak[6]))
    #             self.lineEdit_C8_A.setText("{:.3f}".format(self.accelerationPeak[7]))
    #             self.lineEdit_C8_V.setText("{:.3f}".format(self.velocityPeak[7]))
    #             self.lineEdit_C8_D.setText("{:.3f}".format(self.displacementPeak[7]))

    #             if self.fft_peak[0] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[0]][0] = self.displacementPeak[0]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[0]] = {}
    #                 self.LOG_DATA[self.fft_peak[0]][0] = self.displacementPeak[0]
    #             if self.fft_peak[1] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[1]][1] = self.displacementPeak[1]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[1]] = {}
    #                 self.LOG_DATA[self.fft_peak[1]][1] = self.displacementPeak[1]
    #             if self.fft_peak[2] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[2]][2] = self.displacementPeak[2]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[2]] = {}
    #                 self.LOG_DATA[self.fft_peak[2]][2] = self.displacementPeak[2]
    #             if self.fft_peak[3] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[3]][3] = self.displacementPeak[3]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[3]] = {}
    #                 self.LOG_DATA[self.fft_peak[3]][3] = self.displacementPeak[3]
    #             if self.fft_peak[4] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[4]][4] = self.displacementPeak[4]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[4]] = {}
    #                 self.LOG_DATA[self.fft_peak[4]][4] = self.displacementPeak[4]
    #             if self.fft_peak[5] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[5]][5] = self.displacementPeak[5]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[5]] = {}
    #                 self.LOG_DATA[self.fft_peak[5]][5] = self.displacementPeak[5]
    #             if self.fft_peak[6] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[6]][6] = self.displacementPeak[6]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[6]] = {}
    #                 self.LOG_DATA[self.fft_peak[6]][6] = self.displacementPeak[6]
    #             if self.fft_peak[7] in self.LOG_DATA:
    #                 self.LOG_DATA[self.fft_peak[7]][7] = self.displacementPeak[7]
    #             else:
    #                 self.LOG_DATA[self.fft_peak[7]] = {}
    #                 self.LOG_DATA[self.fft_peak[7]][7] = self.displacementPeak[7]

    #             x = np.hstack([x,v,d])
    #             # Store Data in Buffer for File
    #             self.f.put(x)

    #             if x.shape[0] < 20:
    #                 self.q.put(x)
    #             elif x.shape[0] >= 20 and (x.shape[0] % 20 == 0):
    #                 x_split = np.split(x, 20)
    #                 for x_sub in x_split:
    #                     self.q.put(x_sub)
    #             else:
    #                 x_split = np.split(x, index[1:])
    #                 for x_sub in x_split:
    #                     self.q.put(x_sub)
    #             #print("F %d" % self.q.qsize())
    #             #print("                              STREM Time",(time.time()-ts)*1000)
    #             time.sleep(0.001)
            # '''
            # def myStreamReadCallback(arg):
            #     ret = ljm.eStreamRead(self.labjack.handle)
            #     result = ret[0]
            #     # print("Device %d" % ret[1])    #deviceScanBacklog
            #     # print("Ljm Lib %d" % ret[2])    #ljmScanBackLog
            #     # print("-------------------")
            #     x = np.column_stack((result[::14], result[1::14], result[2::14], result[3::14], result[4::14],
            #                          result[5::14], result[6::14], result[7::14], result[8::14], result[9::14],
            #                          result[10::14], result[11::14], result[12::14], result[13::14]))
            #     x = x.reshape(-1, avg, 14).mean(1)
            #     x = lfilter(b, a, x)
            #     # Multiply
            #     x = x * mul

            #     # TEAR
            #     # if self.TEAR_AVG == True:
            #     #     x = x - self.input_mean

            #     if self.TEAR_AVG == False:
            #         self.input_mean = x.mean(0)
            #         self.TEAR_AVG = True

            #     if self.TEAR_AVG == True:
            #         x = x - self.input_mean

            #     # Store Data in Buffer for File
            #     self.f.put(x)

            #     if x.shape[0] < 20:
            #         self.q.put(x)
            #     elif x.shape[0] >= 20 and (x.shape[0] % 20 == 0):
            #         x_split = np.split(x, 20)
            #         for x_sub in x_split:
            #             self.q.put(x_sub)
            #     else:
            #         x_split = np.split(x, index[1:])
            #         for x_sub in x_split:
            #             self.q.put(x_sub)
            #     # print("F %d" % self.q.qsize())
            #     if not self.STREAM:
            #         ljm.eStreamStop(self.labjack.handle)

            # stream = ljm.eStreamStart(self.labjack.handle, scansPerRead, numAddresses, scanList, scanRate)
            # ljm.setStreamCallback(self.labjack.handle, myStreamReadCallback)
            # '''
        # except:
        #     print("ERROR:")






######################################################################################################################################################################################################################################################
    def getStream(self):
      


            
            # d.streamStart()

            
            # i = 0
            

        data1 = d.streamData()
        
                
        for packet in data1:
            for key, value in packet.items():
                if isinstance(value, (int, bytes)):
                    continue
                else:
                    for x in value:
                            
                        print(x)
                        
                        self.q.put(x)
                        #elemm = self.q[-1]
                        #print(elemm)


        #else:
        # os._exit(1)
            
        time.sleep(0.01)


#the changes have been made in only the enclosed part,please take a look               
###################################################################################################################################################################################################################################################














    def update_plot(self):
        #self.st = time.time()
        # print(self.threadpool.activeThreadCount())
        try:
            data = [0]
            one = True
            plot_type = self.tabWidget.currentIndex()
            while one:
                try:
                    time.sleep(0.1)
                    data = self.q.get_nowait()
                    buffer_length = self.q.qsize()
                    print(buffer_length)
                    #print("                    PLOT Buffer",buffer_length)
                    while (buffer_length - 19) > 0:
                        data = np.append(data, self.q.get_nowait(), axis=0)
                        buffer_length = buffer_length - 1
                        print(buffer_length)
                except queue.Empty: 
                    if self.OFFLINE == False:
                        break

                if self.OFFLINE == False:
                    shift = len(data)
                    # print(self.q.qsize())
                    self.plotdata = np.roll(self.plotdata, -shift, axis=0)
                    self.plotdata[-shift:, :] = data
                    #self.xyplotData = np.append(self.xyplotData, data, axis=0)
                elif self.OFFLINE == True:
                    shift = 0
                    self.plotdata = self.offlinedata

                #print("                                                             UPDATE type",plot_type)
                if plot_type == 2:
                    #if self.OFFLINE == False:
                    self.C1plotDataA = self.plotdata[:, 0]
                    self.C1plotDataV = self.plotdata[:, 8]
                    self.C1plotDataD = self.plotdata[:, 16]
                    self.C2plotDataA = self.plotdata[:, 1]
                    self.C2plotDataV = self.plotdata[:, 9]
                    self.C2plotDataD = self.plotdata[:, 17]
                    self.C3plotDataA = self.plotdata[:, 2]
                    self.C3plotDataV = self.plotdata[:, 10]
                    self.C3plotDataD = self.plotdata[:, 18]
                    #elif self.OFFLINE == True:
                        #pass
                    if self.W1plot_ref is None:
                        self.W1plot_ref = True
                    else:
                        self.C1plotLineRefA.setData(self.C1plotDataA, pen=self.setting.allPlotEnable['C1A'],sampling=self.setting.SAMPLING)
                        self.C1plotLineRefV.setData(self.C1plotDataV, pen=self.setting.allPlotEnable['C1V'],sampling=self.setting.SAMPLING)
                        self.C1plotLineRefD.setData(self.C1plotDataD, pen=self.setting.allPlotEnable['C1D'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefA.setData(self.C2plotDataA, pen=self.setting.allPlotEnable['C2A'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefV.setData(self.C2plotDataV, pen=self.setting.allPlotEnable['C2V'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefD.setData(self.C2plotDataD, pen=self.setting.allPlotEnable['C2D'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefA.setData(self.C3plotDataA, pen=self.setting.allPlotEnable['C3A'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefV.setData(self.C3plotDataV, pen=self.setting.allPlotEnable['C3V'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefD.setData(self.C3plotDataD, pen=self.setting.allPlotEnable['C3D'],sampling=self.setting.SAMPLING)

                elif plot_type == 1:
                    #if self.OFFLINE == False:
                    self.C4plotDataA = self.plotdata[:, 3]
                    self.C4plotDataV = self.plotdata[:, 11]
                    self.C4plotDataD = self.plotdata[:, 19]
                    self.C5plotDataA = self.plotdata[:, 4]
                    self.C5plotDataV = self.plotdata[:, 12]
                    self.C5plotDataD = self.plotdata[:, 20]
                    self.C6plotDataA = self.plotdata[:, 5]
                    self.C6plotDataV = self.plotdata[:, 13]
                    self.C6plotDataD = self.plotdata[:, 21]
                    #elif self.OFFLINE == True:
                        #pass
                    if self.W2plot_ref is None:
                        self.W2plot_ref = True
                    else:
                        self.C4plotLineRefA.setData(self.C4plotDataA, pen=self.setting.allPlotEnable['C4A'],sampling=self.setting.SAMPLING)
                        self.C4plotLineRefV.setData(self.C4plotDataV, pen=self.setting.allPlotEnable['C4V'],sampling=self.setting.SAMPLING)
                        self.C4plotLineRefD.setData(self.C4plotDataD, pen=self.setting.allPlotEnable['C4D'],sampling=self.setting.SAMPLING)
                        self.C5plotLineRefA.setData(self.C5plotDataA, pen=self.setting.allPlotEnable['C5A'],sampling=self.setting.SAMPLING)
                        self.C5plotLineRefV.setData(self.C5plotDataV, pen=self.setting.allPlotEnable['C5V'],sampling=self.setting.SAMPLING)
                        self.C5plotLineRefD.setData(self.C5plotDataD, pen=self.setting.allPlotEnable['C5D'],sampling=self.setting.SAMPLING)
                        self.C6plotLineRefA.setData(self.C6plotDataA, pen=self.setting.allPlotEnable['C6A'],sampling=self.setting.SAMPLING)
                        self.C6plotLineRefV.setData(self.C6plotDataV, pen=self.setting.allPlotEnable['C6V'],sampling=self.setting.SAMPLING)
                        self.C6plotLineRefD.setData(self.C6plotDataD, pen=self.setting.allPlotEnable['C6D'],sampling=self.setting.SAMPLING)
                elif plot_type == 3:
                    #if self.OFFLINE == False:
                    self.C7plotDataA = self.plotdata[:, 6]
                    self.C7plotDataV = self.plotdata[:, 14]
                    self.C7plotDataD = self.plotdata[:, 22]
                    self.C8plotDataA = self.plotdata[:, 7]
                    self.C8plotDataV = self.plotdata[:, 15]
                    self.C8plotDataD = self.plotdata[:, 23]
                    #elif self.OFFLINE == True:
                        #pass
                    if self.W4plot_ref is None:
                        self.W4plot_ref = True
                    else:
                        self.C7plotLineRefA.setData(self.C7plotDataA, pen=self.setting.allPlotEnable['C7A'],sampling=self.setting.SAMPLING)
                        self.C7plotLineRefV.setData(self.C7plotDataV, pen=self.setting.allPlotEnable['C7V'],sampling=self.setting.SAMPLING)
                        self.C7plotLineRefD.setData(self.C7plotDataD, pen=self.setting.allPlotEnable['C7D'],sampling=self.setting.SAMPLING)
                        self.C8plotLineRefA.setData(self.C8plotDataA, pen=self.setting.allPlotEnable['C8A'],sampling=self.setting.SAMPLING)
                        self.C8plotLineRefV.setData(self.C8plotDataV, pen=self.setting.allPlotEnable['C8V'],sampling=self.setting.SAMPLING)
                        self.C8plotLineRefD.setData(self.C8plotDataD, pen=self.setting.allPlotEnable['C8D'],sampling=self.setting.SAMPLING)
                elif plot_type == 4:
                    if self.OFFLINE == False:
                        self.TplotData1 = self.plotdata[:, 0]
                        self.TplotData2 = self.plotdata[:, 1]
                        self.TplotData3 = self.plotdata[:, 2]
                        self.TplotData4 = self.plotdata[:, 3]
                        self.TplotData5 = self.plotdata[:, 4]
                        self.TplotData6 = self.plotdata[:, 5]
                        self.TplotData7 = self.plotdata[:, 6]
                        self.TplotData8 = self.plotdata[:, 7]

                        self.TplotData1[-shift:] = self.TplotData1[-shift:] + self.setting.timePlotOffset[0]
                        self.TplotData2[-shift:] = self.TplotData2[-shift:] + self.setting.timePlotOffset[1]
                        self.TplotData3[-shift:] = self.TplotData3[-shift:] + self.setting.timePlotOffset[2]
                        self.TplotData4[-shift:] = self.TplotData4[-shift:] + self.setting.timePlotOffset[3]
                        self.TplotData5[-shift:] = self.TplotData5[-shift:] + self.setting.timePlotOffset[4]
                        self.TplotData6[-shift:] = self.TplotData6[-shift:] + self.setting.timePlotOffset[5]
                        self.TplotData7[-shift:] = self.TplotData7[-shift:] + self.setting.timePlotOffset[6]
                        self.TplotData8[-shift:] = self.TplotData8[-shift:] + self.setting.timePlotOffset[7]
                    elif self.OFFLINE == True:
                        self.TplotData1 = self.plotdata[:, 0] + self.setting.timePlotOffset[0]
                        self.TplotData2 = self.plotdata[:, 1] + self.setting.timePlotOffset[1]
                        self.TplotData3 = self.plotdata[:, 2] + self.setting.timePlotOffset[2]
                        self.TplotData4 = self.plotdata[:, 3] + self.setting.timePlotOffset[3]
                        self.TplotData5 = self.plotdata[:, 4] + self.setting.timePlotOffset[4]
                        self.TplotData6 = self.plotdata[:, 5] + self.setting.timePlotOffset[5]
                        self.TplotData7 = self.plotdata[:, 6] + self.setting.timePlotOffset[6]
                        self.TplotData8 = self.plotdata[:, 7] + self.setting.timePlotOffset[7]

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
                    else:
                        self.TplotLineRef1.setData(self.TplotData1, pen=self.setting.timePlotEnable[0],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef2.setData(self.TplotData2, pen=self.setting.timePlotEnable[1],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef3.setData(self.TplotData3, pen=self.setting.timePlotEnable[2],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef4.setData(self.TplotData4, pen=self.setting.timePlotEnable[3],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef5.setData(self.TplotData5, pen=self.setting.timePlotEnable[4],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef6.setData(self.TplotData6, pen=self.setting.timePlotEnable[5],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef7.setData(self.TplotData7, pen=self.setting.timePlotEnable[6],
                                                   sampling=self.setting.SAMPLING)
                        self.TplotLineRef8.setData(self.TplotData8, pen=self.setting.timePlotEnable[7],
                                                   sampling=self.setting.SAMPLING)
                elif plot_type == 6:
                    if self.OFFLINE == False:
                        self.C1plotDataA = self.plotdata[:, 0]    #0
                        self.C1plotDataV = self.plotdata[:, 4]    #8
                        self.C1plotDataD = self.plotdata[:, 8]    #16
                        self.C2plotDataA = self.plotdata[:, 1]    #1
                        self.C2plotDataV = self.plotdata[:, 5]    #9
                        self.C2plotDataD = self.plotdata[:, 9]    #17
                        self.C3plotDataA = self.plotdata[:, 2]    #2
                        self.C3plotDataV = self.plotdata[:, 6]    #10
                        self.C3plotDataD = self.plotdata[:, 10]   #18
                    elif self.OFFLINE == True:
                        pass
                    if self.Aplot_ref is None:
                        self.Aplot_ref = True
                        self.C1plotLineRefA = self.C1plotItem.plot()
                        self.C1plotLineRefV = self.C1plotItem.plot()
                        self.C1plotLineRefD = self.C1plotItem.plot()
                        self.C2plotLineRefA = self.C2plotItem.plot()
                        self.C2plotLineRefV = self.C2plotItem.plot()
                        self.C2plotLineRefD = self.C2plotItem.plot()
                        self.C3plotLineRefA = self.C3plotItem.plot()
                        self.C3plotLineRefV = self.C3plotItem.plot()
                        self.C3plotLineRefD = self.C3plotItem.plot()
                    else:
                        self.C1plotLineRefA.setData(self.C1plotDataA, pen=self.setting.allPlotEnable['C1A'],sampling=self.setting.SAMPLING)
                        self.C1plotLineRefV.setData(self.C1plotDataV, pen=self.setting.allPlotEnable['C1V'],sampling=self.setting.SAMPLING)
                        self.C1plotLineRefD.setData(self.C1plotDataD, pen=self.setting.allPlotEnable['C1D'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefA.setData(self.C2plotDataA, pen=self.setting.allPlotEnable['C2A'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefV.setData(self.C2plotDataV, pen=self.setting.allPlotEnable['C2V'],sampling=self.setting.SAMPLING)
                        self.C2plotLineRefD.setData(self.C2plotDataD, pen=self.setting.allPlotEnable['C2D'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefA.setData(self.C3plotDataA, pen=self.setting.allPlotEnable['C3A'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefV.setData(self.C3plotDataV, pen=self.setting.allPlotEnable['C3V'],sampling=self.setting.SAMPLING)
                        self.C3plotLineRefD.setData(self.C3plotDataD, pen=self.setting.allPlotEnable['C3D'],sampling=self.setting.SAMPLING)
                    
                one = False
        except:
            pass
        #print("          PLOT",(time.time()-self.st)*1000)

    def event_SettingWrite(self):
        gains = []
        alias = []
        multis = []
        sampling = int(self.lineEditSampling.text())
        window = int(self.lineEditWindow.text())
        avg = int(self.lineEditAvg.text())

        for i in range(self.setting.CHANNEL):
            comboWidget_name = getattr(self, "comboBoxGainC%d" % (i + 1))
            gains.append(comboWidget_name.currentIndex())
            lineWidget_name = getattr(self, "lineEditAliasC%d" % (i + 1))
            alias.append(lineWidget_name.text())
            lineMulti_name = getattr(self, "lineEditMultiC%d" % (i + 1))
            multis.append(float(lineMulti_name.text()))

        self.setting.setValues(gains, alias, multis, sampling, window, avg)

    def event_SettingDefault(self):
        self.setting.setDefault()
        for i in range(self.setting.CHANNEL):
            comboWidget_name = getattr(self, "comboBoxGainC%d" % (i + 1))
            comboWidget_name.setCurrentIndex(self.setting.GAINS[i])
            lineWidget_name = getattr(self, "lineEditAliasC%d" % (i + 1))
            lineWidget_name.setText(self.setting.ALIAS[i])
        self.lineEditSampling.setText(str(self.setting.SAMPLING))
        self.lineEditWindow.setText(str(self.setting.WINDOW))

    def event_SettingXYcolor(self):
        color = QtWidgets.QColorDialog.getColor()
        self.setting.XY_R = color.getRgb()[0]
        self.setting.XY_G = color.getRgb()[1]
        self.setting.XY_B = color.getRgb()[2]

    def event_SettingXYpen(self):
        color = QtWidgets.QColorDialog.getColor()
        color_hex = '#' + format(color.getRgb()[0], '02x') + format(color.getRgb()[1], '02x') + format(
            color.getRgb()[2], '02x')
        self.setting.XY_pen = color_hex

    def updateSetting(self):
        for i in range(self.setting.CHANNEL):
            comboWidget_name = getattr(self, "comboBoxGainC%d" % (i + 1))
            comboWidget_name.setCurrentIndex(self.setting.GAINS[i])
            lineWidget_name = getattr(self, "lineEditAliasC%d" % (i + 1))
            lineWidget_name.setText(self.setting.ALIAS[i])
            lineWidgetMulti_name = getattr(self, "lineEditMultiC%d" % (i + 1))
            lineWidgetMulti_name.setText(str(self.setting.MULTIPLIER[i]))

        self.lineEditSampling.setText(str(self.setting.SAMPLING))
        self.lineEditWindow.setText(str(self.setting.WINDOW))
        self.lineEditAvg.setText(str(self.setting.AVG))

    def readHeader(self, str):
        gains = self.setting.GAINS
        header_str = str.strip().split('\n')

        line_str = header_str[0].split(',')
        sampling = int(line_str[1])
        window = int(line_str[3])
        avg = int(line_str[5])

        alias = header_str[1].split(',')

        multis = header_str[2].split(',')
        multis = [float(i) for i in multis]

        self.setting.setValues(gains, alias, multis, sampling, window, avg)

        x = header_str[3].split(',')
        y = header_str[4].split(',')
        xmin = header_str[5].split(',')
        xmax = header_str[6].split(',')
        ymin = header_str[7].split(',')
        ymax = header_str[8].split(',')
        for i in range(16):
            self.setting.setXYplotX(int(x[i]), i)
            self.setting.setXYplotY(int(y[i]), i)
            self.setting.setXYplotXmin(float(xmin[i]), i)
            self.setting.setXYplotXmax(float(xmax[i]), i)
            self.setting.setXYplotYmin(float(ymin[i]), i)
            self.setting.setXYplotYmax(float(ymax[i]), i)
        self.updateSetting()

    def writeHeader(self, fHandle):
        fHandle.write('Sampling Rate(Hz),' + str(self.setting.SAMPLING) + ',Window Size,' + str(self.setting.WINDOW) + ',Average,' + str(
            self.setting.AVG) + ',' + self.setting.AUTHOR + ',' + self.setting.DESCRIPTION.replace("\n", "-"))
        fHandle.write('\n')
        fHandle.write(''.join(s + ',' for s in self.setting.ALIAS)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.MULTIPLIER)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_X)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_Y)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_XMIN)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_XMAX)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_YMIN)[:-1])
        fHandle.write('\n')
        fHandle.write(''.join(str(s) + ',' for s in self.setting.XYPLOT_YMAX)[:-1])
        fHandle.write('\n')
        fHandle.write(self.setting.ALIAS[0]+'_Acc(g),' + self.setting.ALIAS[1]+'_Acc(g),' + self.setting.ALIAS[2]+'_Acc(g),' + self.setting.ALIAS[3]+'_Acc(g),' + self.setting.ALIAS[4]+'_Acc(g),' + self.setting.ALIAS[5]+'_Acc(g),' + self.setting.ALIAS[6]+'_Acc(g),' + self.setting.ALIAS[7]+'_Acc(g),' + self.setting.ALIAS[0]+'_Vel(mm/s),' + self.setting.ALIAS[1]+'_Vel(mm/s),' + self.setting.ALIAS[2]+'_Vel(mm/s),' + self.setting.ALIAS[3]+'_Vel(mm/s),' + self.setting.ALIAS[4]+'_Vel(mm/s),' + self.setting.ALIAS[5]+'_Vel(mm/s),' + self.setting.ALIAS[6]+'_Vel(mm/s),' + self.setting.ALIAS[7]+'_Vel(mm/s),' + self.setting.ALIAS[0]+'_Dis(mm),' + self.setting.ALIAS[1]+'_Dis(mm),' + self.setting.ALIAS[2]+'_Dis(mm),' + self.setting.ALIAS[3]+'_Dis(mm),' + self.setting.ALIAS[4]+'_Dis(mm),' + self.setting.ALIAS[5]+'_Dis(mm),' + self.setting.ALIAS[6]+'_Dis(mm),' + self.setting.ALIAS[7]+'_Dis(mm)')
        fHandle.write('\n')

    def event_start(self):
        f = open('config.config', 'r')
        self.readHeader(f.read())
        f.close

    def event_exit(self):
        self.labjack.disconnect()
        
        f = open('config.config', 'w')
        self.writeHeader(f)
        f.close()

        log_df = pd.DataFrame.from_dict(data=self.LOG_DATA, orient='index')
        log_df.fillna(0,inplace=True)
        log_df.sort_index(axis=0, inplace=True)
        if not log_df.empty:
            cols = [self.setting.ALIAS[0]+'_Dis(mm)', self.setting.ALIAS[1]+'_Dis(mm)', self.setting.ALIAS[2]+'_Dis(mm)', self.setting.ALIAS[3]+'_Dis(mm)', self.setting.ALIAS[4]+'_Dis(mm)', self.setting.ALIAS[5]+'_Dis(mm)', self.setting.ALIAS[6]+'_Dis(mm)', self.setting.ALIAS[7]+'_Dis(mm)']
            log_df.to_csv(self.setting.FILENAME+'_AutoLog.csv', header=cols, index_label='Freq(Hz)')
        
        logMan_df = pd.DataFrame.from_dict(data=self.LOG_MAN, orient='index')
        logMan_df.fillna(0,inplace=True)
        logMan_df.sort_index(axis=0, inplace=True)
        if not logMan_df.empty:
            cols = [self.setting.ALIAS[0]+'_Dis(mm)', self.setting.ALIAS[1]+'_Dis(mm)', self.setting.ALIAS[2]+'_Dis(mm)', self.setting.ALIAS[3]+'_Dis(mm)', self.setting.ALIAS[4]+'_Dis(mm)', self.setting.ALIAS[5]+'_Dis(mm)', self.setting.ALIAS[6]+'_Dis(mm)', self.setting.ALIAS[7]+'_Dis(mm)']
            logMan_df.to_csv(self.setting.FILENAME+'_ManLogDisplacement.csv', header=cols, index_label='Freq(Hz)')

        logManVel_df = pd.DataFrame.from_dict(data=self.LOG_MAN_vel, orient='index')
        logManVel_df.fillna(0,inplace=True)
        logManVel_df.sort_index(axis=0, inplace=True)
        if not logManVel_df.empty:
            cols = [self.setting.ALIAS[0]+'_Vel(mm/s)', self.setting.ALIAS[1]+'_Vel(mm/s)', self.setting.ALIAS[2]+'_Vel(mm/s)', self.setting.ALIAS[3]+'_Vel(mm/s)', self.setting.ALIAS[4]+'_Vel(mm/s)', self.setting.ALIAS[5]+'_Vel(mm/s)', self.setting.ALIAS[6]+'_Vel(mm/s)', self.setting.ALIAS[7]+'_Vel(mm/s)']
            logManVel_df.to_csv(self.setting.FILENAME+'_ManLogVelocity.csv', header=cols, index_label='Freq(Hz)')

        logManAcc_df = pd.DataFrame.from_dict(data=self.LOG_MAN_acc, orient='index')
        logManAcc_df.fillna(0,inplace=True)
        logManAcc_df.sort_index(axis=0, inplace=True)
        if not logManAcc_df.empty:
            cols = [self.setting.ALIAS[0]+'_Acc(g)', self.setting.ALIAS[1]+'_Acc(g)', self.setting.ALIAS[2]+'_Acc(g)', self.setting.ALIAS[3]+'_Acc(g)', self.setting.ALIAS[4]+'_Acc(g)', self.setting.ALIAS[5]+'_Acc(g)', self.setting.ALIAS[6]+'_Acc(g)', self.setting.ALIAS[7]+'_Acc(g)']
            logManAcc_df.to_csv(self.setting.FILENAME+'_ManLogAcceleration.csv', header=cols, index_label='Freq(Hz)')


class Setting:
    def __init__(self):
        self.GAINS = []
        self.ALIAS = []
        self.MULTIPLIER = []
        self.SAMPLING = 0
        self.AVG = 0
        self.WINDOW = 0
        self.CHANNEL = 8
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
        self.FILENAME = ''
        self.AUTHOR = ''
        self.DESCRIPTION = ''
        self.XY_R = 0
        self.XY_G = 0
        self.XY_B = 0
        self.XY_pen = '#FFF'
        self.setDefault()  # Remove LATER
        self.timePlotColors = ['#000', '#F00', '#0F0', '#00F', '#FF0', '#0FF', '#F0F', '#500', '#050', '#005', '#550',
                               '#055', '#505', '#555']
        self.timePlotEnable = ['#000', '#F00', '#0F0', '#00F', '#FF0', '#0FF', '#F0F', '#500', '#050', '#005', '#550',
                               '#055', '#505', '#555']
        self.timePlotOffset = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.allPlotEnable = {'C1A':'#000', 'C1V':'#F00', 'C1D':'#00F','C2A':'#000', 'C2V':'#F00', 'C2D':'#00F','C3A':'#000', 'C3V':'#F00', 'C3D':'#00F','C4A':'#000', 'C4V':'#F00', 'C4D':'#00F','C5A':'#000', 'C5V':'#F00', 'C5D':'#00F','C6A':'#000', 'C6V':'#F00', 'C6D':'#00F','C7A':'#000', 'C7V':'#F00', 'C7D':'#00F','C8A':'#000', 'C8V':'#F00', 'C8D':'#00F'}
        self.allPlotColors = {'C1A':'#000', 'C1V':'#F00', 'C1D':'#00F','C2A':'#000', 'C2V':'#F00', 'C2D':'#00F','C3A':'#000', 'C3V':'#F00', 'C3D':'#00F','C4A':'#000', 'C4V':'#F00', 'C4D':'#00F','C5A':'#000', 'C5V':'#F00', 'C5D':'#00F','C6A':'#000', 'C6V':'#F00', 'C6D':'#00F','C7A':'#000', 'C7V':'#F00', 'C7D':'#00F','C8A':'#000', 'C8V':'#F00', 'C8D':'#00F'}
        self.LowerCutoff = 1
        self.HigherCutoff = 20
        self.Order = 3
        self.FilterEnable = False
        self.FFTbins = 50000

    def setDefault(self):
        self.GAINS = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # index to "self.gains". Not Actual values
        #self.A LIAS = ['Channel 01', 'Channel 02', 'Channel 03', 'Channel 04', 'Channel 05', 'Channel 06', 'Channel 07',
                      #'Channel 08', 'Channel 09', 'Channel 10', 'Channel 11', 'Channel 12', 'Channel 13', 'Channel 14']
        self.ALIAS = ['Channel 01', 'Channel 02', 'Channel 03', 'Channel 04', 'Channel 05', 'Channel 06', 'Channel 07', 'Channel 08']
        self.MULTIPLIER = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.SAMPLING = 100
        self.AVG = 10
        self.WINDOW = 1000
        self.CHANNEL = 8
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
        self.XY_R = 1
        self.XY_G = 50
        self.XY_B = 32
        self.XYPLOT_X = [0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0]  # index to "self.setting.ALIAS-CHANNEL Number 0..". Not Actual values
        self.XYPLOT_Y = [10, 11, 12, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0]  # index to "self.setting.ALIAS-CHANNEL Number 0..". Not Actual values
        self.XYPLOT_XMIN = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]
        self.XYPLOT_XMAX = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.XYPLOT_YMIN = [-10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10]
        self.XYPLOT_YMAX = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]

    def setValues(self, gains, alias, multiplier, sampling, window, avg):
        self.GAINS = gains
        self.ALIAS = alias
        self.SAMPLING = sampling
        self.MULTIPLIER = multiplier
        self.WINDOW = window
        self.AVG = avg

    def setSampling(self, sampling):
        self.SAMPLING = sampling

    def setWindow(self, window):
        self.WINDOW = window

    def setAvg(self, avg):
        self.AVG = avg

    # Multiplier
    def setMultiplier(self, channel, value):
        self.MULTIPLIER[channel] = value

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

    # ALL Plot - Enable
    def setAllPlotEnable(self, channel, chk):
        if chk == 0:
            self.allPlotEnable[channel] = None
        elif chk == 2:
            self.allPlotEnable[channel] = self.allPlotColors[channel]

    # Time Plot - Colors
    def setTimePlotColor(self, channel, value):
        self.timePlotColors[channel] = value
        if self.timePlotEnable[channel] != None:
            self.timePlotEnable[channel] = self.timePlotColors[channel]

    # Time Plot - Offset
    def setTimePlotOffset(self, channel, value):
        self.timePlotOffset[channel] = value

    # Session - Description
    def setSession(self, sName, sAuth, sDesc):
        self.FILENAME = sName
        self.AUTHOR = sAuth
        self.DESCRIPTION = sDesc

    # Filter - Setting
    def setFilter(self, lcut, hcut, order):
        self.LowerCutoff = lcut
        self.HigherCutoff = hcut
        self.Order = order


class Labjack:

    # plt = PLOT()
    def __init__(self):
        self.RANGE_VALUES = [10.0, 1.0, 0.1, 0.01] # Map to "self.gains". Actual values
        self.AIN_NAMES = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5"]

        #self.device = u3.U3()
        #print("Device info: ", self.device.configU3())
        

    def writeGain(self,gainIndex):
        self.writeRegister(5000, sum([1<<g for g in gainIndex]))
        print("Wrote Gains")

    def readGain(self):
        ranges = "ranges"
        #results = self.device.readRegister(5000)
        #ranges = [self.RANGE_VALUES[((int(results) >> (2*i)) & 3)] for i in range(6)]
        print(ranges)
        #self.device.close()
        
     


    # def volt(self):
    #       d = u3.U3()

    #       # Read from all available analog inputs
    #       for channel in range(0,19):
    #           try:
    #               # Read the voltage from the channel
    #               voltage = d.getAIN(channel)
    #               print(f"Voltage reading on channel {channel}: {voltage:.2f} V")
    #           except:
    #               # If the voltage reading is not available, print a message
    #               print(f"Channel {channel} not being read")

    #       # Close the LabJack U3 device
    #       d.close()


    # def volt2(self):
    #     self.worker_volt = Worker(self.volt)
    #     self.threadpool.start(worker_volt)
        
    # def connect(self):
    #     connectDialog = PortDialog()
    #     if connectDialog.exec_():
    #         self.PORT = connectDialog.dd.currentText()
    #         if self.PORT != '':
    #             self.COM = serial.Serial(self.PORT, 115200, timeout = 0.1)
    #             print(self.COM)
    #             self.acq_stream = Worker(self.tennsyIO, )
    #             self.pack_stream = Worker(self.packet, )
    #             self.threadpool.start(self.acq_stream)
    #             self.threadpool.start(self.pack_stream)
    #         else:
    #             print(self.COM)

    # def disconnect(self):
    #     self.COM.close()
    #     self.COM = None
    
    # def send_message(self, message):
    #     self.RTS = True
    #     self.COM.write(message.encode('utf-8'))
    #     self.RTS = False

    # def tennsyIO(self):
    #     while self.COM != None:
    #         #print("LOOP")
    #         time.sleep(0.000000001)
    #         if self.ACQ and not self.RTS:
    #             #rs = time.time()
    #             self.raw.put(self.COM.read(800000))
    #             #self.raw.put(self.COM.read(self.COM.in_waiting))
    #             #print("                            **********", self.COM.in_waiting)
    #             #print("ACQ L",self.raw.qsize())
    #             #print("ACQ T",(time.time()-rs)*1000)

    # def packet(self):
    #     test_miss = 0
    #     while self.COM != None:
    #         #print("PACK")
    #         ps = time.time()
    #         serialBuffer_length = self.raw.qsize()
    #         #print("PACK qsize:",serialBuffer_length)
    #         tmp = []
    #         while (serialBuffer_length):
    #             tmp.append(self.raw.get_nowait())
    #             serialBuffer_length = serialBuffer_length - 1
    #         #print("PACK read:",len(tmp))
    #         #print("PACK pend:",self.raw.qsize())
    #         if len(tmp) != 0:
    #             tmp = b''.join(tmp)
    #             tmp = tmp.split(b'\n')
    #             #print("Length",len(tmp))
    #             if len(tmp) == 1:
    #                 #print("PACK",tmp)
    #                 continue
    #             if self.FILE_INIT:
    #                 tmp = tmp[1:]
    #                 self.FILE_INIT = False
    #             else:
    #                 #print(tmp[0])
    #                 if len(tmp[0]) == 0:
    #                     tmp[0] = prev_byte_sample
    #                 elif len(prev_byte_sample) != 0:
    #                     tmp[0] = prev_byte_sample+tmp[0]
    #                 else:
    #                     pass
    #             prev_byte_sample = tmp[-1]
    #             tmp = tmp[:-1]
    #             #print(tmp[0])
    #             #print(prev_byte_sample)
    #             #print("---------------")
    #             #print("                    PACKET-B",len(self.PACKET))
    #             #print("                    PENDING-B",len(self.PENDING))
    #             self.PACKET = self.PENDING + self.PACKET
    #             self.PACKET.extend(tmp)
    #             self.PENDING = []
    #             #print("                    PACKET-A",len(self.PACKET))
    #             #print("                    PENDING-A",len(self.PENDING))
    #             if len(self.PACKET) >= self.LENGTH:
    #                 hex_data = self.PACKET[0:self.LENGTH]
    #                 self.PENDING = self.PACKET[self.LENGTH:]
    #                 self.PACKET = []

    #                 hex_data = [x.decode("utf-8").strip() for x in hex_data]
    #                 dec_channel = [[self.hex2sint(y) for y in x.strip(',').split(',')] for x in hex_data if x[:-1].count(',')==7]
    #                 self.MISSED = self.MISSED + (self.LENGTH-len(dec_channel))
    #                 #print("                                                            ----------MISSED",self.MISSED)
    #                 if test_miss != self.MISSED:
    #                     test_miss = self.MISSED
    #                     # with open("MISS_" + str(test_miss), 'w+') as f:
    #                         # f.write("\n".join(hex_data))
    #                     # f.close()
    #                     # print("    Previous Byte",prev_byte_sample)
    #                 self.sec.put(dec_channel)
    #                 #print("                    PENDING-Sec",self.sec.qsize())
    #                 #x = np.array(dec_channel)
    #                 #print("                    PENDING-Numpy",x.shape)
    #         time.sleep(0.001)

    # def hex2sint(self,val):
    #     if len(val) == 0:
    #         val = '0'
    #     try:
    #         tmp = int(val,16)
    #     except:
    #         tmp = 0
    #     return "{:.5f}".format(tmp * self.SCALE_FACTOR) if tmp < 32768 else "{:.5f}".format((65535 - tmp) * -1 * self.SCALE_FACTOR)



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
        uic.loadUi('images/plot_dlg.ui', self)


class NewSessionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('images/session_dlg.ui', self)


class PortDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        dropdownChoices = [port.name for port in serial.tools.list_ports.comports() if port.pid==1155]

        layout = QtWidgets.QVBoxLayout()
        self.dd = QtWidgets.QComboBox()
        self.dd.addItems(dropdownChoices)
        self.formGroupBox = QtWidgets.QGroupBox("")
        formbox = QtWidgets.QFormLayout()
        formbox.addRow(QtWidgets.QLabel("Available Ports"), self.dd)
        self.formGroupBox.setLayout(formbox)
        layout.addWidget(self.formGroupBox)

        buttonHolder = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonHolder.accepted.connect(self.accept)
        buttonHolder.rejected.connect(self.reject)
        layout.addWidget(buttonHolder)

        self.setLayout(layout)
        self.setWindowTitle("Select COM Port")

class FilterDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('images/filter_dlg.ui', self)

class LogManualDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('images/log_dlg.ui', self)


class PlotItem(pg.PlotItem):
    def __init__(self, *args, **kwargs):
        pg.PlotItem.__init__(self, *args, **kwargs)

    def mouseDoubleClickEvent(self, e):
        print(self.getLabel('title'))


app = QtWidgets.QApplication(sys.argv)
setting = Setting()
labjack = Labjack()
labjack .readGain()
# labjack.check()
window = PLOT(setting,labjack)

window.show()
# window.volt()
#window.getStream()
sys.exit(app.exec_())
