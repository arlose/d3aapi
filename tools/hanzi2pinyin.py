#coding=utf-8
import os
from xpinyin import Pinyin
p = Pinyin()
#p.get_pinyin(u"上海", '')

for parentdir,dirname,filenames in os.walk("."):  
    for filename in filenames:
        ufilename = unicode(filename, "utf-8")
        newname = p.get_pinyin(ufilename, '').encode('utf-8')
        if filename != newname:
            cmd = 'mv %s %s'%(filename, newname)
            os.system(cmd)