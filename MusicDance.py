#モジュールのインポート
import time             #時間
import threading        #スレッド化
import socket           #TCP/IP通信
import pygame.mixer     #音楽再生
import wiringpi         #GPIOピン操作

#グローバル変数
value = 0
motionState = b'keep\n'
tmp = "test"

#信号の受信と送信
def func1():
    global value
    global motionState
    global tmp
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("192.168.3.6", 5001))       # 指定したホスト(IP)とポートをソケットに設定
    while True:
        s.listen(1)                     # 1つの接続要求を待つ
        soc, addr = s.accept()          # 要求が来るまでブロック
        print("Conneted by"+str(addr))  #サーバ側の合図
    
        tmp = value                     #前の状態を保存
        value = soc.recv(1024)          #受信した情報を保存
        print(value)
        
        soc.send(motionState)           #動きの指示を送信
        soc.shutdown(socket.SHUT_RDWR)
        soc.close()                     #接続を終了

#音楽再生と受信情報の処理
def func2():
    global value
    global tmp
    global motionState
    isStart=0
    while True:
        if tmp != value:                                    #受信データが変化したとき
            if value == (b'Start\n'):
                if isStart==0:                              #再生していなければ
                    isStart=1
                    playMusic("/home/pi/Music/fast.mp3")    #fastを再生
                    analysisTempo()                         #テンポを変更
            if value == (b'Start2\n'):
                if isStart==0:                              #再生していなければ
                    isStart=1
                    playMusic("/home/pi/Music/slow.mp3")    #fastを再生
                    analysisTempo()                         #テンポを変更
            if value == (b'Stop\n'):
                if isStart==1:                              #再生されていたら
                    pygame.mixer.music.stop()               #音楽停止
                    isStart=0
                
                motionState = (b'keep\n')                   #動きの停止
                time.sleep(1)

#スレッド処理
if __name__ == "__main__":
    thread_1 = threading.Thread(target=func1)
    thread_2 = threading.Thread(target=func2)

    thread_1.start()
    thread_2.start()
    
def playMusic(file):
    # mixerモジュールの初期化
    pygame.mixer.init()
    # 音楽ファイルの読み込み
    pygame.mixer.music.load(file)
    # 音楽再生、および再生回数の設定(-1はループ再生)
    pygame.mixer.music.play(-1)
    
def analysisTempo():
    global motionState
    # ボタンを繋いだGPIOの端子番号
    button_pin = 14 # 8番端子
    # GPIO初期化
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode( button_pin, 0 )
    wiringpi.pullUpDnControl( button_pin, 2 )

    count=0
    delay=0
    chata=0

    # whileの処理は字下げをするとループの範囲になる（らしい）
    while True:
        # GPIO端子の状態を読み込む
        # センサーをタッチすると「1」、放すと「0」になる
        if count<4:
            if( wiringpi.digitalRead(button_pin) == 1 ):
                # 0V(0)の場合
                chata=1
                time.sleep(0.1)
            else:
                if chata==1:
                    count=count+1
                    print (count)
                    chata=0
                # 5V(1)の場合
                time.sleep(0.01)
            
        if count == 4:
            if( wiringpi.digitalRead(button_pin) == 1 ):
                #テンポに関する情報を送信
                if delay < 1:
                    motionState = (b'fast\n')
                else:
                    motionState = (b'slow\n')
                #経過時間を表示
                print(delay)
                break
            else:
                #処理前の時刻
                t1 = time.time()
                time.sleep(0.01)
                #処理後の時刻
                t2 = time.time()
                elapsed_time = t2 - t1
                delay = delay + elapsed_time
        
