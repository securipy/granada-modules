#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, QThread, QThreadPool, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QWindow, QIcon, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QMenuBar, QStatusBar, QListWidget, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
import sys
from modules.miscellaneous.ListInterfaces import ListInterfaces

class GUI_ListInterfaces(QWidget):
    def __init__(self):
        super().__init__()
        #add worker and threadpool here?
        #self.threadPool = QThreadPool()
        self.thread= QThread()
        self.worker = ListInterfaces()
        self.interfaces = []
        self.setupUI()

    def setupUI(self):
        
        #GUI main objects
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonZone = QWidget(self)
        self.horizontalLayout = QHBoxLayout(self.buttonZone)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ifaceList = QListWidget(self)
        self.ifaceList.itemSelectionChanged.connect(self.checkMonitorModeEnable)
        #self.ifaceList = QTableWidget(self)
        #self.ifaceList.setRowCount(0)
        #self.ifaceList.setColumnCount(2)
        #self.ifaceList.setHorizontalHeaderItem(0, QTableWidgetItem("Interface"))
        #self.ifaceList.setHorizontalHeaderItem(1, QTableWidgetItem("Enable Monitor Mode"))
        
        #self.ifaceList = QListWidget(self)
        self.verticalLayout.addWidget(self.ifaceList)
        self.verticalLayout.addWidget(self.buttonZone)
        self.getIfacesButton = QPushButton(self)
        self.getIfacesButton.setObjectName("List Interfaces")
        self.getIfacesButton.setText(self.getIfacesButton.objectName())
        self.getIfacesButton.clicked.connect(self.getInterfaces)
        self.horizontalLayout.addWidget(self.getIfacesButton)
        self.setMonitorButton = QPushButton(self)
        self.setMonitorButton.setObjectName("Switch Monitor Mode")
        self.setMonitorButton.setEnabled(False)
        self.setMonitorButton.setText(self.setMonitorButton.objectName())
        self.setMonitorButton.clicked.connect(self.enableMonitorMode)
        self.horizontalLayout.addWidget(self.setMonitorButton)
       
      
    # get the worker to work
    def getInterfaces(self):
        if self.worker.thread() != self.thread:
            self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.endProcess)
        self.thread.started.connect(self.worker.getInterfaces)
        self.thread.start()
    
    # put interface into monitor mode if possible
    def enableMonitorMode(self):
        selectedItem = self.ifaceList.selectedItems()[0]
        self.worker.iface = selectedItem.text()
        if "mon" in self.worker.iface:
            self.worker.action = "stop"
        else:
            self.worker.action = "start"
        if not self.thread.isRunning() and self.worker.thread() != self.thread:
            self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.endProcess)
        self.thread.started.connect(self.worker.switchMonitorMode)
        self.thread.start()
    
    # handler to process worker results and close the thread
    @pyqtSlot(int)
    def endProcess(self, returnCode):
        if returnCode == 0:
            #process went well, reload table with results
            self.interfaces = self.worker.result
            self.thread.quit()
            self.thread.wait()
            self.refreshIfaceTable()
        else:
            #show error details
            dialog = QMessageBox()
            dialog.setText("There was an error: " + self.worker.err)
            dialog.setStandardButtons(QMessageBox.OK)
            dialog.exec()
       
    # reload network interfaces table
    def refreshIfaceTable(self):
        self.ifaceList.clear()
        if self.interfaces:
            for iface in self.interfaces:
                #check non duplicates
                #self.ifaceList.addItem(i, 0, QTableWidgetItem(iface[0]))
                #if len(self.ifaceList.findItems(iface, Qt.MatchFixedString)) == 0:
                self.ifaceList.addItem(iface)
    
    def checkMonitorModeEnable(self):
        self.setMonitorButton.setEnabled(False)
        if len(self.ifaceList.selectedItems()) != 0:
            self.setMonitorButton.setEnabled(True)
    # clear the GUI
    def clearInterface(self):
        pass
