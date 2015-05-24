#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-05-12 18:35:26
# @Author  : Matrixdom (Matrixdom@126.com)
# @Link    : 
# @Version : 0.1
#coding=utf-8

import re
import os

templateFilePattern=re.compile("^\w+\.tmp$")


#获取所有模板名
def getAllTemplateFiles(path):
	result=set()
	for parent,dirnames,filenames in 	os.walk(path):
		for fileName in 	filenames:
			m=templateFilePattern.search(fileName)
			if m:
				result.add(m.group())
	return result

def genCodeFile(f):
	line=f.readline()
	lineNum=0
	Temp={}
	Temp["Fileds"]={}
	while line!='':
		if not re.compile(r'^(##.+)|([\r\n])$').match(line):
			line=line.strip("\n")
			if lineNum==0:
				Temp["package"]=line
			else:
				#print(line.split(":"))
				if len(line.split(":"))>1:
					Temp["Fileds"][line.split(":")[0]]=line.split(":")[1]
		lineNum+=1
		line=f.readline()
	return Temp

allTemplates=getAllTemplateFiles(".")

for filename in allTemplates:
	path=os.getcwd()+"/templates/"+filename
	f=open(path)
	#dir(f)
	tmp=genCodeFile(f)
	print(tmp)

