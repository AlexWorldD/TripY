import requests
from lxml import html

class User():
    def __init__(self, id = '', nickname = '', url = ''):
        self.id = id
        self.nickname = nickname
        self.url = url
        self.hometown = ''
        self.member_since = ''
        self.age = ''
        self.gender = ''

    def collect_main_info(self):
        root = download(self.url)
        if root is not None:
            print('collecting user info:', self.nickname)
            main = check(root, "//div[@id='MODULES_MEMBER_CENTER']")
            if main != '':
                left = check(main, "div[@class='leftProfile']")
                if left != '':
                    prof_info = check(left, "div[1]/div[@class='profInfo']")
                    if prof_info != '':
                        self.hometown = check(prof_info, "div[@class='hometown']/p/text()")
                        self.member_since = check(prof_info, "div[@class='ageSince']/p[1]/text()")

                        info = check(prof_info, "div[@class='ageSince']/p[2]/text()").strip()
                        info = info.split(' ')
                        if len(info) >= 2:
                            self.age = info[0]
                            self.gender = info[-1]
                right = check(main, "div[@class='rigthContributions']")

    def dictify(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'url': self.url,
            'hometown': self.hometown,
            'member since': self.member_since,
            'age': self.age,
            'gender': self.gender
        }

from .crawler import download, check
