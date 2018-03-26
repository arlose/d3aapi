# -*- coding: utf-8 -*-

import sys,os,re
import urllib
import urllib2
from bs4 import BeautifulSoup
import codecs
import random
import string
import cv2

def random_char(num):
	return ''.join(random.choice(string.ascii_letters) for x in range(num))

def baidu(filepath, content,start,num):
	url1 = "http://image.baidu.com/search/wisemiddetail?tn=wisemiddetail&ie=utf8&word="
	url2 = "&pn="
	url3 = "&size=small&fr=wiseresult&fmpage=result&pos=imglist"
	dircon = filepath
	cate = content
	if os.access(dircon,os.F_OK):
		pass
	else:
		print 'nodircon'
		os.makedirs(dircon)
	count = 0
	successcount = 0
	flag = 1

	if type(content)==unicode:
	    contentu=cate.encode('utf-8')
	    contentu = urllib2.quote(contentu)	    
 	else:
 	    contentu = content
	    contentu = urllib2.quote(contentu)
	# print 66666,content,cate

	#下载图片
	for i in range(start,start+num):
		# print os.getcwd()
		# print dircon
		if flag == 1:
		    url = url1 + contentu + url2 + str(i) + url3  
		    print url
		    sock = urllib.urlopen(url) 
		    
		    pageSoup = BeautifulSoup(sock)
		    #print pageSoup
		    imageGroup = pageSoup.find_all('a')#,href=re.compile("http.*?\.jpg"))
		    #print imageGroup
		    #reg=re.compile("http.*?\.[jpg, bmp, tif, JPG, JPEG, jpeg, png, PNG]")
		    reg=re.compile("http.*?\.jpg")

		    for groupItem in imageGroup:
		        groupUrl = groupItem.get("href")
		        results=reg.findall(groupUrl)
		    
		        if results:
		            #os.chdir(dircon)
		            for one in results:                   
		                imgeurl=one
		                print "image:" , one
		                #print imgeurl.rindex('.'),len(imgeurl)
		                succname = imgeurl[  int(imgeurl.rindex('.'))+1:int(len(imgeurl))]
		           
		                try:
		                    successcount=successcount+1
		                    namestring = random_char(6)
		                    storename = "b"+str(successcount+start) + "_" + namestring + "." + one.split("/")[-1].split('.')[-1]
		                    savename=dircon+"/"+ storename
		                    downloadimge = urllib2.urlopen(one,timeout=5)#, data, timeout)
		                    f=open(savename,"wb")
		                    f.write(downloadimge.read())
		                    f.close()

		                    img = cv2.imread(savename)
		                    if img is None:
		                    	print 'rm ', savename
		                	os.remove(savename)
		                    #size=os.path.getsize(savename)
		                    #flog.writelines("%s %s %s" % (savename,str(size),one))
		                    print "Baidu Download Success " + str(successcount)
		                    
		                except BaseException,e:
		                    #flog.writelines("%s %s %s" % (savename,e,one))
		                    print "Baidu Fail download %s ... Error %s" % ( imgeurl,e)
		                    continue
		          
	print "Baidu finished: (%s/%s) downloaded" % (str(successcount),str(num))

def sougou(filepath, content,start,num):
	url1 = "http://pic.sogou.com/pic/download.jsp?uID=o8bq39_plHSm88EJ&keyword="
	url2 = "&v=2&mode=1&mood=0&p="
	url3 = "&width=0&height=0&pgs=6&st=5&sst=2&index="
	url4 = "&gp=1&play=0&interval=5"
	cate = content
	r=6
	dircon =filepath
	if os.access(dircon, os.F_OK):
		pass
	else:
		print 'nodircon'
		os.makedirs(dircon)
	count = 0
	successcount = 0
	flag = 1

	if type(content)==unicode:
	    contentu=cate.encode('utf-8')
	    contentu = urllib2.quote(contentu)
 	else:
 	    contentu = content
	    contentu = urllib2.quote(contentu)
	print contentu

	reg=re.compile("http.*?\.jpg")

	#下载图片
	for i in range(start,start+num):
		if flag == 1:
		    pp = i/r + 1
		    idx = i%r + 1
		    url = url1 + contentu + url2 + str(pp) + url3 + str(idx) + url4
		    print url
		    sock = urllib.urlopen(url)

		    pageSoup = BeautifulSoup(sock)
		    #print pageSoup
		    imageGroup = pageSoup.find_all('a')#,href=re.compile("http.*?\.jpg"))
		    #print imageGroup

		    for groupItem in imageGroup:
			groupUrl = groupItem.get("href")
			if groupUrl:
			    results=reg.findall(groupUrl)

			    if results:
			        #os.chdir(dircon)
			        for one in results:
			            imgeurl=one
			            print "image:" , one
			            #print imgeurl.rindex('.'),len(imgeurl)
			            succname = imgeurl[  int(imgeurl.rindex('.'))+1:int(len(imgeurl))]

			            try:
					successcount=successcount+1
					namestring = random_char(6)
					storename = "s"+str(successcount+start) + "_" + namestring + "." + one.split("/")[-1].split('.')[-1]
					savename=dircon+"/"+ storename
					downloadimge = urllib2.urlopen(one,timeout=5)#, data, timeout)
					f=open(savename,"wb")
					f.write(downloadimge.read())
					f.close()

					img = cv2.imread(savename)
					if img is None:
						print 'rm ', savename
						os.remove(savename)
			                #flog.writelines("%s %s %s" % (savename,str(size),one))
			                print "Sogou Download Success " + str(successcount)

			            except BaseException,e:
			                #flog.writelines("%s %s %s" % (savename,e,one))
			                print "Sogou Fail download %s ... Error %s" % ( imgeurl,e)
			                continue

	print "Sogou finished: (%s/%s) downloaded" % (str(successcount),str(num))


if __name__ == "__main__":
	filepath =sys.argv[1]
	engine = sys.argv[2]
	keyword = sys.argv[3]
	start = int(sys.argv[4])
	num = int(sys.argv[5])
	if engine == 'baidu':
		baidu(filepath, keyword, start, num)
	if engine == 'sougou':
		sougou(filepath, keyword, start, num)