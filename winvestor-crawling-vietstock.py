"""1. Crawling <http://vietstock.vn/doanh-nghiep/hoat-dong-kinh-doanh.htm> for the news.
In each news, pull out ArticleID, Title, Summary, URL, datetime && StockCode, note them down in 1 csv file with index.
In this case, return <???> when a news has no StockCode (UpCOM or common news).


2. Creating 2 folders: <html> && <content>,
parsing each line in csv file to get into each URL,
pulling data    from that URL and save into <html>    folder,
pulling content from that URL and save into <content> folder.
"""


import urllib3
import re
import codecs
import csv
import os
import random
from   time            import sleep
from   multiprocessing import Process


http     = urllib3.PoolManager()
my_data  = []
min      = 1
max      = int(input("[?] Enter the last page of <http://vietstock.vn/doanh-nghiep/hoat-dong-kinh-doanh.htm>:\n>>> "))
IDs      = []
newIDs   = []

pattern0 = re.compile(r"'")
pattern1 = re.compile(r'"')
pattern2 = re.compile(r";")

pattern3 = re.compile(r"\\u003c")
pattern4 = re.compile(r"\\u003e")
pattern5 = re.compile(r"\\r\\n")
pattern6 = re.compile(r"\\")

try: os.mkdir("html")
except: pass
try: os.mkdir("content")
except: pass

path = os.getcwd()


def data():
    ###task1 function###
    global ArticleID
    ArticleID  = re.findall('"ArticleID":([0-9]+)', read)
    global Title
    Title      = re.findall('"Title":"(.+?)"', read)
    Title      = pattern0.sub("-", Title[0])
    Title      = pattern1.sub("-", Title)
    Title      = pattern2.sub("-", Title)
    global Head
    Head       = re.findall('"Head":"(.+?)"', read)
    Head       = pattern0.sub("-", Head[0])
    Head       = pattern1.sub("-", Head)
    Head       = pattern2.sub("-", Head)
    global URL
    URL        = re.findall('"URL":"(.+?)"', read)
    global timestring
    timestring = re.findall('"timestring":"(.+?)"', read)
    global StockCode
    StockCode  = re.findall('"StockCode":"(.+?)"', read)


def html_content(index, ArticleID):
    ###task2 function###
    print("> Checking URL at row %d..." %index)
    req = http.request("POST", "http://vietstock.vn/_Partials/ContentGetArticle",
                       {"articleId":ArticleID})
    try:
        resp   = codecs.decode(req.data)
    except Exception as e:
        print(e)
    resp       = pattern3.sub("<", resp)
    resp       = pattern4.sub(">", resp)
    resp       = pattern5.sub("\n", resp)
    resp       = pattern6.sub("", resp)
    pTitle     = re.findall('<p class="pTitle">(.+?)</p>', resp)
    if pTitle == []:
        pTitle = re.findall('<font class="pTitle">(.+?)</font>', resp)
    pHead      = re.findall('<p class="pHead">(.+?)</p>', resp)
    if pHead  == []:
        pHead  = re.findall('<font class="pHead">(.+?)</font>', resp)
    pBodies    = re.findall('<p class="pBody">(.+?)</p>', resp)
    os.chdir("%s/html" %path)
    f = open("%d.html" %index, "w")
    f.write(resp)
    f.close()
    os.chdir("%s/content" %path)
    f = open("%d.txt" %index, "a")
    try:
        f.write(pTitle[0] + "\n")
        f.write(pHead[0] + "\n")
        for pBody in pBodies:
            f.write(pBody + "\n")
        f.close()
    except Exception as e:
        print(e)


def list_slicer(list, piece = 5):
    ###slicing a list to piece-sized small ones###
    for i in range(0, len(list), piece):
        yield list[i:(i + piece)]


print("[*] Starting...")

try:
    f = csv.reader(open("id-title-head-url-time-stock.csv", "r"), delimiter = ";")
    for row in f: IDs.append(int(row[1]))
    lenIDs  = len(IDs)
    for i in range(min, (max+1)):
        print("> Updating...")
        req = http.request("POST", "http://vietstock.vn/_Partials/ListPageArticle",
                           {"item":20,"page":i,"channelid":"737"})
        resp  = codecs.decode(req.data)
        reads = resp.split('},{"row"')
        for read in reads:
            data()
            if int(ArticleID[0]) not in IDs:
                if StockCode != []:
                    my_data.append((lenIDs, ArticleID[0], Title, Head, URL[0], timestring[0], ",".join(StockCode).strip()))
                    newIDs.append((lenIDs, int(ArticleID[0])))
                    lenIDs   += 1
                else:
                    my_data.append((lenIDs, ArticleID[0], Title, Head, URL[0], timestring[0], "???"))
                    newIDs.append((lenIDs, int(ArticleID[0])))
                    lenIDs   += 1
            else: break
        if int(ArticleID[0]) in IDs: break
    with open("id-title-head-url-time-stock.csv", "a") as f:
        for (i,a,t,h,u,ts,s) in my_data:
            f.write("%d; %s; %s; %s; http://vietstock.vn%s; %s; %s\n" %(i,a,t,h,u,ts,s))
    print("[*] Updated!!!")

except FileNotFoundError:
    lenIDs  = 0
    for i in range(min, (max+1)):
        print("> Inspecting page number %003d/%003d..." %(i,max))
        req = http.request("POST", "http://vietstock.vn/_Partials/ListPageArticle",
                           {"item":20,"page":i,"channelid":"737"})
        resp  = codecs.decode(req.data)
        reads = resp.split('},{"row"')
        for read in reads:
            data()
            if StockCode != []:
                my_data.append((lenIDs, ArticleID[0], Title, Head, URL[0], timestring[0], ",".join(StockCode).strip()))
                newIDs.append((lenIDs, int(ArticleID[0])))
                lenIDs   +=1
            else:
                my_data.append((lenIDs, ArticleID[0], Title, Head, URL[0], timestring[0], "???"))
                newIDs.append((lenIDs, int(ArticleID[0])))
                lenIDs   +=1
    with open("id-title-head-url-time-stock.csv", "w") as f:
        for (i,a,t,h,u,ts,s) in my_data:
            f.write("%d; %s; %s; %s; http://vietstock.vn%s; %s; %s\n" %(i,a,t,h,u,ts,s))
    print("[*] Done inspecting!!!")


for newID in list_slicer(newIDs):
    for (index, ArticleID) in newID:
        Process(target = html_content, args = (index, ArticleID,)).start()
        sleep(random.randint(0, 1))

#for (index,ArticleID) in newIDs: html_content(index, ArticleID)

"""When I did it without multi processing, it ran out smoothly.
But with multi process, even if I sliced the list into very small parts, sometimes the data which came back could not decode in utf-8.
And I don't even know why :(
So I have to take a random sleep time after each request...
And it runs perfectly up to now!
But it is even slowlier than the old technique :(


PS:
All the <try> && <except> blocks (except the main one) are there for the defense :D
"""
