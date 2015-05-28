#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-05-12 18:35:26
# @Author  : Matrixdom (Matrixdom@126.com)
# @Link    : 
# @Version : 0.1
# coding=utf-8

import re
import os

templateFilePattern = re.compile("^\w+\.tmp$")


class ClassInfo:
    _feilds = []

    def __init__(self):
        pass

    def addfeild(self, _feildinfo):
        index = len(self._feilds)
        _feildinfo.index = index
        if index != 0:
            self.getfeildbyindex(index - 1).IsLastFeild = False
        _feildinfo.IsLastFeild = True
        self._feilds.append(_feildinfo)

    def getfeildbyindex(self, __index):
        assert __index <= len(self._feilds)
        return self._feilds[__index]


class FeildInfo:
    _classinfo = ClassInfo()

    def __init__(self, __classinfo):
        assert isinstance(__classinfo, ClassInfo)
        self._classinfo = __classinfo

    def getclassinfo(self):
        return self._classinfo


# 获取所有模板名
def getalltemplatefiles(path):
    result = set()
    for parent, dirnames, filenames in os.walk(path):
        for fileName in filenames:
            m = templateFilePattern.search(fileName)
            if m:
                result.add(m.group())
    return result


def gencodefile(filename):
    """

    :rtype : ClassInfo
    """
    path = os.getcwd() + "/templates/" + filename
    f = open(path)
    line = f.readline()
    linenum = 0
    classinfo = ClassInfo()
    classinfo.ClassName = filename.split(".")[0]
    classinfo.Feilds = []
    while line != '':
        if not re.compile(r'^(##.+)|([\r\n])$').match(line):
            line = line.strip("\n")
            if linenum == 0:
                classinfo.PackageName = line
            else:
                # print(line.split(":"))
                if len(line.split(":")) > 1:
                    field = FeildInfo(classinfo)
                    field.Name = line.split(":")[0]
                    field.TypeName = line.split(":")[1]
                    classinfo.Feilds.append(field)
            linenum += 1
        line = f.readline()
    return classinfo


##read content of lang
def getTmplContent(lang):
    path = os.getcwd() + "/" + lang + ".tmpl"
    f = open(path)
    content = f.read()
    f.close()
    return content


allTemplates = getalltemplatefiles(".")

for filename in allTemplates:
    # dir(f)
    classinfo = gencodefile(filename)
    # print(tmp)
    content = getTmplContent("cpp")
    content = re.compile(r"\$PACKAGENAME\$").sub(classinfo.PackageName, content)
    content = re.compile(r"\$CLASSNAME\$").sub(classinfo.ClassName, content)
    forcontents = re.findall(r'(<\s*for\s+(\$\w+?\$)\s+:\s+(\$\w+?\$)\s*>(.*?)</\s*for\s*>)', content, re.S)

    if forcontents:
        # print(forcontents[0])
        for forcontent in forcontents:
            var = forcontent[1]
            col = forcontent[2]
            subcontent = forcontent[3].rstrip("\n")

            newContent = ""
            if col == "$Fields$":
                for filed in classinfo.Feilds:
                    str = subcontent.replace("$PACKAGENAME$", classinfo.PackageName)
                    # print(str.strip("\n"))
                    str = str.replace("$CLASSNAME$", classinfo.PackageName)
                    str = str.replace(var + ".$FieldsName$", filed.Name)
                    str = str.replace(var + ".$FieldsType$", filed.TypeName)
                    newContent += str
            content = content.replace(forcontent[0], newContent)

    print(content)
    print("....................")
# break
