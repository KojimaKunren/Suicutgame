import tkinter as tk
import random
import pygame
from pygame.locals import *
import requests
import json
import textwrap
import dao
import time

W, H = 1280, 720  # ウインドウサイズ
scene = "login"  # シーン設定
username = ""
password = ""
currentuser = None
newuser = None
isClick = False
score = 0  # スコア
timer = 120  # タイマー
mouseClick = False  # マウスクリック
mouseX, mouseY = 0, 0  # マウスの座標
posX, posY = 0, 0  # ターゲットの座標
listNum = 0  # キャラクター変更用変数
imgMix = 0  # img5をランダムで表記するための変数
countTag = 0  # タグ付け用カウント
targetList = []  # 生成されたターゲットを保存するリスト
targetInfoList = []  # ターゲットの基礎情報リスト
targetShakeList = []  # 消去するターゲットを一時保管するリスト
targetNumber = 0  # tag生成時の個別番号用
targetNumberMax = 0
deletecounter = 0
scoreList = []
newRankingList = []
se = None  # se用変数


# マウスクリック
def mouseClick(e):
    global mouseClick, mouseX, mouseY
    mouseX = e.x
    mouseY = e.y
    mouseClick = True
    targetDestroy()


# テキスト描画設定
def text(x, y, text, font, size, color, tag):
    cvs.create_text(x, y, text=text, font=(font, size), fill=color, tag=tag)


# ゲームメイン画面
def main():
    global score, timer, scene, mouseClick, targetList, targetNumber, targetNumberMax
    cvs.delete("all")
    if scene == "login":
        nameLabel.pack()
        nameEntry.pack()
        passLabel.pack()
        passEntry.pack()
        button.pack()
        frame.place(anchor="center", x=W / 2, y=H * 0.2)
        if currentuser != None:
            scene = "title"
            mouseClick = False
            frame.destroy()

    if scene == "title":
        cvs.create_image(640, 360, image=titleImg)
        text(W / 2, H * 0.6, "Click to Start", "Comic Sans MS", 50, "yellow", "title")
        if mouseClick == True:
            scene = "game"
            mouseClick = False

    if scene == "game":
        # root.after(3000, placeFrame)
        cvs.create_image(W / 2, H / 2, image=bgImg)
        cvs.pack()
        cvs.delete("score")
        cvs.delete("timer")
        text(200, 100, "SCORE:" + str(score), "MV Boli", 30, "White", tag="score")
        text(1080, 100, "LIMIT:" + str(timer), "MV Boli", 30, "White", tag="timer")
        if len(targetList) == 0:
            createTarget(targetNumber)
            if (targetNumber + 1) < 5:
                targetNumber += 1
            else:
                targetNumber = 0
        displayTarget(targetList)
        if timer == 0:
            scene = "gameover"
        timer = timer - 1

    if scene == "gameover":
        mouseClick = False
        cvs.delete("all")
        cvs.create_image(W / 2, H / 2, image=bgImg)
        calcRanking(score)
        text(W / 2, H * 0.3, f"SCORE:{score}", "Comic Sans MS", 60, "Yellow", "score")
        text(
            W / 2,
            H * 0.5,
            f"1st:{newRankingList[0]}",
            "Comic Sans MS",
            40,
            "White",
            "ranking1",
        )
        text(
            W / 2,
            H * 0.6,
            f"2nd:{newRankingList[1]}",
            "Comic Sans MS",
            40,
            "White",
            "ranking2",
        )
        text(
            W / 2,
            H * 0.7,
            f"3rd:{newRankingList[2]}",
            "Comic Sans MS",
            40,
            "White",
            "ranking3",
        )
        text(
            W / 2, H * 0.8, "Click to ReStart", "Comic Sans Ms", 30, "white", "gameover"
        )
        cvs.pack()
        if mouseClick == True:
            scene = "game"
            mouseClick = False
    root.after(1000, main)


def displayTarget(targetList):
    for n in targetList:
        cvs.create_image(n.posX, n.posY, image=n.img, tag=n.tag)


def createTarget(targetNumber):
    global countTag
    n = targetInfoList[targetNumber]

    if targetNumber == 0:
        tag = f"{n.name}_{countTag}"
        posX = W / 2
        posY = H / 2
        target = Target(n.name, posX, posY, n.num, n.size, n.score, n.img, tag)
        targetList.append(target)

    elif targetNumber == 1:
        for m in range(n.num):
            tag = f"{n.name}_{countTag}"
            posX = int(random.randint(1, W / 2)) + ((W / 2) * m)
            if posX + n.size > W:
                posX = W - n.size
            elif posX + n.size < 1:
                posX = 1 + n.size
            posY = int(random.randint(1, H))
            if posY + n.size > H:
                posY = H - n.size
            elif posY + n.size < 1:
                posY = 1 + n.size
            target = Target(n.name, posX, posY, n.num, n.size, n.score, n.img, tag)
            targetList.append(target)

    else:
        i = targetNumber - 1  # ターゲット番号から1を引く（2-1=1）
        j = 2**i  # 2の倍数を設定（2）
        k = int(n.num / j)  # ターゲットの生成数を2の倍数で割る（4/2＝2）
        for m in range(n.num):
            tag = f"{n.name}_{countTag}"
            posX = int(random.randint(1, W / k)) + ((W / k) * m)
            if posX + n.size > W:
                posX = W - n.size
            elif posX + n.size < 1:
                posX = 1 + n.size
            posY = int(random.randint(1, H / k)) + ((H / k) * m)
            if posY + n.size > H:
                posY = H - n.size
            elif posY + n.size < 1:
                posY = 1 + n.size

            # img5ランダム設定
            if n == 5:
                imgMix = random.randrange(len(imgList))
                n.img = imgList[imgMix]

            target = Target(n.name, posX, posY, n.num, n.size, n.score, n.img, tag)
            targetList.append(target)
            countTag += 1


# ターゲット揺れの基本設定
def shake(tag):
    cvs.move(tag, 0.1, 0)
    for _ in range(10):
        cvs.move(tag, -0.2, 0)
        cvs.after(50, lambda: cvs.move(tag, 0.2, 0))


# ターゲットを揺らすアニメーション処理
def shakeTarget():
    global targetShakeList, deletecounter
    deletecounter = 0
    for n in targetShakeList:
        shake(n.tag)
        cvs.after(500, lambda: cvs.delete(n.tag))
        cvs.after(501, lambda: targetShakeList.pop(deletecounter))


# ターゲット破壊
def targetDestroy():
    global mouseX, mouseY, targetNumber, targetList, score
    count = 0
    for n in targetList:
        # ターゲット位置とマウス位置の判定
        if (n.posX - n.size) <= mouseX <= (n.posX + n.size) and (
            n.posY - n.size
        ) <= mouseY <= (n.posY + n.size):
            # スコアカウント
            score += n.score
            se.play()
            targetShakeList.append(targetList.pop(count))
            shakeTarget()
            # ターゲットリストのカウントアップ
            # if len(targetList) <= 0:
            #     if (targetNumber + 1) < targetNumberMax:
            #         targetNumber += 1
            #     else:
            #         targetNumber = 0
            # break
        else:
            count += 1


def placeFrame():
    global listNum
    frame2.place(anchor="center", x=W / 2, y=650)  # frame配置
    mainLabel.place(anchor="n", x=W / 2, y=50, relwidth=0.8, relheight=0.3)
    faceCVS.create_image(80, 110, image=faceImgList[listNum])
    faceCVS.place(
        anchor="s",
        x=180,
        y=200,
    )
    root.after(1000, destroyFrame)


def destroyFrame():
    frame2.place_forget()
    faceCVS.delete()
    replaceSecond = random.randint(1, 10) * 1000
    root.after(replaceSecond, replaceFrame)


def replaceFrame():
    mainLabel["text"] = displayProverb()
    faceCVS.create_image(80, 110, image=faceImgList[listNum])
    frame2.place(anchor="center", x=W / 2, y=H / 2)
    faceCVS.place(
        anchor="s",
        x=180,
        y=200,
    )
    root.after(2000, destroyFrame)


def appendProverbs(url, name, key):
    res = requests.get(url)
    data = json.loads(res.text)
    textwrap.fill(data[key], 30)
    proverb = Proverb(name, data[key])
    return proverb


def appendProverbsMulti(url, name, key1, key2):
    res = requests.get(url)
    data = json.loads(res.text)
    worddata = data[key1][key2]
    proverb = Proverb(name, worddata)
    return proverb


def appendProverbsJoint(url, name, key1, key2):
    res = requests.get(url)
    data = json.loads(res.text)
    key1 = data[key1]
    key2 = data[key2]
    texts = f"{key1} \n{key2}"
    proverb = Proverb(name, texts)
    return proverb


# テキスト表記のための乱数、テキスト作成
def displayProverb():
    global listNum
    listNum = random.randrange(len(faceImgList))
    # APIから情報を取得
    if listNum == 0:
        proverb = appendProverbsJoint(url1, "Oldman", "setup", "punchline")
    elif listNum == 1:
        proverb = appendProverbs(url2, "Scientist", "text")
    elif listNum == 2:
        proverb = appendProverbsMulti(url3, "OldWoman", "slip", "advice")
    elif listNum == 3:
        proverb = appendProverbs(url4, "Boy", "activity")
    mainText = f"{proverb.name}\n{proverb.word}"
    return mainText


def getUser():
    global currentuser, newuser
    username = nameEntry.get()
    password = passEntry.get()
    userdata = dao.find_all()
    for n in userdata:
        # ユーザーの検索、パスワードの確認、現在のユーザーに設定
        if n["username"] == username and n["password"] == password:
            currentuser = User(
                n["id"],
                n["username"],
                n["password"],
                n["topscore"],
                n["secondscore"],
                n["thirdscore"],
            )
        # 新規ユーザー登録
        else:
            newuser = NewUser(username, password, 0, 0, 0)
            dao.insert_one(newuser)
            setUser()


# 新規ユーザーを現在のユーザーに設定
def setUser():
    global currentuser, newuser
    userdata = dao.find_one(newuser)
    currentuser = User(
        userdata[0],
        userdata[1],
        userdata[2],
        userdata[3],
        userdata[4],
        userdata[5],
    )


def calcRanking(score):
    global currentuser, newRankingList, scoreList
    scoreList = [currentuser.topscore, currentuser.secondscore, currentuser.thirdscore]
    scoreList.append(score)
    newRankingList = sorted(scoreList, reverse=True)
    del newRankingList[-1]
    return newRankingList


class User:
    def __init__(self, id, username, password, topscore, secondscore, thirdscore):
        self.id = id
        self.username = username
        self.password = password
        self.topscore = topscore
        self.secondscore = secondscore
        self.thirdscore = thirdscore


class NewUser:
    def __init__(self, username, password, topscore, secondscore, thirdscore):
        self.username = username
        self.password = password
        self.topscore = topscore
        self.secondscore = secondscore
        self.thirdscore = thirdscore


# ターゲットインスタンス
class Target:
    def __init__(
        self, name="name", posX=0, posY=0, num=0, size=0, score=0, img="img", tag="tag"
    ):
        self.name = name
        self.posX = posX
        self.posY = posY
        self.num = num
        self.size = size
        self.score = score
        self.img = img
        self.tag = tag


class Proverb:
    def __init__(self, name, word):
        self.name = name
        self.word = word


root = tk.Tk()
root.geometry(f"{W}x{H}")
root.bind("<Button>", mouseClick)

cvs = tk.Canvas(root, width=W, height=H, bg="white")
titleImg = tk.PhotoImage(file="Suicutgame/image/start.png")
bgImg = tk.PhotoImage(file="Suicutgame/image/bg.png")
cvs.pack()

frame2 = tk.Frame(root, width=W, height=H * 0.35)
frame2.propagate(False)


img1 = tk.PhotoImage(file="Suicutgame/image/obj1.png")
img2 = tk.PhotoImage(file="Suicutgame/image/obj2.png")
img3 = tk.PhotoImage(file="Suicutgame/image/obj3.png")
img4 = tk.PhotoImage(file="Suicutgame/image/obj4.png")
img5 = tk.PhotoImage(file="Suicutgame/image/obj5.png")
img5_2 = tk.PhotoImage(file="Suicutgame/image/obj6.png")
imgList = [img5, img5_2]

target1 = Target("target1", 0, 0, 1, 400, 1, img1, "tag")
target2 = Target("target2", 0, 0, 2, 300, 2, img2, "tag")
target3 = Target("target3", 0, 0, 4, 100, 4, img3, "tag")
target4 = Target("target4", 0, 0, 16, 30, 16, img4, "thag")
target5 = Target("target5", 0, 0, 32, 10, 64, img5, "tag")
targetInfoList = [target1, target2, target3, target4, target5]

frameImg = tk.PhotoImage(file="Suicutgame/image/frame.png")
faceImg1 = tk.PhotoImage(file="Suicutgame/image/oldman.png")
faceImg2 = tk.PhotoImage(file="Suicutgame/image/scientist.png")
faceImg3 = tk.PhotoImage(file="Suicutgame/image/oldwoman.png")
faceImg4 = tk.PhotoImage(file="Suicutgame/image/boy.png")
faceImgList = [faceImg1, faceImg2, faceImg3, faceImg4]

url1 = "https://official-joke-api.appspot.com/jokes/random"
url2 = "http://numbersapi.com/random/year?json"
url3 = "https://api.adviceslip.com/advice"
url4 = "https://www.boredapi.com/api/activity/"

mainLabel = tk.Label(
    frame2,
    width=1025,
    height=600,
    compound=tk.CENTER,
    text=displayProverb(),
    image=frameImg,
    fg="red",
    font=("Ink Free", 20),
)

faceCVS = tk.Canvas(frame2, width=160, height=220)

frame = tk.Frame(root, width=W, height=H / 2)
font = ("Family", 20)
nameEntry = tk.Entry(frame)
passEntry = tk.Entry(frame)
nameLabel = tk.Label(frame, text="USER NAME", font=font, fg="Black")
passLabel = tk.Label(frame, text="Password", font=font, fg="Black")
button = tk.Button(frame, text="SEND", command=getUser)


pygame.init()

# 効果音の設定
try:
    se = pygame.mixer.Sound("Suicutgame/bgm/maou_se_system41.mp3")
except:
    pass
se.set_volume(0.2)


# pygame初期設定

main()
root.mainloop()
