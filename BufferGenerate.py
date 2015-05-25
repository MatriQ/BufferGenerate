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

def genCodeFile(filename):
	path=os.getcwd()+"/templates/"+filename
	f=open(path)
	line=f.readline()
	lineNum=0
	Temp={}
	Temp["Class"]=filename.split(".")[0]
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

##read content of lang
def getTmplContent(lang):
	path=os.getcwd()+"/"+lang+".tmpl"
	f=open(path)
	content=f.read()
	f.close()
	return content

allTemplates=getAllTemplateFiles(".")

for filename in allTemplates:
	#dir(f)
	tmp=genCodeFile(filename)
	#print(tmp)
	content=getTmplContent("go")
	content=re.compile(r"\$PACKAGENAME\$").sub(tmp["package"],content)
	content=re.compile(r"\$CLASSNAME\$").sub(tmp["Class"],content)
	forcontents=re.findall(r'(<\s*for\s+(\$\w+?\$)\s+:\s+(\$\w+?\$)\s*>(.*?)</\s*for\s*>)',content,re.S)
	
	if forcontents:
		#print(forcontents[0])
		for forcontent in forcontents:
			var=forcontent[1]
			col=forcontent[2]
			subcontent=forcontent[3].rstrip("\n")

			newContent=""
			if col=="$Fields$":	
				for (filed,T) in tmp["Fileds"].items():
					str=subcontent.replace("$PACKAGENAME$",tmp["package"])
					#print(str.strip("\n"))
					str=str.replace("$CLASSNAME$",tmp["package"])
					str=str.replace(var+".$FieldsName$",filed)
					str=str.replace(var+".$FieldsType$",T)
					newContent+=str
			content=content.replace(forcontent[0],newContent)

	print(content)
	print("....................")
	#break

