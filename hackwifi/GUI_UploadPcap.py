#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.Qt import Qt
from PyQt5.QtCore import QObject, QThread, QThreadPool, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QWindow, QIcon, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QMenuBar, QStatusBar, QFileDialog, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox
import sys
from modules.hackwifi.UploadPcap import UploadPcap 

class GUI_UploadPcap(QWidget):
    def __init__(self):
        super().__init__()
        self.session = ""
        self.thread= QThread()
        self.worker = UploadPcap()
        # beware! slots and signals can be connected many to many
        # take this into account or you will be buried in a bunch of callbacks
        self.worker.finished.connect(self.endProcess)
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
        # set label to show file choosed
        self.fileNameLabel = QLabel(self)
        self.fileNameLabel.setText("File to upload")
        self.verticalLayout.addWidget(self.fileNameLabel)
        self.verticalLayout.addWidget(self.buttonZone)
        self.selectButton = QPushButton(self)
        self.selectButton.setObjectName("Choose file")
        self.selectButton.setText(self.selectButton.objectName())
        self.selectButton.clicked.connect(self.selectFile)
        self.horizontalLayout.addWidget(self.selectButton)
        self.uploadButton = QPushButton(self)
        self.uploadButton.setEnabled(False)
        self.uploadButton.setObjectName("Upload file")
        self.uploadButton.setText(self.uploadButton.objectName())
        self.uploadButton.clicked.connect(self.uploadFile)
        self.horizontalLayout.addWidget(self.uploadButton)
       
      
    # get the worker to work
    def selectFile(self):
        fileChooser = QFileDialog()
        fileChooser.setMimeTypeFilters(["application/vnd.tcpdump.pcap"])
        result = fileChooser.getOpenFileName(self, "Select pcap", "/tmp", "Capture files: (*.cap)")
        if result:
            self.fileNameLabel.setText(result[0])
            self.uploadButton.setEnabled(True)
    
    # put interface into monitor mode if possible
    def uploadFile(self):
        self.worker.session = self.session
        upload = self.createDialog("Do you want to upload " + self.fileNameLabel.text() + "?")
        if upload:
            self.worker.fileName = self.fileNameLabel.text()
            if self.worker.thread() != self.thread:
                self.worker.moveToThread(self.thread)
            # should disconnect all signals to ensure the next one will be the only
            try:
                self.thread.disconnect()
                # try to get current audit when login is implemented
                # if no login/audit, create local audit
            except:
                # no signals were connected yet
                pass
            #self.thread.started.connect(self.worker.selectAudit)
            self.thread.started.connect(self.worker.uploadPcap)
            self.thread.start()
        # TODO get dialog picker to select audit, fix signals to redirect to upload once it's done
        # do we get an audit during login?
        
        
    def createDialog(self,msg):
            dialog = QMessageBox()
            dialog.setText(msg)
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            return dialog.exec() == QMessageBox.Yes
    # handler to process worker results and close the thread
    @pyqtSlot(int)
    def endProcess(self, returnCode):
        self.thread.disconnect()
        if returnCode == 0:
            #process went well, reload table with results
            self.thread.quit()
            self.thread.wait()
            self.refreshInterface()
        else:
            #show error details
            dialog = QMessageBox()
            dialog.setText("There was an error: " + self.worker.err)
            dialog.setStandardButtons(QMessageBox.Yes)
            dialog.exec()
       
    # reload network interfaces table
    def refreshInterface(self):
        self.fileNameLabel.setText(self.fileNameLabel.text() + " was correctly uploaded")
        self.uploadButton.setEnabled(False)
