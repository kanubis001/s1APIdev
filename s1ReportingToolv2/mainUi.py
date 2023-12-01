import sys
import os
import json
from queue import Queue
from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import QtGui, uic
import mainControl
import datetime
import time
from logger import *
import cryptoModule
import shared_module as sm

##############################################version hitory start
# Comsys Tool ReportGenerator
# change versionString when change something.
versionString="v3.0.1"
# version history
# [v3.0.0]
# Start version changed from previous version
# [v3.0.1]
# Add : Calendar integrity check
# Fix : Cannot get all groups and sites
# Fix : Error when using mssp console(Site User)
#
##############################################version hitory end


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form= resource_path('loginmain.ui')
form_class=uic.loadUiType(form)[0]

form_main=resource_path('realMain.ui')
form_mainwindow=uic.loadUiType(form_main)[0]

# root_directory=os.getcwd()+"\\s1_ReportGenerator"
root_directory=f"{os.getcwd()}\s1_ReportGenerator"
tk_dir=os.path.expanduser('~')
# tkfilepath=tk_dir+"\\.tk.json"
tkfilepath=f'{tk_dir}\.tk.json'
# setfilepath=tk_dir+"\\.s1set.json"
setfilepath=f"{tk_dir}\.s1set.json"
mainctrl=mainControl.mainCtrl(root_directory,tkfilepath)
crypt=cryptoModule.AESCipher("kaligo123")
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
    try: 
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        log_write2(sys, "Error: Failed to create the directory.")
        print("Error: Failed to create the directory.")

def chkTokenfile(apitoken):
    try: 
        encapitoken=crypt.encrypt(apitoken)
        # print(encapitoken)
        api={"tk":encapitoken}
        
        if not os.path.exists(tkfilepath):
            with open(tkfilepath, 'w') as f:
                log_write2(sys, "new tk.json file")
                json.dump(api,f)
        else:
            with open(tkfilepath, 'w') as f:
                # debugline=tkfilepath+"file already existed"
                debugline=f"{tkfilepath}file already existed"
                log_write2(sys, debugline)
                json.dump(api,f)
    except OSError:
        log_write2(sys, "Error: Not a file")
        print("Error: Not a file")
   
def chkToken(apitoken):
    try: 
        with open(tkfilepath,"r") as f:
            apitk=json.load(f)
            # 입력된 토큰값과 저장된 토큰값 비교
            decrypt=crypt.decrypt(apitk.get("tk"))
            print(decrypt)
            if apitoken==decrypt:
                log_write2(sys, "token is different. get new token")
                return apitoken
            else:
                log_write2(sys, "token is same.")
                return decrypt
    except OSError:
        print("Error: Not a file")

def chkSettingjson():
    # 파일경로 저장 등 마지막 설정값 저장.
    try: 
        if not os.path.exists(setfilepath):
            with open(setfilepath, 'w') as f:
                log_write2(sys, "new .s1set.json file")
                # root_directory=os.getcwd()+"\\s1_ReportGenerator"
                setting={"root_path":os.getcwd()+"\\s1_ReportGenerator"}
                json.dump(setting,f)
                mainctrl.changeDir(os.getcwd()+"\\s1_ReportGenerator")
                return os.getcwd()+"\\s1_ReportGenerator"
        else:
            with open(setfilepath, 'r') as f:
                debugline=setfilepath+"file already existed"
                log_write2(sys, debugline)
                setdata=json.load(f)
                mainctrl.changeDir(setdata.get("root_path"))
                return setdata.get("root_path")
    except OSError:
        log_write2(sys, "Error: Not a file")
        print("Error: Not a file")

def saveSetting(category, data):
    # 초기 파일 구성시 setting값 사전 정의 필요.(chkSettingjson)
    with open(setfilepath,'r') as f:
        filedata=json.load(f)
    filedata[category] = data
    with open(setfilepath,'w') as f2:
        json.dump(filedata,f2)

class guiThread(QThread):
    # progress bar 용 스레드
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        
    def run(self):
        self.parent.prBar.setVisible(True)
        self.parent.prBar.setMinimum(0)
        self.parent.prBar.setMaximum(0)
        # self.parent.prBar.setMaximum(100)
        # self.parent.prBar.setValue(sm.shared_per)
        # self.parent.lbl_export.setText("리포트 생성 중입니다.")
        while(self.parent.dn==False):
            # print(self.parent.dn)
            self.parent.lbl_export.setText(sm.shared_status)
            # print(sm.shared_status)
            # self.parent.prBar.setValue(sm.shared_per)
            time.sleep(1)
        # self.parent.lbl_export.setText("데이터 수집 중입니다.")
        # for i in range (0,100):
        #     self.parent.prBar.setValue(i)
        #     time.sleep(1)
        #     if i == 5:
        #         self.parent.lbl_export.setText("데이터를 정리합니다.")
        #     if i==30:
        #         self.parent.lbl_export.setText("리포트 생성 중입니다.")
        #     if i ==50:
        #         self.parent.lbl_export.setText("리포트 생성 중입니다. 잠시만 기다려주세요.")
    
    def stop(self):
        # print(self.parent.dn)
        self.parent.prBar.setVisible(False)
        self.quit()
    
class reportingThread(QThread):
    # 실제 리포팅 스레드
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.dn=False
        self.gt=guiThread(self.parent)
        
        
    def run(self):
        self.gt.start()
        # self.parent.prsignal.run("리포트 생성을 시작합니다.")
        self.parent.names=[self.parent.cmb_account.currentText(),self.parent.cmb_site.currentText(),self.parent.cmb_group.currentText()]
        # self.parent.prsignal.run("리포트 생성 중입니다.")
        doneornot=mainctrl.generateReport(self.parent.selInfo,self.parent.names)
        if doneornot:
            filecreated=f"리포트 파일 경로 : {doneornot}"
            self.parent.prsignal.run(filecreated)
            # self.parent.lbl_export.setText(filecreated)
            self.parent.allDisableFunc(False)
            self.parent.dn=True
            self.gt.stop()
        else:
            # self.parent.lbl_export.setText("에러가 발생했습니다.")
            self.parent.prsignal.run("에러가 발생했습니다.")
            self.parent.allDisableFunc(False)
            self.parent.dn=True
            self.gt.stop()
        
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        # 폴더 생성여부 확인
        # mkrootfolder(root_directory)
        self.setupUi(self)
        log_write2(sys, "loginmain.ui started")
        apiToken=self.lineApitk.text()
        # json과 비교
        setTk=chkToken(apiToken)
        
        self.lineApitk.setText(setTk)
        self.btnConfirm.clicked.connect(self.loginChk)
        self.btnExit.clicked.connect(QCoreApplication.instance().quit)
        
    def loginChk(self):
        url=self.comboConsole.currentText()
        apiToken=self.lineApitk.text()
        # 로그인 성공하면 "1" 실패하면 "0" 리턴.
        rtnvalArr=mainctrl.init_conn(url,apiToken)
        rtnval=rtnvalArr[0]
        
        if rtnval=="1":
            chkTokenfile(apiToken)
            message_api=mainctrl.chkAPItokenValid(apiToken)
            if message_api =="notyet":
                pass
            else:
                QMessageBox.warning(self,"API토큰 만료 임박", message_api)
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
        
class prbarSignal(QObject):
    pr_signal=pyqtSignal(str)
    
    def run(self,tmpstr):
        self.pr_signal.emit(tmpstr)

        
class mainWindow(QDialog, QWidget, form_mainwindow):

    def __init__(self):
        super(mainWindow,self).__init__()
        
        self.prsignal=prbarSignal()
        self.prsignal.pr_signal.connect(self.prfunc)
        
        
        self.initUi()
        self.prBar.setVisible(False)
        self.scope=sm.shared_scope
        # scope 알아오는 기능 추가.
        # self.scope=="site" 인 경우, account와 site까지 사전 설정 가능.
        if self.scope=="site":
            self.setAccount(sm.shared_accArr)
        else:
            self.setAccount(None)      
        
        self.show()
        # 리스닝
        self.accJson
        self.selInfo={"startd":[],"endd":[],"accid":[],"siteid":[], "grpid":[]}
        global root_directory
        root_directory=chkSettingjson()
        self.lbl_version.setText(versionString)
        self.line_filepath.setText(root_directory)
        self.btn_filepath.clicked.connect(self.change_path)
        self.cmb_account.currentIndexChanged.connect(self.changeAccount)
        self.cmb_site.currentIndexChanged.connect(self.changeSite)
        self.cmb_group.currentIndexChanged.connect(self.changeGrp)
        self.date_start.setDate(QDate(int(uYEAR_edit), int(uMONTH_edit), int(uDAY)))
        self.date_end.setDate(QDate(int(uYEAR), int(uMONTH), int(uDAY)))
        self.date_start.dateChanged.connect(self.changeDate_start)
        self.date_end.dateChanged.connect(self.changeDate_end)
        self.btn_expConfirm.clicked.connect(self.generateClick)
        self.selInfo["startd"].append(self.date_start.date().toString(Qt.DateFormat.ISODate))
        self.selInfo["endd"].append(self.date_end.date().toString(Qt.DateFormat.ISODate))
        self.dn=False
    
    @pyqtSlot(str)
    def prfunc(self, tmpstr):
        self.str=tmpstr
        self.lbl_export.setText(tmpstr)
        print(self.str)
    
    @pyqtSlot(str)
    def print_data(self,data):
        self.lbl_export.setText(data)

    def initUi(self):
        self.setupUi(self)
        
    def changeAccount(self):
        # self.selInfo={"startd":[],"endd":[],"accid":[],"siteid":[], "grpid":[]}
        # 저장값. 뭔가 있으면 날린다.
        if self.selInfo["accid"]:
            self.selInfo["accid"].pop()
        if self.selInfo["startd"]:
            self.selInfo["startd"].pop()
        if self.selInfo["endd"]:
            self.selInfo["endd"].pop()
        self.selInfo["startd"].append(self.date_start.date().toString(Qt.DateFormat.ISODate))
        self.selInfo["endd"].append(self.date_end.date().toString(Qt.DateFormat.ISODate))
        for acc, id in self.accJson.items():
            if self.cmb_account.currentText()==acc:
                self.cmb_site.clear()
                self.cmb_group.clear()
                self.selInfo["accid"].append(id)
                if self.scope=="site":
                    self.setSite("siteUser")
                else:
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
        if self.date_start.date() > self.date_end.date():
            QMessageBox.warning(self,"error!","날짜 지정 오류. 시작 날짜가 끝 날짜 보다 늦을 수 없습니다.")
            print(str(self.selInfo["startd"][0])[0:4]+str(self.selInfo["startd"][0])[5:7]+str(self.selInfo["startd"][0])[8:10])
            self.date_start.setDate(QDate(int(self.selInfo["startd"][0][0:4]),int(self.selInfo["startd"][0][5:7]),int(self.selInfo["startd"][0][8:10])))
        else:
            if self.selInfo["startd"]:
                self.selInfo["startd"].pop()
            self.startd=self.date_start.date().toString(Qt.DateFormat.ISODate)
            self.selInfo["startd"].append(self.startd)
            print(self.selInfo)
        
    def changeDate_end(self):
        if self.date_start.date() > self.date_end.date():
            QMessageBox.warning(self,"error!","날짜 지정 오류. 시작 날짜가 끝 날짜 보다 늦을 수 없습니다.")
            self.date_end.setDate(QDate(int(self.selInfo["endd"][0][0:4]),int(self.selInfo["endd"][0][5:7]),int(self.selInfo["endd"][0][8:10])))
        else:
            if self.selInfo["endd"]:
                self.selInfo["endd"].pop()
            self.endd=self.date_end.date().toString(Qt.DateFormat.ISODate)
            self.selInfo["endd"].append(self.endd)
            print(self.selInfo)
    
    def change_path(self):
        fname=QFileDialog.getExistingDirectory(self,'디렉토리선택')
        fname=fname.replace("/","\\",20)
        # mkrootfolder(fname)
        global root_directory
        # root_directory=fname+"\\s1_ReportGenerator"
        root_directory=f"{fname}\s1_ReportGenerator"
        self.line_filepath.setText(fname)
        saveSetting("root_path", root_directory)
        mainctrl.changeDir(root_directory)
        
    def setAccount(self,pre_data):
        # pre_data는 site user의 경우. account 이름과 id가 전달되어야 할듯
        self.cmb_account.addItem("account 선택")
        if pre_data:
            self.accJson=mainctrl.getAccount(pre_data)
        else:
            self.accJson=mainctrl.getAccount(None)
            
        for acc, id in self.accJson.items():
            self.cmb_account.addItem(acc)
    
    def setSite(self,accid):
        if accid=="siteUSer":
            self.siteJson=mainctrl.getSite("siteUser")
        else:
            self.siteJson=mainctrl.getSite(accid)
        for site, id in self.siteJson.items():
            self.cmb_site.addItem(site)
            
    def setGroup(self,siteid):
        # self.cmb_group.addItem("group 선택")
        self.grpJson=mainctrl.getGroup(siteid)
        for grp, id in self.grpJson.items():
            self.cmb_group.addItem(grp)
    
    def generateClick(self):
        # Thread 적용
        if len(self.selInfo["accid"])==0:
            print("accid")
            QMessageBox.warning(self,"error!","Account를 반드시 선택해야 합니다.")
        elif len(self.selInfo["siteid"])==0:
            print("siteid")
        elif len(self.selInfo["grpid"])==0:
            print("grpid")
        else:
            rt=reportingThread(self)
            global root_directory
            # print("before generate:",root_directory)
            mkrootfolder(root_directory)
            self.prsignal.run("리포트 생성이 시작됩니다.") 
            self.allDisableFunc(True)
            # memoryFollow("Before Generate")
            rt.start()

        # self.generate()
        
        
    # def generateClick(self):
    #     global root_directory
    #     print("before generate:",root_directory)
    #     mkrootfolder(root_directory)
    #     self.lbl_export.setText("리포트 생성이 시작됩니다.")
    #     self.cmb_account.setDisabled(True)
    #     self.cmb_site.setDisabled(True)
    #     self.cmb_group.setDisabled(True)
    #     self.date_start.setDisabled(True)
    #     self.date_end.setDisabled(True)
    #     self.btn_expConfirm.setDisabled(True)
    #     memoryFollow("Before Generate")
    #     self.generate()
    def generate(self):
        # generate 완료될때까지 버튼 lock
        self.names=[self.cmb_account.currentText(),self.cmb_site.currentText(),self.cmb_group.currentText()]
        doneornot=mainctrl.generateReport(self.selInfo,self.names)
        if doneornot:
            # filecreated="file created! : "+doneornot
            filecreated=f"file created! : {doneornot}"
            self.lbl_export.setText(filecreated)
            self.allDisableFunc(False)
        else:
            self.lbl_export.setText("에러가 발생했습니다.")
            self.allDisableFunc(False)
        
        
    ##########################export 기능
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
    ##########################export 기능
            
    def allDisableFunc(self,torf):
        self.cmb_account.setDisabled(torf)
        self.cmb_site.setDisabled(torf)
        self.cmb_group.setDisabled(torf)
        self.date_start.setDisabled(torf)
        self.date_end.setDisabled(torf)
        self.btn_expConfirm.setDisabled(torf)
        self.btn_filepath.setDisabled(torf)
        self.prBar.setVisible(not(torf))
       
if __name__=='__main__':
    app=QApplication(sys.argv)
    myWindow=WindowClass()
    myWindow.show()
    app.exec()
    