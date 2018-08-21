# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 23:00:28 2018
@author: wangshuai
"""
import urllib
import urllib.request as urllib2
import http.cookiejar as cookielib
import io
import re
import gzip
from selenium import webdriver
import datetime
def get_Time():
    begin = datetime.date(2016,1,1)
    end = datetime.date(2018,4,23)
    time_list = []
    for i in range((end - begin).days+1):
        day = begin + datetime.timedelta(days=i)
        time_list.append(day.strftime("%Y-%m/%d"))
    return time_list

class Config:
    def __init__(self):
        self.config = {}
        self.config["headers"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
        self.config["outputPath"] = "./"
        self.config["keywords"] = ["习近平","习主席","中央军委主席","中共中央总书记","国家主席"]
        self.config["base_url"] = "http://www.81.cn/jfjbmap/content/"     
    def get(self, key, parent=None):
        if key and key in self.config.keys():
            return self.config[key]
def get_Html(url, js = False, time = 0):
    config = Config()
    if js:
        try:
            driver = webdriver.PhantomJS()
            driver.get(url)
        except Exception as err:
            print (err)
            print ("=== 网络不稳定，再次连接 ...")    
            if time==0:
                return -1
            time -= 1
            return get_Html(url, js=True, time=time)
        html = driver.page_source
        driver.close()
        return html
    else:        
        try:
            cj = cookielib.CookieJar()
            proxy = urllib2.ProxyHandler({'https': '127.0.0.1:1080'})
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [("User-agent", config.get("headers"))]
            urllib2.install_opener(opener)
            req=urllib2.Request(url)
            con=urllib2.urlopen(req)
            html=con.read()
            if con.getheader('Content-Encoding') == "gzip":
                buf = io.BytesIO(html) 
                gf = gzip.GzipFile(fileobj=buf)
                html = gf.read()
            html = html.decode('utf-8')
        except Exception as err:
            print (err)
            print ("=== 网络不稳定，再次连接 ...")   
            if time==0:
                return -1
            time -= 1
            return get_Html(url, js=False, time=time)
        return html
def save(info, handler):
    for i in range(len(info["time"])):
        for ss in ["time","title"]:
            txt = info[ss][i].strip(" ")
            if ss=="time":
                txt+="->"
            handler.write(txt)
        handler.write("\r\n")          

class GetArticle:
    def __init__(self, config, handler = None):
        self.config = config
        self.url = self.config.get("base_url")
        self.handler = handler
        self.article={}
        self.article["url"] = []
        self.article["title"] = []
        self.article["detail"] = []
        self.article["time"] = []
    def index_detail(self):        
        pattern_index = re.compile('<li><a href="(.*?)">(.*?)</a></li>')
        pattern_detail = re.compile('<P>(.*?)</P>')
        time_list = get_Time()
#        ifile = open("detail_info.txt","w",encoding='utf-8')
        for i in range(len(time_list)):
            url_loop = self.url+time_list[i]+"/node_2.htm"
            try:                
                index = pattern_index.findall(get_Html(url_loop,js=False,time=3))
                url = urllib.parse.urljoin(url_loop,index[0][0])
                title = index[0][1]
#                detail_list = pattern_detail.findall(get_Html(url,js=False,time=3))
#                detail = ""
#                for j in range(len(detail_list)):
#                    detail += detail_list[j]
                key_flag = 0
                for key in self.config.get("keywords"):
                    if key in title:
                        key_flag = 1
                if key_flag:
                    self.article["time"].append(time_list[i])
                    self.article["title"].append(title)
                    self.article["url"].append(url)
#                    self.article["detail"].append(detail)
#                    ifile.write(time_list[i]+": "+title+"\r\n"+url+"\r\n"+detail+"\r\n")
                    if i%30 == 0:
                        print(str(i)+"->"+time_list[i]+": "+title)
                        print(url)
                else:
                    continue
            except Exception as err:
                print(err)
                print("...网址： "+url_loop+" 获取|解析 错误...")
                continue
#        ifile.close()
        save(self.article, self.handler)



        
        


if __name__ == '__main__':
    config = Config()
    ifile = open(config.get("outputPath")+"rough_info.txt","w",encoding='utf-8')
    getArticle = GetArticle(config, handler = ifile)
    getArticle.index_detail()
    ifile.close()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
