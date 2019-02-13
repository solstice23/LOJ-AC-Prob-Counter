import os
import re
import time
import json
import requests
from urllib import parse
from urllib import request
from bs4 import BeautifulSoup

probDict={}
ACTimeDict={}
probSet=set([])

userDict={}
userList=[]

resDict={}
resList=[]
allAC=0
validAC=0
lastACTime="-"

resJSONList=[]

def writeFile(context): #测试时用
    f=open("test.txt","w")
    f.write(context)
    f.close()

def readUser():# 读取待查询用户列表
    for line in open("users.csv",encoding="gbk"): 
        line=line.replace('\r\n','')
        line=line.replace('\n','')
        if (line[0]=='#'):
            continue
        now=line.split(',')
        userDict[now[0]]=now[1]
        userList.append(now[0])
    print("已读取到 "+format(len(userList))+" 个用户待爬取：")
    print(userList)

def getHTML(url):
    res=""
    while True:
        try:
            res=requests.get(url,timeout=5).text
        except:
            print("请求超时/失败，正在重请求中..")
            time.sleep(0.2)
            continue
        break
    return res

def getStatus(userName,page):
    html=getHTML("https://loj.ac/submissions?&submitter="+parse.quote(userName)+"&status=Accepted&page="+format(page))
    html=format(html)
    # 提取并遍历每一条记录
    reg=re.compile(r'itemList = (.*?);')
    jsonstr=reg.findall(html)[0]
    records=json.loads(jsonstr)
    for entry in records:
        name=entry['info']['problemName']
        proid=entry['info']['problemId']
        ACTime=entry['info']['submitTime']
        probDict[proid]=name
        ACTimeDict[proid]=ACTime
        if (proid not in probSet):
            global allAC,validAC
            allAC=allAC+1
            if (proid>=100):
                validAC=validAC+1
        probSet.add(proid)
    # 记录最后 AC 时间
    if (page==1 and len(records)>0):
        global lastACTime
        lastACTime=records[0]['info']['submitTime']
    # 检测是否有下一页
    dom=BeautifulSoup(html,"html.parser")
    nextbutton=dom.find(id="page_next")
    if (nextbutton==None):
        return 0
    if ("disabled" in nextbutton['class']):
        return 0

def getUserStatus(user):
    global allAC,validAC,resList,lastACTime
    allAC=0
    validAC=0
    lastACTime="-"
    probDict.clear()
    probSet.clear()
    ACTimeDict.clear()
    name=userDict[user]
    print("正在爬取"+user+"("+name+") 的AC记录")
    page=1
    while (1):
        print("爬取第"+format(page)+"页...")
        res=getStatus(user,page)
        if (res==0):
            break
        page=page+1
    result=sorted(probSet)
    resList=result
    resDict[user]=result
    print("")
    print(user+"("+name+") 共AC了 "+format(allAC)+" 道题，有效AC "+format(validAC)+" 题，分别是：")
    print(result)
    print("最后 AC 时间："+lastACTime)
    print("")

def getJSONDict(user):
    res={}
    res['user']=user
    res['name']=userDict[user]
    res['allAC']=allAC
    res['validAC']=validAC
    res['lastACTime']=lastACTime
    probJSONList=[]
    for proid in resList:
        tmp={}
        tmp['id']=proid
        tmp['title']=probDict[proid]
        tmp['time']=ACTimeDict[proid]
        probJSONList.append(tmp)
    res['probs']=probJSONList
    return res


readUser()
for user in userList:
    getUserStatus(user)
    resJSONList.append(getJSONDict(user))
JSON=json.dumps(resJSONList,ensure_ascii=False)
# print(json.dumps(resJSONList,ensure_ascii=False))
# writeFile(json.dumps(resJSONList,ensure_ascii=False))
# 导出HTMl
f=open("assets/res","r",encoding="utf-8")
html="<script>var archivetime='"+time.strftime("%Y-%m-%d %H:%M",time.localtime())+"';var json="+JSON+";</script>"+f.read()
f.close()
f=open("result.html","w",encoding="utf-8")
f.write(html)
f.close()

# 导出CSV
f=open("result.csv","w",encoding="ansi")
f.write("用户名,备注名,AC数,有效AC数,最后AC时间"+"\n")
for i in range(0,len(resJSONList)):
    f.write(format(resJSONList[i]['user'])+","+format(resJSONList[i]['name'])+","+format(resJSONList[i]['allAC'])+","+format(resJSONList[i]['validAC'])+","+format(resJSONList[i]['lastACTime'])+"\n")
f.close()

print("已导出为 HTML(result.html) 和 CSV(result.csv) 文件")
