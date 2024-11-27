import requests
import re
import time
import threading


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
    test_id = re.findall(r'data-val-testid="\d*"', text)[0][17:-1]
    print(test_id)
    return number_list, test_id


def submit(cookie, id):
    url = 'https://zjcai.com/GoTest/FinishTestOne'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    data = {'id': id}
    post = requests.post(url=url, cookies=cookie, headers=headers, data=data)
    print(post.json())


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
        try:
            while num < len(self.l):
                answer = self.verify_answer(self.l[num], self.cookie, num + 1)
                self.save_answer(self.l[num], self.cookie, answer, num + 1)
                num += self.count
        except Exception as e:
            print(f"{num}题重试")

    def save_answer(self, i, cookie, answer, count):
        url = "https://zjcai.com/GoTest/SaveQuestionOne"
        data = {
            "id": i,
            "tail": int(time.time() * 1000),
            'answer': answer,
            'answerext': '',
            'qinfo:': ''
        }
        json = requests.post(url=url, data=data, cookies=cookie).json()
        # print(f"第{count}题 {json}")

    def verify_answer(self, i, cookie, count):
        url = f"https://zjcai.com/GoTest/JudgeQuestionOne1/{i}"
        text = requests.get(url=url, cookies=cookie).text

        answer = str(re.findall("<pre>.*</pre>", text)[0][5:-6])
        if answer.__contains__("|||"):
            answer = answer.replace("|||", "\n")
            answer = answer.split("\n")[0]
        print(f"第{count}题 {answer}")
        return answer


if __name__ == '__main__':
    url = "输入你的url"
    username = input("输入用户名:")
    password = input("输入密码:")
    # url，账号，密码，线程数
    main_handle(url, username, password, 10)
