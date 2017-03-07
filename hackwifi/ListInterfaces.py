#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.QtCore import QObject, QThread, QThreadPool, pyqtSignal, pyqtSlot

import sys, os, subprocess
from time import sleep

class ListInterfaces(QObject):
    
    finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__() 
        #self.command = "ls /sys/class/net"
        self.command = ""
        # start or stop monitor mode
        self.action = ""
        # network interface to act upon
        self.iface = ""
        # process output
        self.out = ""
        # process stderr
        self.err = ""
        # array of device interfaces discovered
        self.result = []
        self.returnCode = 1
       
    # get network interfaces and store as an array
    def getInterfaces(self):
        self.out = ""
        self.err = ""
        self.result = []
        self.command = "ip addr show |grep 'UP' |grep -v 'lo:' | cut -d ':' -f 2 | sed 's/^ //g'"
        
        try:
            procOut = subprocess.Popen(self.command,stdout=subprocess.PIPE,shell=True)
        
            #python3 unicode problem ahead! make sure you translate from ascii
            aux = procOut.communicate()
            self.returnCode = procOut.returncode
            #eval for empty returns
            if aux[0]:
                self.out = aux[0].decode("ascii")
            if aux[1]:
                self.err = aux[1].decode("ascii")
            if self.returnCode == 0:
                for iface in filter(None,self.out.split("\n")):
                    self.result.append(iface)
        except Exception as e:
            print(e)
            self.err += str(e)
        self.finished.emit(self.returnCode)
   
    # clone for API to other modules
    def getMonInterfaces(self):
        self.out = ""
        self.err = ""
        self.result = []
        self.command = "ip addr show |grep 'UP' |grep 'mon' | cut -d ':' -f 2 | sed 's/^ //g'"
        procOut = subprocess.Popen(self.command,stdout=subprocess.PIPE,shell=True)
        
        #python3 unicode problem ahead! make sure you translate from ascii
        aux = procOut.communicate()
        self.returnCode = procOut.returncode
        #eval for empty returns
        if aux[0]:
            self.out = aux[0].decode("ascii")
        if aux[1]:
            self.err = aux[1].decode("ascii")
            print("error")
            print(self.err)
        if self.returnCode == 0:
            for iface in filter(None,self.out.split("\n")):
                self.result.append(iface)
        self.finished.emit(self.returnCode)
    
    def switchMonitorMode(self):
        self.out = ""
        self.err = ""
        self.command = ["airmon-ng", self.action, self.iface]
        procOut = subprocess.Popen(self.command,stdout=subprocess.PIPE)
        
        #python3 unicode problem ahead! make sure you translate from ascii
        aux = procOut.communicate()
        self.returnCode = procOut.returncode
        #eval for empty arrays
        if aux[0]:
            self.out = aux[0].decode("ascii")
        if aux[1]:
            self.err = aux[1].decode("ascii")
        if self.returnCode == 0:
            self.getInterfaces()
        else:
            self.finished.emit(self.returnCode)
