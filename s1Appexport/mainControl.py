import connect
import json
from connect import sess
from datetime import datetime, date,time,timedelta
import pytz
import csv
import openpyxl as op
from logger import *
import sys


class mainCtrl:
    
    def __init__(self,rootpath):
        self.token="init_token"
        self.url="init_url"
        self.sess=sess
        self.rootpath=rootpath
        
        
    def init_conn(self,url,apiToken):
        self.token=connect.connectAPI(url, "token",apiToken)
        self.url=url
        if self.token==0:
            log_write2(sys, "API token 값이 만료되었거나 잘못되었습니다.")
            print("API token 값이 만료 되었거나 잘못 되었습니다.")
            return "0"
        else:
            log_write2(sys, "API 토큰 정상")
            print(self.token)
            return "1"

    def chkAPItokenValid(self,apitoken):
        fullurl=self.url+"/web/api/v2.1/users/api-token-details?token="+str(self.token)
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
        if expireInform.days < 10:
            debugline="API token expired soon"+str(expireInform.days)+"days remained"
            log_write2(sys, debugline)
            self.genAPItoken(self.rootpath)
        else:
            log_write2(sys, str(expireInform.days)+"days remained")
            pass
        

# 만료시 저장해줄 수 있는 로직
    def genAPItoken(self,path):
        fullurl=self.url+"/web/api/v2.1/users/generate-api-token?token="+str(self.token)
        response=self.sess.post(fullurl)
        cont=json.loads(response._content)
        api={"tk":cont.get("data").get("token")}
        with open(path+"\\tk.json", 'w') as f:
            json.dump(api,f)
            log_write2(sys,"token refreshed")
        return(cont.get("data").get("token"))
        
    def getAccount(self):
        fullurl=self.url+"/web/api/v2.1/accounts?token="+str(self.token)
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data")
        self.accData={}
        for data in datas:
            if data.get("state")=="active":
                self.accData[data.get("name")]=data.get("id")
        return self.accData        
    
    def getSite(self,accid):
        fullurl=self.url+"/web/api/v2.1/sites?accountId="+accid+"&token="+str(self.token)
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data").get("sites")
        self.siteData={}
        for data in datas:
            if data.get("state")=="active":
                self.siteData[data.get("name")]=data.get("id")
        return self.siteData
            
    def getGroup(self,siteid):
        fullurl=self.url+"/web/api/v2.1/groups?siteIds="+siteid+"&token="+str(self.token)
        response=self.sess.get(fullurl)
        cont=json.loads(response._content)
        datas=cont.get("data")
        self.grpData={}
        for data in datas:
            self.grpData[data.get("name")]=data.get("id")
        return self.grpData
    
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