import platform;
# import window;
import ctypes;
import sys;
import psutil;
import os;
import re; 
import winreg as reg;
import datetime;
from glob import glob;
import os
now = datetime.datetime.now();
nowDate = now.strftime('%Y%m%d%H%M%S');
reportpath="C:\\temp\\preinstall_check_report_"+nowDate+".txt"
###############################################수정 가능한 부분###################################

# 확인할 프로세스 목록
winAclLists=["sentinelAgent.exe","SentinelServiceHost.exe","fAgent.exe"];

# 검색할 윈도우 폴더 목록
winFolderACL=["sentinel","fasoo","kaspersky","escort"]

# 검색할 레지스트리 목록 
# !!!!!!!! 앞뒤로 | <-이 기호 절대 넣지 말 것. 반드시 중간에만 넣을 것.
regACLs="sentinel|fasoo|kaspersky|escort"

###############################################수정 가능한 부분###################################
#####################################아래는 동작부분. 수정하지 말것.
def start():
    # 윈도우일 경우
    if platform.system()=="Windows":
        # 32bit, 64bit
        arch=platform.architecture()[0];
        plat=platform.platform();
        uname=platform.uname();
        with open(reportpath, "a") as f:
            f.write("* 윈도우 서버의 경우 일반 윈도우 버전으로 표기될 수 있습니다\n");
            f.write("[ OS : "+platform.system()+" ] \n")
            f.write("[ version : "+str(platform.version())+" ] \n")
            f.write("[ 호스트명 : "+ str(uname.node)+" ] \n")
            f.write("[ machine : "+ str(uname.machine)+" ] \n")
        chkbyos(arch);
        # 리눅스 일 경우
    elif platform.system()=="Linux":
        pass;
    # mac일 경우
    elif platform.system()=="darwin":
        pass;
        
def chkbyos(arch):
    win.chkProc(winAclLists);
    win.chkDir(arch,winFolderACL);
    win.chkReg(regACLs);  
    

class window:
    def __init__(self):
        self.rchkval=[]

    pass;
    def chkProc(self,aclLists):
        # 실행중인 프로세스 리스트를 출력합니다.
        with open(reportpath, "a") as f:
            lowAclLists=[];
            f.write("\n=======================실행중인 프로세스 목록 검사=======================\n");
            for acl in aclLists:
                lowAclLists.append(acl.lower());
            for process in psutil.process_iter():
                if(process.name().lower() in lowAclLists):
                    line=process.name() + "\t\t\t["+str(process.status())+"]\n"
                    f.write(line);
                
    def chkDir(self,arch,folderLists):
        with open(reportpath,"a") as f:
            f.write("\n=======================설치 경로 검사=======================\n")
            for i in range(0,2):
                # 32비트 정보
                if(i==0):
                    programfiles_dir=os.environ["PROGRAMFILES(X86)"];
                    f.write("############[ Program Files(x86) ]\n")
                    # print(os.environ["PROGRAMFILES(X86)"]);
                # 64비트 정보
                elif(i==1):
                    f.write("\n############[ Program Files ]\n")
                    programfiles_dir=os.environ["PROGRAMFILES"];
                    # print(os.environ["PROGRAMFILES"]);
                for aclList in folderLists:
                    if(glob(programfiles_dir+"/"+aclList+"*")):
                        # self.chkFolderArr[i].append({aclList:"Y"})
                        f.write(aclList+"\t\t[ O ] : "+str(glob(programfiles_dir+"/"+aclList+"*")).replace("\\\\","\\")+"\n");
                        # print(glob(programfiles_dir+"/"+aclList+"*"));
                    else:
                        f.write(aclList+"\t\t[ X ]"+"\n")
                        # self.chkFolderArr[i].append({aclList:"N"})
    
    def chkReg(self,regACLs):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        rkeypatharr=[reg.HKEY_LOCAL_MACHINE,reg.HKEY_CURRENT_USER]
        with open(reportpath,"a") as f:
            f.write("\n=======================레지스트리에 등록된 소프트웨어 검사=======================\n")
            f.write("*프로그램 추가/제거에 등록된 소프트웨어입니다.\n")
            # 레지스트리에서 설치된 항목 출력
            for path in rkeypatharr:
                self.get_subkeys(key_path,path)
            
            for sw in self.rchkval:
                if re.search(regACLs,sw.lower()):
                    f.write(sw);
    
    def get_subkeys(self,key_path, root_key_path):
        try:
            # 루트 레지스트리 키
            root_key = root_key_path

            # 레지스트리 키 열기
            key = reg.OpenKey(root_key, key_path)

            # 하위 키 열거
            subkeys = []
            index = 0
            while True:
                try:
                    subkey = reg.EnumKey(key, index)
                    subkeys.append(subkey)
                    index += 1
                except OSError:
                    # 더 이상 하위 키가 없을 때 예외 발생
                    break

            #세부값
            values=[]
            for subkey in subkeys:
                if (str(subkey)[0:1]=="{"):
                    subkey_path=key_path+"\\"+subkey
                    subkey_key=reg.OpenKey(root_key, subkey_path)
                    try:
                        value, value_type = reg.QueryValueEx(subkey_key, "DisplayName")
                        self.rchkval.append(value)
                    except FileNotFoundError:
                        continue
                else:
                    self.rchkval.append(subkey)
            # 결과 반환
        except FileNotFoundError:
            print("레지스트리 키가 존재하지 않습니다.")
        except PermissionError:
            print("레지스트리에 접근할 권한이 없습니다.")
        except Exception as e:
            print("오류 발생:", str(e))
        return []
    
if __name__ == '__main__':
    win=window()
    with open(reportpath, "w") as f:
        f.write("############### 센티넬원 설치환경 보고서 ###############\n");
    start()
    print("[ "+reportpath+" ] 경로에 리포트가 생성되었습니다.")
    os.system("pause")