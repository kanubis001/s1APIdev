from sqlite3 import PrepareProtocol
import mainReporting
import connect as conn
from connect import sess
import mkReport


procs=[]
url="https://apne1-samsungsds.sentinelone.net"
apiToken="IwdlMxqistO4F57BwUQ8Gwkkr4ATPPXXGWYtfbwbI1t5Gx9qiyKBQXsmc9JkSPopdXaH1XwOFawDyDRR"
gid="1213456060215715837"
sid="815520265168496110"
id=sid
startday="2022-05-01T00:00:00.000000Z"
endday="2022-08-31T23:59:59.999999Z"
token=conn.connectAPI(url,"token",apiToken)

mR=mainReporting.mainReporting(url,apiToken,id,token,startday,endday)
# 기간 입력 받기

datas=mR.get("date","site")

#type은 malicious, suspicious, all
type="all"

#보고서 생성(전체 리스트)
mR.reForgeCont(datas,type)

#차트 생성(위협별)
mR.gatherThreatscnt(datas,type)

# mR.reForgeCont(datas,type)
# mR.gatherThreatsThread(datas,type)
conn.disconnectAPI()

