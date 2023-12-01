import json
import pandas as pd
from connect import sess
import sys
from logger import *

class getThreats:

    def __init__(self, s1Site, sess, ids, token, mkreport):
        self.cursor = 'start'
        self.sess = sess
        self.ids = ids
        self.cnt = 0
        self.limit = 1000
        self.uri = s1Site+"/web/api/v2.1/threats?limit="+str(self.limit)+"&"
        self.token = token
        self.totItems = 10
        self.totcnt = 0
        self.makeReport = mkreport
        self.threatsData = []
        self.mnmb={"mitigated":0,"not_mitigated":0,"marked_as_benign":0}
        log_write2(sys,"for debug")

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
        log_write2(sys,"for debug")
        self.glUrl=getUrl
        response = self.sess.get(getUrl)
        contents = json.loads(response._content)
        totItems = contents.get('pagination').get('totalItems')
        self.cursor = contents.get('pagination').get('nextCursor')
        self.gfdcolumn = 33
        self.gfdrow = totItems
        if self.cursor==None and totItems==0:
            self.dataArr=[]
        else:
            self.dataArr = [[0 for _ in range(self.gfdcolumn)] for _ in range(self.gfdrow)]
        # self.makeReport.writeTitle("기간별 전체 탐지 내역", 2)
        # self.makeReport.mkTable_detail(self.gfdrow+1, 6)
        self.saveDataArr(contents)

        # self.saveThreatInfo(contents)
        if self.cursor==None:
            self.cursor="none"
        try:
            while self.cursor != "none":
                getUrl2 = getUrl+"&cursor="+self.cursor
                response = self.sess.get(getUrl2)
                contents = json.loads(response._content)
                # self.totItems=contents.get('pagination').get('totalItems')
                self.cursor = contents.get('pagination').get('nextCursor')
                # self.saveThreatInfo(contents)
                self.saveDataArr(contents)
                if totItems == self.totcnt:
                    log_write2(sys,"for debug")
                    break
        except Exception as e:
            print("getThreats-getfromDate",e)
            return "none"
        # self.makeReport.saveDoc()
        # print(self.dataArr)
        # print("Dataarr",self.dataArr)
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
        cnt=0;
        for data in datas:
            #감염여부 확인
            # print(data)
            if data[4]!=0:
                if data[4] in dic_t20agents.keys():
                    a=int(dic_t20agents.get(data[4]))
                    a+=1
                    dic_t20agents[data[4]]=a
                else:
                    dic_t20agents[data[4]]=1
            else : 
                cnt+=1
        print(cnt)
        sorted_dic=dict(sorted(dic_t20agents.items(),key=lambda x:x[1],reverse=True))
        # print (sorted_dic)
        return sorted_dic
    
    def cntMitiStatus(self,type):
        if type == "m":
            _url = self.glUrl+"&mitigationStatuses=mitigated&limit=1000"
        if type == "nm":
            _url = self.glUrl+"&mitigationStatuses=not_mitigated&limit=1000"
        if type == "b":
            _url = self.glUrl+"&mitigationStatuses=marked_as_benign&limit=1000"
        response = self.sess.get(_url)
        contents = json.loads(response._content)
        log_write2(sys,"for debug")
    
    def mnmb_call(self):
        return self.mnmb
    
    def saveDataArr(self, contents):
        init = self.cnt
        end = self.cnt+len(contents.get('data'))
        if init != 0:
            end = end-init-1
            init = 0
        # print("init",init,end)
        # print(contents.get('data'))
        for i in range(init, end):
            dataFcont = contents.get('data')[i]
            if dataFcont.get("threatInfo").get("mitigationStatus")=="mitigated":
                self.mnmb["mitigated"]+=1
            if dataFcont.get("threatInfo").get("mitigationStatus")=="not_mitigated":
                self.mnmb["not_mitigated"]+=1
            if dataFcont.get("threatInfo").get("mitigationStatus")=="marked_as_benign":
                self.mnmb["marked_as_benign"]+=1
            try:
                # print(self.totcnt)
                # print(dataFcont)
                self.dataArr[i][0] = dataFcont.get("agentRealtimeInfo").get("accountName")
                self.dataArr[i][1] = dataFcont.get("agentRealtimeInfo").get("siteName")
                self.dataArr[i][2] = dataFcont.get("agentRealtimeInfo").get("groupName")
                self.dataArr[i][3] = dataFcont.get("agentRealtimeInfo").get("agentDomain")
                self.dataArr[i][4] = dataFcont.get("agentRealtimeInfo").get("agentComputerName")
                self.dataArr[i][5] = dataFcont.get("agentRealtimeInfo").get("agentOsName")
                self.dataArr[i][6] = dataFcont.get("agentRealtimeInfo").get("agentOsType")
                self.dataArr[i][7] = dataFcont.get("agentRealtimeInfo").get("agentMachineType")
                self.dataArr[i][8] = dataFcont.get("agentRealtimeInfo").get("agentUuid")
                self.dataArr[i][9] = dataFcont.get("agentRealtimeInfo").get("agentVersion")
                self.dataArr[i][10] = dataFcont.get("agentRealtimeInfo").get(
                    "networkInterfaces")[0].get("inet")[0]
                self.dataArr[i][11] = dataFcont.get("agentRealtimeInfo").get("agentNetworkStatus")
                self.dataArr[i][12] = dataFcont.get("agentRealtimeInfo").get("agentMitigationMode")
                self.dataArr[i][13] = dataFcont.get("threatInfo").get("analystVerdict")
                self.dataArr[i][14] = dataFcont.get("threatInfo").get("classification")
                self.dataArr[i][15] = dataFcont.get("threatInfo").get("classificationSource")
                self.dataArr[i][16] = dataFcont.get("threatInfo").get("confidenceLevel")
                self.dataArr[i][17] = dataFcont.get("threatInfo").get("detectionType")
                self.dataArr[i][18] = dataFcont.get("threatInfo").get("createdAt")
                self.dataArr[i][19] = dataFcont.get("threatInfo").get("engines")[0]
                self.dataArr[i][20] = dataFcont.get("threatInfo").get("incidentStatus")
                self.dataArr[i][21] = dataFcont.get("threatInfo").get("isFileless")
                self.dataArr[i][22] = dataFcont.get("threatInfo").get("maliciousProcessArguments")
                self.dataArr[i][23] = dataFcont.get("threatInfo").get("mitigationStatus")
                self.dataArr[i][24] = dataFcont.get("threatInfo").get("pendingActions")
                self.dataArr[i][25] = dataFcont.get("threatInfo").get("filePath")
                self.dataArr[i][26] = dataFcont.get("threatInfo").get("originatorProcess")
                self.dataArr[i][27] = dataFcont.get("threatInfo").get("processUser")
                self.dataArr[i][28] = dataFcont.get("threatInfo").get("publisherName")
                self.dataArr[i][29] = dataFcont.get("threatInfo").get("updatedAt")
                self.dataArr[i][30] = dataFcont.get("indicators")
                self.dataArr[i][31] = dataFcont.get("threatInfo").get("threatName")
                self.dataArr[i][32] = dataFcont.get("threatInfo").get("sha1")
                self.totcnt += 1
                # self.makeReport.writeDown(self.dataArr[i][4])
                # print(self.dataArr)
                # print(self.dataArr[i])
                # self.threatsData[i]
            except IndexError:
                if dataFcont.get("indicators")==" ":
                    indicatorinfo="nothing"
                else:
                    indicatorinfo=dataFcont.get("indicators")
                if contents.get('data')[i].get("agentRealtimeInfo").get("networkInterfaces") ==" ":
                    inet4="삭제된 PC"
                else:
                    inet4 = dataFcont.get("agentRealtimeInfo").get("networkInterfaces")
                self.dataArr[i][0] = dataFcont.get("agentRealtimeInfo").get("accountName")
                self.dataArr[i][1] = dataFcont.get("agentRealtimeInfo").get("siteName")
                self.dataArr[i][2] = dataFcont.get("agentRealtimeInfo").get("groupName")
                self.dataArr[i][3] = dataFcont.get("agentRealtimeInfo").get("agentDomain")
                self.dataArr[i][4] = dataFcont.get("agentRealtimeInfo").get("agentComputerName")
                self.dataArr[i][5] = dataFcont.get("agentRealtimeInfo").get("agentOsName")
                self.dataArr[i][6] = dataFcont.get("agentRealtimeInfo").get("agentOsType")
                self.dataArr[i][7] = dataFcont.get("agentRealtimeInfo").get("agentMachineType")
                self.dataArr[i][8] = dataFcont.get("agentRealtimeInfo").get("agentUuid")
                self.dataArr[i][9] = dataFcont.get("agentRealtimeInfo").get("agentVersion")
                self.dataArr[i][10] = inet4
                self.dataArr[i][11] = dataFcont.get("agentRealtimeInfo").get("agentNetworkStatus")
                self.dataArr[i][12] = dataFcont.get("agentRealtimeInfo").get("agentMitigationMode")
                self.dataArr[i][13] = dataFcont.get("threatInfo").get("analystVerdict")
                self.dataArr[i][14] = dataFcont.get("threatInfo").get("classification")
                self.dataArr[i][15] = dataFcont.get("threatInfo").get("classificationSource")
                self.dataArr[i][16] = dataFcont.get("threatInfo").get("confidenceLevel")
                self.dataArr[i][17] = dataFcont.get("threatInfo").get("detectionType")
                self.dataArr[i][18] = dataFcont.get("threatInfo").get("createdAt")
                self.dataArr[i][19] = dataFcont.get("threatInfo").get("engines")[0]
                self.dataArr[i][20] = dataFcont.get("threatInfo").get("incidentStatus")
                self.dataArr[i][21] = dataFcont.get("threatInfo").get("isFileless")
                self.dataArr[i][22] = dataFcont.get("threatInfo").get("maliciousProcessArguments")
                self.dataArr[i][23] = dataFcont.get("threatInfo").get("mitigationStatus")
                self.dataArr[i][24] = dataFcont.get("threatInfo").get("pendingActions")
                self.dataArr[i][25] = dataFcont.get("threatInfo").get("filePath")
                self.dataArr[i][26] = dataFcont.get("threatInfo").get("originatorProcess")
                self.dataArr[i][27] = dataFcont.get("threatInfo").get("processUser")
                self.dataArr[i][28] = dataFcont.get("threatInfo").get("publisherName")
                self.dataArr[i][29] = dataFcont.get("threatInfo").get("updatedAt")
                self.dataArr[i][30] = indicatorinfo
                self.dataArr[i][31] = dataFcont.get("threatInfo").get("threatName")
                self.dataArr[i][32] = dataFcont.get("threatInfo").get("sha1")
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



    def mkurlResolved(self, url, yorn):
        if yorn == "r":
            url_fM = url+"&resolved=true"
        elif yorn == "nr":
            url_fM = url+"&resolved=false"
        return url_fM
