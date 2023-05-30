import discord
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from typing import Optional
import random
import cogs.GameCog as GameCog
import asyncio
import re

description = '''テスト用botです'''

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
dad = now.date().strftime('%Y/%m/%d')
#ハッキング用グローバル変数
Play_TF = False
Target_IP = 0
Now_IP = 0
My_IP = 0
porttemp = 0
Term_lock = True
Task = False

intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = commands.Bot(command_prefix='?', description=description, intents=intents)

PortList = {0:"\nPort#: 80 - HTTP WebServer", 1:"\nPort#: 25 - SMTP MailServer", 2:"\nPort#: 21 - FTP Server", 3:"\nPort#: 22 - SSH"}
ToolPort = {"SSHCrack":"22", "WebServerWorm":"80", "FTPBounce":"21", "SMTPoverflow":"25"}
HNuser = {"blank": 999}
IPlist = []
TermList = {0:"MegaCorp Asset Server@", 1:"Coel Gateway@", 2:"Fisher Laptop@"}
Dir = {"Default":":home\n:log\n:bin\n:sys"}
ToolList = ["SSHCrack", "WebServerWorm", "FTPBounce", "SMTPoverflow"]
#タスク目標用
Target_file = []


#ここからクラス===================
class Node:
    def OpenPort(num):
        random.sample(range(5), num)
    
    @staticmethod
    def target_file():
        pass

class TimerIsActive(Exception):
    pass 

class TimerManger:
    _timer: Optional[asyncio.Task] = None #現在動いているタイマー(noneは動いていない)

    @staticmethod
    def _timer_reset(task):
        TimerManger._timer = None #タイマーを消去

    @staticmethod
    async def timer_start(second: int):
        if TimerManger.is_active():
            raise TimerIsActive("タイマーはすでに動作中")
        TimerManger._timer = asyncio.create_task(asyncio.sleep(second))
        TimerManger._timer.add_done_callback(TimerManger._timer_reset)
        await TimerManger._timer #タイマーが終わるのを待つ
    
    @staticmethod
    def is_active():
        return TimerManger._timer is not None
#ここまでクラス===================

@bot.event
async def on_ready():
    print('-----')
    print(bot.user.name)
    print(bot.user.id)
    print('-----')

@tasks.loop(seconds=10)
async def taskcheck():
    global Target_file, Task
    if Dir[Target_IP] in Target_file:
        pass
    else:
        Task = True

@bot.command()
async def WorkStart(ctx, name: str):
    global Play_TF, Target_IP, My_IP, Now_IP, IPlist, Target_file
    if Play_TF == True:
        await ctx.send("現在他の方がプレイ中です。")
    else:
        await ctx.send("> 端末を起動します。\n注意：これはデモミッションです。?NetHelpでコマンド一覧が確認できます。")
        Play_TF = True
        Target_IP = str(random.randrange(199)) + "." + str(random.randrange(199)) + "." + str(random.randrange(199)) + "." + str(random.randrange(199))
        My_IP = str(random.randrange(199)) + "." + str(random.randrange(199)) + "." + str(random.randrange(199)) + "." + str(random.randrange(199))
        IPlist += [Target_IP, My_IP]
        Dir[My_IP] = ":home\n:log\n:bin\n:sys"
        Dir[Target_IP] = ":home\n:log\n:bin\n:sys\n:T_Virus.aes\n:CT_log19200804.aes"
        Target_file = ["CT_log19200804.aes", "T_Virus.aes"]
        print(Dir)
        Now_IP = My_IP
        taskcheck.start()
        await asyncio.sleep(3)
        await ctx.send("```------------------\n" + "ようこそ、" + name + "様。現在のIPは" + My_IP + "です。" + "\n>>一件のメールが届いています。```")
        await ctx.send("```<bit>\n" + "件名：仕事の依頼" + "\nやあ、" + name + "。Entropyから君へ依頼だ。\n\nあるハッカーが製薬企業から開発中の新薬の情報を盗み出した。\
    \nそいつは素人だったんだが、ちょうど会社のセキュリティソフトにゼロデイ脆弱性が存在し、そこを突いたらしい。\n\n会社は内密に、我々に盗まれたデータの削除を依頼してきた。\
        \n\n君の仕事は単純、そいつの端末にハッキングして、データを削除してもらえればいい。IPは " + Target_IP + " だ。よろしく頼む。```")
        await TimerManger.timer_start(300)
        if Play_TF == True:
            await ctx.send("残念、時間切れです。端末を強制終了します。")
            Play_TF = False
            taskcheck.cancel()
        else:
            pass

@bot.command()
async def connect(ctx, msg: str):
    global Now_IP
    if Play_TF == True:
        if msg in IPlist:
            await ctx.send("> Scanning For " + msg)
            await asyncio.sleep(5)
            await ctx.send("> Connection Established ::")
            await ctx.send("> Connected To " + TermList[2] + msg)
            Now_IP = msg
        else:
            await ctx.send("> Error: Node Not Found")
    else:
        await ctx.send("現在起動中の端末はありません。")


@bot.command()
async def probe(ctx):
    global Now_IP
    if Play_TF == True:
        await ctx.send("> Probing " + Now_IP)
        await asyncio.sleep(3)
        await ctx.send("\n-----------------------" +
                        "\nProbe Complete - Open Ports" +
                        "\n-----------------------" +
                        PortList[0] + PortList[1] + PortList[2] + PortList[3] +
                        "\n-----------------------" +
                        "\nOpen Ports Required for Crack : " +
                        "2")
    else:
        await ctx.send("現在起動中の端末はありません。")      

@bot.command()
async def report(ctx):
    global Task, Play_TF
    if Play_TF == True:
        await ctx.send("> 目標達成をクライアントに報告します。")
        if Task == True:
            await ctx.send("> 目標を達成しました。報酬が振り込まれます。")
        else:
            await ctx.send("> 目標は未達成です。端末を終了します。")
        Play_TF = False
        taskcheck.cancel()
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def exit(ctx):
    global Play_TF
    if Play_TF == True:
        Play_TF = False
        await ctx.send("> 端末をシャットダウンします。")
        taskcheck.cancel()
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def ls(ctx):
    if Play_TF == True:
        global Now_IP
        dirLoc = Dir[Now_IP]
        await ctx.send(str(dirLoc))
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def rm(ctx, delet: str):
    if Play_TF == True:
        if Term_lock == False:
            global Now_IP
            delet_T = "\n" + delet
            Now_dir = (Dir[Now_IP]).replace(delet_T,"")
            Dir[Now_IP] = Now_dir
            await ctx.send("> Deleting File...")
            await asyncio.sleep(3)
            await ctx.send((Dir[Now_IP]))
        else:
            await ctx.send("> Access Denied")
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def exe(ctx, tool: str, port: str):
    global porttemp
    if Play_TF == True:
        if tool in ToolList:
            if port == ToolPort[tool]:
                await ctx.send("> Tool Running...")
                await asyncio.sleep(3)
                await ctx.send("> ---" + tool + " Complete---")
                porttemp += 1
            else:
                await ctx.send("> Port not found")
        else:
            await ctx.send("> Command is not found")
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def porthack(ctx):
    if Play_TF == True:
        global Now_IP, Term_lock
        await ctx.send("> Porthack Initialized -- Running")
        await asyncio.sleep(3)
        await ctx.send("> --Porthack Complete--")
        Term_lock = False
    else:
        await ctx.send("現在起動中の端末はありません。")

@bot.command()
async def NetHelp(ctx):
    text = "```?WorkStart [任意名] - ゲームを開始します```\
            ```\n?ls - 現在のディレクトリ内容を表示```\
            ```\n?connect [ip] - 目標のノードに接続します```\
            ```\n?exe [ツール名] [引数] - ツールを起動します```\
            ```\n?cat - ファイルを開きます```\
            ```\n?probe - 対象端末のポートを確認します```\
            ```\n?porthack - 侵入したポートを利用して接続先をクラックします```\
            ```\n?rm [対象]- 対象を削除する```\
            ```\n?report - 依頼を終了します```"
    
    embed=discord.Embed(description=text, color=0xfdc700)
    await ctx.send(embed=embed)

bot.run('MTA3MjEwODcxNDAxNTg3MTAzNw.G6Tqbr.OQkLB7Gsm7VOohETEzBKGNq7OdmRDfaoTVfJmY')