import connect as conn
from connect import sess
import csv
import json
import os

# url = "https://apne1-samsungsds.sentinelone.net"
url = "https://apne1-1110-mssp.sentinelone.net" #성우하이텍
# apiToken = "srlbtO0l8pmpMKNwFUkxiD1b2RcaMszL3wBqfO1GHfnfAoXy4hvLubnPZ5u2Lxsx2hnCUCIyVAu3VTOJ"
apiToken="VIUTkmrYXPCv6WCuA3IpSP71dUlzbOpikpVWeZOtWVnJqQIFiZiqMxeAgtyIPUmxKtrXYULlmomr56nL" #1110 mssp

add_url = "/web/api/v2.1/agents/actions/manage-tags?"

token = conn.connectAPI(url, "token", apiToken)
# print(token)

full_url = url+add_url+"&token="+token
accountIds=""
# siteIds="815520265168496110"
siteIds="1670801463174575408" #성우하이텍
# groupIds="1213456060215715837"
# groupIds="1671384044762509156" #성우하이텍 PC Group
# groupIds="1671384369250646034" #성우하이텍 Server Group


csv_file = open("C:\\OneDrive_folder\\OneDrive\\Develop_private\\Python_git\\s1APIdev\\tag_bulk\\Sentinels_Report_20230426_110017_한글변환.csv", "r", errors="", newline="")
csv_file2 = open("C:\\OneDrive_folder\\OneDrive\\Develop_private\\Python_git\\s1APIdev\\tag_bulk\\Sentinels_Report_20230426_110017_한글변환.csv", "r", errors="", newline="")
i = 0
catarr = []
errcnt=0;
errarr=[]
# /web/api/v2.1/tag-manager post
def insertTag(key,value):
    global errcnt
    global errcont
    add_url="/web/api/v2.1/tag-manager"
    full_url2 = url+add_url+"?token="+token
    # print(full_url2,key,value)
    keydata = {
        "filter": {
            "siteIds": [siteIds]
        },
        "data": {
            "type":"agents",
            "key": key,
            "value": value
        }
    }
    try:
        response = sess.post(full_url2, json=keydata)
        data=json.loads(response._content)
        # print("tag 삽입 성공",data.get("data").get("id"))
        return data.get("data").get("id");
    except AttributeError as e:
        errcnt+=1;
        errcont=key+":"+value
        errarr.append(errcont)
        # print("error",e)


def findTag(key,value):
    try:
        add_gettags_url="/web/api/v2.1/agents/tags?"
        # print(key)
        key=key.replace("&","%26")
        value=value.replace("&","%26")
        full_gettags_url=url+add_gettags_url+"key="+key+"&value="+value+"&siteIds="+siteIds+"&token="+token
        # print(full_gettags_url)
        # print(full_gettags_url)
        res = sess.get(full_gettags_url)
        # print(res)
        datas_forid=json.loads(res._content)
        # print(datas_forid.get("data")[0])
        return datas_forid.get("data")[0].get("id")
    except TypeError as e:
        print(e,key,":",value)

def run_insertTag():
    f = csv.DictReader(csv_file, delimiter=",", doublequote=True,
                   lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    for row2 in f:
        # row2는dictionary
        # row2["column_name"] or row2.get("column_name")으로 필요한 항목을 취득할 수 있다.
        splitstr = row2["Tags"].split(":", 1)
        
        # print(i, row2["Agent UUID"], row2["Tags"], splitstr[0])

        # "a888d7baf9de475aacd561ca6882c088"
        if splitstr[0] != "None":
            key = str(splitstr[0].rstrip())
            value = str(splitstr[1].lstrip())
            insertTag(key,value);
def run_tags():
    i=0
    not_aff_cnt=0
    aff_cnt=0
    f2 = csv.DictReader(csv_file2, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    # try:
    for data_row in f2:
        # print(data_row)
        i += 1
        # data_row는dictionary
        # data_row["column_name"] or data_row.get("column_name")으로 필요한 항목을 취득할 수 있다.
        splitstr = data_row["Tags"].split(":", 1)
        if splitstr[0] != "None":
            key = str(splitstr[0].rstrip())
            value = str(splitstr[1].lstrip())
            uuid = data_row["Agent UUID"]
            tagid=findTag(key,value);

            # print(type(tagid))
            add_url = "/web/api/v2.1/agents/actions/manage-tags?"
            full_url = url+add_url+"token="+token
            # print(full_url)
            # key 카테고리 저장
            if key in catarr:
                # print("already exists")
                pass
            else:
                catarr.append(key)

            data = {
                "filter": {
                    "siteIds": [siteIds],
                    "uuid": uuid,
                },
                "data": [
                    {
                        "operation": "override",
                        "tagId": tagid
                    }
                ]
            }
            # print(catarr)
            response = sess.post(full_url, json=data)
            # print("적용",response._content)
            try:
                data_res=json.loads(response._content)
                if(data_res.get("data").get("affected")==0):
                    not_aff_cnt+=1
                elif(data_res.get("data").get("affected")==1):
                    aff_cnt+=1
                # print(data_res.get("data").get("affected"))
                print(i)
                # os.system('cls')
            except AttributeError as abe:
                print(abe,response._content,key,value)
        else:
            print("else")
    print("전체 : ",i,"적용 : ",aff_cnt,"미 적용 : ",not_aff_cnt)
    # except:
    #     print("except")
if __name__ == "__main__":
    # run_insertTag();
    print("Tag 삽입 에러 정보",errcnt,"개 에러(이미 삽입되었을 수도 있음) =>",errarr);
    run_tags()