import asyncio
import datetime
import re
import urllib.request
from bs4 import BeautifulSoup
import discord
from setting import token


def list_to_str(list, option=""):
    str = ""
    for i in list:
        str += i + option
    return str


def _time(when="now"):
    KST = datetime.timedelta(hours=9)
    if when == "now":
        date_time = str(datetime.datetime.now() + KST)
    elif when == "next":
        date_time = str(datetime.datetime.now() + datetime.timedelta(hours=6) + KST)
    time = {
        "year": date_time[:4],
        "month": date_time[5:7],
        "day": date_time[8:10],
        "time": int(date_time[11:13]) * 60 + int(date_time[14:16]),
        "ymd": date_time[:10],
    }
    return time


def crawling_split(time, re_pattern):
    # def crawling(time):
    url = f"https://stu.gen.go.kr/sts_sci_md00_001.do?schulCode=F100000120&schulCrseScCode=4&schulKndScCode=04&ay={time['year']}&mm={time['month']}"
    page = urllib.request.urlopen(url).read().decode("utf-8")
    soup = BeautifulSoup(page, "html.parser")
    items = soup.select("#contents > div > table > tbody > tr > td > div")
    # return items

    # def split(time, items, re_pattern):
    menu = {}
    for i in items:
        str_i = str(i)
        if str_i.startswith("<div>" + time["day"] + "<"):  # <div>31< 식으로 날짜 구분
            i_list = re_pattern["amp;"].findall(      # 치킨&맥주 와 같이 한 음식이 치킨&amp;맥주 로 표기되어서 amp;삭제
                str_i
            )
            l_t_s = list_to_str(i_list)
            lts_split = l_t_s.split("[")  # [조식]뭐뭐[석식]뭐뭐 식으로 구별되어있는 것을 나눔
            del lts_split[0]  # [조식] 전의 필요 없는 첫 문자 제거
            menu["breakfast"] = "없음"
            menu["lunch"] = "없음"
            menu["dinner"] = "없음"
            for j in lts_split:
                if j[:2] == "조식":
                    menu["breakfast"] = re_pattern["korean"].findall(j[2:])
                elif j[:2] == "중식":
                    menu["lunch"] = re_pattern["korean"].findall(j[2:])
                elif j[:2] == "석식":
                    menu["dinner"] = re_pattern["korean"].findall(j[2:])
            break
    return menu


class SMBot(discord.Client):
    def __init__(self):
        super().__init__()

    def basic_setting(self):
        self.re_pattern = {
            "amp;": re.compile("[^amp;]+"),
            "korean": re.compile("[가-힣\s]*[&]?[,]?[가-힣\s]*[&]?[,]?[(]?[가-힣\s]+[)]?"),
        }
        self.endtime = {
            "breakfast": (8) * 60 + 0,
            "lunch": (12 + 1) * 60 + 0,
            "dinner": (12 + 7) * 60 + 0,
        }
        self.time = {  # 현재 크롤링 되어있는 메뉴의 날짜
            "year": "2020",
            "month": "01",
            "day": "01",
            "time": int("23") * 60 + int("59"),
            "ymd": "2019-11-26",
        }
        self.time = _time()
        self.menu = {
            "breakfast": ["밥", "곰탕"],
            "lunch": ["떡볶이", "순대"],
            "dinner": ["치킨&맥주", "파인애플"],
        }
        self.menu = crawling_split(self.time, self.re_pattern)

    async def on_ready(self):
        self.basic_setting()
        game = "일"
        await self.change_presence(
            status=discord.Status.online, activity=discord.Game(game)
        )
        print(self.user.name, self.user.id)

    async def on_message(self, message):
        self.content = ""
        self.embed = discord.Embed()
        if "급식" in message.content and not message.author.bot:
            menu = self.what_time()
            report = list_to_str(menu, "\n")
            self.embed_setting(report, message.author)
            await message.channel.send(content=self.content, embed=self.embed)

    def what_time(self):
        now_time = _time()
        if now_time["time"] >= self.endtime["dinner"]:  # 저녁식사 이후면 크롤링할 정보는 다음날의 정보
            now_time = _time("next")
        if self.time["ymd"] != now_time["ymd"]:  # 당일 첫 크롤링
            self.menu = crawling_split(now_time, self.re_pattern)
        self.time = now_time
        if self.time["time"] < self.endtime["breakfast"]:
            menu = self.menu["breakfast"]
            self.mealtime = "아침"
        elif self.time["time"] < self.endtime["lunch"]:
            menu = self.menu["lunch"]
            self.mealtime = "점심"
        elif self.time["time"] < self.endtime["dinner"]:
            menu = self.menu["dinner"]
            self.mealtime = "저녁"
        else:  # self.time['time'] >= self.endtime['dinner']:
            menu = self.menu["breakfast"]
            self.mealtime = "아침"
        return menu

    def embed_setting(self, menu, author):
        self.embed = discord.Embed(
            title=self.mealtime,
            colour=discord.Colour(0x44B34E),
            description=menu,
            timestamp=datetime.datetime.now(),
        )
        self.embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/645939779665657866/648692896744210433/9k.png"
        )
        self.embed.set_author(name=author, icon_url=author.avatar_url)
        self.embed.set_footer(
            text="남진명",
            icon_url="https://cdn.discordapp.com/attachments/645939779665657866/648692002384248843/54a94f8f98bd7264.png",
        )


bot = SMBot()
bot.run(token)
