import json
import requests
import sys
from logger import *
sess=requests.Session()
def connectAPI(s1Site,loginType,apiToken):
    # api 접속가능한 user 정보
    s1username='kaligo@pro-comsys.com'
    s1userpassword='kaligo123!@'
    # api토큰
    s1reason="Appexport Tool"
    # apiToken="z1z8wmDsu0c1tdFoxYz7cOQb4XdU49WDFJjo60mpVDwrM3juKGaT8YyyVzhdxTit9eBzx0X8RQ1N5h0Z"
    
    if loginType == "pw":
        loginData={
           'username': s1username,
           'password': s1userpassword,
           'rememberMe': 'true'
        }
        url=s1Site+'/web/api/v2.1/users/login'
    if loginType == "token":
        # apiToken 로그인(2FA인증은 요렇게 로그인 하면 됨) 6개월에 한번 갱신
        loginData={
            "data":{
                'reason':s1reason,
                'apiToken':apiToken
            }
        }
        url=s1Site+'/web/api/v2.1/users/login/by-api-token'
    
    response=sess.post(url,json=loginData)
    # print(json.loads(response._content))
    try :
        token=json.loads(response._content).get("data").get("token")
    except :
        token=0
    # print(response._content)

    # token=json.loads(response._content).get("data").get("token")
    
    if response.status_code == 200 :
        log_write2(sys,"connection success. session start")
        # print("접속 성공. 세션 유지")
    else:
        debug=str(response.status_code)+" connection error"
        log_write2(sys,debug)
        # print(response.status_code, " 접속 에러")
    return token

def disconnectAPI():
    log_write2(sys,"session close")
    # print("세션 해제")
    sess.close()

def connectAPItest(s1Site,loginType,apiToken):
    # api 접속가능한 user 정보
    s1username='kaligo@pro-comsys.com'
    s1userpassword='kaligo123!@'
    # api토큰
    s1reason="s1 Reporting Tool"
    # apiToken="z1z8wmDsu0c1tdFoxYz7cOQb4XdU49WDFJjo60mpVDwrM3juKGaT8YyyVzhdxTit9eBzx0X8RQ1N5h0Z"
    
    if loginType == "pw":
        loginData={
           'username': s1username,
           'password': s1userpassword,
           'rememberMe': 'true'
        }
        url=s1Site+'/web/api/v2.1/users/login'
    if loginType == "token":
        # apiToken 로그인(2FA인증은 요렇게 로그인 하면 됨) 6개월에 한번 갱신
        loginData={
            "data":{
                'reason':s1reason,
                'apiToken':apiToken
            }
        }
        url=s1Site+'/web/api/v2.1/users/login/by-api-token'
    
    response=sess.post(url,json=loginData)

    if response.status_code == 200 :
        status=1
    else:
        debug=str(response.status_code)+" connection error"
        log_write2(sys,debug)
        print(response.status_code, " 접속 에러")
        status=0
        sess.close()
    return status