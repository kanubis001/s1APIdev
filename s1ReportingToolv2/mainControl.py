import connect
import json
from connect import sess
from datetime import datetime, date,time,timedelta
import pytz
import csv
import openpyxl as op
import mkReport, mainReporting
from logger import *
import sys
import shared_module as sm


class mainCtrl:
    
    def __init__(self,rootpath,tkfilepath):
        self.token="init_token"
        self.url="init_url"
        self.sess=sess
        self.rootpath=rootpath
        self.tkfilepath=tkfilepath
        self.scopeinfo=sm.shared_scope
        
    def init_conn(self,url,apiToken):
        self.token=connect.connectAPI(url, "token",apiToken)
        self.url=url
        userinformUrl=f"{url}/web/api/v2.1/user?token={self.token}"
        uinfoRes=self.sess.get(userinformUrl)
        # 로그인 사용자 정보 저장.
        uinfoCont=json.loads(uinfoRes._content).get("data")
        
        if self.token==0:
            log_write2(sys, "API token 값이 만료되었거나 잘못되었습니다.")
            print("API token 값이 만료 되었거나 잘못 되었습니다.")
            return "0"
        else:
            log_write2(sys, "API 토큰 정상")
            # 정상 로그인시 공유 변수에 scope 정보와 scopeRoles 저장.
            sm.shared_scope=uinfoCont.get("scope")
            sm.shared_accArr=uinfoCont.get("scopeRoles")
            print(sm.shared_accArr)
            print(f"debug : {self.token}")
            return "1"

    def chkAPItokenValid(self,apitoken):
        # fullurl=self.url+"/web/api/v2.1/users/api-token-details?token="+str(self.token)
        fullurl=f"{self.url}/web/api/v2.1/users/api-token-details?token={str(self.token)}"
        apitkJson={
            "data":{
            "apiToken": apitoken}
            }
        response=self.sess.post(fullurl, json=apitkJson)
        cont=json.loads(response._content)
        expiredate=cont.get("data").get("expiresAt")
        expiredate=expiredate[0:10]
        expiredate_datetype=datetime.strptime(expiredate,"%Y-%m-%d")
        expireInform=expiredate_datetype-datetime.today()
        if expireInform.days < 7:
            # debugline="API token expired soon"+str(expireInform.days)+"days remained"
            # printmessage="API 토큰 값이 곧 만료 됩니다. 남은 기간 : "+str(expireInform.days)+" days remain.\n 콘솔에서 API 토큰을 갱신해서 사용하세요."
            debugline=f"API token expired soon{str(expireInform.days)}days remained"
            printmessage=f"API 토큰 값이 곧 만료 됩니다. 남은 기간 : {str(expireInform.days)} days remain.\n 콘솔에서 API 토큰을 갱신해서 사용하세요."
            log_write2(sys, debugline)
            return printmessage
            # OTP 필수 사용으로 아래 기능 사용 불가.
            # self.genAPItoken()
        else:
            log_write2(sys, f"{str(expireInform.days)}days remained")
            return "notyet"
        

# 만료시 저장해줄 수 있는 로직
    def genAPItoken(self):
        # fullurl=self.url+"/web/api/v2.1/users/generate-api-token?token="+str(self.token)
        fullurl=f"{self.url}/web/api/v2.1/users/generate-api-token?token={str(self.token)}"
        response=self.sess.post(fullurl)
        cont=json.loads(response._content)
        # print(cont)
        api={"tk":cont.get("data").get("token")}
        with open(self.tkfilepath, 'w') as f:
            json.dump(api,f)
            log_write2(sys,"token refreshed")
        return(cont.get("data").get("token"))
        
    def getAccount(self,pre_datas):
        self.pre_datas=pre_datas
        # fullurl=self.url+"/web/api/v2.1/accounts?token="+str(self.token)
        if pre_datas:
            self.accData={}
            for data in pre_datas:
                if data.get("accountName") not in self.accData:
                    self.accData[data.get("accountName")]=data.get("roleId")
        else:
            fullurl=f"{self.url}/web/api/v2.1/accounts?token={str(self.token)}"
            response=self.sess.get(fullurl)
            cont=json.loads(response._content)
            datas=cont.get("data")
            self.accData={}
            for data in datas:
                if data.get("state")=="active":
                    self.accData[data.get("name")]=data.get("id")
        return self.accData        
    
    def getSite(self,accid):
        print(self.pre_datas)
        if accid=="siteUser":
            self.siteData={}
            for data in self.pre_datas:
                if data.get("id") not in self.siteData:
                    self.siteData[data.get("name")]=data.get("id")
        else:
            fullurl=self.url+"/web/api/v2.1/sites?accountId="+accid+"&token="+str(self.token)+"&limit=300"
            response=self.sess.get(fullurl)
            cont=json.loads(response._content)
            print(cont)
            datas=cont.get("data").get("sites")
            self.siteData={}
            for data in datas:
                if data.get("state")=="active":
                    self.siteData[data.get("name")]=data.get("id")
        return self.siteData
            
    def getGroup(self,siteid):
        fullurl=self.url+"/web/api/v2.1/groups?siteIds="+siteid+"&token="+str(self.token)+"&limit=300"
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data")
        self.grpData={}
        for data in datas:
            self.grpData[data.get("name")]=data.get("id")
        return self.grpData
    
    def changeDir(self,dir):
        self.rootpath=dir
    
    def generateReport(self, selInfo, names):
        try:
            startd,endd,accid,siteid,grpid=selInfo["startd"][0],selInfo["endd"][0],selInfo["accid"][0],selInfo["siteid"][0],selInfo["grpid"][0]
            # 현재 그룹단위 지정만되게.
            id=grpid
            stype="group"
            # url, 생성할 id, 조건 줄 기간
            mR=mainReporting.mainReporting(self.url, id,self.token, startd,endd,stype,names, self.rootpath)
            log_txt=str(startd)+" ~ "+str(endd) +";"+str(stype)+";"+str(names[0])+";"+str(names[1])+";"+str(names[2])
            log_write2(sys,log_txt)
            log_write2(sys,"mainReporting start")
            datas=mR.get("date",stype,id)
            log_write2(sys,"data get")
            
            # type은 malicious, suspicious, all
            type = "all"
            # 보고서 생성(전체 리스트)
            if datas=="none":
                dir = "데이터가 없습니다."
                return dir+" 범위를 수정해주세요."
            else: 
                res_reForge = mR.reForgeCont(datas, type)
            log_write2(sys,"start func reforge completed")
            # print(res_reForge)
            if res_reForge == 0:
                dir = "데이터가 없습니다."
                return dir+" 범위를 수정해주세요."
            else:
                sm.shared_status="엔드포인트 정보를 수집합니다."
                sm.shared_per=15
                mR.getEndpoints(id,stype)
                # memoryFollow("getEndpoints")
                sm.shared_status="Top20 위협 엔드포인트를 분석합니다."
                sm.shared_per=30
                mR.getTop20(datas)
                
                # memoryFollow("getTop20")
                sm.shared_per=45
                sm.shared_status="위협 정보를 수집중입니다."
                mR.gatherThreatscnt(datas, type)
                sm.shared_per=60
                sm.shared_status="엔진별 위협정보를 분석합니다."
                mR.gatherByEngine(datas)
                sm.shared_per=75
                sm.shared_status="위협 해결 여부를 분석합니다."
                mR.getSolved()
                sm.shared_per=90
                sm.shared_status="감염된 엔드포인트의 세부정보를 분석합니다."
                mR.getInfectedDetail(datas)
                # memoryFollow("getInfectedDetail")
            
                dir = mR.endSave()
                sm.shared_status="보고서를 마무리 하는 중입니다."
                sm.shared_per=95
                return dir
        except IndexError:
            dir="scope 지정 오류"
            return dir
        
##########################export 기능
    def exportfile(self, selInfo, type, date):
        startd,endd,accid,siteid,grpid=selInfo["startd"][0],selInfo["endd"][0],selInfo["accid"][0],selInfo["siteid"][0],selInfo["grpid"][0]
        # 일단 group 기준
        cntUrl=self.url+"/web/api/v2.1/agents/count?groupIds="+str(grpid)+"&token="+str(self.token)
        cntres=self.sess.get(cntUrl)
        cntcont=json.loads(cntres._content)
        totalAgent=cntcont.get("data").get("total")
        if totalAgent>=1000:
            log_write2(sys, "over 1000 endpoints. need to repair.")
            print("1000대가 넘습니다. 로직 수정 필요.")
        
        fullurl=self.url+"/web/api/v2.1/agents?limit=1000&groupIds="+str(grpid)+"&token="+str(self.token)
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data")
        accname=self.findkey(self.accData,str(accid))
        sitename=self.findkey(self.siteData,str(siteid))
        grpname=self.findkey(self.grpData,str(grpid))

        if type=="csv":
            export_filename=accname+"_"+sitename+"_"+grpname+"_"+date+".csv"
            wholefilepath=self.rootpath+"\\"+export_filename
            with open(wholefilepath, 'w', newline='',encoding="utf8") as f:
                wr=csv.writer(f)
                wr.writerow(["name", "Installed", "AgentName"])
            f.close()
            i=0
            for data in datas:
                i+=1
                print(i,"/",len(datas))
                # print(data.get("id"),":",data.get("isActive"),data.get("isDecommissioned"),data.get("computerName"))
                app=self.getApplications(str(data.get("id")))
                self.writeCSV(data.get("computerName"), app, startd, endd,wholefilepath)
            print("done!")
            log_write2(sys,"done with the csv file making")
            return wholefilepath
               
        elif type=="xlsx":
            # 아직 미구현
            export_filename=r"test.xlsx"
            wb=op.Workbook()
            ws = wb.create_sheet("application")
            wb.save(export_filename)
        
    def writeCSV(self,name,apps,startd,endd,wholefilepath):
        with open(wholefilepath, 'a', newline='',encoding="utf8") as f:
            wr=csv.writer(f)
            startDate=self.timeReturn(startd[0:4],startd[5:7],startd[8:10],0,0,0)
            endDate=self.timeReturn(endd[0:4],endd[5:7],endd[8:10],0,0,0)
            try:
                for app in apps:
                    if app.get("installedDate") >= startDate and app.get("installedDate") <=endDate:
                        print(app.get("installedDate"))
                        print(startDate)
                        print(app.get("installedDate") >= startDate and app.get("installedDate") <=endDate)
                        print("==================")
                        installeddate=str(app.get("installedDate")[0:10]+" "+app.get("installedDate")[11:16])
                        wr.writerow([str(app.get("name")), installeddate, name])
                        # print (name)
                        # print(app.get("installedDate"))
                        # print(app.get("name"))
                        # print(app.get("publisher"))
                        # print(app.get("size"))

            except:
                print("err")
                print(app)
            

    def writeXlsx(self,name,apps,startd,endd):
        # 아직 미구현
        pass
    
    def findkey(self, dict, findval):    
        for val1, val2 in dict.items():
            if val2==findval:
                return val1
##########################export 기능 
    def getApplications(self,id):
        fullurl=self.url+"/web/api/v2.1/agents/applications?ids="+id+"&token="+str(self.token)
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data")
        return datas
    
    def ksttimeReturn(self,year, month,day,hour,min,sec):
        tz=pytz.timezone('UTC')
        d=date(int(year),int(month),int(day))
        t=time(hour,min,sec)
        dt=datetime.combine(d,t,tz)
        ksttime=dt-timedelta(hours=9)
        chtime=ksttime.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
        return chtime
    
    def timeReturn(self,year, month,day,hour,min,sec):
        tz=pytz.timezone('UTC')
        d=date(int(year),int(month),int(day))
        t=time(hour,min,sec)
        dt=datetime.combine(d,t,tz)
        chtime=dt.strftime('%Y-%m-%dT%H:%M:%S.000000Z')
        return chtime