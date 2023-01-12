import connect as conn
from connect import sess
import json

url="https://apne1-samsungsds.sentinelone.net"
apiToken="IwdlMxqistO4F57BwUQ8Gwkkr4ATPPXXGWYtfbwbI1t5Gx9qiyKBQXsmc9JkSPopdXaH1XwOFawDyDRR"

token=conn.connectAPI(url,"token",apiToken)
fulluri=url+"/web/api/v2.1/agents/actions/start-remote-shell?token="+token
print(fulluri)
data={
      "data": {
    "historyPassword": "kaligo123!@",
    "columns": "80",
    "twoFaCode": "103754",
    "rows": "25"
  },
  "filter": {
    "uuid": "ff819e70af13be381993075eb0ce5f2f6de05be2"
    }
}
res=sess.post(fulluri,data)
print(res)

conn.disconnectAPI()

