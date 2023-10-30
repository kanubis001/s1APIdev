import sys
import os
import json
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import QtGui, uic
import mainControl
import datetime
import time
from logger import *

##############################################version hitory start
# Comsys Tool ApplicationExporter
# change versionString when change something.
versionString="v1.0.1"
# version history
# [v1.0.0]
# Start version
# 
# [v1.0.1]
# Fix date bug 
##############################################version hitory end


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form= resource_path('loginmain.ui')
form_class=uic.loadUiType(form)[0]

form_main=resource_path('realMain.ui')
form_mainwindow=uic.loadUiType(form_main)[0]
root_directory=os.getcwd()+"\\s1_exported"
mainctrl=mainControl.mainCtrl(root_directory)
log_write2(sys, str(root_directory))

#########################################날짜 관련 함수
now = datetime.datetime.now()
nowDate = now.strftime('%Y%m%d')
uYEAR = now.strftime('%Y')
uMONTH = now.strftime('%m')
uDAY = now.strftime('%d')
uYEAR_edit=uYEAR
if int(uMONTH) == 1:
    uYEAR_edit=int(uYEAR)-1
    uMONTH_edit=10
elif int(uMONTH) ==2:
    uYEAR_edit=int(uYEAR)-1
    uMONTH_edit=11
elif int(uMONTH) ==3:
    uYEAR_edit=int(uYEAR)-1
    uMONTH_edit=12
else:
    uMONTH_edit=int(uMONTH)-3
#########################################날짜 관련 함수

def mkrootfolder(directory):
    print(directory)
    try: 
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        log_write2(sys, "Error: Failed to create the directory.")
        print("Error: Failed to create the directory.")

def chkTokenfile(apitoken):
    filepath=root_directory+"\\tk.json"
    try: 
        api={"tk":apitoken}
        
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                log_write2(sys, "new tk.json file")
                json.dump(api,f)
        else:
            with open(filepath, 'w') as f:
                debugline=filepath+"file already existed"
                log_write2(sys, debugline)
                json.dump(api,f)
    except OSError:
        log_write2(sys, "Error: Not a file")
        print("Error: Not a file")
   
def chkToken(apitoken):
    try: 
        with open(root_directory+"\\tk.json","r") as f:
            apitk=json.load(f)
            # 입력된 토큰값과 저장된 토큰값 비교
            if apitoken==apitk.get("tk"):
                log_write2(sys, "token is different. get new token")
                return apitoken
            else:
                log_write2(sys, "token is same.")
                return apitk.get("tk")
    except OSError:
        print("Error: Not a file")


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        # s1_exported 생성여부 확인
        mkrootfolder(root_directory)
        self.setupUi(self)
        log_write2(sys, "loginmain.ui started")
        apiToken=self.lineApitk.text()
        # json과 비교
        setTk=chkToken(apiToken)
        self.lineApitk.setText(setTk)
        self.btnConfirm.clicked.connect(self.loginChk)
        
    def loginChk(self):
        url=self.comboConsole.currentText()
        apiToken=self.lineApitk.text()
        # 로그인 성공하면 "1" 실패하면 "0" 리턴.
        rtnval=mainctrl.init_conn(url,apiToken)
        chkTokenfile(apiToken)
        if rtnval=="1":
            mainctrl.chkAPItokenValid(apiToken)
            log_write2(sys, "login available")
            # UI부분
            self.btn_login()
        else:
            # 실패시 메세지 띄우기
            
            QMessageBox.warning(self,"Error","API token 값이 만료되었거나 잘못되었습니다.")
            # self.close()
    
    def btn_login(self):
        # 로그인 완료되면 -> self.hide()(로그인 창 닫힘)
        self.hide()
        self.mainwin=mainWindow()
        log_write2(sys,"mainWindow를 띄웁니다")
        self.mainwin.exec()
        self.show()
        self.close()
        
        
class mainWindow(QDialog, QWidget, form_mainwindow):
    def __init__(self):
        super(mainWindow,self).__init__()
        self.initUi()
        self.setAccount()
        # scope 알아오는 기능 추가.
        self.show()
        # 리스닝
        self.accJson
        self.lbl_version.setText(versionString)
        self.cmb_account.currentIndexChanged.connect(self.changeAccount)
        self.cmb_site.currentIndexChanged.connect(self.changeSite)
        self.cmb_group.currentIndexChanged.connect(self.changeGrp)
        self.date_start.setDate(QDate(int(uYEAR_edit), int(uMONTH_edit), int(uDAY)))
        self.date_end.setDate(QDate(int(uYEAR), int(uMONTH), int(uDAY)))
        self.date_start.dateChanged.connect(self.changeDate_start)
        self.date_end.dateChanged.connect(self.changeDate_end)
        self.btn_expConfirm.clicked.connect(self.exportClick)

    def initUi(self):
        self.setupUi(self)
        
        
    def changeAccount(self):
        self.selInfo={"startd":[],"endd":[],"accid":[],"siteid":[], "grpid":[]}
        self.selInfo["startd"].append(self.date_start.date().toString(Qt.DateFormat.ISODate))
        self.selInfo["endd"].append(self.date_end.date().toString(Qt.DateFormat.ISODate))
        # 저장값. 뭔가 있으면 날린다.
        if self.selInfo["accid"]:
            self.selInfo["accid"].pop()
        for acc, id in self.accJson.items():
            if self.cmb_account.currentText()==acc:
                self.cmb_site.clear()
                self.cmb_group.clear()
                self.selInfo["accid"].append(id)
                self.setSite(id)
                
    def changeSite(self):
        if self.selInfo["siteid"]:
            self.selInfo["siteid"].pop()
        for site, id in self.siteJson.items():
            if self.cmb_site.currentText()==site:
                self.cmb_group.clear()
                self.selInfo["siteid"].append(id)
                self.setGroup(id)
                
    def changeGrp(self):
        if self.selInfo["grpid"]:
            self.selInfo["grpid"].pop()
        for grp,id in self.grpJson.items():
            if self.cmb_group.currentText()==grp:
                self.selInfo["grpid"].append(id)
                print(self.selInfo)
                
    def changeDate_start(self):
        self.selInfo["startd"].pop()
        self.startd=self.date_start.date().toString(Qt.DateFormat.ISODate)
        self.selInfo["startd"].append(self.startd)
        print(self.startd)
        print(self.selInfo)
        
    def changeDate_end(self):
        self.selInfo["endd"].pop()
        self.endd=self.date_end.date().toString(Qt.DateFormat.ISODate)
        self.selInfo["endd"].append(self.endd)
        print(self.endd)
        print(self.selInfo)
        
    def setAccount(self):
        self.cmb_account.addItem("account 선택")
        self.accJson=mainctrl.getAccount()
        for acc, id in self.accJson.items():
            self.cmb_account.addItem(acc)
    
    def setSite(self,accid):
        self.siteJson=mainctrl.getSite(accid)
        for site, id in self.siteJson.items():
            self.cmb_site.addItem(site)
            
    def setGroup(self,siteid):
        # self.cmb_group.addItem("group 선택")
        self.grpJson=mainctrl.getGroup(siteid)
        for grp, id in self.grpJson.items():
            self.cmb_group.addItem(grp)
            
    def exportClick(self):
        self.lbl_export.setText("csv로 추출이 시작됩니다.")
        self.cmb_account.setDisabled(True)
        self.cmb_site.setDisabled(True)
        self.cmb_group.setDisabled(True)
        self.date_start.setDisabled(True)
        self.date_end.setDisabled(True)
        self.btn_expConfirm.setDisabled(True)
        self.export()
        
    def export(self):
        # export 완료될때까지 버튼 lock
        doneornot=mainctrl.exportfile(self.selInfo,"csv",nowDate)
        if doneornot:
            filecreated="file created! : "+doneornot
            self.lbl_export.setText(filecreated)
            self.allDisableFunc(False)
        else:
            self.lbl_export.setText("에러가 발생했습니다.")
            self.allDisableFunc(False)
            
    def allDisableFunc(self,torf):
        self.cmb_account.setDisabled(torf)
        self.cmb_site.setDisabled(torf)
        self.cmb_group.setDisabled(torf)
        self.date_start.setDisabled(torf)
        self.date_end.setDisabled(torf)
        self.btn_expConfirm.setDisabled(torf)
        
if __name__=='__main__':
    app=QApplication(sys.argv)
    myWindow=WindowClass()
    myWindow.show()
    app.exec()
    