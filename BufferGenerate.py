#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-05-12 18:35:26
# @Author  : Matrixdom (Matrixdom@126.com)
# @Version : 0.1
# coding=utf-8

import re
import os
import sys
import os.path
import traceback
import argparse
import glob
import xml.dom.minidom
import airspeed


from time import time
from optparse import OptionParser

VERSION = '0.1'

templateFilePattern = re.compile("^\w+\.tmp$")

targetTmpl = []


class TaretFile:
    fileName=""
    fileContent=""
    def __init__(self, filename, filecontent):
        self.fileName = filename
        self.fileContent = filecontent

class PackageInfo:
    packageId = 0
    packageName = ""
    packageDesc = ""

    def __init__(self, id, name, desc):
        self.packageId = id
        self.packageName = name
        self.packageDesc = desc


class ClassInfo:
    classId = 0
    className = ""
    classTag = 0
    classDesc = ""
    package = None
    isBean=False
    fields = []

    def __init__(self, id, name, desc):
        self.classId = id
        self.className = name
        self.classDesc = desc
        self.fields=[]

    def setPackage(self, package):
        self.package = package

    def getPackage(self):
        return self.package

    def addField(self, _Fieldinfo):
        index = len(self.fields)
        _Fieldinfo.index = index
        if index != 0:
            self.getFieldByIndex(index - 1).isLastField = False
        _Fieldinfo.isLastField = True
        self.fields.append(_Fieldinfo)

    def getFieldByIndex(self, __index):
        assert __index <= len(self.fields)
        return self.fields[__index]


class FieldInfo:
    fieldName = ""
    fieldType = ""
    fieldDesc = ""
    isSimpleType=True

    def __init__(self, name, type, desc):
        self.fieldName = name
        self.fieldType = type
        self.fieldDesc = desc

    def getClassInfo(self):
        return self.classInfo


# 获取所有模板名
def getalltemplatefiles(tmpls):
    result = []
    for tmpl in tmpls:
        path = os.path.abspath(tmpl)
        result.append(path)
    return result


def getFieldsFromSource(classInfo, node):
    for fnode in node.childNodes:
    #nodes = node.getElementsByTagName("field")
    #for fnode in nodes:
        if fnode.nodeName=="field" or fnode.nodeName=="list":
            fieldName = fnode.getAttribute("name")
            fieldDesc = fnode.getAttribute("explain")
            fieldType = fnode.getAttribute("class")
            fieldInfo = FieldInfo(fieldName, fieldType, fieldDesc)
            if fnode.nodeName=="list":
                fieldInfo.isList=True
            classInfo.addField(fieldInfo)
            print("add field:"+fieldName+" to "+classInfo.className+" fields count:"+str(len(classInfo.fields)))

def getAllClassInfo(source):
    classes = []
    dom = xml.dom.minidom.parse(source)
    root = dom.documentElement

    # package
    #print("get class info from" + source)
    id = int(root.getAttribute("id"))
    name = root.getAttribute("package")
    packageinfo = PackageInfo(id, name, "")

    # bean
    nodes = root.getElementsByTagName("bean")
    for node in nodes:
        className = node.getAttribute("name")
        classDesc = node.getAttribute("explain")
        classInfo = ClassInfo(0, className, classDesc)
        classInfo.ClassTag = classTag = -1
        classInfo.isBean=True
        classInfo.setPackage(packageinfo)
        classes.append(classInfo)
        getFieldsFromSource(classInfo, node)


    # classes
    nodes = root.getElementsByTagName("message")
    for node in nodes:
        classId = node.getAttribute("id")
        className = node.getAttribute("name")
        classDesc = node.getAttribute("explain")
        classInfo = ClassInfo(classId, className, classDesc)
        classInfo.ClassTag = 0 if node.getAttribute("type") == "CS" else 1
        classInfo.setPackage(packageinfo)
        classes.append(classInfo)
        getFieldsFromSource(classInfo, node)
    return classes

def gencodefilebytmpl(classInfo, tmplpath):
    fields=classInfo.fields
    targetFiles=[]
    f = open(tmplpath)
    content=f.read()
    f.close()
    if content.find("#filestart")==-1:
        raise ValueError("Template file:"+tmplpath+" not include #filestart")

    r=re.compile("#filestart:.+?(?=#fileend)",re.S)
    results=r.findall(content)
    for result in results:
        #print "result:"+result
        match=re.compile("(?<=#filestart:).+?(?=\n)",re.S)
        #print(match.search(result).group())
        t=airspeed.Template(match.search(result).group())
        filename=""
        if t!=None:
            filename=t.merge(locals())
        match=re.compile("(?<=\n).+",re.S).search(result)
        filecontent=""
        if match!=None:
            filecontent=match.group()
        t=airspeed.Template(filecontent)
        filecontent=t.merge(locals())

        filename=re.sub(r"(?<=[^\\])\\0","",filename)
        filecontent=re.sub(r"(?<=[^\\])\\0","",filecontent)

        targetFiles.append(TaretFile(filename,filecontent))
    return targetFiles

def _check_python_version():
    major_ver = sys.version_info[0]
    if major_ver > 2:
        print ("The python version is %d.%d. But python 2.x is required. (Version 2.7 is well tested)\n"
               "Download it here: https://www.python.org/" % (major_ver, sys.version_info[1]))
        return False

    return True


def help():
    print("\n%s %s \n A command line tool for generate message code" %
          (sys.argv[0], VERSION))
    #print("\nAvailable commands:")
    print("\nAvailable arguments:")
    print("\t-h, --help\tShow this help information")
    print("\t-v, --version\tShow the version of this command tool")
    print("\t")
    print("\tsource \tA dir of xml files,or some xml files")
    print("\t-t, --tmpl\tSome template files")
    print("\t-r, --regex\tA regex of file filter")
    print("\t-d, --dir\tThe target output folder,default is src")

    print("Example:")
    print("\tpython BufferGenerate.py Message.xml -t cpp.tmpl")
    print("\tpython BufferGenerate.py sources -t cpp.tmpl lua.tmpl -d targetsrc")

def main():

    #print dir(airspeed)
    workpath = os.path.dirname(os.path.realpath(__file__))

    if not _check_python_version():
        exit()

    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
        help()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ('-v', '--version'):
        print("%s" % VERSION)
        sys.exit(0)

    try:
        # command = sys.argv[1]
        argvs = sys.argv[1:]
        if len(argvs) == 0:
            print ("Args cannot empty")
            return

        parser = argparse.ArgumentParser(description="This is a description of %(prog)s",
                                         epilog="This is a epilog of %(prog)s",
                                         prefix_chars="-+",
                                         fromfile_prefix_chars="@",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("source",
                            help="xml source dir",
                            nargs="+")

        parser.add_argument("-t", "-tmpl",
                            required=True,
                            nargs="+",
                            dest="template",
                            help="used tmpls")

        parser.add_argument("-r", "-regex",
                            dest="regex",
                            help="regex")

        parser.add_argument("-d", "-dir",
                            dest="targetdir",
                            default="src",
                            help="target dir")
        args = parser.parse_args(argvs)

        targetTmpl = getalltemplatefiles(args.template)

        # get source pathes
        pathes = []
        for s in args.source:
            sourcepath = os.path.abspath(s)
            if not os.path.exists(sourcepath):
                print("source path:" + sourcepath + " is not exists")
                continue
            elif os.path.isdir(sourcepath):
                # dir
                p = re.compile(".+\\.xml")
                for f in glob.glob(sourcepath + os.sep + '*.xml'):
                    if not os.path.isdir(f):
                        pathes.append(f)
            else:
                pathes.append(sourcepath)

        classes = []
        for path in pathes:
            classes.extend(getAllClassInfo(path))

        for classInfo in classes:
            for tmpl in targetTmpl:
                targetFiles = gencodefilebytmpl(classInfo, tmpl)
                targetDir = os.path.join(os.path.abspath(args.targetdir),os.path.splitext(os.path.basename(tmpl))[0])
                if not os.path.exists(os.path.dirname(targetDir)):
                    os.mkdir(os.path.dirname(targetDir))
                if not os.path.exists(targetDir):
                    print "mkdir:"+targetDir
                    os.mkdir(targetDir)
                for targetFile in targetFiles:
                    path = os.path.join(targetDir, targetFile.fileName)
                    f = open(path, "w+")
                    f.write(targetFile.fileContent)
                    print("write file:"+targetFile.fileName)
                    f.close()

    except Exception, e:
        traceback.print_exc()
        # raise e
        # else:
        #    pass
        # finally:
        #    pass

# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
