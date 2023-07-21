import psutil;
import os;
import re;
import winreg as reg;
from glob import glob;

class window:
    def __init__(self):
        # self.chkFolderArr=[];
        # self.chkFolderArr = [[0] * 0] * 2
        self.rchkval=[]

    pass;
    def chkProc(self,aclLists):
        # 실행중인 프로세스 리스트를 출력합니다.
        with open("C:\\temp\\report.txt", "a") as f:
            lowAclLists=[];
            f.write("\n=======================실행중인 프로세스 목록을 검사=======================\n");
            for acl in aclLists:
                lowAclLists.append(acl.lower());
            for process in psutil.process_iter():
                if(process.name().lower() in lowAclLists):
                    line=process.name() + "\t\t\t["+str(process.status())+"]\n"
                    f.write(line);
                    print(line, end='');
                    # print(process.name() + "\t"+str(process.status()));
                
    def chkDir(self,arch,folderLists):
        with open("C:\\temp\\report.txt","a") as f:
            f.write("\n=======================설치 경로를 검사=======================\n")
            # if(arch=="32bit"):
            #     programfiles_dir=os.environ["PROGRAMFILES(X86)"];
            #     print(os.environ["PROGRAMFILES(X86)"]);
            # elif(arch=="64bit"):
            #     programfiles_dir=os.environ["PROGRAMFILES"];
            #     print(os.environ["PROGRAMFILES"]);
            # programdata_dir=os.environ["PROGRAMDATA"];
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
                        f.write(aclList+"\t\t[ O ] : "+str(glob(programfiles_dir+"/"+aclList+"*"))+"\n");
                        print(glob(programfiles_dir+"/"+aclList+"*"));
                    else:
                        f.write(aclList+"\t\t[ X ]"+"\n")
                        # self.chkFolderArr[i].append({aclList:"N"})
                    
                    # print("?")
                # if(os.path.exists(programfiles_dir+"/"+aclList)==True):
                #     self.chkFolderArr.append({aclList,"Y"})
                #     print(os.listdir(programfiles_dir+"/"+aclList));
                # elif(os.path.exists(programfiles_dir+"/"+aclList)==False):
                #     self.chkFolderArr.append({aclList,"N"})
                #     print("사전에 설치된 에이전트가 없습니다.")
        # print(self.chkFolderArr)
    
    def chkReg(self,regACLs):
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
        rkeypatharr=[reg.HKEY_LOCAL_MACHINE,reg.HKEY_CURRENT_USER]
        with open("C:\\temp\\report.txt","a") as f:
            f.write("\n=======================레지스트리에 등록된 소프트웨어 검사=======================\n")
            f.write("*프로그램 추가/제거에 등록된 소프트웨어입니다.\n")
            # 레지스트리에서 설치된 항목 출력
            for path in rkeypatharr:
                self.get_subkeys(key_path,path)
            
            # 이 부분 부터 체크.
            # 정규표현식을 통해서 설치된 프로그램 확인 및 검색
            for sw in self.rchkval:
                if re.search(regACLs,sw.lower()):
                    f.write(sw);

            # if subkeys:
            #     print("하위 키 목록:")
            #     for subkey in subkeys:
            #         print(subkey)
            # else:
            #     print("하위 키 없음")
    
    
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
                    # print(subkey)
                    self.rchkval.append(subkey)
            # 결과 반환
        except FileNotFoundError:
            print("레지스트리 키가 존재하지 않습니다.")
        except PermissionError:
            print("레지스트리에 접근할 권한이 없습니다.")
        except Exception as e:
            print("오류 발생:", str(e))
        
        return []