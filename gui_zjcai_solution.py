import requests
import re
import time
import threading
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QTextEdit
from PyQt5.QtGui import QIntValidator


class MainLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mainLayout = QVBoxLayout()
        userinfoLayout = QHBoxLayout()
        mainLayout.addLayout(userinfoLayout)

        # 用户名
        username = QLabel("用户名:", self)
        self.usernameLine = QLineEdit(self)
        self.usernameLine.setMaxLength(10)
        # 密码
        password = QLabel("密码:", self)
        self.passwordLine = QLineEdit(self)
        # 线程数
        thread = QLabel("线程数(可以不写，默认5个)", self)
        self.threadNum = QLineEdit(self)
        self.threadNum.setValidator(QIntValidator(0, 100))
        self.threadNum.setMaxLength(3)
        self.threadNum.setFixedWidth(80)
        # 按钮
        self.button = QPushButton("登录开始答题", self)
        self.button.clicked.connect(self.login)
        # 副布局添加组件
        userinfoLayout.addWidget(username)
        userinfoLayout.addWidget(self.usernameLine)
        userinfoLayout.addWidget(password)
        userinfoLayout.addWidget(self.passwordLine)
        userinfoLayout.addWidget(thread)
        userinfoLayout.addWidget(self.threadNum)
        userinfoLayout.addWidget(self.button)
        # url
        urlLabel = QLabel("url:")
        self.urlLine = QLineEdit(self)
        textLabel = QLabel("打印信息")
        self.text = QTextEdit(self)
        # 主布局添加组件
        mainLayout.addWidget(urlLabel)
        mainLayout.addWidget(self.urlLine)
        mainLayout.addWidget(textLabel)
        mainLayout.addWidget(self.text)

        # 设置字体
        username.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.usernameLine.setStyleSheet("font-size: 26px; font-family: Arial;")
        password.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.passwordLine.setStyleSheet("font-size: 26px; font-family: Arial;")
        thread.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.threadNum.setStyleSheet("font-size: 26px; font-family: Arial;")
        urlLabel.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.urlLine.setStyleSheet("font-size: 26px; font-family: Arial;")
        textLabel.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.text.setStyleSheet("font-size: 26px; font-family: Arial;")
        self.button.setStyleSheet("font-size: 26px; font-family: Arial;")

        # 设置大小
        self.setFixedHeight(800)
        self.setFixedWidth(1300)

        self.setLayout(mainLayout)
        self.setWindowTitle("iStudy作业通解-by 无敌の星仔")

    def login(self):
        username = self.usernameLine.text()
        password = self.passwordLine.text()
        url = self.urlLine.text()
        threadText = self.threadNum.text()
        threadingNum = 5
        if threadText is not None and not threadText.__eq__(""):
            if int(threadText) > 0:
                threadingNum = int(threadText)

        # url，账号，密码，线程数
        main_handle_thread = threading.Thread(target=lambda: main_handle(url, username, password, threadingNum))
        main_handle_thread.start()
        # main_handle_thread.join()
        # self.layout().addWidget(self.button)

    def append_info(self, info):
        self.text.append(str(info))


def logon(username, password):
    url = "https://zjcai.com/account/LogOn"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {'UserName': username, 'Password': password}
    post = requests.post(url=url, data=data, headers=headers, allow_redirects=False)
    cookie = {}
    cookies = post.cookies
    for c in cookies:
        cookie[c.name] = c.value
    return cookie


def go_test(cookie):
    url = 'https://zjcai.com/GoTest'
    get = requests.get(url=url, cookies=cookie, allow_redirects=False)
    for c in get.cookies:
        cookie[c.name] = c.value
    return cookie


def login(username, password):
    c = logon(username, password)
    c = go_test(c)
    return c


def get_list(url, cookie):
    text = requests.get(url=url, cookies=cookie).text
    findall = re.findall(r'<a href="javascript:;" data-val-id="\d+">', text)
    number_list: list[int] = []
    for e in findall:
        number_list.append(int(e[36:-2]))
    print(number_list)
    window.append_info(number_list)
    test_id = re.findall(r'data-val-testid="\d*"', text)[0][17:-1]
    print(test_id)
    window.append_info(test_id)
    return number_list, test_id


def submit(cookie, id):
    url = 'https://zjcai.com/GoTest/FinishTestOne'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    data = {'id': id}
    post = requests.post(url=url, cookies=cookie, headers=headers, data=data)
    json = post.json()
    print(json)
    window.append_info(json)
    print("提交成功")
    window.append_info("提交成功")


def main_handle(url, username, password, thread_num=5):
    cookie = login(username, password)
    l, id = get_list(url, cookie)
    sol: list[Solution] = []
    for i in range(thread_num):
        solution = Solution(i, l, cookie, thread_num)
        sol.append(solution)
        solution.start()
    for e in sol:
        e.join()
    submit(cookie, id)


class Solution(threading.Thread):
    def __init__(self, i, l, cookie, count):
        super().__init__()
        self.i = i
        self.l = l
        self.cookie = cookie
        self.count = count

    def run(self):
        num = self.i
        while num < len(self.l):
            try:
                answer = self.verify_answer(self.l[num], self.cookie, num + 1)
                self.save_answer(self.l[num], self.cookie, answer, num + 1)
                num += self.count
            except Exception as e:
                err1 = f"{num}题报错{e}"
                print(err1)
                window.append_info(err1)
                err2 = f"{num}题重试"
                print(err2)
                window.append_info(err2)

    def save_answer(self, i, cookie, answer, count, p=True):
        url = "https://zjcai.com/GoTest/SaveQuestionOne"
        data = {
            "id": i,
            "tail": int(time.time() * 1000),
            'answer': str(answer),
            'answerext': '',
            'qinfo:': ''
        }
        json = requests.post(url=url, data=data, cookies=cookie).json()
        if p:
            dataInfo = f"第{count}题 {data}"
            print(dataInfo)
            window.append_info(dataInfo)
            jsonInfo = f"第{count}题 {json}"
            print(jsonInfo)
            window.append_info(jsonInfo)

    def verify_answer(self, i, cookie, count):
        url = f"https://zjcai.com/GoTest/JudgeQuestionOne1/{i}"
        while True:
            text = requests.get(url=url, cookies=cookie).text
            if len(re.findall('阅卷没有成功', text)) > 0:
                self.save_answer(i, cookie, [], count, False)
                time.sleep(1)
                continue
            findall = re.findall("<pre>.*</pre>", text)
            answer_list = []
            for e in findall:
                if not str(e[5:-6]).__eq__(""):
                    answer = e[5:-6]
                    if answer.__contains__("|||"):
                        answer = answer.replace("|||", "\n")
                        answer = answer.split("\n")[0]
                    answer_list.append(answer)
            listInfo = f"第{count}题 {answer_list}"
            print(listInfo)
            window.append_info(listInfo)
            return answer_list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainLayout()
    window.show()
    sys.exit(app.exec_())
