from multiprocessing import Process
import mainReporting
import connect as conn
from connect import sess


def reForgeCont(datas,type):
    if type=='all':
        for data in datas:
            print(data[15],"/",data[10],"/",data[16],"/",data[14])
    else:  
        for data in datas:
            if type in data:
                print(data[15],"/",data[10],"/",data[16],"/",data[14])
    
def gatherThreatsThread(datas,type):
    threatsGubun=[]
    for data in datas:
        if data[14] not in threatsGubun:
            threatsGubun.append(data[14])
    print(threatsGubun)

def f1(datas,type,mR):
    mR.reForgeCont(datas,type)
 
if __name__ == '__main__':
    url="https://apne1-samsungsds.sentinelone.net"
    apiToken="IwdlMxqistO4F57BwUQ8Gwkkr4ATPPXXGWYtfbwbI1t5Gx9qiyKBQXsmc9JkSPopdXaH1XwOFawDyDRR"
    gid="1213456060215715837"
    sid="815520265168496110"
    id=sid
    startday="2022-01-01T00:00:00.000000Z"
    endday="2022-08-11T23:59:59.999999Z"
    token=conn.connectAPI(url,"token",apiToken)

    mR=mainReporting.mainReporting(url,apiToken,id,token,startday,endday)
    datas=mR.get("date","site")
    type=all
    p1 = Process(target=f1, args=(datas,type,mR,))
    # p2 = Process(target=f2, args=(datas,type,mR,))
 
    p1.start(); p1.join()
    # p2.start(); p2.join()
    # 다른 클래스는 멀티 프로세싱으로 안되는 듯
