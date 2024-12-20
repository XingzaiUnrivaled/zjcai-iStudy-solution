# zjcai-iStudy-solution

www.zjcai.com 网站，iSudy计算机教学实验考试平台作业通解脚本

**仅供学习参考**

![](image/img_1.png)

这个代码使用起来十分简单，只需要把python文件 `zjcai_solution.py` 下载到本地即可

需要先安装[python](https://www.python.org)

需要用到的库只有

* requests(需要安装)
* re(自带)
* time(自带)
* threading(自带)

```bash
pip3 install requests
```

创建本脚本的目的主要是每次都选择非常的麻烦，所以选择使用脚本，本脚本从登录，到多线程答题，到提交全是自动化操作，用户只需要登录。

本脚本针对的只有这个部分

![](image/img_2.png)

![](image/img_3.png)

使用的时候只需要复制下图的链接即可

![](image/img_4.png)

然后在代码中替换到这个位置

![](image/img_5.png)

就即可使用

## GUI(图形化界面) 版本

![](image/img_6.png)

v1.0.2 版本新增

所需新的依赖为pyqt5

```bash
pip install PyQt5
```

已将图形化界面打包成了.exe文件

## 版本更新

v1.0.1

1. 修复了不能答多个空的题目的bug
2. 修复了阅卷不成功的bug

v1.0.2

1. 更新了GUI界面的代码，可以选择要不要GUI
2. 打包成了.exe文件在release里

v1.0.3
1. 修复了前端字符的转译bug
