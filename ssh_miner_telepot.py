# -*-coding:utf-8-*-

import pymongo
import time
import paramikoWrapper as wrap
import telepot
import re
import copy
import pprint
from datetime import datetime, timedelta

# miners_no_log 로그 없는 마이너들
#2,9윈도우. 7,37장비 없음. 11, 13, 14
miners_no_log = [2,9,11,12,13,37]
miners_farm1 = [1,3,4,5,6,7,8,14]
miners_farm2 = [10]
miners_farm3 = [i for i in range(15,39) if i is not 37 ]
miner_list = miners_farm1 + miners_farm2 + miners_farm3
cp_miner_list = copy.deepcopy(miner_list)



mongoClient = pymongo.MongoClient("52.78.93.195", 27017)
mongoDB = mongoClient.di


idlist = [161289242, 33612976, 180121526]
# idlist = [161289242]
bot = telepot.Bot("254864168:AAHq16HhIx5J0jrySsN8nzNYliQOtZejBXk")

def mkLog(num):
    # logList, nowTimeStr = logging(i)
    # print 'nowTimeStr', nowTimeStr
    logList = logging(num)
    lastLogToStr = "".join(logList[-1])

    logToStr = "".join(logList)
    logToStr = logToStr.encode('utf-8')
    # print "logToStr: ", type(logToStr)

    # if i in miners_no_log :
    #     print "miner %d LOG does not exist" %i
    return logList, lastLogToStr, logToStr


# 로그의 마지막 시간과 현재시간의 차이를 비교한다.
# 마이너가 멈춰있는지 아닌지를 식별한다.
def timeGap(logList):
    # lastLogTime 최신 마지막 로그 기록 type은 string
    # print logList, '\n'

    lastLogTime = (re.findall("\d{2}:\d{2}:\d{2}",logList[-1])[0]).encode('utf-8')
    # lastLogTime = str(re.findall("\d{2}:\d{2}:\d{2}",logList[9].split()[2])[0])
    # print type(lastLogTime)
    # print 'logList[-1]: ', logList[-1]


    # print '.split(): ',logList[-1].split()
    # print '.split()[2]: ',logList[-1].split()[2]
    # print 'lastLogTime', lastLogTime


    # print ':-----',lastLogTime.split(':')
    # print 'len-----',len(lastLogTime.split(':'))
    # print '1-----',lastLogTime.split(':')[1]
    # print 'i0-----',int(lastLogTime.split(':')[0])
    # print 'i1-----',int(lastLogTime.split(':')[1])
    # print 'i2-----',int(lastLogTime.split(':')[2])
    FMT = '%H:%M:%S'
    # print lastLogTime


    nowTimeStr = datetime.now().strftime(FMT)
    # print 'nowTimeStr', nowTimeStr
    n = int(nowTimeStr.split(':')[1])
    # print '현재시간', n
    l = int(lastLogTime.split(':')[1])
    # print '마지막시간', l

    timeGap = n - l
    timeGap = abs(timeGap)
    # print '시간 차', timeGap

    # tdelta = datetime.strptime(nowTimeStr, FMT) - datetime.strptime(lastLogTime, FMT)
    # # timeGap 단위는 minutes임
    # timeGap = tdelta.seconds/60

    # print "timeGap:", timeGap
    # 3분 이상이면 1을 리턴한다.
    if bool(timeGap > 4) == True :
        # True 1
        return 1
    else :
        # False 0
        return 0




# DB에서 데이터 받아서 20초 마다 ‘0’해시 확인
def checkHash():
    while True :
        # # print '1) cp_miner_list', cp_miner_list
        # if set(miner_list) == set(cp_miner_list):
        #     mlist = miner_list
        # else:
        #     # print '2) cp_miner_list', cp_miner_list
        #     mlist = cp_miner_list
        # print 'mlist', mlist
        for i in miners_no_log :
            if i in cp_miner_list:
                cp_miner_list.remove(i)
        mlist = cp_miner_list


        for i in mlist :
            try :
                # 'i' is miner number, type(i) is int
                logList, lastLogToStr, logToStr = mkLog(i)
                # print 'lastLogToStr', lastLogToStr
                # print 'logToStr','\n',logToStr

                if bool(re.search('0.00MH/s', logToStr)) == True :
                    print 'logToStr','\n',logToStr
                    mess = "miner%s: 0.00MH/s " % str(i)
                    print mess
                    # log10줄에서 0.00MH/s가 있으면 다시 로그를 불러온다
                    # 마지막 로그에 0.00MH/s가 있는지 확인하고 메세지 한다.
                    # timeGap이 참이면, 자동 재부팅한다.
                    for j in range(1) :
                        time.sleep(17)
                        logList, lastLogToStr, logToStr = mkLog(i)
                        if bool(re.search('0.00MH/s', lastLogToStr)) == True :
                            print 'lastLogToStr','\n',lastLogToStr
                            mess1 = "miner%s: HashRate is 0.00MH/s " % str(i)
                            result1 = reboot(i)
                            print result1
                            mess2 = 'Ok, auto-reboot miner%s' % i
                            mess = mess1 +'\n'+ mess2
                            sendMessageToidList(mess)
                        else :
                            print "miner %s is operating.." % str(i)

                # elif i in miners_no_log :
                # print "miner %d LOG does not exist" %i
                elif bool(re.search('Subscribed to stratum server', logToStr)) == True :
                    print 'logToStr','\n',logToStr
                    print 'stratum server', re.search('Subscribed to stratum server', logToStr)
                    # log10줄에서 stratum server가 있으면 다시 로그를 불러온다
                    # 마지막 로그에 stratum server가 있는지 확인하고 메세지 한다.
                    # timeGap이 참이면, 자동 재부팅한다.
                    for j in range(1) :
                        time.sleep(17)
                        logList, lastLogToStr, logToStr = mkLog(i)
                        if bool(re.search('Subscribed to stratum server', logToStr)) == True :
                            if timeGap(logList) == 1 :
                                # print 'logToStr','\n',logToStr
                                mess1 = " miner%s: Subscribed to stratum server" % str(i)
                                result1 = reboot(i)
                                print result1
                                mess2 = 'Ok, auto-reboot miner%s' % i
                                mess = mess1 +'\n'+ mess2
                                sendMessageToidList(mess)
                            else :
                                print 'logToStr','\n',logToStr
                                mess = " miner%s: Subscribed to stratum server" % str(i)
                                sendMessageToidList(mess)
                        else :
                            print "miner %s is operating.." % str(i)

                elif bool(re.search('Submitting stale solution.', logToStr)) == True :
                    print 'logToStr','\n',logToStr
                    print 'stale', re.search('Submitting stale solution.', logToStr)
                    # log10줄에 stale 에러가 있으면, 다시 로그를 불러온다
                    # 또다시 stale 에러가 있으면 자동 재부팅한다.
                    for j in range(1) :
                        time.sleep(17)
                        logList, lastLogToStr, logToStr = mkLog(i)
                        if bool(re.search('Submitting stale solution.', logToStr)) == True :
                            print 'logToStr','\n',logToStr
                            mess1 = " miner%s: Submitting stale solution. " % str(i)
                            result1 = reboot(i)
                            print result1
                            mess2 = 'Ok, auto-reboot miner%s' % i
                            mess = mess1 +'\n'+ mess2
                            sendMessageToidList(mess)
                        else :
                            print "miner %s is operating.." % str(i)

                elif bool(re.search('FAILURE:', logToStr)) == True :
                    print 'logToStr','\n',logToStr
                    print 'FAILURE', re.search('FAILURE:', logToStr)
                    # log10줄에 FAILURE 에러가 있으면, 다시 로그를 불러온다
                    # 또다시 FAILURE 에러가 있으면 자동 재부팅한다.
                    for j in range(1) :
                        time.sleep(17)
                        logList, lastLogToStr, logToStr = mkLog(i)
                        if bool(re.search('FAILURE:', logToStr)) == True :
                            print 'logToStr','\n',logToStr
                            mess1 = " miner%s: FAILURE:GPU gave incorrect result! " % str(i)
                            result1 = reboot(i)
                            print result1
                            mess2 = 'Ok, auto-reboot miner%s' % i
                            mess = mess1 +'\n'+ mess2
                            sendMessageToidList(mess)
                        else :
                            print "miner %s is operating.." % str(i)

                else :
                    # timeGap이 참이면, 자동 재부팅한다.
                    if timeGap(logList) == 1 :
                        print 'logToStr','\n',logToStr
                        mess1 = " miner%s: stop! " % str(i)
                        result1 = reboot(i)
                        print result1
                        mess2 = 'Ok, auto-reboot miner%s' % i
                        mess = mess1 +'\n'+ mess2
                        sendMessageToidList(mess)
                    else :
                        print "miner %s is operating.." % str(i)

            except Exception as e :
                m, r = "miner%s: [Error] " % str(i), e
                # mess = m + repr(r)
                mess = m + repr(r)+'\n'+ logToStr
                print mess
                sendMessageToidList(mess)

        # time.sleep(150)
        # 9분
        time.sleep(540)

def sendMessageToidList(message):
    # bot.sendMessage(161289242, message)
    for id in idlist:
        bot.sendMessage(id, message)

    # for i in token(tokenlist):
    #     for j in idlist:
    #         i.sendMessage(j, message)

# tokenlist = ["254864168:AAHq16HhIx5J0jrySsN8nzNYliQOtZejBXk"]
# def token(tokenlist):
#     bot_list = []
#     for t in tokenlist:
#         bot_list.append(telepot.Bot(t))
#     return result


def logging(minerNum):
    # try:
        # result = ""

        # if minerNum in miners_no_log :
        #     result = "miner%d: LOG does not exist" % minerNum

        # elif (minerNum < 9) or (minerNum == 14) :
        if (minerNum < 9) | (minerNum == 14):
            client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

            # result is list type
            result = client.execute('tail -10 ethminer.err.log')['out']
            # a = result.encode('utf-8').....에러
            # print a ...리스트
            # print len(result)

        # elif minerNum in [10,11,12,13,14]:
        #     portMapping = {9:8080,  10:22, 11:443, 12:444, 13:80, 14:3390}
        #     client = wrap.SSHClient('ggs134.gonetis.com', portMapping[int(minerNum)], 'miner'+str(minerNum), 'rlagnlrud' )
        #     result = client.execute('tail -10 ethminer.err.log')['out']

        else:
            client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
            result = client.execute('tail -10 ethminer.err.log')['out']

        # nowTimeStr = datetime.now().strftime('%H:%M:%S')
        # return result, nowTimeStr
        return result




# def recmessage(tokenlist):
#     result=[]
#     for i in token(tokenlist):
#         for j in i:
#             result.append(j.getUpdates()[-1]['message']['text'])

def restartAll(minerNum):
    if (minerNum < 9) | (minerNum == 14):
        client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

    result = client.execute('sudo supervisorctl restart all', sudo=True)
    return result['out']


def stop(minerNum):
    if (minerNum < 9) | (minerNum == 14):
        client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

    result = client.execute('sudo supervisorctl stop ethminer', sudo=True)
    return result['out']


def reread(minerNum):
    if (minerNum < 9) | (minerNum == 14):
        client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

    result = client.execute('sudo supervisorctl reread', sudo=True)
    return result['out']


def update(minerNum):
    if (minerNum < 9) | (minerNum == 14):
        client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

    result = client.execute('sudo supervisorctl update', sudo=True)
    return result['out']

def reboot(minerNum):
    if (minerNum < 9) | (minerNum == 14):
        client = wrap.SSHClient('222.98.97.238', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )
    else:
        client = wrap.SSHClient('goldrush.iptime.org', 50000+int(minerNum), 'miner'+str(minerNum), 'rlagnlrud' )

    result = client.execute('sudo reboot', sudo=True)
    return result



# 텔레그램에 로그 확인 log(숫자) 메세지 보내면 텔레그램에서 로그 보여줌
def recieveMessage(id, msg):
    # while 1:
        # response = bot.getUpdates()
    res = msg['text']
    try:
        # if bool(re.search('l(?i)og\(*', res)) == True:
        if bool(re.search("l(?i)og", res)) == True:
            # type(res) is list
            res = re.findall(r"[0-9]*",res)
            # type(res[0]) is string
            # print 'res',res
            minerNum = res[3]
            print type(minerNum)
            result1 = logging(int(minerNum))
            result = convert_list(result1)
            bot.sendMessage(id, result)

            # for k in range(3, len(res)):
            #     if (k%2==1) == True:
            #         minerNum = res[k]
            #         # print k, minerNum
            #         # type(minerNum) is string
            #         result1 = logging(int(minerNum))
            #         print result1, type(result1)
            #         # type(result1) is list
            #         print res
            #         result = convert_list(result1)
            #         # type(result) is list
            #         # sendMessage(result)
            #         print result
            #         bot.sendMessage(id, result)

        elif bool(re.search("r(?i)estart", res)) == True:
            res = re.findall(r"[0-9]*",res)
            # print res
            minerNum = res[7]
            # print minerNum
            # type(minerNum) is string
            print "restartAll start"
            result1 = restartAll(int(minerNum))
            print result1
            bot.sendMessage(id, 'Ok, restartAll miner%s' % minerNum)

        elif bool(re.search("s(?i)top", res)) == True:
            res = re.findall(r"[0-9]*",res)
            # print res
            minerNum = res[4]
            # print minerNum
            # type(minerNum) is string
            print "stop start"
            result1 = stop(int(minerNum))
            print result1
            bot.sendMessage(id, 'Ok, stop miner%s' % minerNum)

        elif bool(re.search("r(?i)eread", res)) == True:
            res = re.findall(r"[0-9]*",res)
            # print res
            minerNum = res[6]
            # print minerNum
            # type(minerNum) is string
            print "reread start"
            result1 = reread(int(minerNum))
            print result1
            bot.sendMessage(id, 'Ok, reread miner%s' % minerNum)

        elif bool(re.search("u(?i)pdate", res)) == True:
            res = re.findall(r"[0-9]*",res)
            # print res
            minerNum = res[6]
            # print minerNum
            # type(minerNum) is string
            print "update start"
            result1 = update(int(minerNum))
            print result1
            bot.sendMessage(id, 'Ok, update miner%s' % minerNum)

        elif bool(re.search("r(?i)eboot", res)) == True:
            res = re.findall(r"[0-9]*",res)
            # print res
            # minerNum = res[6]
            # print 'res[6]', minerNum
            # print 'len(res)', len(res)
            for k in range(6, len(res)):
                if (k%2==0) == True:
                    minerNum = res[k]
                    # print k, minerNum
                    # print type(minerNum)
                    # print "reboot start"
                    result1 = reboot(int(minerNum))
                    print result1
                    bot.sendMessage(id, 'Ok, reboot miner%s' % minerNum)


        # on off = 알람 끄고 켜기
        elif bool(re.search('o(?i)ff', res)) == True:
            res = re.findall(r"[0-9]+",res)
            # print res
            # print len(res)
            # minerNum = res[0]
            # print minerNum

            for k in range(len(res)):
                minerNum = res[k]
                cp_miner_list.remove(int(minerNum))
                # sendMessage('TurnOff miner%s' % minerNum)
                bot.sendMessage(id, 'Ok, alarmOff miner%s' % minerNum)

        elif bool(re.search('o(?i)n', res)) == True:
            res = re.findall(r"[0-9]+",res)
            # print res
            # print len(res)
            for k in range(len(res)):
                minerNum = res[k]
                print minerNum
                cp_miner_list.append(int(minerNum))
                # sendMessage('TurnOn miner%s' % minerNum)
                bot.sendMessage(id, 'Ok, alarmOn miner%s' % minerNum)

        # 알람 켜진 마이너 리스트
        elif bool(re.search('l(?i)ist', res)) == True:
            for i in miners_no_log:
                if i in cp_miner_list:
                    cp_miner_list.remove(i)
            print cp_miner_list

            mlist= str(list(set(cp_miner_list)))
            bot.sendMessage(id, 'Operating miners%s' % mlist)

        else:
            pass
        # time.sleep(20)
    except Exception as e :
        m, r = "miner%s: [Error] " %minerNum, e
        # mess = m + repr(r)
        mess = m + repr(r)
        print mess
        sendMessageToidList(mess)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # print content_type, chat_type, chat_id
    if content_type == 'text':
        # pprint.pprint(msg)
        recieveMessage(chat_id, msg)


def convert_list(lst):
    newLst = [i.encode("utf-8").replace("[","") for i in lst]
    # res = [re.sub(r"\d{2}m|\d{1}m","",j).decode("utf-8") for j in newLst ]
    res = [re.sub(r"\d{2}m|\d{1}m|\f","",j).decode("utf-8") for j in newLst ]
    # res = [str(i) for i in lst]
    return res

# def fromid(idlist):
#     fromid_list = []
#     for f in idlist:
#         fromid_list.append()

if __name__ == '__main__':
    # checkHash()
    # recieveMessage()
    # print "hello"
    bot.message_loop(handle)
    print "listening.."
    # while 1:
    #     time.sleep(10)
    checkHash()
