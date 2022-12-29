import json
import pandas as pd
from connect import sess

class getThreats:

    def __init__(self, s1Site, sess, ids, token, mkreport):
        self.cursor = 'start'
        self.sess = sess
        self.ids = ids
        self.cnt = 0
        self.limit = 50
        self.uri = s1Site+"/web/api/v2.1/threats?limit="+str(self.limit)+"&"
        self.token = token
        self.totItems = 10
        self.totcnt = 0
        self.makeReport = mkreport
        self.threatsData = []
        print("getThreats init")

    def getfromDate(self, startD, endD, searchType,id):
        self.ids=id
        getUrl = self.uri+"createdAt__gte="+startD+"&createdAt__lte="+endD
        if searchType == "group":
            getUrl = getUrl+"&groupIds="+self.ids+"&token="+self.token
        elif searchType == "site":
            getUrl = getUrl+"&siteIds="+self.ids+"&token="+self.token
        elif searchType == "account":
            getUrl = getUrl+"&accountIds="+self.ids+"&token="+self.token
        elif searchType == "all":
            getUrl = getUrl+"&token="+self.token
        print("getfromDate")
        response = self.sess.get(getUrl)
        contents = json.loads(response._content)

        totItems = contents.get('pagination').get('totalItems')
        self.cursor = contents.get('pagination').get('nextCursor')
        self.gfdcolumn = 32
        self.gfdrow = totItems
        self.dataArr = [[0 for _ in range(self.gfdcolumn)] for _ in range(self.gfdrow)]
        # self.makeReport.writeTitle("기간별 전체 탐지 내역", 2)
        # self.makeReport.mkTable_detail(self.gfdrow+1, 6)
        self.saveDataArr(contents)

        # self.saveThreatInfo(contents)

        try:
            while self.cursor != True:
                getUrl2 = getUrl+"&cursor="+self.cursor
                response = self.sess.get(getUrl2)
                contents = json.loads(response._content)
                # self.totItems=contents.get('pagination').get('totalItems')
                self.cursor = contents.get('pagination').get('nextCursor')
                # self.saveThreatInfo(contents)
                self.saveDataArr(contents)
                if totItems == self.totcnt:
                    print("totItem Done")
                    break
        except:
            # print(type(self.cursor))
            print("err")
        # self.makeReport.saveDoc()
        # print(self.dataArr)
        return self.dataArr
        # print(self.dataArr)

    def saveThreatInfo(self, contents):
        init = self.cnt
        end = self.cnt+len(contents.get('data'))
        if init != 0:
            end = end-init-1
            init = 0
        # print("init",init,end)
        for i in range(init, end):
            self.totcnt += 1
            # print(self.totcnt)
            detectInfo = str(self.totcnt)+" uuid :"+contents.get('data')[i].get('agentDetectionInfo').get('agentUuid')+" / IPv4 :"+contents.get('data')[i].get(
                'agentDetectionInfo').get('agentIpV4')+" / MitigationMode : "+contents.get('data')[i].get('agentDetectionInfo').get('agentMitigationMode')
            # self.makeReport.writeDown(detectInfo)
            # print(detectInfo)
        # for i in range(0,self.limit):
        #     detectInfo="uuid :"+contents.get('data')[i].get('agentDetectionInfo').get('agentUuid')+" / IPv4 :"+contents.get('data')[i].get('agentDetectionInfo').get('agentIpV4')+" / MitigationMode : "+contents.get('data')[i].get('agentDetectionInfo').get('agentMitigationMode')
        #     self.makeReport.writeDown(detectInfo)
        #     print(detectInfo)
        #     print(self.totItems)

    def getTop20fromThreat(self,datas):
        dic_t20agents={}
        for data in datas:
            #감염여부 확인
            # print(data)
            if data[4] in dic_t20agents.keys():
                a=int(dic_t20agents.get(data[4]))
                a+=1
                dic_t20agents[data[4]]=a
            else:
                dic_t20agents[data[4]]=1
        sorted_dic=dict(sorted(dic_t20agents.items(),key=lambda x:x[1],reverse=True))
        return sorted_dic
    
    def saveDataArr(self, contents):
        init = self.cnt
        end = self.cnt+len(contents.get('data'))
        if init != 0:
            end = end-init-1
            init = 0
        # print("init",init,end)

        for i in range(init, end):
            try:
                dataFcont = contents.get('data')[i]
                # print(self.totcnt)
                # print(dataFcont.get("threatInfo"))
                self.dataArr[self.totcnt][0] = dataFcont.get("agentRealtimeInfo").get("accountName")
                self.dataArr[self.totcnt][1] = dataFcont.get("agentRealtimeInfo").get("siteName")
                self.dataArr[self.totcnt][2] = dataFcont.get("agentRealtimeInfo").get("groupName")
                self.dataArr[self.totcnt][3] = dataFcont.get("agentRealtimeInfo").get("agentDomain")
                self.dataArr[self.totcnt][4] = dataFcont.get("agentRealtimeInfo").get("agentComputerName")
                self.dataArr[self.totcnt][5] = dataFcont.get("agentRealtimeInfo").get("agentOsName")
                self.dataArr[self.totcnt][6] = dataFcont.get("agentRealtimeInfo").get("agentOsType")
                self.dataArr[self.totcnt][7] = dataFcont.get("agentRealtimeInfo").get("agentMachineType")
                self.dataArr[self.totcnt][8] = dataFcont.get("agentRealtimeInfo").get("agentUuid")
                self.dataArr[self.totcnt][9] = dataFcont.get("agentRealtimeInfo").get("agentVersion")
                self.dataArr[self.totcnt][10] = dataFcont.get("agentRealtimeInfo").get(
                    "networkInterfaces")[0].get("inet")[0]
                self.dataArr[self.totcnt][11] = dataFcont.get("agentRealtimeInfo").get("agentNetworkStatus")
                self.dataArr[self.totcnt][12] = dataFcont.get("agentRealtimeInfo").get("agentMitigationMode")
                self.dataArr[self.totcnt][13] = dataFcont.get("threatInfo").get("analystVerdict")
                self.dataArr[self.totcnt][14] = dataFcont.get("threatInfo").get("classification")
                self.dataArr[self.totcnt][15] = dataFcont.get("threatInfo").get("classificationSource")
                self.dataArr[self.totcnt][16] = dataFcont.get("threatInfo").get("confidenceLevel")
                self.dataArr[self.totcnt][17] = dataFcont.get("threatInfo").get("detectionType")
                self.dataArr[self.totcnt][18] = dataFcont.get("threatInfo").get("createdAt")
                self.dataArr[self.totcnt][19] = dataFcont.get("threatInfo").get("engines")[0]
                self.dataArr[self.totcnt][20] = dataFcont.get("threatInfo").get("incidentStatus")
                self.dataArr[self.totcnt][21] = dataFcont.get("threatInfo").get("isFileless")
                self.dataArr[self.totcnt][22] = dataFcont.get("threatInfo").get("maliciousProcessArguments")
                self.dataArr[self.totcnt][23] = dataFcont.get("threatInfo").get("mitigationStatus")
                self.dataArr[self.totcnt][24] = dataFcont.get("threatInfo").get("pendingActions")
                self.dataArr[self.totcnt][25] = dataFcont.get("threatInfo").get("filePath")
                self.dataArr[self.totcnt][26] = dataFcont.get("threatInfo").get("originatorProcess")
                self.dataArr[self.totcnt][27] = dataFcont.get("threatInfo").get("processUser")
                self.dataArr[self.totcnt][28] = dataFcont.get("threatInfo").get("publisherName")
                self.dataArr[self.totcnt][29] = dataFcont.get("threatInfo").get("updatedAt")
                self.dataArr[self.totcnt][30] = dataFcont.get("indicators")
                self.dataArr[self.totcnt][31] = dataFcont.get("threatInfo").get("threatName")
                self.totcnt += 1
                # self.makeReport.writeDown(self.dataArr[self.totcnt][4])
                # print(self.dataArr)
                # print(self.dataArr[i])
                # self.threatsData[i]
            except IndexError:
                # print(contents.get('data')[i])
                if dataFcont.get("indicators")==" ":
                    indicatorinfo="nothing"
                else:
                    indicatorinfo=dataFcont.get("indicators")
                if contents.get('data')[i].get("agentRealtimeInfo").get("networkInterfaces") ==" ":
                    inet4="삭제된 PC"
                else:
                    inet4 = dataFcont.get("agentRealtimeInfo").get("networkInterfaces")
                self.dataArr[self.totcnt][0] = dataFcont.get("agentRealtimeInfo").get("accountName")
                self.dataArr[self.totcnt][1] = dataFcont.get("agentRealtimeInfo").get("siteName")
                self.dataArr[self.totcnt][2] = dataFcont.get("agentRealtimeInfo").get("groupName")
                self.dataArr[self.totcnt][3] = dataFcont.get("agentRealtimeInfo").get("agentDomain")
                self.dataArr[self.totcnt][4] = dataFcont.get("agentRealtimeInfo").get("agentComputerName")
                self.dataArr[self.totcnt][5] = dataFcont.get("agentRealtimeInfo").get("agentOsName")
                self.dataArr[self.totcnt][6] = dataFcont.get("agentRealtimeInfo").get("agentOsType")
                self.dataArr[self.totcnt][7] = dataFcont.get("agentRealtimeInfo").get("agentMachineType")
                self.dataArr[self.totcnt][8] = dataFcont.get("agentRealtimeInfo").get("agentUuid")
                self.dataArr[self.totcnt][9] = dataFcont.get("agentRealtimeInfo").get("agentVersion")
                self.dataArr[self.totcnt][10] = inet4
                self.dataArr[self.totcnt][11] = dataFcont.get("agentRealtimeInfo").get("agentNetworkStatus")
                self.dataArr[self.totcnt][12] = dataFcont.get("agentRealtimeInfo").get("agentMitigationMode")
                self.dataArr[self.totcnt][13] = dataFcont.get("threatInfo").get("analystVerdict")
                self.dataArr[self.totcnt][14] = dataFcont.get("threatInfo").get("classification")
                self.dataArr[self.totcnt][15] = dataFcont.get("threatInfo").get("classificationSource")
                self.dataArr[self.totcnt][16] = dataFcont.get("threatInfo").get("confidenceLevel")
                self.dataArr[self.totcnt][17] = dataFcont.get("threatInfo").get("detectionType")
                self.dataArr[self.totcnt][18] = dataFcont.get("threatInfo").get("createdAt")
                self.dataArr[self.totcnt][19] = dataFcont.get("threatInfo").get("engines")[0]
                self.dataArr[self.totcnt][20] = dataFcont.get("threatInfo").get("incidentStatus")
                self.dataArr[self.totcnt][21] = dataFcont.get("threatInfo").get("isFileless")
                self.dataArr[self.totcnt][22] = dataFcont.get("threatInfo").get("maliciousProcessArguments")
                self.dataArr[self.totcnt][23] = dataFcont.get("threatInfo").get("mitigationStatus")
                self.dataArr[self.totcnt][24] = dataFcont.get("threatInfo").get("pendingActions")
                self.dataArr[self.totcnt][25] = dataFcont.get("threatInfo").get("filePath")
                self.dataArr[self.totcnt][26] = dataFcont.get("threatInfo").get("originatorProcess")
                self.dataArr[self.totcnt][27] = dataFcont.get("threatInfo").get("processUser")
                self.dataArr[self.totcnt][28] = dataFcont.get("threatInfo").get("publisherName")
                self.dataArr[self.totcnt][29] = dataFcont.get("threatInfo").get("updatedAt")
                self.dataArr[self.totcnt][30] = indicatorinfo
                self.dataArr[self.totcnt][31] = dataFcont.get("threatInfo").get("threatName")
                # print(contents.get('data')[i].get("agentRealtimeInfo"))



# 활용 가능한 모듈
    # 만들기만 한 함수
    def mkurlMalicious(self, url, yorn):
        if yorn == "y":
            url_fM = url+"&confidenceLevels=malicious"
        elif yorn == "n":
            url_fM = url+"&confidenceLevels=suspicious"
        elif yorn == "b":
            url_fM = url+"&confidenceLevels=malicious,suspicious"
        return url_fM

    def mkurlStatus(self, url, yorn):
        if yorn == "r":
            url_fM = url+"&incidentStatuses=resolved"
        elif yorn == "u":
            url_fM = url+"&incidentStatuses=unresolved"
        elif yorn == "i":
            url_fM = url+"&incidentStatuses=in_progress"
        elif yorn == "ru" or yorn == "ur":
            url_fM = url+"&incidentStatuses=resolved,unresolved"
        elif yorn == "ri" or yorn == "ir":
            url_fM = url+"&incidentStatuses=resolved,in_progress"
        elif yorn == "ui" or yorn == "iu":
            url_fM = url+"&incidentStatuses=unresolved,in_progress"
        elif yorn == "rui" or yorn == "riu" or yorn == "uir" or yorn == "uri" or yorn == "iur" or yorn == "iru":
            url_fM = url+"&incidentStatuses=resolved,unresolved,in_progress"
        return url_fM

    def mkurlMitigated(self, url, yorn):
        if yorn == "m":
            url_fM = url+"&mitigationStatuses=mitigated"
        elif yorn == "nm":
            url_fM = url+"&mitigationStatuses=not_mitigated"
        return url_fM

    def mkurlResolved(self, url, yorn):
        if yorn == "r":
            url_fM = url+"&resolved=true"
        elif yorn == "nr":
            url_fM = url+"&resolved=false"
        return url_fM
