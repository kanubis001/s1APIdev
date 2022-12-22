import mainReporting
import json
import connect as conn
from connect import sess
import mkReport


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
            print("value err!")

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
            print("value err!")

    def findAccount(self):
        try:
            accurl = self.url+"/web/api/v2.1/accounts"+"?token="+self.token
            response = sess.get(accurl)
            contents = json.loads(response._content)
            # print(contents)
            numofSites, cont = len(contents.get("data")), contents.get("data")
            column, row = 3, numofSites
            self.accountInfo = [[0 for _ in range(column)] for _ in range(row)]
            for i in range(0, numofSites):
                self.accountInfo[i][0] = cont[i].get(
                    "name")
                self.accountInfo[i][1] = cont[i].get("numberOfSites")
                self.accountInfo[i][2] = cont[i].get("id")
            return self.accountInfo
        except ValueError:
            print("value err!")

    def start(self, id, start, end, groupornot):
        if groupornot==False:
            stype="site"
        else:
            stype="group"
        id = id
        startday = str(start)+"T00:00:00.000000Z"
        endday = str(end)+"T23:59:59.999999Z"
        # print(startday)
        mR = mainReporting.mainReporting(
            self.url, self.apiToken, id, self.token, startday, endday,str(start),str(end))
        datas = mR.get("date", stype, id)
        
        # type은 malicious, suspicious, all
        type = "all"
        # 보고서 생성(전체 리스트)
        res_reForge = mR.reForgeCont(datas, type)
        if res_reForge == 0:
            dir = "데이터가 없습니다."
            return dir+" 범위를 수정해주세요."
        else:
            mR.gatherThreatscnt(datas, type)
            mR.gatherByEngine(datas)
            dir = mR.endSave()
            return dir+" 위치에 보고서가 생성되었습니다."
        

        # 차트 생성(위협별)
