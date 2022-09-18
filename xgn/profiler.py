import json
from math import sqrt
import random
import webbrowser
from tqdm import tqdm
import ssl
import urllib.parse
import urllib.request
import re
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from PIL import Image
tagOf=dict()

def parseJs(js, tags):
    # print(str(js)[:500],tags)
    for i in js['subcategories']:
        # print(i)
        parseJs(i['content'],tags+[i['name']])
    for i in js['pages']:
        if i['page'] not in tagOf:
            tagOf[i['page']]=set()
        # print(i['page'],tags)
        for val in tags:
            tagOf[i['page']].add(val)


ssl._create_default_https_context = ssl._create_unverified_context

def openURL(url):
    headers={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',

        'Cache-Control':'max-age=0',

        'Connection':'keep-alive',

        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4882.400 QQBrowser/9.7.13059.400'
    }
    print("访问开始:"+url)
    request=urllib.request.Request(url,headers=headers)
    response=urllib.request.urlopen(request)
    return response

def getURL(url):
    response=openURL(url)
    
    html=response.read()
    return html.decode('utf-8')

def sim(a,b):
    return len(tagOf[a].intersection(tagOf[b]))/sqrt(len(tagOf[a])*len(tagOf[b]))

def rec(userinfo):
    lst=[]
    for item in tqdm(tagOf):
        if item not in userinfo:
            score=0
            for viewed in userinfo:
                score+=(userinfo[viewed]-3)*sim(item,viewed)
            lst.append((score,item))
    lst.sort()
    lst.reverse()
    return lst
    
print("Parsing data...")
with open("data.json","r",encoding="utf-8") as data:
    js=json.load(data)
    parseJs(js,[])

print(f"Done! Char count:{len(tagOf)}")

print("Start asking random questions...")

with open("user.txt","r",encoding="utf-8") as userf:
    userinfo={}
    for i in userf.readlines():
        x,y=i.strip().split(" ")
        userinfo[x]=float(y)

reimg=re.compile(r'"https:\/\/img\.moegirl\.org\.cn\/common\/thumb\/.\/..\/[^ ]*?"')

with open("user.txt","a",encoding="utf-8") as userf:
    todo=set()
    for i in tagOf:
        if i not in userinfo:
            todo.add(i)
    
    while len(todo)>0:
        lst=rec(userinfo)
        rngc=random.choice(lst[:50])
        rng=rngc[1]
        print("Top 50:",lst[:50])
        print(f"Chosen {rng} to ask for score {rngc[0]} with tag {tagOf[rng]}")

        # content=getURL(f"https://zh.moegirl.org.cn/{urllib.parse.quote(rng)}")
        # imgs=reimg.findall(content)
        # for i in imgs:
        #     i=i.replace('"',"")
        #     if "px" in i and "svg" not in i:
        #         print("Chosen Image:",i)
                                
        #         urllib.request.urlretrieve(i, "tmp.png")
        #         Image.open("tmp.png").show()
        #         break
        webbrowser.open(f"https://zh.moegirl.org.cn/{rng}")
        val=float(input(f"On a scale of 5, how much would you rate {rng}:"))
        todo.remove(rng)
        userinfo[rng]=val
        userf.write(f"{rng} {val}\n")
        userf.flush()
