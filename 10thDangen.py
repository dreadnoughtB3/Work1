import discord
import random
import openpyxl
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands

#Excel参照
book = openpyxl.load_workbook('excel/10thDangen.xlsx')
event = openpyxl.load_workbook('excel/Event.xlsx')
active_sheet = book.worksheets[0]
floor2 = book.worksheets[1]
floor3 = book.worksheets[2]
floor4 = book.worksheets[3]
event_sheet = event.active

#ダンジョン探索結果参照用
DList = ["B2","B3","B4","B5","B6","B7","B8","B9","B10","B11","B12","B13","B14","B15","B16","B17","B18","B19","B20","B21","B22","B23","B24","B25","B26","B27","B28","B29","B30","B31","ev1","ev2","ev3","stair1","stair2","stair3","stair4","ENY1","ENY2","ENY3","ENY4","ENY5","ENY6"]
Elist = ["B50", "C50", "D50", "E50", "F50"]
BList = ["B51","C51","D51","E51","F51"]
EvntList = {"ev11":{"T":"B2","F":"B3"},"ev12":{"T":"B4","F":"B5"},"ev13":{"T":"B6","F":"B7"},
            "ev21":{"T":"B8","F":"B9"},"ev22":{"T":"B10","F":"B11"},"ev23":{"T":"B12","F":"B13"},
            "ev31":{"T":"B14","F":"B15"},"ev32":{"T":"B16","F":"B17"},"ev33":{"T":"B18","F":"B19"}}
#プレイヤーデータ格納用
ID_manage = {}
player = {}

#ボタン用クラス
class TrueButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "yes", eventCode:str = "001"):
        super().__init__(style=style, label=label, disabled=False)
        self.eventCode = eventCode
        self.dic = EvntList[self.eventCode]["T"]

    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"> {interaction.user.display_name}は{self.label}を選択しました。\n" + (event_sheet[self.dic].value))
        await interaction.message.delete()
        

class FalseButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "no", eventCode:str = "001"):
        super().__init__(style=style, label=label, disabled=False)
        self.eventCode = eventCode
        self.dic = EvntList[self.eventCode]["F"]
        
    async def callback(self, interaction: Interaction):
        await interaction.response.send_message(f"> {interaction.user.display_name}は{self.label}を選択しました。\n" + (event_sheet[self.dic].value))
        await interaction.message.delete()


description = '''ダンジョン管理bot'''
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = commands.Bot(command_prefix='?',  help_command = None, description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user} (ID: {bot.user.id})')
    print("10thDangen.py起動")
    print('------')

@bot.command()
async def fdgtstart(ctx):
    #global active_sheet
    usr_id = int(ctx.author.id)
    if usr_id in ID_manage:
        await ctx.send("> >>あなたは既にダンジョンの内部にいます")
    else:
        ID_manage[usr_id] = 1 #ID管理辞書にUIDと現在階層を追加
        await ctx.send("> 注意: このコマンドを実行した方が進行コマンドを振ってください。")
        player[usr_id] = 1
        #usr_id = DataManage(usr_id)

        await ctx.send("> >>インスタンスが生成されました。")
        dice = random.randrange(6)
        file_E = discord.File(fp="image/Dang_Ent2.jpg",filename="Dang_Ent2.jpg",spoiler=False)
        embed=discord.Embed(title="西方の古代遺跡", description="堕神の地の奥深く、山中に存在する古代の遺跡。\nアールヴ帝国の時代に建設されたと思しきその地下巨大構造物には、無数の秘宝が眠っているという。", color=0xff9300)
        embed.set_image(url=f"attachment://Dang_Ent2.jpg")
        await ctx.send(file=file_E,embed=embed)
        file_E.close
        await ctx.send("**現在地点: 1階層 - 入口**")
        await ctx.send("> 進行状況: 1/10")

#1階層
@bot.command()
async def fdgt11(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            await ctx.send("> 探索限界です。帰還します。")
            del player[usr_id]
            del ID_manage[usr_id]
        elif player[usr_id] < 10 and ID_manage[usr_id] == 2: #もし探索回数が10回未満でかつ、UIDの階層が1以外であれば
            await ctx.send("> あなたは1階層には居ません")
        else:
            await ctx.send("**現在地点: 1階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(2)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((active_sheet[Ecell_name].value) + "\n x" + Enum)
            #階段発見処理
            elif "stair" in cell_name:
                file = discord.File("image/stair.png", filename="stair.png")
                embed=discord.Embed(title="第一階層: 地下への道",
                                    description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                    color=0x6E6636)
                embed.set_image(url="attachment://stair.png")
                await ctx.send(file=file,embed=embed)
                file.close()
                ID_manage[usr_id] = 2 #現在階層を2層に設定
                player[usr_id] = 1 #進捗状況をリセット
            #イベント処理
            elif cell_name == "ev1":
                await event_001(ctx)
            elif cell_name == "ev2":
                await event_002(ctx)
            elif cell_name == "ev3":
                await event_003(ctx)
            else:
                await ctx.send((active_sheet[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#2階層
@bot.command()
async def fdgt12(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            await ctx.send("> 探索限界です。帰還します。")
            del player[usr_id]
            del ID_manage[usr_id]
        elif player[usr_id] < 10 and ID_manage[usr_id] == 1: #もし探索回数が10回未満でかつ、UIDの階層が2以外であれば
            await ctx.send("> あなたは2階層には居ません")
        else:
            await ctx.send("**現在地点: 2階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(3)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor2[Ecell_name].value) + "\n x" + Enum)
            #階段発見処理
            elif "stair" in cell_name:
                file = discord.File("image/stair2.png", filename="stair2.png")
                embed=discord.Embed(title="第二階層: 地下への道",
                                    description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                    color=0x6E6636)
                embed.set_image(url="attachment://stair2.png")
                await ctx.send(file=file,embed=embed)
                file.close()
                ID_manage[usr_id] = 3 #現在階層を3層に設定
                player[usr_id] = 1 #進捗状況をリセット
            #イベント処理
            elif cell_name == "ev1":
                await event_011(ctx)
            elif cell_name == "ev2":
                await event_012(ctx)
            elif cell_name == "ev3":
                await event_013(ctx)
            else:
                await ctx.send((floor2[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#3階層
@bot.command()
async def fdgt13(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 10: #もし探索回数が10回なら
            await ctx.send("> 探索限界です。帰還します。")
            del player[usr_id]
            del ID_manage[usr_id]
        elif player[usr_id] < 10 and ID_manage[usr_id] == 1: #もし探索回数が10回未満でかつ、UIDの階層が3以外であれば
            await ctx.send("> あなたは3階層には居ません")
        else:
            await ctx.send("**現在地点: 3階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/10")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(4)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor3[Ecell_name].value) + "\n x" + Enum)
            #ボス発見処理
            elif "stair" in cell_name:
                Bcell = random.choice(BList) #ボスランダム選択
                file = discord.File("image/FLOOR3BOSS.png", filename="FLOOR3BOSS.png")
                embedB=discord.Embed(title="> フロアボス",description=(floor3[Bcell].value),color=0x6E6636)
                embed=discord.Embed(title="第三階層: フロアの主",
                                    description="地下へと続く階段を発見したが、階段を守る存在に行く手を塞がれた。\n次の階層に進む為には、この守護者を倒さなければならない。",
                                    color=0x6E6636)
                embed.set_image(url="attachment://FLOOR3BOSS.png")
                await ctx.send(file=file,embed=embed)
                await ctx.send(embed=embedB)
                file.close()
                ID_manage[usr_id] = 4 #現在階層を4層に設定
                player[usr_id] = 1 #進捗状況をリセット
            #イベント処理
            elif cell_name == "ev1":
                await event_001(ctx)
            elif cell_name == "ev2":
                await event_002(ctx)
            elif cell_name == "ev3":
                await event_002(ctx)
            else:
                await ctx.send((floor3[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")
   

#4階層
@bot.command()
async def fdgt14(ctx):
    usr_id = (ctx.author.id)
    if usr_id in ID_manage: #もしUIDが登録されていれば
        if player[usr_id] >= 15: #もし探索回数が15回なら
            await ctx.send("> 探索限界です。帰還します。")
            del player[usr_id]
            del ID_manage[usr_id]
        elif player[usr_id] < 10 and ID_manage[usr_id] == 1: #もし探索回数が10回未満でかつ、UIDの階層が3以外であれば
            await ctx.send("> あなたは4階層には居ません")
        else:
            await ctx.send("**現在地点: 4階層**")
            player[usr_id] += 1 #進捗状況をインクリメント
            await ctx.send("> 進行状況: " + str(player[usr_id]) + "/15")
            cell_name = random.choice(DList)
            print(cell_name)
            #接敵時処理
            if "ENY" in cell_name:
                Ecell_name = random.choice(Elist)
                Enum = str(random.randrange(4)+1)    
                await ctx.send("> **敵だ！**")             
                await ctx.send((floor4[Ecell_name].value) + "\n x" + Enum)
            #ボス発見処理
            elif "stair" in cell_name:
                file = discord.File("image/stair4.jpg", filename="stair04.jpg")
                embed=discord.Embed(title="第四階層: 地下への階段",
                                    description="地下へと続く階段を発見した。\n次の階層に進まなくてはならない。",
                                    color=0x6E6636)
                embed.set_image(url="attachment://stair04.jpg")
                await ctx.send(file=file,embed=embed)
                file.close()
                ID_manage[usr_id] = 5 #現在階層を4層に設定
                player[usr_id] = 1 #進捗状況をリセット
            #イベント処理
            elif cell_name == "ev1":
                await event_001(ctx)
            elif cell_name == "ev2":
                await event_002(ctx)
            elif cell_name == "ev3":
                await event_002(ctx)
            else:
                await ctx.send((floor4[cell_name].value))
    else:   
        await ctx.send("> あなたはまだダンジョンに入っていません")

#第一階層イベント
async def event_001(ctx):
    file = discord.File("image/event.png", filename="event.png")
    embed=discord.Embed(title="第一階層: 不可思議な物音",
                        description="ダンジョンを進んでいたあなたは、突然開けた空間に出た。\n地下だというのに、窓からは日光のような光が差し込んでいる。\nそうしているうち、どこからか奇妙な音が聞こえることにあなたは気が付いた。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<確認しに行く>",eventCode="ev11"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev11"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_002(ctx):
    file = discord.File("image/event_2.png", filename="event_2.png")
    embed=discord.Embed(title="第一階層: 奇妙な臭気",
                        description="通路を進んでいると、奇妙な臭気が立ち込める部屋を発見した。\n悪臭とまでは言えないが、なんとなく鼻につくような臭いだ。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_2.png")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev12"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<正体を確かめる>",eventCode="ev12"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_003(ctx):
    file = discord.File("image/event_3.jpg", filename="event_3.jpg")
    embed=discord.Embed(title="第一階層: 奇妙な光",
                        description="ダンジョンを進んでいると、崩落した壁の瓦礫の下で何かが光っているのを見つけた。\nかなり奥の方にあるようだが、退けられるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_3.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev13"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<瓦礫を退ける(スタミナ-2)>",eventCode="ev13"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#第二階層イベント
async def event_011(ctx):
    file = discord.File("image/event_11.jpg", filename="event_11.jpg")
    embed=discord.Embed(title="第二階層: 分岐路",
                        description="ダンジョンを進んでいると、途中で道が二方向に分かれている場所に出くわした。\nどちらの通路に進むべきだろうか？",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_11.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<右の道を進む>",eventCode="ev21"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<左の道を進む>",eventCode="ev21"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_012(ctx):
    file = discord.File("image/event_3.jpg", filename="event_3.jpg")
    embed=discord.Embed(title="第二階層: 歪んだ扉",
                        description="ダンジョンを進んでいると、歪んで開かなくなった扉を見つけた。\nその先は暗いが、何か良いものがあるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_3.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<無視する>",eventCode="ev22"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<扉をこじ開ける(スタミナ-2)>",eventCode="ev22"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

async def event_013(ctx):
    file = discord.File("image/event_13.jpg", filename="event_13.jpg")
    embed=discord.Embed(title="第二階層: 展示室",
                        description="開けた空間に出た。損壊もあまり激しくないようで、魔導灯が室内を照らしている。\n室内にはいくつかのガラスケースがあり、その中の二つはまだ中に何かが置かれているようだ。\nケースを割れば取り出せるかもしれない。",
                        color=0x6E6636)         
    embed.set_image(url="attachment://event_13.jpg")    
    view = discord.ui.View()  
    view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="<大きなケースを割る>",eventCode="ev23"))
    view.add_item(FalseButton(style=discord.ButtonStyle.primary,label="<小さなケースを割る>",eventCode="ev23"))
    await ctx.send(file=file,embed=embed)
    await ctx.send(view=view)
    file.close()

#汎用コマンド
@bot.command()
async def escape(ctx):
    usr_id = ctx.author.id
    if usr_id in ID_manage:
        await ctx.send("> ダンジョンから脱出します")
        del player[usr_id]
        del ID_manage[usr_id]
    else:
        await ctx.send("> あなたはまだダンジョンに入っていません")

#@bot.command()
#async def purge(ctx):
#    channel = ctx.message.channel
#    deleted = await channel.purge(limit=1000,check = is_me,bulk=False)
#    await channel.send(f'Deleted {len(deleted)} message(s)')

bot.run("MTA3MjEwODcxNDAxNTg3MTAzNw.G6Tqbr.OQkLB7Gsm7VOohETEzBKGNq7OdmRDfaoTVfJmY")