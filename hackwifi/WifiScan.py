#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.QtCore import QObject, QThread, QThreadPool, pyqtSignal, pyqtSlot

import sys, os, subprocess, io, csv
from time import sleep
from datetime import date

class WifiScan(QObject):
    #kill and normal end signals
    refreshed = pyqtSignal()
    finished = pyqtSignal(int)
    def __init__(self, iface = "wlan0mon"):
        super().__init__() 
        self.exit = False
        d = date.today()
        # scanning interfaces
        self.iface = iface
        # data of the network to get packets from
        self.essid = ""
        self.bssid = ""
        self.channel = ""
        # filename in tmp
        self.outputFile = "airodump" 
        self.fileFilter = ""
        self.command = ["airodump-ng", "--write", "/tmp/" + self.outputFile, "-o", "csv ", iface]
        self.result = []
        self.returnCode = 1
    
    # methods for stopping and resetting the action method
    def prepareAction(self):
        self.exit = False
    
    def prepareExit(self):
        self.exit = True
        
    def setNetwork(self,essid, bssid, channel):
        self.essid = essid
        self.bssid = bssid
        self.channel = channel
    
    def prepareOutput(self):
        self.result = []
        fileName = ''
        countLines = '0'
        # the next concat of commands parses airodump and filters some fields
        fileFilter = "ls -Art /tmp | grep " + self.fileFilter + " | tail -n 1"
        fileNameProc = subprocess.Popen(fileFilter, shell = True, stdout=subprocess.PIPE)
        fileName = fileNameProc.communicate()[0].decode("utf-8").split('\n')[0]
        if fileName:
            countLinesCommand = "cat /tmp/" + fileName + " | grep -an '^Station' | cut -d ':' -f1"
            countLinesProc = subprocess.Popen(countLinesCommand, shell = True, stdout = subprocess.PIPE)
            countLines = countLinesProc.communicate()[0].decode("utf-8").split("\n")[0]
        if countLines and countLines != "0":
            cmd = "cat /tmp/" + fileName + " | head -n " + countLines + " | grep -av '^BSSID' | grep -av '^Station' | grep -a -v -e '^[[:space:]]*$'" 
            #cmd = "cat /tmp/$(ls -Art /tmp | grep airodump| tail -n 1) | head -n $(cat /tmp/$(ls -Art /tmp | grep airodump | tail -n 1) | grep -n '^Station' | cut -d ':' -f1) | grep -v '^BSSID' | grep -v '^Station' | grep -v -e '^[[:space:]]*$'" 
            #" | cut -d ',' -f1,6,7,8,9,11,14 > aux.csv"
            procOut = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            outputData = procOut.stdout.read().decode("utf-8")
            procData = procOut.communicate()
            self.returnCode = procOut.returncode
            # process ok
            if self.returnCode == 0:
                airodumpFile = io.StringIO(outputData)
                #convert csv to dict() objects
                conv = lambda row: {'ESSID': row[13], 'BSSID': row[0], 'Channel': row[3], 'privacy': row[5], 'cipher': row[6], 'auth': row[7], 'power': row[8], 'data': row[10]}
                data = [row for row in csv.reader(airodumpFile, delimiter=",") if len(row) != 0]
                #for row in csv.reader(airodumpFile, delimiter = ","):
                    #print(conv(row))
                self.result = [conv(row) for row in data]
        self.refreshed.emit()
        
    def doWork(self):
        FNULL = open(os.devnull, "w")
        #try to reach monitor mode
        try:
            print(self.bssid)
            # get data from an specific network or scan networks around
            if self.bssid:
                self.outputFile = self.bssid
                # set filter for csv files. Both pcap and csv files will be created when scanning a network.
                # csv holds airodump iface data we need to display in the GUI, pcap is the packet capture
                self.fileFilter = "csv$"
                self.command = ["airodump-ng", "--write", "/tmp/" + self.outputFile, "-o", "csv,pcap", "--bssid", self.bssid, "--channel", self.channel, self.iface]
            else:
                self.outputFile = "airodump"
                # file filter is a literal, so nothing to do here
                self.fileFilter = self.outputFile
                self.command = ["airodump-ng", "--write", "/tmp/" + self.outputFile , "-o", "csv ", self.iface]
            print(self.command)
            print(self.outputFile)
            process = subprocess.Popen(self.command, stdout=FNULL, stdin=FNULL, stderr=FNULL)
            i = 0
            while not self.exit:
                self.prepareOutput()
                sleep(1)
            #gone this far, kill the process and format output
            process.terminate()
            print("killed")
            self.finished.emit(self.returnCode)
        except Exception as e:
            print(e)
            self.finished.emit(1)
