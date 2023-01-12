import json
import requests
sess=requests.Session()
def connectAPI(s1Site,loginType,apiToken):
    # api 접속가능한 user 정보
    s1username='kaligo@pro-comsys.com'
    s1userpassword='kaligo123!@'
    # api토큰
    s1reason="Reporting Tool"
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
    print(json.loads(response._content))
    try :
        token=json.loads(response._content).get("data").get("token")
    except :
        token=0
    # print(response._content)

    # token=json.loads(response._content).get("data").get("token")
    
    if response.status_code == 200 :
        print("접속 성공. 세션 유지")
    else:
        print(response.status_code, " 접속 에러")
    return token

def disconnectAPI():
    print("세션 해제")
    sess.close()

def connectAPItest(s1Site,loginType,apiToken):
    # api 접속가능한 user 정보
    s1username='kaligo@pro-comsys.com'
    s1userpassword='kaligo123!@'
    # api토큰
    s1reason="SDSconsole_HyundaiDept_Test"
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
        print(response.status_code, " 접속 에러")
        status=0
        sess.close()
    return status