import connect as conn
from connect import sess
import datetime
import getThreats
import getAgents
from multiprocessing import Process, Queue
import mkReport
import progressbar
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.use('agg')

class mainReporting:
    def __init__(self, url, apitoken, gid, token, startday, endday,st,en):
        self.s1Site = url
        self.apitoken = apitoken
        self.groupIds = gid
        self.token = token
        self.startD = startday
        self.endD = endday
        self.makeReport = mkReport.mkReport(st,en)
        self.GT = getThreats.getThreats(
            self.s1Site, sess, self.groupIds, self.token, self.makeReport)

        print("mainReporting init", self.s1Site, self.apitoken)
        # self.filepath=csv
        # self.logFile=logFile
        # self.log=open(logFile,'a')
        # log=str(datetime.datetime.now())+" "+"url : "+str(self.s1Site)+" apiToken : "+"***********" + " Group ID : "+self.groupIds+" CSV filepath : "+self.filepath+"\n"
        # self.log.write(log)
        # print(url,apitoken,gid,csv)

    def get(self, menu, sType,id):
        # menu => 날짜로 검색 date
        menu = "date"
        if menu == "date":
            return self.GT.getfromDate(self.startD, self.endD, sType,id)
        
    def getEndpoints(self,findid):
        GA=getAgents.getAgents(self,self.s1Site, sess, self.groupIds, self.token)
        
        pass
    
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
                    self.makeReport.writeDownTable(data, i)
                    i += 1
                    self.makeReport.saveDoc()
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
                    if data[14]==0:
                        pass
                    else: 
                        threatsGubun.append(data[14])
            print(threatsGubun)
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
            plt.pie(ratio, labels=labels, autopct="%.1f%%",counterclock=False, wedgeprops=wedgeprops)
            # plt.show()
            picpath = './savePieChart.png'
            plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
            plt.clf()
            self.makeReport.writeDown("")
            self.makeReport.writeTitle("2. 위협별 탐지", 2)
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
            
    def gatherByEngine(self,datas):
        engineGubun = []
        for data in datas:
            if data[19] not in engineGubun:
                if data[19]==0:
                    pass
                else: 
                    engineGubun.append(data[19])
        print(engineGubun)
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
        print(engineCnt)
        y=np.arange(len(engineCnt))
        x_axis=[]
        y_axis=[]
        j=0
        #표를 위한 자료 정제
        for i in range(len(engineCnt)):
            # if engineCnt[i][1] < 10:
            #     # etclabel = etclabel+engineCnt[i][0]+", "
            #     x_axis[0] = x_axis[0]+engineCnt[i][1]
            # else:
            j += 1
            y_axis.insert(j, engineCnt[i][0])
            x_axis.insert(j, engineCnt[i][1])
        print(x_axis)
        print(y_axis)
        plt.barh(y,x_axis)
        plt.yticks(y,y_axis)
        picpath = './saveBarChart.png'
        plt.savefig(picpath, facecolor='#FFFFFF', bbox_inches='tight')
        plt.clf()
        # print(datas)
        self.makeReport.writeDown("")
        self.makeReport.writeTitle("3. 엔진별 탐지", 2)
        self.makeReport.addPic(picpath)
        self.makeReport.mkTblenginechart(len(engineCnt), 2)
        for i in range(0, len(engineCnt)):
            self.makeReport.wrTblenginechart(i+1, 0, engineCnt[i][0])
            self.makeReport.wrTblenginechart(i+1, 1, str(engineCnt[i][1]))
        self.makeReport.saveDoc()

    def endSave(self):
        return self.makeReport.saveDoc()
