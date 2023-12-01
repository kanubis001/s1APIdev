import json
# import pandas as pd
import sys
from logger import *
from connect import sess


class getEndpoints:

    def __init__(self, s1Site, sess, id, stype, token):
        self.cursor = 'start'
        self.networkInterfaceInet__contains = "0"
        self.externalIp__contains = "0"
        self.sess = sess
        self.chkex = True
        self.endpointInfo = []
        self.cnt_coms = 0
        self.cnt_err_coms = 0
        self.id=id
        self.stype=stype
        uri = "/web/api/v2.1/agents?"
        self.fullsiteurl = s1Site
        self.fulluri = s1Site+uri
        self.token = token
        self.classver=[]
        self.classos=[]
        self.osname=[]
        self.dic_os={}
        self.dic_ver={}

    def getAll(self):
        if self.stype == "site":
            url=self.fulluri+"siteIds="+self.id
        if self.stype=="group":
            url=self.fulluri+"groupIds="+self.id
        # print(url)
        while(True):
            # print(self.cursor)
            if self.cursor != 'start':
                response = self.sess.get(url+"&cursor="+self.cursor+"&token="+self.token)
                # print("cursor start")
            else:
                response = self.sess.get(url+"&token="+self.token)
                # print(self.cursor)
            contents = json.loads(response._content)
            # print(contents)
            try:
                # print(len(contents.get("data")))
                for i in range(0, len(contents.get("data"))):
                    try:
                        #################### debug용 출력
                        # print(contents.get("data")[i].get("uuid"))
                        # print(contents.get("data")[i].get("computerName"), "==>", contents.get(
                        #     "data")[i].get("networkInterfaces")[0].get("inet")[0])
                        # contents.get("data")[i].get("computerName"),"==>",contents.get("data")[i].get("networkInterfaces")[0].get("inet")[0]
                        # endpointInfo에 원하는 내용 삽입.
                        if contents.get("data")[i].get("networkInterfaces") ==[]:
                            ip="no ipv4"
                        elif contents.get("data")[i].get("networkInterfaces")[0].get("inet")[0]==[]:
                            ip="no ipv4"
                        else:
                            if contents.get("data")[i].get("networkInterfaces")[0].get("inet")[0]==[]:
                                ip="no ipv4"
                            else:
                                ip=contents.get("data")[i].get("networkInterfaces")[0].get("inet")[0]
                        # print(contents.get("data")[i])
                        self.endpointInfo.append([
                            contents.get("data")[i].get("computerName"),
                            contents.get("data")[i].get("accountName"),
                            contents.get("data")[i].get("siteName"),
                            contents.get("data")[i].get("groupName"), 
                            contents.get("data")[i].get("agentVersion"),
                            contents.get("data")[i].get("infected"),
                            ip,
                            contents.get("data")[i].get("externalIp"),
                            contents.get("data")[i].get("osArch"),
                            contents.get("data")[i].get("osName"),
                            contents.get("data")[i].get("osType"),
                            contents.get("data")[i].get("uuid"),
                            contents.get("data")[i].get("machineType"),
                            contents.get("data")[i].get("activeThreats"),
                            True,
                            True
                            ])
                    except IndexError as e:
                        # debug=str("Exception log; endPoints IndexError: "+ contents.get("data")[i])
                        self.cnt_err_coms += 1
                        print("indexerr",contents.get("data")[i],i)
                        # log_write2(sys, contents.get("data")[i])
                    except TypeError as e:
                        print("TypeErr",contents.get("data")[i],i)
                        # debug=str("Exception log; TypeError: "+ contents.get("data")[i])
                        # log_write2(sys,contents.get("data")[i])
                        # print("Exception log; TypeError: ", e)
                        break
                    self.cnt_coms += 1
            except TypeError as e:
                print(contents.get("data")[i])
                # debug=str("Exception log; TypeError: "+ contents.get("data")[i])
                # log_write2(sys,contents.get("data")[i])
                # print("Exception log; TypeError: ", e)
                break

            if str(contents.get("pagination").get("nextCursor")) == 'None':
                debug=str("log; noneCursor: ")
                log_write2(sys,debug)
                # print("log; noneCursor: "+self.cursor)
                break
            else:
                self.cursor = str(contents.get("pagination").get("nextCursor"))
                # print(cursor)
        debug="Computer : "+str(self.cnt_coms)+"대"
        debug2="Error Computer : "+str(self.cnt_err_coms)+"대"
        log_write2(sys,debug)
        log_write2(sys,debug2)
        # conn.disconnectAPI()
        return self.endpointInfo

    def getbyOS(self):
        for data in self.endpointInfo:
            #os별 갯수
            if data[10] in self.dic_os.keys():
                a=int(self.dic_os.get(data[10]))
                a+=1
                self.dic_os[data[10]]=a
            else:
                self.dic_os[data[10]]=1
        return self.dic_os

    def getbyversion(self):
        for data in self.endpointInfo:
            #ver별 갯수
            if data[4] in self.dic_ver.keys():
                a=int(self.dic_ver.get(data[4]))
                a+=1
                self.dic_ver[data[4]]=a
            else:
                self.dic_ver[data[4]]=1
        return self.dic_ver

    def getbyinfected(self):
        dic_infected={}
        try:
            for data in self.endpointInfo:
                #감염여부 확인
                if data[5] in dic_infected.keys():
                    a=int(dic_infected.get(data[5]))
                    a+=1
                    dic_infected[data[5]]=a
                else:
                    dic_infected[data[5]]=1
            if True in dic_infected:
                if False in dic_infected:
                    dic_infected['Healthy']=dic_infected.pop(False)
                    dic_infected['Infected']=dic_infected.pop(True)
                else:
                    dic_infected['Infected']=dic_infected.pop(True)
            else:
                dic_infected['Healthy']=dic_infected.pop(False)
            # print(dic_infected)
            return dic_infected
        except KeyError:
            log_write2(sys,"dic_infected not exist")

    def getbyInfectedDetail(self):
        infectedDatas=[]
        for data in self.endpointInfo:
            if data[5]==True:
                infectedDatas.append(data)
        return infectedDatas
    
   
# 함수 사용 보류
    def classification(self):
        datas=self.endpointInfo
        i=0
        j=0
        for data in datas:
        #os classification
            if data[10] in self.classos:
                pass
            else:
                self.classos.insert(i,data[10])
                i+=1
        #version classification
            if data[4] in self.classver:
                pass
            else:
                self.classver.insert(j,data[4])
                j+=1



# getAgents 일부 내용
    def setFindUuid(self, inIP, exIP):
        if exIP == "0":
            self.chkex = False
            self.networkInterfaceInet__contains = inIP
        else:
            self.networkInterfaceInet__contains = inIP
            self.externalIp__contains = exIP

    def getUuid(self):
        if self.chkex == False:
            url = str(self.edit_req_url)+"&networkInterfaceInet__contains=" +str(self.networkInterfaceInet__contains)+"&token="+str(self.token)
        elif self.chkex == True:
            url = self.fulluri+"&networkInterfaceInet__contains="+self.networkInterfaceInet__contains + "&externalIp__contains="+self.externalIp__contains+"&token="+self.token
        response = sess.get(url)
        # print(url)
        contents = json.loads(response._content)
        # print(contents[1])
        try:
            if contents.get("pagination").get("totalItems") == 0:
                return "No", "No"
            else:
                # print(contents.get("data")[0].get("computerName")," : ",contents.get("data")[0].get("uuid"))
                return contents.get("data")[0].get("uuid"), contents.get("data")[0].get("computerName")
        except AttributeError as e:
            return "No", "No"
        # if contents.get("pagination").get("totalItems") == 0:
        #     return "No", "No"
        # else:
        #     # print(contents.get("data")[0].get("computerName")," : ",contents.get("data")[0].get("uuid"))
        #     return contents.get("data")[0].get("uuid"), contents.get("data")[0].get("computerName")

    def getCustomerid(self, uuids):
        # print(uuids)
        log_write2(sys,"uuid : "+str(uuids))
        if uuids == None:
            return "No_uuid"
        url = self.fulluri+"&uuids="+uuids
        response = self.sess.get(url)
        contents = json.loads(response._content)
        if contents.get("data")[0].get("externalId") == "":
            return "empty"
        else:
            debug=str("externalId:", contents.get("data")[0].get("externalId"))
            log_write2(sys,debug)
            # print("externalId:", contents.get("data")[0].get("externalId"))
            return contents.get("data")[0].get("externalId")

    def countAgent(self, groupIds):
        url = self.fullsiteurl+"/web/api/v2.1/agents/count?"
        response = self.sess.get(url+"groupIds="+groupIds)
        response2 = self.sess.get(
            self.fullsiteurl+"/web/api/v2.1/groups/"+groupIds)
        contents = json.loads(response._content)
        grname_contents = json.loads(response2._content)
        return contents.get("data").get("total"), grname_contents.get("data")

    def getGroups(self, accountIds):
        url = self.fullsiteurl+"/web/api/v2.1/groups"
        url2 = self.fullsiteurl+"/web/api/v2.1/groups?"+"accountIds="+accountIds

        response = self.sess.get(url)
        response2 = self.sess.get(url2)
        contents2 = json.loads(response2._content)
        # print(contents2.get("data"))
        debug=str(contents2.get("data"))
        log_write2(sys,""+debug)
        contents = json.loads(response._content)
        return contents.get("data")


#
#API 접속 해제 및 세션 해제
