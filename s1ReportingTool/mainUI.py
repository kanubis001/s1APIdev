import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from mainControl import controller
from connect import sess
import datetime
import time
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
# F5tOMpddR1wFy5R5QskXTIhx0VeHFBoVO4LeUmqVHosC7iLIgsnwkvd3uEpxKFpJiLAWwPUsXLcHJjRJ
#사이트 권한을 가진 사용자의 토큰 - 사이트 권한 사용자 보고서 생성시 사용

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path('./reporterMain.ui')
form_class = uic.loadUiType(form)[0]
# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
# form_class = uic.loadUiType('main.ui')[0]

# 화면을 띄우는데 사용되는 Class 선언
directory = os.path.expanduser('~\\s1report')
class mkreportInfo(QThread):
    def __init__(self,parent=None):
        super().__init__()
        self.main=parent
        self.working=True
        
    def run(self):
        self.main.setInfo()
        self.__del__()
        
    def __del__(self):
        print("end setting")
            
class progressThread(QThread):
    per_changed=pyqtSignal(int)
    
    def __init__(self,per=0,parent=None):
        super().__init__()
        self.main=parent
        self.working=True
        self.main.prbar.setValue(0)
        self.per=per
        
    def __del__(self):
        print("end progress bar")
        
    def run(self):
        self.main.prbar.reset()
        # self.main.prbar.setRange(0,len(self.main.groups))
        self.main.prbar.setRange(0,0)
        total=len(self.main.groups)
        # i=int(100/total)
        
        while self.working:
            if self.per==total:
                self.main.prbar.setRange(0,100)
                self.per_changed.emit(100)
                self.__del__()
            else:
                self.per_changed.emit(self.per)
            # self.per+=1
            # self.sleep(1)
        # self.per_changed.emit(total)
        self.main.prbar.setRange(0,100)
        self.per_changed.emit(100)
        self.__del__()
    
    def add_per(self):
        self.per+=1
        
    
       
class WindowClass(QMainWindow, form_class):
    add_per_sig=pyqtSignal()
    
    def __init__(self):
        super().__init__()
        #chkgrouporsite False면 그룹 아이디 필요 없음
        self.enablegroupid=True
        self.setupUi(self)
        self.percnt=0
        self.btnReporting.setEnabled(False)
        self.comboConsole.currentIndexChanged.connect(self.urlFunc)
        self.btnConfirm.clicked.connect(self.confirmFunc)
        self.btnRepair.clicked.connect(self.repairFunc)
        self.comboAcc.currentIndexChanged.connect(self.siteSetFunc)
        self.comboSite.currentIndexChanged.connect(self.groupSetFunc)
        self.btnReporting.clicked.connect(self.threadControl)
        self.btnChk.clicked.connect(self.check)
        self.dateStart.setDate(QDate(int(uYEAR_edit), int(uMONTH_edit), int(uDAY)))
        self.dateEnd.setDate(QDate(int(uYEAR), int(uMONTH), int(uDAY)))
        # self.setI=reportThread(self)
        self.bar=progressThread(parent=self)
        self.set=mkreportInfo(parent=self)
        self.bar.per_changed.connect(self.per_update)
    
    @pyqtSlot(int)
    def per_update(self,per):
        self.prbar.setValue(per)
        
    @pyqtSlot(int)
    def per_add(self,per):
        self.prbar.setValue(per)    
    
    @pyqtSlot()
    def bar_start(self):
        print(len(self.groups))
        self.prbar.setRange(0,len(self.groups))
        self.bar.working=True
        self.bar.start()
        
    
    @pyqtSlot()
    def bar_stop(self):
        self.bar.working = False
           
    @pyqtSlot()
    def set_start(self):
        self.set.working=True
        self.set.start()    
    
    @pyqtSlot()
    def set_stop(self):
        self.set.working = False   
        

    def threadControl(self):
        # self.bar_start()
        self.set_start()
        # self.setInfo()
    
    def check(self):
        self.startDate = self.dateStart.date()
        self.endDate = self.dateEnd.date()
        print(self.startDate)
        self.startd = self.startDate.toString(Qt.ISODate)
        self.endd = self.endDate.toString(Qt.ISODate)
        print(self.startd)
        grperr,siterr,accerr,daterr=True,True,True,True
        
        if self.comboGrp.currentText() == "":
            reply=QMessageBox.question(self, "그룹 없음", "그룹이 선택되지 않았습니다. 사이트 단위로 보고서를 생성하시겠습니까?",QMessageBox.Yes|QMessageBox.No)
            if reply==QMessageBox.Yes:
                self.enablegroupid=False
                pass
            else:
                QMessageBox.warning(self, "그룹 오류", "그룹을 선택해주세요")
                self.enablegroupid=True
                grperr=False
        else:
            self.enablegroupid=True
        if self.comboSite.currentText() == "":
            QMessageBox.warning(self, "사이트 오류", "사이트가 선택되지 않았습니다.")
            siterr=False
        if self.comboAcc.currentText() == "":
            QMessageBox.warning(self, "어카운트 오류", "어카운트가 선택되지 않았습니다.")
            accerr=False
        if self.startDate > self.endDate:
            QMessageBox.warning(self, "날짜 오류", "시작날짜가 끝 날짜보다 나중입니다")
            daterr=False
        daylong = self.startDate.daysTo(self.endDate)
        if daylong <= 7:
            QMessageBox.warning(self, "날짜 오류", "기간이 너무 짧습니다.")
            daterr=False
        elif daylong > 100:
            QMessageBox.warning(self, "날짜 오류", "기간이 너무 깁니다. 최대 3개월(100일)까지 지정할 수 있습니다.")
            daterr=False

        if grperr==False or siterr==False or accerr==False or daterr==False:
            pass
        else:
            self.gotoSetproc()
                
    def gotoSetproc(self):
        self.btnReporting.setEnabled(True)
        self.dateEnd.setEnabled(False)
        self.dateStart.setEnabled(False)
        self.comboAcc.setEnabled(False)
        self.comboSite.setEnabled(False)
        self.comboGrp.setEnabled(False)
        self.btnChk.setEnabled(False)
        self.btnConfirm.setEnabled(False)
        self.comboConsole.setEnabled(False)
        self.lineApitk.setEnabled(False)
        
    def setInfo(self):
        self.btnReporting.setEnabled(False)
        if self.enablegroupid==False:
            print(self.comboSite.currentText())
            idTxt=self.comboSite.currentText()
            targetArr=self.sites
            self.names=[self.comboAcc.currentText(),self.comboSite.currentText()]
        if self.enablegroupid==True:
            print(self.comboGrp.currentText())
            idTxt = self.comboGrp.currentText()
            targetArr=self.groups
            self.names=[self.comboAcc.currentText(),self.comboSite.currentText(),self.comboGrp.currentText()]
        
        # print(idTxt)
        for i in range(0, len(targetArr)):
            # self.per_update(i)
            if idTxt == targetArr[i][0]:
                self.finalid = targetArr[i][1]
                reporDir = controller.start(self, self.finalid, self.startd, self.endd,self.enablegroupid,self.names)
                self.labelDirectory.setEnabled(True)
                self.labelDirectory.setText(reporDir)
                self.btnReporting.setEnabled(False)
                self.bar.working=False
                break
        # self.setI.stop()

    def repairFunc(self):
        self.btnConfirm.setEnabled(True)
        self.comboConsole.setEnabled(True)
        self.lineApitk.setEnabled(True)
        self.btnReporting.setEnabled(False)
        self.dateEnd.setEnabled(True)
        self.dateStart.setEnabled(True)
        self.comboAcc.setEnabled(True)
        self.comboSite.setEnabled(True)
        self.comboGrp.setEnabled(True)
        self.btnChk.setEnabled(True)
        self.labelDirectory.setEnabled(False)
        self.labelAcc_2.setFixedWidth(0)
        self.labelSite_2.setFixedWidth(0)
        self.labelGrp_2.setFixedWidth(0)
        self.prbar.reset()
        # self.set_stop()
        

    def groupSetFunc(self):
        sitetxt = self.comboSite.currentText()
        self.comboGrp.clear()
        for i in range(0, len(self.sites)):
            if sitetxt == self.sites[i][0]:
                self.groups = controller.findGroup(self, self.sites[i][1])
                self.labelGrp_2.setFixedWidth(120)
                self.comboGrp.addItem("")
                for group in self.groups:
                    self.comboGrp.addItem(group[0])

    def siteSetFunc(self):
        acctxt = self.comboAcc.currentText()
        self.comboSite.clear()
        acclists=self.accs[0]
        if self.accs[1]=="site":
            self.sites = controller.findSite(self, self.accs[2])
            self.labelSite_2.setFixedWidth(120)
            self.comboSite.addItem("")
            for site in self.sites:
                self.comboSite.addItem(site[0])
        else:
            for i in range(0, len(acclists)):
                if acctxt == acclists[i][0]:
                    self.sites = controller.findSite(self, acclists[i][2])
                    self.labelSite_2.setFixedWidth(120)
                    self.comboSite.addItem("")
                    for site in self.sites:
                        self.comboSite.addItem(site[0])
        self.labelAcc_2.setFixedWidth(120)

    def urlFunc(self):
        print(self.comboConsole.currentText())

    def confirmFunc(self):
        self.btnConfirm.setDisabled(True)
        self.comboConsole.setDisabled(True)
        self.lineApitk.setDisabled(True)
        self.setmain(self.comboConsole.currentText(), self.lineApitk.text())
        self.findAccount()

    def findAccount(self):
        self.comboAcc.clear()
        self.accs = controller.findAccount(self)
        acclists=self.accs[0]
        self.labelSite_2.setFixedWidth(0)
        self.comboAcc.addItem("")
        if self.accs[1]=="site":
            self.comboAcc.addItem(self.accs[3])
        elif self.accs[1]=="account":
            for i in acclists:
                self.comboAcc.addItem(i[0])

    def setmain(self, _url, _apiToken):
        controller.setVar(self, _url, _apiToken)


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
