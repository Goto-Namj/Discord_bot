import discord
import asyncio
import setting
import datetime
import requests
from bs4 import BeautifulSoup
import re


token = setting.token

def nowtime():
    dt = str(datetime.datetime.now())
    time = {
        'year': dt[:4],
        'month': dt[5:7],
        'day': dt[8:10],
        'time': int(dt[11:13]) * 60 + int(dt[14:16]),
        'ymd': dt[:10]
    }
    return time

def nexttime():
    next_time = datetime.datetime.now() + datetime.timedelta(days = 1) 
    dt = str(next_time)
    time = {
        'year': dt[:4],
        'month': dt[5:7],
        'day': dt[8:10],
        'time': int(dt[11:13]) * 60 + int(dt[14:16]),
        'ymd': dt[:10]
    }
    return time

def crawling_split(time, re_pattern, amp_pattern):
    # def crawling(time, re_pattern):
    url = f"https://stu.gen.go.kr/sts_sci_md00_001.do?schulCode=F100000120&schulCrseScCode=4&schulKndScCode=04&ay={time['year']}&mm={time['month']}"
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    items = soup.select("#contents > div > table > tbody > tr > td > div")
    #return items

    # def split(time, items):
    menu = {}
    for i in items:
        si = str(i)
        if si.startswith('<div>' + time['day'] + '<'):

            si = amp_pattern.findall(si)
            ri = ''
            for j in si:
                ri+=j
            si = ri.split('[')
            del si[0]
            menu['breakfast'] = re_pattern.findall(si[0][2:])
            menu['lunch'] = re_pattern.findall(si[1][2:])
            menu['dinner'] = re_pattern.findall(si[2][2:])
            break
    return menu


class SMBot(discord.Client):
    async def on_ready(self):
        self.amp_pattern = re.compile("[^amp;]+")
        self.re_pattern = re.compile("[가-힣\s]*&?[가-힣\s]+")
        self.time = nowtime()
        self.menu = crawling_split(self.time, self.re_pattern, self.amp_pattern)
        self.endtime = {
            'breakfast': (  8  )*60+  0,
            'lunch': (12+  1  )*60+  0,
            'dinner': (12+  7  )*60+  0
        }

        game ="일"
        print(self.user.name, self.user.id)
        await self.change_presence(status=discord.Status.online, activity=discord.Game(game))

    async def on_message(self, message):
        if '급식' in message.content and not message.author.bot:
            channel = message.channel
            report = ''
            time = nowtime()

            if self.time['ymd'] != time['ymd']:
                if self.time['time'] >= self.endtime['dinner']:
                    time = nexttime()
                    self.menu = crawling_split(time, self.re_pattern, self.amp_pattern)
                else:
                    self.time = time
                    self.menu = crawling_split(self.time, self.re_pattern, self.amp_pattern)

            if self.time['time'] < self.endtime['breakfast']:
                menu = self.menu['breakfast']
            elif self.time['time'] < self.endtime['lunch']:
                menu = self.menu['lunch']
            elif self.time['time'] < self.endtime['dinner']:
                menu = self.menu['dinner']
            else:#self.time['time'] >= self.endtime['dinner']:
                menu = self.menu['breakfast']
                
            for i in menu:
                report += i+'\n'

            print(message.author, datetime.datetime.now())
            await channel.send("```"+report+"```")

bot = SMBot()
bot.run(token)