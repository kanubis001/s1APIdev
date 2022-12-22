import json
import pandas as pd
from connect import sess


class getAgents:

    def __init__(self, s1Site, sess, groupIds, token):
        self.cursor = 'start'
        self.networkInterfaceInet__contains = "0"
        self.externalIp__contains = "0"
        self.sess = sess
        self.chkex = True
        self.endpointInfo = []
        self.cnt_coms = 0
        self.cnt_err_coms = 0
        uri = "/web/api/v2.1/agents?"
        self.fullsiteurl = s1Site
        self.fulluri = s1Site+uri
        self.token = token
        ################# 아래 항목을 수정해서 API url 컨트롤
        self.edit_req_url = self.fulluri+"groupIds="+groupIds
        ###################################################
        self.req_url = self.edit_req_url+"&cursor="+self.cursor

    def setVar(self, s1Site, sess, groupIds):
        uri = "/web/api/v2.1/agents?"
        self.fullsiteurl = s1Site
        self.fulluri = s1Site+uri

        # computerName__like="DESKTOP"
        # accountIds="926627569543769282"
        # siteIds="815520265168496110"
        # # groupIds="1213456060215715837"
        # limit="1000"
        # sortOrder="desc"
        # updatedAt__gt="2021-10-20T00:00:00.000000Z"
        # skipnum=0

        ################# 아래 항목을 수정해서 API url 컨트롤
        self.edit_req_url = self.fulluri+"groupIds="+groupIds
        ###################################################
        self.req_url = self.edit_req_url+"&cursor="+self.cursor

    def getAll(self):
        while(True):
            if self.cursor != 'start':
                response = self.sess.get(self.req_url+"&token="+self.token)
            else:
                response = self.sess.get(
                    self.edit_req_url+"&token="+self.token)
            contents = json.loads(response._content)
            print(contents)
            try:
                for i in range(0, len(contents.get("data"))):
                    try:
                        #################### debug용 출력
                        # print(contents.get("data")[i].get("uuid"))
                        print(contents.get("data")[i].get("computerName"), "==>", contents.get(
                            "data")[i].get("networkInterfaces")[0].get("inet")[0])
                        # contents.get("data")[i].get("computerName"),"==>",contents.get("data")[i].get("networkInterfaces")[0].get("inet")[0]
                        # endpointInfo에 원하는 내용 삽입.
                        self.endpointInfo.append([contents.get("data")[i].get("computerName"), contents.get("data")[
                                                 i].get("networkInterfaces")[0].get("inet")[0], contents.get("data")[i].get("externalIp")])
                    except IndexError as e:
                        self.cnt_err_coms += 1
                        print("Exception log; IndexError: ", e,
                              contents.get("data")[i].get("computerName"))
                    self.cnt_coms += 1
            except TypeError as e:
                print("Exception log; TypeError: ", e)
                break

            if str(contents.get("pagination").get("nextCursor")) == 'None':
                print("log; noneCursor: "+self.cursor)
                break
            else:
                self.cursor = str(contents.get("pagination").get("nextCursor"))
                # print(cursor)

        print("Computer 갯수 : "+str(self.cnt_coms)+"대")
        print("Error Computer 갯수 : "+str(self.cnt_err_coms)+"대")
        # conn.disconnectAPI()
        return self.endpointInfo

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
        print(uuids)
        if uuids == None:
            return "No_uuid"
        url = self.fulluri+"&uuids="+uuids
        response = self.sess.get(url)
        contents = json.loads(response._content)
        if contents.get("data")[0].get("externalId") == "":
            return "empty"
        else:
            print("externalId:", contents.get("data")[0].get("externalId"))
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
        print(contents2.get("data"))
        contents = json.loads(response._content)
        return contents.get("data")


#
#API 접속 해제 및 세션 해제
