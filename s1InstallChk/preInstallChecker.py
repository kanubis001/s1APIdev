# -*- coding:utf-8 -*-
#################################################
# version : 1.1.1
# author : Jaeho Kim
# company : Comsys
# name : preInstallChecker
# description : 센티넬원 설치 전 사전 점검 툴
# history : 2023.7.18 1.0.0 first release
#           2023.7.21 1.0.1 윈도우11 일부에서 나타나는 문제점 fix 
#           2023.7.21 1.0.2 Cipher Suites 검색로직 수정 
#           2023.7.24 1.1.0 윈도우8버전 핫픽스 목록 업데이트, hotfix 검색 로직 수정 
#           2023.7.24 1.1.1 win2008, win11 구분 로직 및 출력내용 변경
#################################################
import platform
import psutil
import os
import re 
import datetime
import ssl
from glob import glob

now = datetime.datetime.now()
nowDate = now.strftime('%Y%m%d%H%M%S')

if platform.system()=="Windows":
    import winreg as reg
    from windows_tools.updates import get_windows_updates
###############################################수정 가능한 부분###################################
    # 파일 저장경로 지정
    # reportpath="C:\\temp\\preinstall_check_report_"+nowDate+".txt"
    reportpath=".\\preinstall_check_report_"+nowDate+".txt"
elif (platform.system()=="Linux" or platform.system()=="darwin"):
    reportpath="./preinstall_check_report_"+nowDate+".txt"
    
# 확인할 프로세스 목록
# 윈도우
winAclLists=["SentinelAgent.exe","SentinelServiceHost.exe","SentinelHelperService.exe","SentinelUI.exe","SentinelStaticEngine.exe","SentinelStaticEngineScanner.exe","SentinelAgentWorker.exe","fAgent.exe"]

# 검색할 윈도우 폴더 목록
winFolderACL=["sentinel","fasoo","kaspersky","incops3","pcdrm"]

# 검색할 레지스트리 목록 
# !!!!!!!! 앞뒤로 | <-이 기호 절대 넣지 말 것. 반드시 중간에만 넣을 것.
regACLs="sentinel|fasoo|kaspersky|escort|nasca|incaps|pcdrm"

# 검사할 hotfix 목록
# 윈도우7, 윈도우 서버 2008r2 sp1
win7win2008r2sp1=["KB2533623","KB2758857","KB4457144","KB3140245","KB3033929","KB3020369","KB3042058"]
# 일반 윈도우 서버 2012
win2012=["KB3003729","KB3042058","KB3140245","KB3140245"]
# 윈도우 서버 2012r2. KB2919355 hotfix는 하위 hotfix를 포함해서 해당 버전이 있을 경우 win2012r2 목록은 검사하지 않음
win2012r2only=["KB2919355"]
# 윈도우 서버 2012r2
win2012r2 = ["KB3021910", "KB3042058", "KB3172614", "KB3197875", "KB2919442", "KB2932046", "KB2959977", "KB2937592",
              "KB2938439", "KB2934018"]
# 윈도우 8,8.1
win8win81=["KB2919355", "KB2932046", "KB2959977", "KB2937592", "KB2938439", "KB2934018"]
winclientOther = []
# 기타 다른 윈도우 서버
winserverOther = ["KB2919355", "KB2932046", "KB2959977", "KB2937592", "KB2938439", "KB2934018"]


# 검사할 ciphersuites 목록 새로 추가시 unsupportedCiphersuites와 unsupportedCiphersuites2는 _와 -를 맞춰서 작성
# supportedCiphersuites와 supportedCiphersuites2는 TLS_ 유무
unsupportedCiphersuites = [
    "ECDHE_RSA_WITH_AES_256_CBC_SHA384",
    "ECDHE_RSA_WITH_AES_128_CBC_SHA",
    "RSA_WITH_AES_256_GCM_SHA384",
    "RSA_WITH_AES_128_CBC_SHA256",
    "ECDHE_RSA_WITH_AES_128_CBC_SHA256",
    "RSA_WITH_AES_256_CBC_SHA",
    "RSA_WITH_AES_256_CBC_SHA256",
    "RSA_WITH_AES_128_GCM_SHA256",
    "ECDHE_RSA_WITH_AES_256_CBC_SHA",
    "RSA_WITH_CAMELLIA_128_CBC_SHA",
    "RSA_WITH_CAMELLIA_256_CBC_SHA"
]
supportedCiphersuites = [
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "TLS_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA256",
    "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_AES_256_CCM_8",
    "TLS_DHE_RSA_WITH_AES_256_CCM",
    "TLS_DHE_RSA_WITH_AES_128_CCM_8",
    "TLS_DHE_RSA_WITH_AES_128_CCM",
    "TLS_RSA_WITH_AES_256_CCM_8",
    "TLS_RSA_WITH_AES_256_CCM",
    "TLS_RSA_WITH_AES_128_CCM_8",
    "TLS_RSA_WITH_AES_128_CCM",
    "TLS_ECDHE_RSA_WITH_CAMELLIA_256_CBC_SHA384",
    "TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA256",
    "TLS_ECDHE_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    "TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA256",
    "TLS_DHE_RSA_WITH_CAMELLIA_256_CBC_SHA",
    "TLS_DHE_RSA_WITH_CAMELLIA_128_CBC_SHA",
    "TLS_RSA_WITH_CAMELLIA_256_CBC_SHA256",
    "TLS_RSA_WITH_CAMELLIA_128_CBC_SHA256"
]

mustCiphersuites=[
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384"
    ]
# 리눅스, 맥os는 보류
# 리눅스
aclprocLinux=["s1-agent","s1-scanner","s1-network","s1-orchestrator","s1-firewall"]
# 맥OS
aclprocMac=["sentinelctl","SentinelAgent","sentineld","sentineld_updater","sentineld_guard","sentineld_helper","sentinel_helper","sentineld_shell","sentinel_shell"]

###############################################수정 가능한 부분###################################
#####################################아래는 동작부분. 수정하지 말것.
def start():
    # 윈도우일 경우
    if platform.system()=="Windows":
        # 32bit, 64bit
        with open(reportpath, "w", encoding="utf-8") as f:
            f.write("############### 센티넬원 설치환경 보고서 ###############\n")
        arch=platform.architecture()[0]
        uname=platform.uname()
        srv2008sp=""
        path_product=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        key=reg.OpenKey(reg.HKEY_LOCAL_MACHINE,path_product,0)
        # cnt=0
        for cnt in range(0,30):
            try:
                name, data , kind = reg.EnumValue(key,cnt)  
                # cnt += 1
                if name=="CSDVersion":
                    srv2008sp=data
                elif name=="InstallationType":
                    ostype=data
                elif name=="CurrentBuild":
                    osbuildver=data
                elif name=="ProductName":
                    osversion=data
                else:
                    continue
            except Exception as e:
                pass
            
        diplayVer=osversion[8:].lower()
        relver=str(platform.release())
        if int(osbuildver)>=22000:
            osversion=osversion.replace("10","11")
            relver="11"
        else:
            pass

        with open(reportpath, "a", encoding="utf-8") as f:
            f.write("[ OS : "+osversion+" ] \n")
            f.write("[ release : "+relver+" ] \n")
            f.write("[ build version : "+osbuildver+" ] \n")
            f.write("[ 호스트명 : "+ str(uname.node)+" ] \n")
            f.write("[ machine : "+ str(uname.machine)+" ] \n")
        chkbyos(arch,ostype,diplayVer,srv2008sp)
        # 리눅스 일 경우
    elif platform.system()=="Linux":
        with open(reportpath, "w", encoding="utf-8") as f:
            f.write("############### 센티넬원 설치환경 보고서 ###############\n")
        arch=platform.architecture()[0]
        with open(reportpath, "a", encoding="utf-8") as f:
            f.write("[ OS : "+platform.system()+" ] \n")
            f.write("[ version : "+str(platform.version())+" ] \n")
            f.write("[ release : "+str(platform.release())+" ] \n")
            f.write("[ 호스트명 : "+ str(platform.uname()[1])+" ] \n")
            f.write("\n=======================실행중인 프로세스 목록 검사=======================\n")
            proccnt=0
            for process in psutil.process_iter():
                if process.name().lower() in aclprocLinux:
                    line=process.name() + "\t\t\t["+str(process.status())+"]\n"
                    f.write(line)
                    
            f.write("\n=======================설치 디렉토리 검사=======================\n")
            if os.path.exists("/opt/sentinelone")==True:
                f.write("/opt/sentinelone 디렉토리가 존재합니다.\n")
                f.write("\n=======================설치된 sentinelone 버전=======================\n")
                s1Info=os.popen('/opt/sentinelone/bin/sentinelctl version').read()
                f.write(str(s1Info))
    # mac일 경우
    elif platform.system()=="darwin":
        with open(reportpath, "w", encoding="utf-8") as f:
            f.write("############### 센티넬원 설치환경 보고서 ###############\n")
        arch=platform.architecture()[0]
        with open(reportpath, "a", encoding="utf-8") as f:
            f.write("[ OS : "+platform.system()+" ] \n")
            f.write("[ version : "+str(platform.version())+" ] \n")
            f.write("[ release : "+str(platform.release())+" ] \n")
            f.write("[ 호스트명 : "+ str(platform.uname()[1])+" ] \n")
            f.write("\n=======================실행중인 프로세스 목록 검사=======================\n")
            for process in psutil.process_iter():
                if process.name().lower() in aclprocMac:
                    line=process.name() + "\t\t\t["+str(process.status())+"]\n"
                    f.write(line)
            f.write("\n=======================설치 디렉토리 검사=======================\n")
            if os.path.exists("/opt/sentinelone")==True:
                f.write("/opt/sentinelone 디렉토리가 존재합니다.\n")
                f.write("\n=======================설치된 sentinelone 버전=======================\n")
                s1Info=os.popen('/opt/sentinelone/bin/sentinelctl version').read()
                f.write(str(s1Info))
    print("[ "+reportpath+" ] 경로에 리포트가 생성되었습니다.")
        
def chkbyos(arch,ostype,displayVer,srv2008sp):
    win.chkSystem(ostype,displayVer,srv2008sp)
    win.chkProc(winAclLists)
    win.chkDir(arch,winFolderACL)
    win.chkReg(regACLs)
    win.chkCipherSuite()

def get_windows_updates_info():
    import win32com.client
    try:
        update_session = win32com.client.Dispatch("Microsoft.Update.Session")
        update_searcher = update_session.CreateUpdateSearcher()
        search_result = update_searcher.Search("IsInstalled=1")
        updates_info = []

        for update in search_result.Updates:
            update_info = {}
            update_info["Title"] = update.Title
            update_info["Description"] = update.Description
            update_info["SupportUrl"] = update.SupportUrl
            update_info["MoreInfoUrls"] = [url for url in update.MoreInfoUrls]
            update_info["IsMandatory"] = update.IsMandatory
            update_info["IsInstalled"] = update.IsInstalled
            update_info["LastDeploymentChangeTime"] = update.LastDeploymentChangeTime
            # 필요한 추가 정보를 가져올 수 있습니다.
            updates_info.append(update_info)

        return updates_info

    except Exception as e:
        print("Err occur:", e)
        return None

class window:
    def __init__(self):
        self.rchkval=[]
        
    def chkProc(self,aclLists):
        # 실행중인 프로세스 리스트를 출력합니다.
        with open(reportpath, "a", encoding="utf-8") as f:
            lowAclLists=[]
            proccnt=0
            f.write("\n=======================실행중인 프로세스 목록 검사=======================\n")
            f.write("*해당 목록이 존재하면 설치에 문제가 있을 수 있습니다\n")
            for acl in aclLists:
                lowAclLists.append(acl.lower())
            for process in psutil.process_iter():
                if(process.name().lower() in lowAclLists):
                    line=process.name() + "\t\t\t[ "+str(process.status())+" ]\n"
                    f.write(line)
                
    def chkDir(self,arch,folderLists):
        with open(reportpath,"a", encoding="utf-8") as f:
            f.write("\n=======================설치 경로 검사=======================\n")
            f.write("*해당 목록이 존재하면 설치에 문제가 있을 수 있습니다\n")
            for i in range(0,2):
                # 32비트 정보
                if(i==0):
                    programfiles_dir=os.environ["PROGRAMFILES(X86)"]
                    f.write("############[ Program Files(x86) ]\n")
                # 64비트 정보
                elif(i==1):
                    f.write("\n############[ Program Files ]\n")
                    programfiles_dir=os.environ["PROGRAMFILES"]
                for aclList in folderLists:
                    if(glob(programfiles_dir+"/"+aclList+"*")):
                        # self.chkFolderArr[i].append({aclList:"Y"})
                        f.write(aclList+"\t\t[ O ] : "+str(glob(programfiles_dir+"/"+aclList+"*")).replace("\\\\","\\")+"\n")
                    else:
                        pass
                        # f.write(aclList+"\t\t[ X ]"+"\n")
                        # self.chkFolderArr[i].append({aclList:"N"})
    
    def chkReg(self,regACLs):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        rkeypatharr=[reg.HKEY_LOCAL_MACHINE,reg.HKEY_CURRENT_USER]
        
        with open(reportpath,"a", encoding="utf-8") as f:
            f.write("\n=======================레지스트리에 등록된 소프트웨어 검사=======================\n")
            f.write("*프로그램 추가/제거에 등록된 소프트웨어입니다.\n")
            f.write("*해당 목록이 존재하면 설치에 문제가 있을 수 있습니다\n")
            # 레지스트리에서 설치된 항목 출력
            for path in rkeypatharr:
                self.get_subkeys(key_path,path)
            
            for sw in self.rchkval:
                if re.search(regACLs,sw.lower()):
                    f.write(sw+"\n")
    
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
    
    def chkSystem(self,ostype,displayVer,srv2008sp):
        with open(reportpath,"a", encoding="utf-8") as f:
            f.write("\n=======================설치된 hotfix 버전 확인=======================\n")
            try:
                # offline용#####################
                kbinfos = os.popen('wmic qfe list full /format:table').read()
                updates_info=re.findall(r'KB[0-9]{7}',kbinfos)
                ###################################
                updateKBarr=None
                dispVer=displayVer.lower()
                # 2012 r2 버전 확인할때 사용함. True -> 2012r2
                chkr2=False
                if ostype=="Server":
                    if dispVer.find("2008")!=-1:
                        if srv2008sp!="Service Pack 1":
                            f.write("서비스팩1이 설치되어 있어야합니다.\n")
                            updateKBarr=[]
                        else:
                            updateKBarr=win7win2008r2sp1
                    elif dispVer.find("2012")!=-1:
                        if dispVer.find("r2"):
                            chkr2=True
                            updateKBarr=win2012r2
                        else:
                            updateKBarr=win2012
                    else:
                        updateKBarr=winserverOther
                    # elif dispVer.find("2019")!=-1:
                    #     updateKBarr=win2019
                        # pass
                elif ostype=="Client":
                    if dispVer.find("7")!=-1:
                        updateKBarr=win7win2008r2sp1
                    elif dispVer.find("8")!=-1 | dispVer.find("8.1")!=-1:
                        updateKBarr=win8win81
                    else:
                        updateKBarr=winclientOther
                else:
                    f.write("OS 버전이 검색되지 않습니다.")
                cnt=0
                updatecnt=0
                update_done=[]
                # 반드시 업데이트 되어야 하는 목록. 업데이트 되어 있으면 해당 목록에서 하나씩 지움.
                # 남아 있는 업데이트 목록이 반드시 업데이트 되어야하는 목록.
                mustupdate=updateKBarr
                
                # updates_info=get_windows_updates_info()
                for update in updates_info:
                    # if update["IsInstalled"]==True:
                    #     cnt+=1
                    #     name_KB=update["Title"][-10:-1]
                    #     if(name_KB==None):
                    #         pass
                    #     else:
                    if chkr2:
                        if update in win2012r2only:
                            f.write(update+" : 해당 업데이트 버전은 하위 업데이트 버전을 포함합니다.\n")
                            mustupdate=[]
                            break
                        else:
                            if update in updateKBarr:
                                mustupdate.remove(update)
                            else:
                                update_done.append(update)
                    else:
                        if update in updateKBarr:
                            mustupdate.remove(update)
                            # f.write(u"[ " + update + u" ] 설치됨\n")
                            # updatecnt += 1
                        else:
                            update_done.append(update)
                    # else:
                    #     pass
                if len(mustupdate)==0:
                    if srv2008sp != "Service Pack 1":
                        pass
                    f.write("필요한 hotfix가 모두 있습니다.\n")
                else:
                    f.write("아래 업데이트 목록은 반드시 설치 되어야 합니다.\n")
                for mup in mustupdate:
                    f.write("[ "+mup+" ]\n")
                    
            except Exception as e:
                f.write("에러가 발생했습니다. 에러코드 : "+e+"\n")
                pass
                # errmsg=traceback.format_exc()
                # f.write(str(errmsg)+"\n")
    
    def chkCipherSuite(self):
        with open(reportpath, "a", encoding="utf-8") as f:
            key_path = r"SYSTEM\CurrentControlSet\Control\Cryptography\Configuration\Local\SSL\00010002"
            root_key = reg.HKEY_LOCAL_MACHINE

            # 레지스트리 키 열기
            key = reg.OpenKey(root_key, key_path,0)
            cnt = 0
            while True:
                try:
                    name, data, kind = reg.EnumValue(key, cnt)
                    if name=="Functions":
                        ciphers=data
                        break
                    cnt += 1
                except Exception:
                    f.write(u'Cipher suites Error\n')
                    break
            f.write(u"\n=======================Cipher Suites 확인=======================\n")
            scs=supportedCiphersuites
            uscs=unsupportedCiphersuites
            mcs=mustCiphersuites
            mcnt=0
            for cipher in ciphers:
                if cipher in scs:
                    if cipher not in mcs:
                        f.write("cipher suite : [ "+cipher+" ]\n")
                    elif cipher in mcs:
                        f.write("센티넬원 필수 cipher suite : [ "+cipher+" ]\n")
                        mcnt=mcnt+1
                    else:
                        pass
                if cipher in uscs:
                    f.write("[ "+cipher+"] : 해당 cipher suites는 지원되지 않습니다.\n")
            if mcnt==0:
                f.write("필수 cipher suite가 없습니다.\n")
                f.write(mcs)
            else:
                pass
if __name__ == '__main__':
    win=window()
    start()
    if platform.system()=="Windows":
        os.system("pause")
        
        
#########################################################함수 쓰레기통
# def chkCipherSuite(self):
#     with open(reportpath,"a", encoding="utf-8") as f:
#         f.write("\n=======================Cipher Suites 확인=======================\n")
#         ctx=ssl.SSLContext(ssl.PROTOCOL_TLS)
#         ciphers=ctx.get_ciphers()
#         i=0
#         scs=supportedCiphersuites+supportedCiphersuites2
#         uscs=unsupportedCiphersuites
#         mcs=mustCiphersuites
#         for cipher in ciphers:
#             cp=cipher.get("name").replace("-","")
#             cpname=cp.replace("_","")
#             print(cpname)
#             if cpname in scs:
#                 if cpname not in mcs:
#                     f.write("cipher suite : [ "+cipher.get("name")+" ]\n")
#                 elif cpname in mcs:
#                     f.write("센티넬원 필수 cipher suite : [ "+cipher.get("name")+" ]\n")
#                 else:
#                     pass
#             if cpname in uscs:
#                 f.write("[ "+cipher.get("name")+"] : 해당 cipher suites는 지원되지 않습니다.")
#         self.chkCipherSuite2()


#  구 버전 library 이용하는 kb 검색 로직
# for update in get_windows_updates(filter_duplicates=True, include_all_states=False):
#     if(update.get("result")=='succeeded'):
#         cnt+=1
#         if(update.get("kb")==None):
#             pass
#         else:
#             if chkr2:
#                 if update.get("kb") in win2012r2only:
#                     print(update.get("kb")," : 해당 업데이트 버전은 하위 업데이트 버전을 포함합니다.\n")
#                     break
#                 else:
#                     if update.get("kb") in updateKBarr:
#                         f.write("[ "+update.get("kb")+" ] hotfix가 설치되어야 합니다.\n")
#                         updatecnt+1
#             else:
#                 if update.get("kb") in updateKBarr:
#                     f.write("[ "+update.get("kb")+" ] hotfix가 설치되어야 합니다.\n")
#                     updatecnt+1
#     else:
#         pass