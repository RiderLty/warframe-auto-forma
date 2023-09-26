import json
import os
from os.path import join
from time import sleep

import aircv as ac
import cv2
import numpy as np
import requests
from bottle import *
from PIL import Image, ImageDraw

from utils.adbInterface import adbInterface as device
from utils.adbInterface import noExtendDisplayRootedInterface as rootDevice


def matchImg(target: bytes, templateBytes: bytes, threshold: float):
    targetImgArr = np.array(Image.open(BytesIO(target)), dtype=np.uint8)
    templateImgArr = np.array(Image.open(BytesIO(templateBytes)), dtype=np.uint8)
    return ac.find_template(targetImgArr, templateImgArr, threshold)

def matchAndClick(phone:device, name:str , count = 5):
    app_main = open( join(join(os.path.split(__file__)[0],"sources"),name), 'rb' ).read()
    for __ in range(count):
        screen = phone.screenCap()
        result = matchImg(screen, app_main, 0.9)
        if result != None:
            print(result)
            phone.tap(int(result["result"][0]), int(result["result"][1]))
            return True
    return False


def unLock(phone:device):
    print("解锁")
    phone.execute("input keyevent 26")
    sleep(1)
    phone.swipe(720, 3000, 720,1000, 200)
    lookPoints = json.load(open( join(os.path.split(__file__)[0],"screenlock.points.json"), 'r' ))
    rootDevice().drag(
        lookPoints,
        100
    )
    print("解锁完成")

if __name__ == "__main__":
    os.system("adb kill-server")
    print("adb kill-server")
    os.system("setprop service.adb.tcp.port 5555")
    os.system("stop adbd")
    os.system("start adbd")
    os.system("adb connect 127.0.0.1:5555")
    print("adb connected")
    phone = device( "127.0.0.1:5555", 0 )
    unLock(phone)
    print("启动warframe")
    phone.launchApp("com.digitalextremes.warframenexus/com.digitalextremes.warframenexus.WarframeCompanionActivity")
    print("等待启动")
    sleep(3)
    print("匹配主页面")
    if not matchAndClick(phone,"app_main.jpg"): exit(1)
    sleep(1)
    print("匹配菜单页面")
    if not matchAndClick(phone,"menu_open.jpg"): exit(2)
    sleep(1)
    print("匹配仓库页面")
    if not matchAndClick(phone,"inventory.jpg"): exit(3)
    sleep(1)
    print("匹配所有种类按钮")
    if not matchAndClick(phone,"all_kind.jpg"): exit(4)
    sleep(1)
    print("输入 forma 按下 Enter")
    phone.execute("input text forma")
    phone.execute("input keyevent 66")
    phone.execute("input keyevent 66")#中文输入法

    secondDetect = False

    success = False

    print("第一次匹配forma")
    if matchAndClick(phone,"forma.jpg"):
        sleep(0.5)
        if matchAndClick(phone,"get.jpg",1):
            print("领取成功")
            secondDetect = True
        elif matchAndClick(phone,"acc.jpg",1):
            print("加速制造 但是不点")
        elif matchAndClick(phone,"build.jpg",1):
            print("点击制造")
            sleep(0.3)
            print("点击确认")
            if matchAndClick(phone,"confirm.jpg",5):
                success = True
        
        elif matchAndClick(phone,"not_enough.jpg",1):
            print("没有足够的材料")
        else:
            print("没有匹配")

    if secondDetect:
        print("等待领取")
        sleep(3)
        print("第二次匹配forma")
        if matchAndClick(phone,"forma.jpg"):
            sleep(0.3)
            if matchAndClick(phone,"build.jpg",1):
                print("点击制造")
                sleep(0.3)
                print("点击确认")
                if matchAndClick(phone,"confirm.jpg",5):
                    success = True

            else:
                print("没有匹配")
    print("kill")
    phone.killApp("com.digitalextremes.warframenexus")
    print("lock")
    phone.execute("input keyevent 26")
    print("完成")
    if success:
        exit(0)
    else:
        exit(5)
