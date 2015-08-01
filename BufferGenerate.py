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

from time import time
from optparse import OptionParser

VERSION = '0.1'

templateFilePattern = re.compile("^\w+\.tmp$")

targetTmpl = []


class SourceItem:
    id = 0
    name = ""

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def toString(self):
        return "{id:" + self.id + ",name:" + self.name + "}"


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
    feilds = []

    def __init__(self, id, name, desc):
        self.classId = id
        self.className = name
        self.classDesc = desc
        self.feilds=[]

    def setPackage(self, package):
        self.package = package

    def getPackage(self):
        return self.package

    def addFeild(self, _feildinfo):
        index = len(self.feilds)
        _feildinfo.index = index
        if index != 0:
            self.getFeildByIndex(index - 1).IsLastFeild = False
        _feildinfo.IsLastFeild = True
        self.feilds.append(_feildinfo)

    def getFeildByIndex(self, __index):
        assert __index <= len(self.feilds)
        return self.feilds[__index]


class FeildInfo:
    fieldName = ""
    fieldType = ""
    fieldDesc = ""

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
    nodes = node.getElementsByTagName("field")
    for fnode in nodes:
        fieldName = fnode.getAttribute("name")
        fieldType = fnode.getAttribute("class")
        fieldDesc = fnode.getAttribute("explain")
        fieldInfo = FeildInfo(fieldName, fieldType, fieldDesc)
        classInfo.addFeild(fieldInfo)
        print("add field:"+fieldName+"to "+classInfo.className+" fields count:"+str(len(classInfo.feilds)))


def getAllClassInfo(source):
    classes = []
    dom = xml.dom.minidom.parse(source)
    root = dom.documentElement

    # package
    print("get class info from" + source)
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
        classInfo.setPackage(packageinfo)
        classes.append(classInfo)
        getFieldsFromSource(classInfo, node)


    # classes
    nodes = root.getElementsByTagName("message")
    for node in nodes:
        classId = node.getAttribute("id")
        className = node.getAttribute("name")
        classDesc = node.getAttribute("explain")
        classInfo = ClassInfo(0, className, classDesc)
        classInfo.ClassTag = 0 if node.getAttribute("type") == "CS" else 1
        classInfo.setPackage(packageinfo)
        classes.append(classInfo)
        getFieldsFromSource(classInfo, node)
    return classes

def replaceKeyWords(src,classInfo):
    src = re.compile(r"\$PACKAGENAME\$").sub(classInfo.package.packageName, src)
    src = re.compile(r"\$CLASSNAME\$").sub(classInfo.className, src)
    forcontents = re.findall(r'(<\s*for\s+(\$\w+?\$)\s+:\s+(\$\w+?\$)\s*>(.*?)</\s*for\s*>)', src, re.S)

    if forcontents:
        for forcontent in forcontents:
            var = forcontent[1]
            col = forcontent[2]
            subcontent = forcontent[3].rstrip("\n")

            newContent = ""
            if col == "$Fields$":
                for filed in classInfo.feilds:
                    # print("create field:"+classInfo.Package.PackageName+"."+classInfo.ClassName+"."+filed.fieldName)
                    str = subcontent.replace("$PACKAGENAME$", classInfo.package.packageName)
                    # print(str.strip("\n"))
                    str = str.replace("$CLASSNAME$", classInfo.package.packageName)
                    str = str.replace(var + ".$FieldsName$", filed.fieldName)
                    str = str.replace(var + ".$FieldsType$", filed.fieldType)
                    newContent += str
            src = src.replace(forcontent[0], newContent)
    return src

def gencodefilebytmpl(classInfo, tmplpath):
    filename=""
    f = open(tmplpath)

    str=f.readline()
    str=replaceKeyWords(str,classInfo)
    if str.find("#filename:"):
        print(str)
        #filename=str.split(":")[1]
        print "filename:"+filename

    tmplContent = f.read()
    tmplContent=replaceKeyWords(tmplContent,classInfo)
    f.close()

    return tmplContent,filename


def _check_python_version():
    major_ver = sys.version_info[0]
    if major_ver > 2:
        print ("The python version is %d.%d. But python 2.x is required. (Version 2.7 is well tested)\n"
               "Download it here: https://www.python.org/" % (major_ver, sys.version_info[1]))
        return False

    return True


def help():
    print("\n%s %s - BufferGenerate console: A command line tool for generate message code" %
          (sys.argv[0], VERSION))
    print("\nAvailable commands:")
    # parse = Cocos2dIniParser()
    # classes = parse.parse_plugins()
    '''max_name = max(len(classes[key].plugin_name(
    ) + classes[key].plugin_category()) for key in classes.keys())
    max_name += 4
    for key in classes.keys():
        plugin_class = classes[key]
        category = plugin_class.plugin_category()
        category = (category + ' ') if len(category) > 0 else ''
        name = plugin_class.plugin_name()
        print("\t%s%s%s%s" % (category, name,
                              ' ' * (max_name - len(name + category)),
                              plugin_class.brief_description()))
    '''
    print("\nAvailable arguments:")
    print("\t-h, --help\tShow this help information")
    print("\t-v, --version\tShow the version of this command tool")
    # print("\nExample:")
    # print("\t%s new --help" % sys.argv[0])
    # print("\t%s run --help" % sys.argv[0])


def readSourceItems(source, reg):
    path = os.path.abspath(source)
    dom = xml.dom.minidom.parse(path)
    root = dom.documentElement
    nodes = root.getElementsByTagName("message")

    items = []
    for node in nodes:
        id = node.getAttribute("id")
        name = node.getAttribute("name")
        if reg != "":
            p = re.compile(reg)
            if not p.match(name):
                continue
        item = SourceItem(id, name)
        items.append(item)
    return items


def main():
    workpath = os.path.dirname(os.path.realpath(__file__))

    if not _check_python_version():
        exit()

    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
        help()
        # DataStatistic.terminate_stat()
        # sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ('-v', '--version'):
        print("%s" % VERSION)
        # DataStatistic.terminate_stat()
        # sys.exit(0)

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
                content = gencodefilebytmpl(classInfo, tmpl)
                targetDir = os.path.join(os.path.abspath(args.targetdir),os.path.splitext(os.path.basename(tmpl))[0])
                if not os.path.exists(os.path.dirname(targetDir)):
                    os.mkdir(os.path.dirname(targetDir))
                if not os.path.exists(targetDir):
                    print "mkdir:"+targetDir
                    os.mkdir(targetDir)
                path = os.path.join(targetDir, classInfo.className)
                print(path)
                f = open(path, "w+")
                f.write(content)
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
