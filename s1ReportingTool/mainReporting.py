import connect as conn
from connect import sess
import datetime
import getThreats
import getEndpoints
from multiprocessing import Process, Queue
import mkReport
import progressbar
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import json

matplotlib.use('agg')


class mainReporting:
    def __init__(self, url, apitoken, gid, token, startday, endday, st, en, stype, names):
        self.s1Site = url
        self.apitoken = apitoken
        self.groupIds = gid
        self.token = token
        self.startD = startday
        self.endD = endday
        self.stype = stype
        if stype == "site":
            self.makeReport = mkReport.mkReport(st, en, [names[0], names[1]])
        else:
            self.makeReport = mkReport.mkReport(st, en, names)
        self.GT = getThreats.getThreats(
            self.s1Site, sess, self.groupIds, self.token, self.makeReport)

        print("mainReporting init", self.s1Site, self.apitoken)
        # self.filepath=csv
        # self.logFile=logFile
        # self.log=open(logFile,'a')
        # log=str(datetime.datetime.now())+" "+"url : "+str(self.s1Site)+" apiToken : "+"***********" + " Group ID : "+self.groupIds+" CSV filepath : "+self.filepath+"\n"
        # self.log.write(log)
        # print(url,apitoken,gid,csv)

    def get(self, menu, sType, id):
        # menu => 날짜로 검색 date
        menu = "date"
        if menu == "date":
            return self.GT.getfromDate(self.startD, self.endD, sType, id)

    def getEndpoints(self, findid, sType):
        mkr = self.makeReport
        GE = getEndpoints.getEndpoints(
            self.s1Site, sess, findid, sType, self.token)
        GE.getAll()
        #OS별 대수 확인 및 return(dictionary type)
        osdatas = GE.getbyOS()
        mkr.writeDown(" ")
        mkr.writeTitle("1. OS별 엔드포인트", 2)
        mkr.mktable_getbyos(len(osdatas)+1, 2)
        self.mkdictypetable(osdatas, "getbyos")

        #버전별 대수 확인 및 return(dictionary type)
        verdatas = GE.getbyversion()
        mkr.writeDown(" ")
        mkr.writeTitle("2. 버전별 엔드포인트", 2)
        mkr.mktable_getbyver(len(verdatas)+1, 2)
        self.mkdictypetable(verdatas, "getbyver")

        #감염 PC, 안전한 PC(True(감염), False)
        infdatas = GE.getbyinfected()
        mkr.writeDown(" ")
        mkr.writeTitle("3. 보호되고 있는 엔드포인트", 2)
        mkr.mktable_getbyinf(len(infdatas)+1, 2)
        self.mkdictypetable(infdatas, "getbyinf")

        #감염된 detail 정보 return(감염PC 전체)
        # GE.getbyInfectedDetail()

    def getTop20(self, datas):
        top20 = self.GT.getTop20fromThreat(datas)
        self.makeReport.writeTitle("4. 기간별 Top20 탐지 Endpoints", 2)
        if len(top20) < 20:
            row = len(top20)+1
        else:
            row = 21
        self.makeReport.mkTop20Table_detail(row, 3)
        i = 0
        for key in top20.keys():
            # print(top20.get(key))
            self.makeReport.writeDownTop20Table(key, top20.get(key), i)
            i += 1
            if i == 20:
                break
        self.makeReport.saveDoc()




    #2열 짜리 테이블 내용 입력
    def mkdictypetable(self, datas, cat):
        mkr = self.makeReport
        i = 0
        for key in datas.keys():
            # print(datas.get(key))
            mkr.writeDownTable_endpoints(key, datas.get(key), i, cat)
            i += 1
        mkr.saveDoc()

    def reForgeCont(self, datas, type):
        if len(datas) == 0:
            print("data is zero")
            return 0
        else:
            i = 0
            cntper = 0
            per = len(datas)/100
            full = len(datas)
            bar = progressbar.ProgressBar(maxval=full).start()
            if type == 'all':
                for data in datas:
                    # if i%4==0:
                    #     cntper+=per
                    # progressper=(cntper/full)*100
                    # # print(data[15],"/",data[10],"/",data[16],"/",data[14])
                    # # print(per, full, cntper, i)
                    # if round(progressper,1) >= 99:
                    #     progressper=99
                    #     if i==full:
                    #         progressper=100
                    # print(round(progressper,1),"%")
                    bar.update(i)
                    # self.makeReport.writeDownTable(data, i)
                    i += 1
                    # self.makeReport.saveDoc()
            else:
                for data in datas:
                    if type in data:
                        print(data[15], "/", data[10],
                              "/", data[16], "/", data[14])
            bar.finish()
            return 1

    def gatherThreatscnt(self, datas, type):
        try:
            # 위협 종류 파악 리스트
            threatsGubun = []
            for data in datas:
                if data[14] not in threatsGubun:
                    if data[14] == 0:
                        pass
                    else:
                        threatsGubun.append(data[14])
            # print(threatsGubun)
            column = 2
            row = len(threatsGubun)
            # 위협별 갯수 카운트 리스트
            gubunCnt = [[0 for _ in range(column)] for _ in range(row)]
            # 도표를 만들기 위해...
            ratiocnt = []
            labelcnt = []
            etclabel = "etc("
            labelcnt.insert(0, "ETC")
            ratiocnt.insert(0, 0)
            j = 0
            for i in range(len(threatsGubun)):
                gubunCnt[i][0] = threatsGubun[i]
                for data in datas:
                    if data[14] == 0:
                        pass
                    elif data[14] in threatsGubun[i]:
                        gubunCnt[i][1] += 1
            #표를 위한 자료 정제
            for i in range(len(gubunCnt)):
                if gubunCnt[i][1] < 3:
                    etclabel = etclabel+gubunCnt[i][0]+", "
                    ratiocnt[0] = ratiocnt[0]+gubunCnt[i][1]
                else:
                    j += 1
                    labelcnt.insert(j, gubunCnt[i][0])
                    ratiocnt.insert(j, gubunCnt[i][1])
            etclabel += ")"
            ratio = ratiocnt
            labels = labelcnt
            wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
            plt.pie(ratio, labels=labels, autopct="%.1f%%",
                    counterclock=False, wedgeprops=wedgeprops)
            # plt.show()
            picpath = './savePieChart.png'
            plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
            plt.clf()
            self.makeReport.writeDown("")
            self.makeReport.writeTitle("5. 위협별 탐지", 2)
            self.makeReport.addPic(picpath)
            self.makeReport.mkTblthreatpie(len(labelcnt), 2)
            for i in range(0, len(labelcnt)):
                if i == 0:
                    self.makeReport.wrTblthreatpie(i+1, 0, etclabel)
                else:
                    self.makeReport.wrTblthreatpie(i+1, 0, labelcnt[i])
                self.makeReport.wrTblthreatpie(i+1, 1, str(ratiocnt[i]))
            self.makeReport.saveDoc()
        except ValueError:
            print("Value err!")
        except TypeError:
            print("Type Err!")

    def gatherByEngine(self, datas):
        engineGubun = []
        for data in datas:
            if data[19] not in engineGubun:
                if data[19] == 0:
                    pass
                else:
                    engineGubun.append(data[19])
        # print(engineGubun)
        column = 2
        row = len(engineGubun)
        # 엔진별 갯수 카운트 리스트
        engineCnt = [[0 for _ in range(column)] for _ in range(row)]
        for i in range(len(engineGubun)):
            engineCnt[i][0] = engineGubun[i]
            for data in datas:
                if data[19] == 0:
                    pass
                elif data[19] in engineGubun[i]:
                    engineCnt[i][1] += 1
        # print(engineCnt)
        y = np.arange(len(engineCnt))
        x_axis = []
        y_axis = []
        j = 0
        #표를 위한 자료 정제
        for i in range(len(engineCnt)):
            # if engineCnt[i][1] < 10:
            #     # etclabel = etclabel+engineCnt[i][0]+", "
            #     x_axis[0] = x_axis[0]+engineCnt[i][1]
            # else:
            j += 1
            y_axis.insert(j, engineCnt[i][0])
            x_axis.insert(j, engineCnt[i][1])
        # print(x_axis)
        # print(y_axis)
        plt.barh(y, x_axis)
        plt.yticks(y, y_axis)
        picpath = './saveBarChart.png'
        plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
        plt.clf()
        # print(datas)
        self.makeReport.writeDown("")
        self.makeReport.writeTitle("6. 엔진별 탐지", 2)
        self.makeReport.addPic(picpath)
        self.makeReport.mkTblenginechart(len(engineCnt), 2)
        for i in range(0, len(engineCnt)):
            self.makeReport.wrTblenginechart(i+1, 0, engineCnt[i][0])
            self.makeReport.wrTblenginechart(i+1, 1, str(engineCnt[i][1]))
        self.makeReport.saveDoc()
        
    def getInfectedDetail(self, datas):
        mkr = self.makeReport
        mkr.writeDown(" ")
        mkr.writeTitle("7. 주요 탐지 내역 세부 사항", 2)
        colname = ["파일명", "분류", "조치여부", "탐지경로",
                   "Originator Process", "엔진", "구조/행위분석"]
        for data in datas:
            #indicator 값이 있는 것에 대해서만 보고서 작성
            if data[30]:
                indicators = ""
                rowdata = [data[31], data[14], data[23],
                           data[25], data[26], data[19], indicators]
                mkr.mktable_thDetail(7, 2)
                # mkr.writeDownTable_thDetail("파일명",1,0)
                # mkr.writeDownTable_thDetail(str(data[31]),1,1)
                k = 0
                for col in colname:
                    mkr.writeDownTable_thDetail(col, k, 0)
                    if k == 6:
                        for i in range(len(data[30])):
                            for key in data[30][i].keys():
                                # print(key,":",data[30][i].get(key))
                                tacData = data[30][i].get(
                                    "category")+"\n"+data[30][i].get("description")+"\n"
                                if key == "tactics":
                                    if not data[30][i].get(key):
                                        pass
                                    else:
                                        tactics_detail = data[30][i].get(key)[
                                            0]
                                        for key in tactics_detail.keys():
                                            tacData += "\n" + \
                                                tactics_detail.get(
                                                    "source")+" : "+tactics_detail.get("name")+" "
                                            for techData in tactics_detail.get("techniques"):
                                                tacData += "[" + \
                                                    techData.get("name")+"]"
                                                mkr.writeDownTable_thDetail(
                                                    tacData, k, 1)
                    else:
                        mkr.writeDownTable_thDetail(rowdata[k], k, 1)
                    k += 1
                mkr.writeDown(" ")
            else:
                pass
            
    def endSave(self):
        return self.makeReport.saveDoc()
