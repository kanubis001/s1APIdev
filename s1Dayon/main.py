# 배포용 스크립트
import connect
import json
import time as time2
import sys
import os
from datetime import datetime, date, time, timedelta
import pytz


input=sys.stdin.readline
# url="https://apne1-1002.sentinelone.net/"
url="https://apne1-samsungsds.sentinelone.net/"
apitoken="cvzLzGJ3NgUI4LygtRYB1tqpOnRKnIjIb00RZUGbHDxIv1lZ5FKO2RNa739LvFOb6TWKxqlLEUEerL7g"
token=connect.connectAPI(url, "token", apitoken)
print("-------------------------------------------------------------------------------")
print("입력하는 날짜, 시간 이후 부터 설치된 에이전트를 보여줍니다.(10초 간격)")
print("날짜를 입력하세요. 년도, 월, 일을 공백으로 구분해서 입력해주세요 (example:2023년 1월 2일 -> 2023 1 2).\n 양식을 반드시 지키세요.")
year,month,day=map(int,input().split())
print("시간을 입력하세요. 시, 분을 공백으로 구분하고 입력하세요.(24시간 단위) (example:오후 1시 9분 -> 13 9).\n 양식을 반드시 지키세요.")
hour,minute=map(int,input().split())

tz=pytz.timezone('UTC')
d=date(year,month,day)
t=time(hour,minute,0)
dt=datetime.combine(d,t,tz)
ksttime=dt-timedelta(hours=9)
starttime=ksttime.strftime('%Y-%m-%dT%H:%M:%S.000000Z')

accountid="1728064451923735869"
furl=url+"web/api/v2.1/agents?limit=1000&accountIds="+accountid+"&registeredAt__gte="+starttime
furl2=url+"web/api/v2.1/agents?limit=1000&accountIds="+accountid
sess=connect.sess

while(1):
    response=sess.get(furl)
    fullres=sess.get(furl2)
    conts=json.loads(response._content)
    conts2=json.loads(fullres._content)
    installed=[]
    cnt=0
    for data in conts.get("data"):
        regDate=data.get("registeredAt")
        date_edit=datetime.strptime(regDate,'%Y-%m-%dT%H:%M:%S.%fZ')
        date_print=date_edit+timedelta(hours=9)
        dp=date_print.strftime('%Y-%m-%d %H:%M:%S')
        installed.append([data.get("computerName"), data.get("osName"), dp])
        cnt+=1
    installed.sort(key=lambda x:x[2])
    os.system('cls')
    for com in installed:
        print(com)
    print("전체 설치 대수 :", conts2.get("pagination").get("totalItems"),"|| 설정된 시간 내 설치 대수 : ",cnt)
    time2.sleep(10)
    