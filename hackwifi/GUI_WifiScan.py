#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, QThread, QThreadPool, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QWindow, QIcon, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QMenuBar, QStatusBar, QTableWidget, QTableWidgetItem, QAbstractItemView, QInputDialog, QMessageBox, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout 
import sys
from modules.hackwifi.WifiScan import WifiScan
from modules.hackwifi.ListInterfaces import ListInterfaces

class GUI_WifiScan(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        
        #GUI main objects
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        # button holder widget to apply new layout
        self.buttonZone = QWidget(self)
        self.horizontalLayout = QHBoxLayout(self.buttonZone)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        # Table, only one row selectable, trigger on select change
        self.scanTable = QTableWidget(self)
        self.scanTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scanTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.scanTable.itemSelectionChanged.connect(self.setTargetNetwork)
        # main layout contents: table and button holder
        self.verticalLayout.addWidget(self.scanTable)
        self.verticalLayout.addWidget(self.buttonZone)
        # button initialization
        self.scanButton = QPushButton(self)
        self.scanButton.setObjectName("Scan Wifis")
        self.scanButton.setText(self.scanButton.objectName())
        self.scanButton.clicked.connect(self.getMonitorInterfaces)
        self.horizontalLayout.addWidget(self.scanButton)
        self.stopScanButton = QPushButton(self)
        self.stopScanButton.setObjectName("Stop scan")
        self.stopScanButton.setText(self.stopScanButton.objectName())
        self.stopScanButton.setEnabled(False)
        self.stopScanButton.clicked.connect(self.stopProcess)
        self.horizontalLayout.addWidget(self.stopScanButton)
        
        # create class auxiliary objects, signals
        self.thread= QThread()
        self.worker = WifiScan()
        self.worker.refreshed.connect(self.refreshResults)
        self.worker.finished.connect(self.endProcess)
        self.workerListInterfaces = ListInterfaces()
        self.workerListInterfaces.finished.connect(self.parseMonitorInterfaces)
        # monitor interfaces
        self.interfaces = []
        # selected interface to scan
        self.selectedInterface = ""
        # scan dict for table
        self.scan = {}
     
    # get the worker to work
    def doWork(self):
        if self.interfaces:
            ifaceChoice = QInputDialog.getItem(self, "Monitor interfaces", "Select an interface", self.interfaces, 0, False)
            # array, pos0 for value, pos1 for button pressed (bool)
            if ifaceChoice[1]:
                self.selectedInterface = ifaceChoice[0]
        else:
            dialog = QMessageBox()
            dialog.setText("There are no monitor interfaces or a problem ocurred")
            dialog.setStandardButtons(QMessageBox.Yes)
            dialog.exec()
        if self.selectedInterface:
            self.worker.iface = self.selectedInterface
            #ensure the worker will not exit when it's launched
            self.worker.prepareAction()
            if self.worker.thread() != self.thread:
                self.worker.moveToThread(self.thread)
            try:
                self.thread.disconnect()
            except:
                pass
            self.thread.started.connect(self.worker.doWork)
            self.thread.start()
            self.stopScanButton.setEnabled(True)
    
    # handler to process worker results and close the thread
    @pyqtSlot(int)
    def endProcess(self):
        self.stopScanButton.setEnabled(False)
        self.scanButton.setEnabled(True)
        self.scanButton.setText("New Wifi Scan")
        self.scan = self.worker.result
        self.thread.quit()
        self.thread.wait()
        self.refreshScanTable()
        
    @pyqtSlot()
    def refreshResults(self):
        self.scan = self.worker.result
        self.refreshScanTable()
        
    #stop process
    def stopProcess(self):
        self.worker.prepareExit()
    
    # select monitor mode interface
    def getMonitorInterfaces(self):
        if self.workerListInterfaces.thread() != self.thread:
            self.workerListInterfaces.moveToThread(self.thread)
        try:
            self.thread.disconnect()
        except:
            pass
        self.thread.started.connect(self.workerListInterfaces.getMonInterfaces)
        self.thread.start()
        self.scanButton.setText("Scanning")
        self.scanButton.setEnabled(False)
        
    # parse ListInterfaces worker result
    @pyqtSlot(int)
    def parseMonitorInterfaces(self, returnCode):
        if returnCode == 0:
            #process went well, reload table with results
            self.interfaces = self.workerListInterfaces.result
            self.thread.quit()
            self.thread.wait()
        else:
            #show error details
            dialog = QMessageBox()
            dialog.setText("An error ocurred while searching for interfaces: " + self.worker.err)
            dialog.setStandardButtons(QMessageBox.Yes)
            dialog.exec()
        self.doWork()
        
    def initialyzeTable(self):
        if self.scanTable.columnCount() == 0:
            self.scanTable.setColumnCount(len(self.scan[0]))
            header = ["ESSID", "BSSID","Channel", "Privacy", "Cipher", "Auth", "Power", "Data"]
            self.scanTable.setHorizontalHeaderLabels(header)
        self.scanTable.setRowCount(len(self.scan))
            
    # reload network interfaces table
    def refreshScanTable(self):
        if self.scan:
            self.initialyzeTable()
            self.scanTable.clearContents()
            i = 0
            for ap in self.scan:
                item = QTableWidgetItem(ap["ESSID"])
                self.scanTable.setItem(i,0,item)
                item = QTableWidgetItem(ap["BSSID"])
                self.scanTable.setItem(i,1,item)
                item = QTableWidgetItem(ap["Channel"])
                self.scanTable.setItem(i,2,item)
                item = QTableWidgetItem(ap["privacy"])
                self.scanTable.setItem(i,3,item)
                item = QTableWidgetItem(ap["cipher"])
                self.scanTable.setItem(i,4,item)
                item = QTableWidgetItem(ap["auth"])
                self.scanTable.setItem(i,5,item)
                item = QTableWidgetItem(ap["power"])
                self.scanTable.setItem(i,6,item)
                item = QTableWidgetItem(ap["data"])
                self.scanTable.setItem(i,7,item)
                i += 1
            self.scanTable.resizeColumnsToContents()
    
    # change target network according to table
    def setTargetNetwork(self):
        print('set target network')
        if self.scanTable.selectedItems():
            aux = self.scanTable.selectedItems()[0]
            essid = self.scanTable.item(aux.row(),0).text()
            bssid = self.scanTable.item(aux.row(),1).text()
            channel = self.scanTable.item(aux.row(),2).text()
            self.worker.setNetwork(essid, bssid, channel)
            print(self.worker.essid + self.worker.bssid + self.worker.channel)
            
        else:
            self.worker.essid = ""
            self.worker.bssid = ""
            
    # clear the GUI
    def clearInterface(self):
        pass
