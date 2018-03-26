#coding=utf-8
import os

IMAGE_EXTENSIONS = set(['jpg', 'JPG', 'jpeg','png', 'bmp', 'PNG', 'BMP'])
IMAGE_EXTENSIONS1 = set(['jpg', 'JPG', 'jpeg','png', 'bmp', 'PNG', 'BMP', 'txt'])

def genlabel(label):
	string = '{"length": 1, "objects": [{"x_start": 0.0, "y_start": 0.0, "x_end": 1.0, "y_end":1.0, "tag": ["%s"], "info": " "}]}'%(label)
	return string

#os.mkdir("data")

def gentag(taglist):
	string = '{"listname":["种类"],"taglist":{"种类":['
	num = len(taglist)
	i=0
	for tag in taglist:
		string += '"%s"'%(tag)
		i=i+1
		if i<num:
			string += ","
	string += ']}}'
	return string

imgNum =0

os.system("rm -rf ./data")

taglist = {}

for parentdir,dirname,filenames in os.walk("."):  
	for filename in filenames:  
		if filename.split('.')[-1] in IMAGE_EXTENSIONS:   
			imgNum = imgNum+1
			label = parentdir.split('/')[-1]
			#print label
			if label not in taglist:
				taglist[label] = 1
			else:
				taglist[label] = taglist[label]+1

			imgpath = parentdir+'/'+filename
			labelpath = imgpath+'.txt'
			fh = open(labelpath, 'w')
			fh.write(genlabel(label))
			fh.close()

if os.path.exists("./data") == False:
	os.mkdir("data")

fileNum = 0

for parentdir,dirname,filenames in os.walk("."):  
	for filename in filenames:
		if parentdir != './data':
			if filename.split('.')[-1] in IMAGE_EXTENSIONS1:   
				fileNum = fileNum+1
				# print filename
				filepath = parentdir+'/'+filename
				# print filepath
				i =0
				for char in filepath:
					if char == ' ':
						i=i+1
				splitNames = []
				newfilepath = ""
				if i>=1:
					splitNames = filepath.split(' ')
					newfilepath = splitNames[0]
				for j in range(len(splitNames)-1):
					newfilepath = newfilepath+"\ "+splitNames[j+1]
				#print newfilepath
				cmd = ''
				if i==0:
					cmd = 'mv '+filepath+' ./data/'+parentdir+'_'+filename
				if i>=1:
					cmd = 'mv '+newfilepath+' ./data/'+parentdir+'_'+filename.split(' ')[-1]
					# print cmd
				os.system(cmd)
print imgNum,fileNum

ft = open('tag.json', 'w')
tagstring = gentag(taglist)
print tagstring
ft.write(tagstring)
ft.close()