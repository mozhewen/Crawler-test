from time import time
from datetime import datetime
from random import randint


_SOURCE_URL = 'https://www.wjx.cn/jq/{}.aspx'
_PROCESS_URL = 'https://www.wjx.cn/joinnew/processjq.ashx?submittype=1&curID={}&t={}&starttime={}&rn={}'

class question:
    def __init__(self, _title=None, _type=None, _option=None, _value=None):
        self.title = _title
        self.type = _type
        self.option = _option
        self.value = _value

class questionnair:
    def __init__(self, _ID, _rn, _num):
        self.ID = _ID
        self.rn = _rn
        self.__qnList = [question() for i in range(_num)]
    def __getitem__(self, index):
        return self.__qnList[index]
    def __setitem__(self, index, value):
        self.__qnList[index] = value
    def __len__(self):
        return self.__qnList.__len__()


def getQN(session, ID):
    # 1. 发起 HTTP 请求
    response = session.get(_SOURCE_URL.format(ID))
    # 2. 解析网页
    # 2.1 找到那个随机数 rndnum，提交表单时需要用到
    rn = response.html.search('rndnum="{}"')[0].split('.')[0]
    # 2.2 找到表单域
    questions = response.html.find('fieldset', first=True).find('.div_question')
    qn = questionnair(ID, rn, len(questions))
    # 2.3 对于每一道题
    for i, q in enumerate(questions):
        #   获取题目
        qn[i].title = q.find('.div_title_question', first=True).text
        #   题目类型（目前只支持这些类型）
        #     填空题
        if q.find('.inputtext', first=True) != None:
            qn[i].type = 'textarea'
        #     选择题
        elif q.find('.ulradiocheck', first=True) != None:
            if q.find('input[type=radio]', first=True) != None: # 单选
                qn[i].type = 'radio'
            elif q.find('input[type=checkbox]', first=True) != None: # 多选
                qn[i].type = 'checkbox'
            #       把每个选项的内容提取出来
            qn[i].option = [it.text for it in q.find('li')]
        #     未知类型
        else:
            qn[i].type = 'UNKNOWN'
    return qn


def fillInQN(qn, data):
    for i in range(len(data)):
        qn[i].value = data[i]


def showQN(qn):
    for i, q in enumerate(qn):
        # 题目
        print(i+1, q.title)
        # 标记一下跳过的题目
        if q.value == None:
            print('<Skipped>')
        # 题目类型
        #   填空题
        if q.type == 'textarea':
            print(f'[  {q.value}  ]')
        #   单选题
        elif q.type == 'radio':
            for j, it in enumerate(q.option):
                if j+1 == q.value:
                    front = '(*)'
                else:
                    front = '( )'
                print(front, it)
        #   多选题
        elif q.type == 'checkbox':
            for j, it in enumerate(q.option):
                if q.value != None and j+1 in q.value:
                    front = '[*]'
                else:
                    front = '[ ]'
                print(front, it)
        print()


def submitQN(session, qn):
    # 1. 编码表单数据
    formData = {'submitdata':''}
    for i, q in enumerate(qn):
        if q.type == 'textarea':
            if q.value == None:
                code = '(跳过)'
            else:
                code = q.value
        elif q.type == 'radio':
            if q.value == None:
                code = str(-3)
            else:
                code = str(q.value)
        elif q.type == 'checkbox':
            if q.value == None:
                code = str(-3)
            else:
                code = '|'.join(map(str, q.value))
        formData['submitdata'] += f'{i+1}${code}}}'
    #   去除最后一个'}'
    formData['submitdata'] = formData['submitdata'][:-1]

    # 2. 计算填表时间
    #   t: 提交时间
    t_raw = round(time(), 3) # 精确到毫秒
    t = int(t_raw*1000)
    #   starttime: 开始填表时间
    #     假装是在 t 的1到2分钟以前填表的
    date = datetime.fromtimestamp(int(t_raw) - randint(60, 60*2))
    starttime = f'{date.year}/{date.month}/{date.day} {date.hour}:{date.minute}:{date.second}'

    # 3. 生成表单处理程序的URL
    URL = _PROCESS_URL.format(qn.ID, t, starttime, qn.rn)

    # 4. POST
    response = session.post(URL, formData)

    print('Status Code: ', response.status_code)
