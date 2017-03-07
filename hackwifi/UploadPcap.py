#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO insert names, disclaimer
# GPL
from PyQt5.QtCore import QObject, QThread, QThreadPool, pyqtSignal, pyqtSlot

import sys, os, subprocess, requests, json, base64
from time import sleep

class UploadPcap(QObject):
    
    finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__() 
        self.session = ""
        self.fileName = ""
        # process output
        self.out = ""
        # process stderr
        self.err = ""
        # array of device interfaces discovered
        self.result = []
        self.returnCode = 1
        
    #def selectAudit
    def selectAudit(self):
        self.session.getAudits()
        audits = []
        for audit in self.session.audits:
            audits.append(audit["name"])
        auditSelected = QInputDialog.getItem(self, "Audit", "Select an audit", audits, 0, False)
        if auditSelected[1]:
            for audit in self.session.audits:
                if audit["name"] == auditSelected[0]:
                    self.session.currentAudit = audit["id"]   
    def selectAudit(self):
        self.out = ""
        self.err = ""
        self.result = []
        r2 = requests.post(self.APIURL + '/auth/login', data = {'email':self.email,'password':self.password})
        data = json.loads(r2.text)
        token = data['result']
        headers = {self.HeaderName:token}
        r2 = requests.get(self.APIURL + "/audit/list", headers=headers)
        jsonAudits = json.loads(r2.text)
        for audit in jsonAudits['result']:
            self.result += str(audit['id'])
            
        self.finished.emit(0)
            
    def uploadPcap(self):
        filename = self.fileName
        print(self.fileName)
        # TODO migrate login, select audit, etc to session class
        aux = filename[:-4]
        aux = aux.split("-")[0]
        bssid = aux.split("/")[-1]
        print(bssid)
        #r2 = requests.post(self.APIURL + '/auth/login', data = {'email':self.sessionemail,'password':self.password})
        #data = json.loads(r2.text)
        #token = data['result']
        headers = {"GRANADA-TOKEN":self.session.token, "audit":self.session.currentAudit}

        files = {'pcap': open(filename, 'rb')}

        base64Token = self.session.token.split('.')[1]
        clearToken = base64.b64decode
        r = requests.post(self.session.APIURL + '/wifi/register', data = {'name':bssid,'mac':bssid},files=files,headers=headers,stream=True)
        print(r.status_code)
        print(r.text)
        self.finished.emit(0)
