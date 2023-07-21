import mainReporting
import sys
import json
import connect as conn
from connect import sess
import mkReport
from logger import *
        
class controller:
    def __init__(self):
        self.url = ""
        self.apiToken = ""
        self.accountInfo

    def setVar(self, url, apiToken):
        self.url = url
        self.apiToken = apiToken
        self.token = conn.connectAPI(self.url, "token", self.apiToken)

# 11월 14일 수정했음. 추가 수정. 예외처리 해야함+
    def findGroup(self, site_id):
        try:
            grurl = self.url+"/web/api/v2.1/groups" + \
                "?siteIds="+site_id+"&token="+self.token
            response = sess.get(grurl)
            contents = json.loads(response._content)
            # print(contents)
            cont, numofGroups = contents.get("data"), len(contents.get("data"))
            column, row = 2, numofGroups
            self.groupInfo = [[0 for _ in range(column)] for _ in range(row)]
            for i in range(0, numofGroups):
                self.groupInfo[i][0] = cont[i].get("name")
                self.groupInfo[i][1] = cont[i].get("id")
            return self.groupInfo
        except ValueError:
            log_write2(sys,"value err")
            # print("value err!")

    def findSite(self, account_id):
        try:
            siteurl = self.url+"/web/api/v2.1/sites" + \
                "?accountId="+account_id+"&token="+self.token
            response = sess.get(siteurl)
            contents = json.loads(response._content)
            cont, numofSites = contents.get("data").get("sites"), len(
                contents.get("data").get("sites"))
            column, row = 2, numofSites
            self.siteInfo = [[0 for _ in range(column)] for _ in range(row)]
            for i in range(0, numofSites):
                self.siteInfo[i][0] = cont[i].get("name")
                self.siteInfo[i][1] = cont[i].get("id")
            return self.siteInfo
        except ValueError:
            log_write2(sys,"value err")
            # print("value err!")

    def findAccount(self):
        try:
            accurl = self.url+"/web/api/v2.1/accounts"+"?limit=100&token="+self.token
            response = sess.get(accurl)
            contents = json.loads(response._content)
            print(contents)
            if contents.get('errors'):
                if contents.get('errors')[0].get("detail")=="Action is not allowed to site users":
                    siteurl = self.url+"/web/api/v2.1/sites"+"?token="+self.token
                    response2 = sess.get(siteurl)
                    contents2 = json.loads(response2._content)
                    numofSites, cont = len(contents2.get("data").get("sites")), contents2.get("data").get("sites")
                    # print(numofSites)
                    column, row = 3, numofSites
                    # print(cont)
                    self.accountInfo = [[0 for _ in range(column)] for _ in range(row)]
                    for i in range(0, numofSites):
                        # print(cont[i])
                        self.accountInfo[i][0] = cont[i].get("name")
                        self.accountInfo[i][1] = 1
                        self.accountInfo[i][2] = cont[i].get("id")
                        data=[self.accountInfo, "site",cont[i].get("accountId"),cont[i].get("accountName")]
                    return data
            else:
                numofSites, cont = len(contents.get("data")), contents.get("data")
                column, row = 3, numofSites
                self.accountInfo = [[0 for _ in range(column)] for _ in range(row)]
                for i in range(0, numofSites):
                    self.accountInfo[i][0] = cont[i].get("name")
                    self.accountInfo[i][1] = cont[i].get("numberOfSites")
                    self.accountInfo[i][2] = cont[i].get("id")
                    data=[self.accountInfo, "account"]
                return data
        except ValueError:
            log_write2(sys,"value err")
            return "err"
        except TypeError as e:
            log_write2(sys,"type err")
            return "err"
        
    def setPrbar(self,id,start,end,groupornot,names):
        if groupornot==False:
            stype="site"
        else:
            stype="group"
        id = id
        startday = str(start)+"T00:00:00.000000Z"
        endday = str(end)+"T23:59:59.999999Z"
        log_write2(sys,"set prbar maximum")
        self.mR = mainReporting.mainReporting(
            self.url, self.apiToken, id, self.token, startday, endday,str(start),str(end),stype,names)
        datas = self.mR.get("date", stype, id)
        return len(datas)
        # print(startday)
        
        
    def start(self, id, start, end, groupornot,names):
        if groupornot==False:
            stype="site"
        else:
            stype="group"
        id = id
        startday = str(start)+"T00:00:00.000000Z"
        endday = str(end)+"T23:59:59.999999Z"
        # print(startday)
        mR = mainReporting.mainReporting(
            self.url, self.apiToken, id, self.token, startday, endday,str(start),str(end),stype,names)
        print(startday,"/",endday)
        datas = mR.get("date", stype, id)
        log_write2(sys,"start func begin")
        
        # type은 malicious, suspicious, all
        type = "all"
        # 보고서 생성(전체 리스트)
        res_reForge = mR.reForgeCont(datas, type)
        log_write2(sys,"start func reforge completed")
        # try:
        if res_reForge == 0:
            dir = "데이터가 없습니다."
            return dir+" 범위를 수정해주세요."
        else:
            mR.getEndpoints(id,stype)
            mR.getTop20(datas)
            mR.gatherThreatscnt(datas, type)
            mR.gatherByEngine(datas)
            mR.getSolved()
            mR.getInfectedDetail(datas)
        
            dir = mR.endSave()
            return dir+" 위치에 보고서가 생성되었습니다."
        # except :
        #     print(res_reForge)
        #     log_write2(sys,"exception occur")
            
        
        

        # 차트 생성(위협별)
