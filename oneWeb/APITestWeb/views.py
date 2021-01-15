#coding:utf-8

import os
import shutil
import time
import zipfile
from base64 import encode

from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect

# Create your views here.
from APITest.Run import getRun
from django.utils.encoding import escape_uri_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  #oneWeb
FBASE_DIR = os.path.abspath(os.path.dirname(os.getcwd()))  #git


newFileName = ''
newFileNameType = ''
def zip_files(dir_path, zip_path,isDel=False):
    """
    :param dir_path: 需要压缩的文件目录
    :param zip_path: 压缩后的目录
    :return:
    """

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as f:
        for root, _, file_names in os.walk(dir_path):
            for filename in file_names:
                f.write(os.path.join(root, filename), filename)
                if isDel:
                    os.remove(os.path.join(root, filename))

def checkReport():
    try:
        reportPath =  BASE_DIR+"/APITest/report"
        fileSize = 0
        for root, dirs, files in os.walk(reportPath, topdown=False):
            for file in files:
                fileSize += os.path.getsize(os.path.join(root, file))
        if fileSize >= 1024 * 1024 * 100:
            zip_files(reportPath,BASE_DIR+"APITest/ZIP/" + str(int(time.time())) + '.zip', isDel=True)
    except Exception as e:
        print("检测报告文件夹大小是否超过10MB失败："+str(e))

def delFiles(fpath):
    try:
        if not os.path.isdir(fpath):
            print("请确认输入的是正确的路径！")
        else:
            dataList = os.listdir(fpath)
            for i in dataList:
                f = os.path.join(fpath,i)
                if os.path.isdir(f):
                    os.rmdir(f)
                elif os.path.isfile(f):
                    os.remove(f)
                else:
                    print(str(f)+'无法识别文件！')
    except Exception as e:
        print('删除文件失败： '+str(e))

def mycopyfile(srcfile,dstpath):                       # 移动函数
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(srcfile)             # 分离文件名和路径
        if not os.path.exists(dstpath):
            os.makedirs(dstpath)  # 创建路径
        fileList = os.listdir(dstpath)
        p = fname.split('.')[0]
        typ = fname.split('.')[-1]
        k = 1
        while fname in fileList:
            fname = p + '(' + str(k) + ').' + typ
            k += 1
        shutil.copy(srcfile, dstpath + fname)          # 移动文件
        print ("move %s -> %s"%(srcfile, dstpath + fname))
#废弃
def renameFile(fpaths,name):
    try:
        global newFileNameType
        if not os.path.isfile(fpaths):
            raise KeyError
        else:
            fpath,fname = os.path.split(fpaths)
            fileType = fname.split('.')[-1]
            newFileNameType = fileType
            fileNameList = os.listdir(fpath)
            os.rename(fpaths,fpath+'/'+name+'.'+fileType)
            print('更改后的名称：'+fpaths,fpath+'/'+name+'.'+fileType)

    except Exception as e:
        print('重命名文件失败：'+str(e))


def getFile(request):
    global newFileName
    try:
        if request.method == 'POST':
            # name = newFileName
            # delFiles(BASE_DIR +'/APITest/TestData/')
            # mycopyfile(os.path.join(BASE_DIR+"\report", name),'D:/GIT/Test/APITest/TestData/')
            # renameFile('D:/GIT/Test/APITest/TestData/'+name,'数字乡村接口自动化')
            #删除旧日志文件，生成新日志文件

            end = getRun(newFileName)
            if end == 1:
                result = '启动成功！'
            else:
                result = '启动失败！'
            with open(BASE_DIR + '/APITest/log/logging.log','r') as f:
                log = f.readlines()
                f.close()

            file = BASE_DIR+"/APITest/code"
            listData = os.listdir(file)
            mycopyfile(BASE_DIR + '/APITest/log/logging.log', BASE_DIR + "/APITest/LOGZIP/")
            content = {'result':result,'log':log,'codeFile':listData}
            with open(BASE_DIR + '/APITest/log/logging.log','w') as f:
                f.close()
            checkReport()
            return render(request,'result.html',content)
        else:
            return redirect('/uploadFile/')
    except Exception as e:
        print("处理文件失败："+str(e))
        return HttpResponse(str(e))


def getCodeFile(request):
    try:
        if request.method == 'POST':
            myFile = request.FILES.get('code_file', None)
            if not myFile:
                return redirect("/upload/")  # home page should with error
            fileList = os.listdir(BASE_DIR+"/APITest/code")
            # oldFileName = myFile.name
            fileName = myFile.name
            p = myFile.name.split('.')[0]
            typ = myFile.name.split('.')[-1]
            k = 1
            while fileName in fileList:
                fileName = p + '(' + str(k) + ').' + typ
                k += 1
            destination = open(
                os.path.join(BASE_DIR+"/APITest/code", fileName), 'wb+')

            for chunk in myFile.chunks():
                destination.write(chunk)
            destination.close()
            # name = fileName
            # mycopyfile(os.path.join(BASE_DIR+"\report", name),'D:/GIT/Test/APITest/code/')
            # renameFile('D:/GIT/Test/APITest/code/'+name,p)

            return redirect('/upload/')

        else:
            return redirect('/upload/')
    except Exception as e:
        print("处理文件失败："+str(e))


def upload(request):
    global newFileName
    if request.method == "POST":
        myFile = request.FILES.get('upload_file', None)
        if not myFile:
            return redirect("/upload/")  # home page should with error
        fileList = os.listdir(BASE_DIR+"/APITest/TestData")
        fileName = myFile.name
        p = myFile.name.split('.')[0]
        typ = myFile.name.split('.')[-1]
        k = 1
        while fileName in fileList:
            fileName = p+'('+str(k)+').'+typ
            k+=1
        destination = open(
            os.path.join(BASE_DIR+"/APITest/TestData", fileName), 'wb+')

        for chunk in myFile.chunks():
            destination.write(chunk)
        destination.close()
        newFileName = fileName

        listData = os.listdir(BASE_DIR+"/APITest/TestData")
        context = {
            "MkdirData": listData
        }
        return render(request,'uploadFinish.html',context)

    else:
        return redirect("/uploadFile/")

def getMkdir(request):


    listData = os.listdir(BASE_DIR+'/APITest/TestData')
    fileCodeList = os.listdir(BASE_DIR+'/APITest/code')

    context = {
        "MkdirData":listData,'codeFile': fileCodeList
    }
    return render(request,'upload.html',context)


def download_template(request):
    resultFile = open(BASE_DIR + "/APITest/模板.xlsx", 'rb')

    response = FileResponse(resultFile)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(escape_uri_path("demo.xlsx"))
    return response

def download_user(request):
    resultFile = open(BASE_DIR + "/APITest/接口自动化操作手册.docx", 'rb')

    response = FileResponse(resultFile)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(escape_uri_path("接口自动化使用手册.docx"))
    print(response['Content-Disposition'])
    return response

def download_report(request):
    resultFile = open(BASE_DIR + "/APITest/TestData/"+newFileName, 'rb')
    print(BASE_DIR + "/APITest/TestData/"+newFileName)
    response = FileResponse(resultFile)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(escape_uri_path(newFileName))
    print(response['Content-Disposition'])
    return response



def download_code(request):
    filename = request.GET.get('fn')
    print(BASE_DIR + "/APITest/code/"+filename)
    resultFile = open(BASE_DIR + "/APITest/code/"+filename, 'rb')
    response = FileResponse(resultFile)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename*=utf-8''{}".format(escape_uri_path(filename))
    print(response)
    print(response['Content-Disposition'])
    return response
