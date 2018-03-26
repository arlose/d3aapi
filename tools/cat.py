# coding: utf-8

import os

name = 'cat'
fi = open(name+'.txt')
lines = fi.readlines()
fi.close()

for line in lines:
    txtname = line.strip()
    jpgname = txtname.replace('.jpg.txt','.jpg')
    txtfile = "./data/%s"%(txtname)
    jpgfile = "./data/%s"%(jpgname)
    cmd = 'cp %s %s'%(txtfile, name)
    os.system(cmd)
    cmd = 'cp %s %s'%(jpgfile, name)
    os.system(cmd)