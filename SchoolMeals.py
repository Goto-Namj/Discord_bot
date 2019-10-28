import discord
import asyncio
from urllib.request import urlopen
from bs4 import BeautifulSoup

client = discord.Client()

token = "NjM4MTY4NTY1Nzk0NjAzMDE5.XbZuOQ.dSdKmI3Mzu9tlyTiZsE7fSTwmyI"

ch = 0
def sl(a):
    global ch
    for i in range(128):
        if ord(a) == 38:
            if ch == 0:
                ch = 1
                return ''
            return a
        if ord(a) == i:
            return ''
    return a

@client.event
async def on_ready():
    print("이거이거 : ", client.user.name, client.user.id)
    game ="크롤링"
    await client.change_presence(status=discord.Status.online, activity=discord.Game(game))

@client.event
async def on_message(message):
    if '급식' in message.content:
        html = urlopen("http://www.gsm.hs.kr/main/main.php")  
        bsObject = BeautifulSoup(html, "html.parser")
        l,iff,c,li = map(sl,str(bsObject.dd)),0,0,['']
        global ch
        ch = 0
        tmp = 0
        for i in l:
            if i != '':
                tmp = 0
                if i == '&':
                    tmp = 1
                iff = 1
                li[c] += i
            elif iff == 1 and tmp == 0:
                li.append('')
                iff=0
                c+=1
                tmp = 0
    
        result = ''
        for i in li:
            if i == '에너지':
                break
            result += i+'\n'

        channel = message.channel
        await channel.send("```"+result+"```")


    # if message.content == "!ping":
    #     channel = message.channel
    #     await channel.send('pong')

client.run(token)