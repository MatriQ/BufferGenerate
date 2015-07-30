#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-05-12 18:35:26
# @Author  : Matrixdom (Matrixdom@126.com)
# @Link    : 
# @Version : 0.1
# coding=utf-8

import re
import os
import sys
import os.path
import traceback

from time import time
from optparse import OptionParser


VERSION = '0.1'

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

def GeneCode():
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
    #parse = Cocos2dIniParser()
    #classes = parse.parse_plugins()
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
    #print("\nExample:")
    #print("\t%s new --help" % sys.argv[0])
    #print("\t%s run --help" % sys.argv[0])


def main():
    workpath = os.path.dirname(os.path.realpath(__file__))

    if not _check_python_version():
        exit()

    if len(sys.argv) == 1 or sys.argv[1] in ('-h', '--help'):
        help()
        #DataStatistic.terminate_stat()
        #sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] in ('-v', '--version'):
        print("%s" % VERSION)
        #DataStatistic.terminate_stat()
        #sys.exit(0)
    parser = OptionParser()

    parser.add_option('-r', '--remove-download',
                      action="store", type="string", dest='remove_downloaded', default=None,
                      help="Whether to remove downloaded zip file, 'yes' or 'no'")

    parser.add_option("-f", "--force-update",
                      action="store_true", dest="force_update", default=False,
                      help="Whether to force update the third party libraries")

    parser.add_option("-d", "--download-only",
                      action="store_true", dest="download_only", default=False,
                      help="Only download zip file of the third party libraries, will not extract it")

    (opts, args) = parser.parse_args()
    print opts.remove_downloaded, opts.force_update, opts.download_only
    print args
# -------------- main --------------
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
