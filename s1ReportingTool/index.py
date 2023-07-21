import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6 import QtCore
from PyQt6 import uic
from PyQt6.QtGui import *
from connect import sess
from logger import *
from threading import *

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

formindex = resource_path('./index.ui')
index_form_class = uic.loadUiType(formindex)[0]
# UI파일 연결
# 단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
# form_class = uic.loadUiType('main.ui')[0]

# 화면을 띄우는데 사용되는 Class 선언
directory = os.path.expanduser('~\\s1report')
            
class indexWin(QMainWindow, index_form_class):
    def __init__(self,mainWinClass):
        super().__init__();
        self.setupUi(self);
        self.btnReportIntro.clicked.connect(self.gotoReport)
        self.statusBar().showMessage('2.0.0b')
        qPixmapVar=QPixmap()
        qPixmapVar.load("s1APIdev\s1ReportingTool\icon\콤시스 로고3.png")
        qPixmapVar=qPixmapVar.scaledToWidth(100)
        self.logolabel.setPixmap(qPixmapVar)
        
    def gotoReport(self):
        self.hide() #해당 윈도우 숨김
        self.repowin=self.mainWinClass
        self.repowin.exec()  # 두번째 창 닫을 때까지 기다림
        self.show()  # 두번째 창 닫으면 첫번째 창 다시 보임

if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # mainWinClass의 인스턴스 생성
    myWindow = indexWin()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec()
