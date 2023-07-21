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
from logger import *
import sys

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
        cont=str(self.s1Site)+str(self.apitoken)
        log_write2(sys,"mainReporting init"+cont)
        # print("mainReporting init", self.s1Site, self.apitoken)
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
            log_write2(sys,"get func menu date"+sType)
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
        log_write2(sys,"1. OS별 엔드포인트 생성")

        #버전별 대수 확인 및 return(dictionary type)
        verdatas = GE.getbyversion()
        mkr.writeDown(" ")
        mkr.writeTitle("2. 버전별 엔드포인트", 2)
        mkr.mktable_getbyver(len(verdatas)+1, 2)
        self.mkdictypetable(verdatas, "getbyver")
        log_write2(sys,"2. 버전별 엔드포인트 생성")

        #감염 PC, 안전한 PC(True(감염), False)
        infdatas = GE.getbyinfected()
        mkr.writeDown(" ")
        mkr.writeTitle("3. 보호되고 있는 엔드포인트", 2)
        mkr.mktable_getbyinf(len(infdatas)+1, 2)
        self.mkdictypetable(infdatas, "getbyinf")
        log_write2(sys,"3. 보호되고 있는 엔드포인트 생성")
        #감염된 detail 정보 return(감염PC 전체)
        # GE.getbyInfectedDetail()

    def getTop20(self, datas):
        # print(datas)
        top20 = self.GT.getTop20fromThreat(datas)
        self.makeReport.writeTitle("4. 기간내 Top20 탐지 Endpoints", 2)
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
        log_write2(sys,"4. 기간내 Top20 탐지 Endpoints 생성")

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
            log_write2(sys,"reForgeCont data is zero")
            # print("data is zero")
            return 0
        else:
            i = 0
            cntper = 0
            per = len(datas)/100
            full = len(datas)
            # bar = progressbar.ProgressBar(maxval=full).start()
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
                    # bar.update(i)
                    # self.makeReport.writeDownTable(data, i)
                    i += 1
                    # self.makeReport.saveDoc()
            else:
                for data in datas:
                    if type in data:
                        print(data[15], "/", data[10],
                              "/", data[16], "/", data[14])
                        cont=str(data[15]+"/"+data[10]+"/"+data[16]+"/"+data[14])
                        log_write2(sys, "type not all : "+cont)
            # bar.finish()
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
                if gubunCnt[i][1] < 10:
                    etclabel = etclabel+gubunCnt[i][0]+", "
                    ratiocnt[0] = ratiocnt[0]+gubunCnt[i][1]
                else:
                    j += 1
                    labelcnt.insert(j, gubunCnt[i][0])
                    ratiocnt.insert(j, gubunCnt[i][1])
            etclabel += ")"
            ratio = ratiocnt
            labels = labelcnt
            wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 3}
            pie=plt.pie(ratio, autopct="%.1f%%",counterclock=False, wedgeprops=wedgeprops)
            plt.legend(pie[0],labels,fontsize=8,loc="best",bbox_to_anchor=(0.85,1.025))
            # plt.show()
            picpath = './savePieChart.png'
            plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
            plt.clf()
            self.makeReport.writeDown("")
            self.makeReport.writeTitle("5. 위협별 탐지", 2)
            log_write2(sys,"5. 위협별 탐지")
            self.makeReport.addPic2(picpath)
            self.makeReport.mkTblthreatpie(len(labelcnt), 2)
            for i in range(0, len(labelcnt)):
                if i == 0:
                    self.makeReport.wrTblthreatpie(i+1, 0, etclabel)
                else:
                    self.makeReport.wrTblthreatpie(i+1, 0, labelcnt[i])
                self.makeReport.wrTblthreatpie(i+1, 1, str(ratiocnt[i]))
            self.makeReport.saveDoc()
        except ValueError:
            # print("Value err!")
            log_write2(sys,"5. 위협별 탐지 Value err!")
        except TypeError:
            log_write2(sys,"5. 위협별 탐지 Type err!")
            # print("Type Err!")

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
        plt.barh(y, x_axis,color=['r','g','b'])
        plt.yticks(y, y_axis)
        picpath = './saveBarChart.png'
        plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
        plt.clf()
        # print(datas)
        self.makeReport.writeDown("")
        self.makeReport.writeTitle("6. 엔진별 탐지", 2)
        log_write2(sys,"6. 엔진별 탐지")
        self.makeReport.addPic(picpath)
        self.makeReport.mkTblenginechart(len(engineCnt), 2)
        for i in range(0, len(engineCnt)):
            self.makeReport.wrTblenginechart(i+1, 0, engineCnt[i][0])
            self.makeReport.wrTblenginechart(i+1, 1, str(engineCnt[i][1]))
        self.makeReport.saveDoc()
    
    def getSolved(self):
        mnmb=self.GT.mnmb_call()
        # print(mnmb.get("mitigated"))
        # print(mnmb.get("not_mitigated"))
        # print(mnmb.get("marked_as_benign"))
        mkr = self.makeReport
        mkr.writeDown(" ")
        mkr.writeTitle("7. 해결된 위협 정보", 2)
        log_write2(sys,"7. 해결된 위협")
        mkr.mktable_getSolved(3,2)
        mkr.writeDownTable_getSolved("mitigated",mnmb.get("mitigated"),0)
        mkr.writeDownTable_getSolved("marked_as_benign",mnmb.get("marked_as_benign"),1)
        
        
    
    def getInfectedDetail(self, datas):
        mkr = self.makeReport
        mkr.writeDown(" ")
        mkr.writeTitle("8. 주요 탐지 내역 세부 사항", 2)
        colname = ["파일명", "분류", "조치여부", "탐지경로", "Originator Process", "엔진", "탐지 횟수", "구조/행위분석"]
        indiDetail={}
        indiData={}
        indicators = ""
        cnt=1
        for data in datas:
            if data[19]=="DBT - Executables":
                engine_name="Behavioral AI Engine"
            else:
                engine_name=data[19]
            rowdata = [data[31], data[14], data[23],data[25], data[26], engine_name, cnt, indicators]
            if data[32] in indiDetail :
                indiDetail[data[32]]=data[30]+data[30]
                indiData[data[32]]=rowdata
                indiData[data[32]][6]+=1
            else:
                indiDetail[data[32]]=data[30]
                indiData[data[32]]=rowdata
            if not indiDetail.get(data[32]):
                pass
            else:
                for i in range(len(indiDetail.get(data[32]))):
                    pass
        # indiData가 써야할 일반적인 내용
        # indiDetail은 행위/탐지 세부 내역임
        for iData in indiData:
            # iData는 파일의 sha1값을 불러옴
            if not indiData.get(iData):
                pass
            else:
                if indiData.get(iData)[2]=="not_mitigated":
                    # print(iData)
                    # print(indiData.get(iData)[6])
                    # print("====================================")
                # if data[23]:
                    # if data[19]=="DBT - Executables":
                    #     engine_name="Behavioral AI Engine"
                    # else:
                    #     engine_name=data[19]
                    # rowdata = [data[31], data[14], data[23],
                    #         data[25], data[26], engine_name, indicators]
                    mkr.mktable_thDetail(8, 2)
                    k = 0
                    for col in colname:
                        mkr.writeDownTable_thDetail(col, k, 0)
                        if k == 7:
                            tacData=""
                            for i in range(len(indiDetail.get(iData))):
                                tacData += "\n"+indiDetail.get(iData)[i].get("category")+"\n"+indiDetail.get(iData)[i].get("description")+"\n"
                                for key in indiDetail.get(iData)[i].keys():
                                    if key == "tactics":  
                                        if not indiDetail.get(iData)[i].get(key):
                                            pass
                                        else:
                                            # print("---------------------------------")
                                            # print(data[30][i].get(key))
                                            # print("---------------------------------")
                                            for detail in (indiDetail.get(iData)[i].get(key)):
                                                tactics_detail = detail
                                                # for key in tactics_detail.keys():
                                                tacData += "\n" + tactics_detail.get("source")+" : "+tactics_detail.get("name")+" "
                                                for techData in tactics_detail.get("techniques"):
                                                    tacData += "[" + techData.get("name")+"]"
                                    else:
                                        pass
                            mkr.writeDownTable_thDetail(str(tacData), k, 1)        
                        elif k==6:
                            # 총 탐지 횟수
                            mkr.writeDownTable_thDetail(str(indiData.get(iData)[k])+"회", k, 1)
                        else:
                            # 구조/행위분석 부분을 제외한 나머지 내용 채우는 부분
                            mkr.writeDownTable_thDetail(indiData.get(iData)[k], k, 1)
                        k += 1
                    log_write2(sys,"상세내역 ")
                    mkr.writeDown(" ")    
                else:
                    pass   
                
                    '''     

        for data in datas:
            #indicator 값이 있는 것에 대해서만 보고서 작성
            if data[30]:
                indicators = ""
                rowdata = [data[31], data[14], data[23],
                           data[25], data[26], data[19], indicators]
                mkr.mktable_thDetail(7, 2)
                # mkr.writeDownTable_thDetail("파일명",1,0)
                # mkr.writeDownTable_thDetail(str(data[31]),1,1)
                # print(data[30])
                k = 0
                for col in colname:
                    mkr.writeDownTable_thDetail(col, k, 0)
                    if k == 6:
                        tacData=""
                        for i in range(len(data[30])):
                            # print(data[30][i],"\n")
                            # print(" ")
                            tacData += "\n"+data[30][i].get("category")+"\n"+data[30][i].get("description")+"\n"
                            for key in data[30][i].keys():
                                # print(key,":",data[30][i].get(key))
                                if key == "tactics":
                                    if not data[30][i].get(key):
                                        pass
                                    else:
                                        # print("---------------------------------")
                                        # print(data[30][i].get(key))
                                        # print("---------------------------------")
                                        for detail in (data[30][i].get(key)):
                                            # print(detail)
                                            tactics_detail = detail
                                            # for key in tactics_detail.keys():
                                            tacData += "\n" + tactics_detail.get("source")+" : "+tactics_detail.get("name")+" "
                                            for techData in tactics_detail.get("techniques"):
                                                tacData += "[" + techData.get("name")+"]"
                        '''
                        # mkr.writeDownTable_thDetail(tacData, k, 1)
                                            
                                            
                                            
                                        # tactics_detail = data[30][i].get(key)[0]
                                        # print(len(data[30][i].get(key)))
                                        # for key in tactics_detail.keys():
                                        #     tacData += "\n" + \
                                        #         tactics_detail.get(
                                        #             "source")+" : "+tactics_detail.get("name")+" "
                                        #     for techData in tactics_detail.get("techniques"):
                                        #         tacData += "[" + \
                                        #             techData.get("name")+"]"
                                        #         mkr.writeDownTable_thDetail(
                                        #             tacData, k, 1)

            
    def endSave(self):
        return self.makeReport.saveDoc()
