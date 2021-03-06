import json
import os

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

termCodes = {1: '21', 2: '22', 3: '19', 4: '20', 5: '17', 6: '18', 7: '15', 8: '16', 9: '13', 10: '14',
             11: '1', 12: '2', 13: '43', 14: '63', 15: '84', 16: '103', 17: '123'}
classKind = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 'L': 11}


class student(object):
    my_header = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/47.0.2526.80 Safari/537.36 QQBrowser/9.3.6581.400',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Host': 'idas.uestc.edu.cn',
        'DNT': '1'
    }

    lt = None
    dllt = None
    execution = None
    _eventId = None
    rmShown = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login()

    def get(self, url):
        response = self.session.get(url=url, headers=self.my_header, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def post(self, url, postInfo):
        response = self.session.post(url=url, headers=self.my_header, data=postInfo, timeout=30)
        return response

    def login(self):
        loginURL = 'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/index.portal'
        soup = self.get(loginURL)
        self.lt = soup.find('input', {'name': 'lt'})['value']
        self.dllt = soup.find('input', {'name': 'dllt'})['value']
        self.execution = soup.find('input', {'name': 'execution'})['value']
        self._eventId = soup.find('input', {'name': '_eventId'})['value']
        self.rmShown = soup.find('input', {'name': 'rmShown'})['value']
        postInfo = {'username': self.username, 'password': self.password, 'lt': self.lt, 'dllt': self.dllt,
                    'execution': self.execution, '_eventId': self._eventId, 'rmShown': self.rmShown}
        response = self.post(loginURL, postInfo)
        if response.status_code == 200:
            print('登陆失败，学号或密码错误，请重试\n')
            main()

    def getGrade(self, term):
        print('\n当前为第{}学期:'.format(term))
        termCode = ((int(self.username[0:4])) - 2008) * 2 + term
        gradeURL = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!search.action?' \
                   'semesterId=' + termCodes[termCode] + '&projectType='
        gradeSoup = self.get(gradeURL).find_all('tr')
        self.outPut(gradeSoup)
        self.creditCount(gradeSoup)

    def allGrade(self):
        gradeURL = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action' \
                   '?projectType=MAJOR'
        gradeSoup = self.get(gradeURL).find_all('tr')[8:]
        print(gradeSoup)
        # self.outPut(gradeSoup)
        # self.creditCount(gradeSoup)

    def outPut(self, gradeSoup):
        courseTable = PrettyTable(['学期', '课程代码', '课程名称', '课程种类', '学分', '正考成绩', '补考成绩', '最终成绩', '绩点'])
        for i in range(1, len(gradeSoup)):
            term = gradeSoup[i].contents[1].contents[0].strip()
            courseCode = gradeSoup[i].contents[3].contents[0].strip()
            # courseNum = gradeSoup[i].contents[5].contents
            courseName = gradeSoup[i].contents[7].contents[0].strip()
            courseKind = gradeSoup[i].contents[9].contents[0].strip()
            courseCredit = gradeSoup[i].contents[11].contents[0].strip()
            firstGrade = gradeSoup[i].contents[13].contents[0].strip()
            secondGrade = gradeSoup[i].contents[14].contents[0].strip()
            finalGrade = gradeSoup[i].contents[15].contents[0].strip()
            GPA = gradeSoup[i].contents[16].contents[0].strip()
            courseTable.add_row(
                [term, courseCode, courseName, courseKind, courseCredit, firstGrade, secondGrade, finalGrade, GPA])
        print(courseTable)

    def creditCount(self, gradeSoup):
        total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(1, len(gradeSoup)):
            kind = gradeSoup[i].contents[3].contents[0].strip()[0]
            if kind in classKind.keys():
                if gradeSoup[i].contents[16].contents[0].strip() == '0':
                    continue
                total[classKind[kind]] += float(gradeSoup[i].contents[11].contents[0].strip())
            else:
                total[12] += float(gradeSoup[i].contents[11].contents[0].strip())
        x, y = getCreditTable(total)
        print('{}\n{}'.format(x, y))
        for i in range(len(sumAll)):
            sumAll[i] += total[i]


sumAll = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def getCreditTable(total):
    detailTable = PrettyTable(['种类', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'X', '总和'])
    detailTable.add_row(['已修', total[0], total[1], total[2], total[3], total[4], total[5], total[6], total[7],
                         total[8], total[9], total[10], total[11], total[12], sum(total)])
    classifyTable = PrettyTable(['小类', 'A', 'B', 'C', 'D', 'E + F + G', 'H + I + J', 'K + L', 'X', '总和'])
    classifyTable.add_row(['已修合计', total[0], total[1], total[2], total[3], (sum(total[4:6])),
                           (sum(total[7:9])), (sum(total[10:11])), total[12], sum(total)])
    return detailTable, classifyTable


def getCreditDescribeTable():
    describeTable = PrettyTable(['课程代码', '说明', '所需学分'])
    describeTable.add_row(['A', '核心通识', '4'])
    describeTable.add_row(['B', '基础通识', '32'])
    describeTable.add_row(['C', '交叉通识', '3'])
    describeTable.add_row(['D', '学科通识', '27'])
    describeTable.add_row(['E + F + G', '学科基础+学科拓展+专业核心', '50'])
    describeTable.add_row(['H + I + J', '专业选修+素质教育+创新拓展', '29'])
    describeTable.add_row(['K + L', '实验课程+实习实训', '25'])
    describeTable.add_row(['X', '未知类别', ''])
    describeTable.add_row(['', '毕业共需', '170'])
    return describeTable


def getUserInfo():
    try:
        with open('loginInfo.json', 'r') as f:
            userinfo = json.load(f)
            username = userinfo['username']
            password = userinfo['password']
            ifUse = input('查询到本地有保存的学号密码文件，是否使用（N:不使用，默认使用）:')
            if ifUse == 'N' or ifUse == 'n':
                raise None
    except Exception as e:
        username = input('输入学号：')
        password = input('信息门户密码：')
        ifStore = input('是否储存学号及密码到本地，明文储存非信任的电脑勿选（Y:存，默认不存）：')
        if ifStore == 'Y' or ifStore == 'y':
            with open('loginInfo.json', 'w') as f:
                userinfo = json.dumps({'username': username, 'password': password}, sort_keys=True, indent=4)
                f.write(userinfo)
    return username, password


def main():
    for i in sumAll:
        i = 0
    username, password = getUserInfo()
    s = student(username, password)
    print('登陆成功！\n')
    term = int(input('将查询前N个学期的学分(请勿大于所学学期总数),输入N='))
    for i in range(term):
        s.getGrade(i + 1)
        # s.allGrade()
    detailTable, classifyTable = getCreditTable(sumAll)

    classifyTable.add_row(['毕业共需', 4.0, 32.0, 3.0, 27.0, 50.0, 29.0, 25.0, 0.0, 170.0])
    classifyTable.add_row(['还需', 4.0 - sumAll[0], 32.0 - sumAll[1], 3.0 - sumAll[2], 27.0 - sumAll[3],
                           50.0 - sum(sumAll[4:6]), 29.0 - sum(sumAll[7:9]), 25.0 - sum(sumAll[10:11]),
                           0.0 - sumAll[12], 170.0 - sum(sumAll)])

    describeTable = getCreditDescribeTable()

    print('\n\n前{}学期合计统计如下:\n{}\n{}\n\n说明:\n{}'.format(term, detailTable, classifyTable, describeTable))
    print('数据来源于教务系统，仅供参考使用，以培养方案为准！！！\n\n')


def checkNew():
    version = '0.2.0'
    import urllib.request
    latestURL = 'https://api.github.com/repos/Cheain/creditAnalysis-UESTC/releases/latest'
    latestInfo = urllib.request.urlopen(latestURL).read().decode(encoding='utf-8')
    latestInfo = json.loads(latestInfo)
    if latestInfo['tag_name'] <= version:
        print('***当前版本为最新版,请继续使用***\n')
    else:
        tag = input('当前版本不是最新版，是否更新（N:不更新，默认更新）：')
        if tag != 'N' and tag != 'n':
            urllib.request.urlretrieve(latestInfo['assets'][0]['browser_download_url'],
                                       'main-{}.exe'.format(latestInfo['tag_name']))
            print('***已下载最新版，请重启***\n')
            os.system('pause')
            exit()


if __name__ == '__main__':
    print('***说明：供成电理工类专业查询学分，推荐全屏使用***\n')
    try:
        checkNew()
        main()
    except Exception as e:
        print('出错:{}\n程序异常请联系:https://github.com/Cheain/creditAnalysis-UESTC/issues'.format(e))
    finally:
        os.system('pause')
