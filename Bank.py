import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio
import openpyxl
import random
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

#スプレッドシート関連
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
json = 'strl-380010-d9b3efdea4a1.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1vXe0TvwhgoOypM4xGF-fkQPYSNaLwTJVN06LmonCfoA'
workbook = gc.open_by_key(SPREADSHEET_KEY)
worksheet = workbook.worksheet("ID管理")
products = workbook.worksheet("ブラックマーケット商品")
products_data = workbook.worksheet("ブラックマーケット商品データ")
medal = workbook.worksheet("白勲章交換")
medal_data = workbook.worksheet("白勲章データ")

#Excel参照
book = openpyxl.load_workbook('excel/BANK.xlsx')
ID_sheet = book.worksheets[0]
BANK_HEIST = book.worksheets[1]
ART_GALLERY = book.worksheets[2]
GO_BANK = book.worksheets[3]
JEWERLY_STORE = book.worksheets[4]
THE_BIG_BANK = book.worksheets[5]

UseCN = False
Bank_TF = False
selected_mission = 0
phase = 0
valt = {0:{"num":1,"gold":2501},1:{"num":2,"gold":1875},2:{"num":1,"gold":3750},3:{"num":5,"gold":875},4:{"num":2,"gold":3125}}
missions = ["BANK HEIST","ART GALLERY","GO BANK","JEWELRY STORE","THE BIG BANK"]
User = []
Menu_User = {} #メニューページをユーザーごとに管理する用の辞書

#excelからローグIDを取得
for i in range(2,10):
    ids = str(ID_sheet.cell(row=i, column=1).value)
    User.append(ids)

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
dad = now.date().strftime('%Y/%m/%d')
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

description = '''テスト用botです'''
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?',  help_command = None, description=description, intents=intents)

#クラス
class TrueButton(discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, label:str = "yes",now_ctx):
        super().__init__(style=style, label=label, disabled=False)
        self.ctx = now_ctx

    async def callback(self, interaction: Interaction):
        global selected_mission,Bank_TF
        Bank_TF = True
        await interaction.response.send_message("依頼を受諾しました: " + missions[selected_mission])
        await interaction.message.delete()
        await loading(self.ctx)

class ControlButton(discord.ui.View,discord.ui.Button):
    def __init__(self, *, style: ButtonStyle = ButtonStyle.secondary, disabled,label:str = "default",now_ctx,embed,contents,uid,page):
        discord.ui.Button.__init__(self,style=style, label=label, disabled=disabled)
        Menu_User[uid] = 1 #インスタンス生成時、ユーザーIDで辞書を作成
        self.ctx = now_ctx
        self.label = label
        self.embed = embed
        self.contents = contents
        self.uid = uid
        self.pages = page

    async def callback(self, interaction: Interaction): #ボタンが押された時に呼び出される関数
        if self.label == "切断": #そのボタン（インスタンス）のラベルが切断であれば
            await interaction.message.delete()
            await self.embed.delete()
            del Menu_User[self.uid] #メニューを使用中のユーザー一覧から現在のユーザーを削除
        #そのボタン（インスタンス）のラベルが>であり、ページ数と現在ページが一致しなければ
        elif self.label == ">" and Menu_User[self.uid] != self.pages: 
            Menu_User[self.uid] += 1
            await self.embed.edit(embed=self.contents[Menu_User[self.uid] -1])
            await interaction.response.defer()
            print(Menu_User[self.uid])
        elif self.label == "<" and Menu_User[self.uid] > 1:
            Menu_User[self.uid] -=1
            await self.embed.edit(embed=self.contents[Menu_User[self.uid] -1])
            await interaction.response.defer()
            print(Menu_User[self.uid])
        elif self.label == ">>":
            Menu_User[self.uid] = self.pages
            await self.embed.edit(embed=self.contents[Menu_User[self.uid] -1])
            await interaction.response.defer()
            print(Menu_User[self.uid])
        elif self.label == "<<":
            Menu_User[self.uid] = 1
            await self.embed.edit(embed=self.contents[Menu_User[self.uid] -1])
            await interaction.response.defer()
            print(Menu_User[self.uid])
        else:
            await interaction.response.defer()
    async def on_timeout(self):
        print("timeout")

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user} (ID: {bot.user.id})')
    print(now)
    print("Bank.py")
    print('------')

@bot.command()
async def BlackMarket(ctx):
    df = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])
    df2 = pd.DataFrame(products.get_all_values()[1:],columns=products.get_all_values()[0])
    dfa=df.set_index("ユーザーID")
    dfa2=df2.set_index("ID")
    usr_id = str(ctx.author.id)

    if usr_id in str(df["ユーザーID"]):
        await ctx.send("`> Launching Rorg Browser...`")
        prog = await ctx.send("`[Starting...]`")        
        await asyncio.sleep(0.5)
        await prog.edit(content="`[Connecting to a Rorg relay...]`")
        await asyncio.sleep(1.7)
        await prog.edit(content="`[Negotiating to a Rorg relay...]`")
        await asyncio.sleep(2)
        await prog.edit(content="`[Establishing an encrypted directry connection...]`")
        await asyncio.sleep(1.5)
        await prog.edit(content="`[Retrieving network status...]`")
        await asyncio.sleep(1.5)
        await prog.edit(content="`[Loading network status...]`")
        await asyncio.sleep(0.8)
        await prog.edit(content="`[Connected to a Rorg network!]`")
        #メインメニュー
        embed_title=discord.Embed(title=">𝚆𝚎𝚕𝚌𝚘𝚖𝚎 𝚝𝚘 𝚆𝚘𝚘𝚕𝚁𝚘𝚊𝚍.𝚗𝚘𝚛！",
                            description="```ローグ専用の非合法取引ウェブサイト、ウールロードへようこそ！\n何をお求めでしょうか？```",
                            color=0x6E6636) 
        embed_title.add_field(name="`Connected User:`", value=dfa.at[usr_id,"ユーザー名"], inline=True)
        embed_title.add_field(name="`User Rogue Coin:`", value=dfa.at[usr_id,"コイン数"], inline=True)
        embed_title.set_thumbnail(url="https://cdn.discordapp.com/attachments/1081260969256296528/1082058150124994661/silkroad.png")
        await asyncio.sleep(3)
        menu = await ctx.send(embed=embed_title)

        #フォーマット化リスト
        formated_wep = ""
        for i in range(1,5):
            formated_wep += (dfa2.at[str(i),"武器"]) + "\n"
        formated_SG = ""
        for i in range(1,7):
            formated_SG += (dfa2.at[str(i),"アイテム"]) + "\n"
        formated_LMG = ""
        for i in range(1,3):
            formated_LMG += (dfa2.at[str(i),"兵器"]) + "\n"
        formated_SR = ""
        for i in range(1,3):
            formated_SR += (dfa2.at[str(i),"車両"]) + "\n"

        #menu
        embed_menu=discord.Embed(title=">𝙿𝚛𝚘𝚍𝚞𝚌𝚝𝚜: Menu",
                            description="```製品一覧をお選びください。\n -武器\n -アイテム\n -兵器\n -車両```",
                            color=0x6E6636) 
        embed_menu.set_footer(text="WoolRoad.nor/Menu")

        #AR
        embed_gun=discord.Embed(title=">𝙿𝚛𝚘𝚍𝚞𝚌𝚝𝚜: 𝚆𝚎𝚊𝚙𝚘𝚗s(1/4)",
                            description="**武器**",
                            color=0x6E6636)
        embed_gun.add_field(name="`List:`", value=formated_wep, inline=True)
        embed_gun.set_footer(text="WoolRoad.nor/Weapon")

        #SG
        embed_shotgun=discord.Embed(title=">𝙿𝚛𝚘𝚍𝚞𝚌𝚝𝚜: Items(2/4)",
                            description="**アイテム**",
                            color=0x6E6636) 
        embed_shotgun.add_field(name="`List:`", value=formated_SG, inline=True)
        embed_shotgun.set_footer(text="WoolRoad.nor/Item")

        #LMG
        embed_LMG=discord.Embed(title=">𝙿𝚛𝚘𝚍𝚞𝚌𝚝𝚜: Armored(3/4)",
                            description="**兵器**",
                            color=0x6E6636) 
        embed_LMG.add_field(name="`List:`", value=formated_LMG, inline=True)
        embed_LMG.set_footer(text="WoolRoad.nor/Armored")

        #SR
        embed_SR=discord.Embed(title=">𝙿𝚛𝚘𝚍𝚞𝚌𝚝𝚜: Vehicles(4/4)",
                            description="**車両**",
                            color=0x6E6636) 
        embed_SR.add_field(name="`List:`", value=formated_SR, inline=True)
        embed_SR.set_footer(text="WoolRoad.nor/Weapon/Vehicles")

        content = [embed_menu,embed_gun,embed_shotgun,embed_LMG,embed_SR]
        menu = await ctx.send(embed=embed_menu)
        view = discord.ui.View(timeout=None)  
        view.add_item(ControlButton(style=discord.ButtonStyle.primary,disabled=False,label="<<",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=5))
        view.add_item(ControlButton(style=discord.ButtonStyle.success,disabled=False,label="<",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=5))
        view.add_item(ControlButton(style=discord.ButtonStyle.danger,disabled=False,label="切断",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=5))
        view.add_item(ControlButton(style=discord.ButtonStyle.success,disabled=False,label=">",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=5))
        view.add_item(ControlButton(style=discord.ButtonStyle.primary,disabled=False,label=">>",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=5))
        await ctx.send(view=view)
    else:
        await ctx.send("`> あなたにはアクセス権がありません。`")

@bot.command()
async def knight(ctx):
    usr_id = str(ctx.author.id)
    df = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])
    dfa = df.set_index("ホワイトユーザーID")
    df1 = pd.DataFrame(medal.get_all_values()[1:],columns=medal.get_all_values()[0])
    df1a = df1.set_index("ID")
    if usr_id in str(df["ホワイトユーザーID"]):
        #メインメニュー
        embed_title=discord.Embed(title="〈White Knight Equipment Shop〉",
                            description="```ホワイトナイト専用の装備品購入サイトへようこそ。\nあなたの日々の貢献に感謝します。```",
                            color=0xFFFFFF) 
        embed_title.add_field(name="`NAME:`", value=dfa.at[usr_id,"ホワイトユーザー名"], inline=True)
        embed_title.add_field(name="`MEDAL:`", value=dfa.at[usr_id,"勲章数"], inline=True)
        embed_title.set_author(name="ホワイトナイト統合監督委員会")
        embed_title.set_footer(text=f"Made by まよなか | {daytime}")

        #フォーマット化リスト
        formated_weapon = ""
        for i in range(1,5):
            formated_weapon += (df1a.at[str(i),"武器"]) + "\n"
        formated_item = ""
        for i in range(1,3):
            formated_item += (df1a.at[str(i),"アイテム"]) + "\n"
        formated_vehicle = ""
        for i in range(1,3):
            formated_vehicle+= (df1a.at[str(i),"乗用物"]) + "\n"

        #ウェポン
        embed_weapon=discord.Embed(title=">Item: Weapon",
                            description="**交換品目 - ウェポン**",
                            color=0xFFFFFF)
        embed_weapon.add_field(name="List:", value=formated_weapon, inline=True)
        embed_weapon.set_footer(text=f"Made by まよなか | {daytime}")
        #アーマー
        embed_item=discord.Embed(title=">Item: Items",
                            description="**交換品目 - アイテム**",
                            color=0xFFFFFF)
        embed_item.add_field(name="List:", value=formated_item, inline=True)
        embed_item.set_footer(text=f"Made by まよなか | {daytime}")
        #ガジェット
        embed_vehicle=discord.Embed(title=">Item: Vehicle",
                            description="**交換品目 - 乗用物**",
                            color=0xFFFFFF)
        embed_vehicle.add_field(name="List:", value=formated_vehicle, inline=True)
        embed_vehicle.set_footer(text=f"Made by まよなか | {daytime}")
        #ページ操作
        content=[embed_title,embed_weapon,embed_item,embed_vehicle]
        menu = await ctx.send(embed=embed_title)
        view = discord.ui.View(timeout=None)  
        view.add_item(ControlButton(style=discord.ButtonStyle.primary,disabled=False,label="<<",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=4))
        view.add_item(ControlButton(style=discord.ButtonStyle.success,disabled=False,label="<",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=4))
        view.add_item(ControlButton(style=discord.ButtonStyle.danger,disabled=False,label="切断",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=4))
        view.add_item(ControlButton(style=discord.ButtonStyle.success,disabled=False,label=">",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=4))
        view.add_item(ControlButton(style=discord.ButtonStyle.primary,disabled=False,label=">>",now_ctx=ctx,embed=menu,contents=content,uid=usr_id,page=4))
        await ctx.send(view=view)
    else:
        await ctx.send("あなたには接続権限がありません。")

@bot.command()
async def buy(ctx,number:str):
    usr_id = str(ctx.author.id)
    df = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])
    #処理の中身
    if usr_id in str(df["ユーザーID"]):
        await ctx.send("`> 購入処理中...`")
        await asyncio.sleep(2)
        dfa = df.set_index("ユーザーID")
        dfdata = pd.DataFrame(products_data.get_all_values()[1:],columns=products_data.get_all_values()[0])
        dfdataB = dfdata.set_index("商品ID")
        current_coin = int(dfa.at[usr_id,"コイン数"]) - int(dfdataB.at[number,"価格"])
        target_ind = (dfa.index.get_loc(usr_id)) + 2
        target_clm = 4
        if current_coin >= 0:
            worksheet.update_cell(target_ind,target_clm,str(current_coin))
            await ctx.send("`> お買い上げありがとうございます。`")
            await ctx.send(f"> 購入者:{ctx.author.display_name}\n> 購入日時:{daytime}\n> 購入品:"+(dfdataB.at[number,"データ"]))
        else:
            await ctx.send("`エラー：残高不足です`")
    elif usr_id in str(df["ホワイトユーザーID"]): #ID管理のホワイトユーザーIDにUIDがあれば
        await ctx.send("`> 購入処理中...`")
        await asyncio.sleep(2)
        dfa = df.set_index("ホワイトユーザーID") #ホワイトユーザーIDをインデックスに設定
        dfwdata = pd.DataFrame(medal_data.get_all_values()[1:],columns=medal_data.get_all_values()[0])
        dfwdataA = dfwdata.set_index("商品ID")
        current_medal = int(dfa.at[usr_id,"勲章数"]) - int(dfwdataA.at[number,"価格"])
        target_ind = (dfa.index.get_loc(usr_id)) + 2
        target_clm = 8
        if current_medal >= 0:
            worksheet.update_cell(target_ind,target_clm,str(current_medal))
            await ctx.send("`> お買い上げありがとうございます。`")
            await ctx.send(f"`> 購入者:{ctx.author.display_name}`\n`> 購入日時:{daytime}`\n`> 購入品:"+(dfwdataA.at[number,"データ"]+"`"))
        else:
            await ctx.send("`エラー：残高不足です`")
    else:
        await ctx.send("`> あなたにはアクセス権がありません。`")

@bot.command()
async def exchange(ctx,number:str):
    usr_id = str(ctx.author.id)
    df = pd.DataFrame(worksheet.get_all_values()[1:],columns=worksheet.get_all_values()[0])
    guil = int(number) * 100
    if usr_id in str(df["ユーザーID"]):
        dfa = df.set_index("ユーザーID")
        target_ind = (dfa.index.get_loc(usr_id)) + 2
        target_clm = 4
        current_coin = int(dfa.at[usr_id,"コイン数"]) + int(number)
        worksheet.update_cell(target_ind,target_clm,str(current_coin))
        await ctx.send(f"`> {guil}Gを消費し、{number}RCを残高に追加しました。`")
        await ctx.send(f"`追加者名:{ctx.author.display_name} | 追加日時:{daytime}`")
    elif usr_id in str(df["ホワイトユーザーID"]):
        dfw = df.set_index("ホワイトユーザーID")
        target_ind = (dfw.index.get_loc(usr_id)) + 2
        target_clm = 8
        current_medal = int(dfw.at[usr_id,"勲章数"]) + int(number)
        worksheet.update_cell(target_ind,target_clm,str(current_medal))
        await ctx.send(f"`> {guil}Gを消費し、{number}KCを残高に追加しました。`")
        await ctx.send(f"`追加者名:{ctx.author.display_name} | 追加日時:{daytime}`")
    else:
        await ctx.send("`> あなたにはアクセス権がありません。`")

@bot.command()
async def CrimeNet(ctx):
    global Bank_TF, selected_mission, UseCN
    pages = 5
    cur_page = 1
    usr_id = str(ctx.author.id)
  
    #リアクションチェック用関数
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

    if usr_id not in User:
        await ctx.send("`>あなたには利用権がありません。`")
    elif usr_id in User and UseCN == True:
        await ctx.send("他の方が利用中です。")
    elif usr_id in User and UseCN == False:
        UseCN = True
        await ctx.send("`> Crime.netに接続中...`")
        prog_bar = await ctx.send("`[=    ]`")
        await asyncio.sleep(0.2)
        await prog_bar.edit(content="`[==   ]`")
        await asyncio.sleep(0.2)
        await prog_bar.edit(content="`[===  ]`")
        await asyncio.sleep(0.2)
        await prog_bar.edit(content="`[==== ]`")
        await asyncio.sleep(0.2)
        await prog_bar.edit(content="`[=====]`")
        await asyncio.sleep(0.2)
        await ctx.send("`> 接続完了`")
        
        #メインメニュー
        embed_title=discord.Embed(title="CRIMENet:Main Menu",
                            description="世界中のローグが利用する犯罪斡旋サービス、Crime.Netへようこそ。\nミッションを選択してください。",
                            color=0x6E6636)         
        embed_title.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081264384107622500/logo.jpg")  

        #ミッション1  
        embed_m1 = discord.Embed(title="BANK HEIST:",
                            description="> The Harvest & Trustee銀行は中規模の銀行支店で、金庫は奥にあり、幾つかの出入口がある。\n> 中には金塊や札束がたんまりと保管されている筈だ。",
                            color=0x6E6636)
        embed_m1.add_field(name="Enemy:", value="警備員x4", inline=True)
        embed_m1.add_field(name="Reward:", value="5,000 - 20,000G", inline=True)
        embed_m1.add_field(name="Cost:", value="3,000G", inline=False)
        embed_m1.set_footer(text="s2f31jx93jfnqxqofj3.nor")
        embed_m1.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081261030052737074/Heist1.png")  

        #ミッション2
        embed_m2 = discord.Embed(title="ART GALLERY:",
                            description="> 例の美術館に行くぞ。パンフレットには「芸術の文化的な重要性」について書かれているが、もっと重要なのは金額について書いてあることだ。とてつもない値段でな。",
                            color=0x6E6636)
        embed_m2.add_field(name="Enemy:", value="警備員x3", inline=True)
        embed_m2.add_field(name="Reward:", value="3,750 - 15,000G", inline=True)
        embed_m2.add_field(name="Cost:", value="2,000G", inline=False)
        embed_m2.set_footer(text="9j54f73pk86e7apaazp66n345i7zkm.nor")
        embed_m2.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081261029511676014/Heist2.png")  

        #ミッション3
        embed_m3 = discord.Embed(title="GO BANK:",
                            description="> 銀行強盗の時間だ。\n> ここはそれほどデカい支店ってわけじゃないが、調べたところによると金庫には輸送中の現金が大量に一時保管されているらしい。外国為替用の紙幣だな。",
                            color=0x6E6636)
        embed_m3.add_field(name="Enemy:", value="警備員x4", inline=True)
        embed_m3.add_field(name="Reward:", value="7,500 - 30,000G", inline=True)
        embed_m3.add_field(name="Cost:", value="3,500G", inline=False)
        embed_m3.set_footer(text="erty78cmc4ctj72p9hpnu7cs8gpja6.nor")
        embed_m3.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081695725764747345/Heist3.png") 

        #ミッション4
        embed_m4 = discord.Embed(title="JEWELRY STORE:",
                            description="> この街は宝石を捌くのに最高の場所だ、楽に捌ける。\n> 業者や「歳の差美人妻」どもが買っていくよ、何も聞かずにな。\n> 簡単な仕事だ。さあ始めよう。",
                            color=0x6E6636)
        embed_m4.add_field(name="Enemy:", value="警備員x5\n武装警官x1", inline=True)
        embed_m4.add_field(name="Reward:", value="8,750 - 35,000G", inline=True)
        embed_m4.add_field(name="Cost:", value="4,000G", inline=False)
        embed_m4.set_footer(text="5ck2fyjcibpydnpsmys33fg8z9gr8j.nor")
        embed_m4.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081695726108688485/Heist4.png")   

        #ミッション5
        embed_m5 = discord.Embed(title="THE BIG BANK:",
                            description="> The Benevolent Bank は歴史ある銀行だ。アメリアで最も古い銀行で、1812年にはアルヴィアに接収され、南北戦争の金を保管し、ルーズベルトが買った最初の債券もここが発行した。\n> ああ、お前の10ドル札の裏を見るとここの写真が載っていやがったりもするな。それで次は何だと思う？\n> 歴史上、強盗が成功したことは一度もないんだ。一度もだ。\n> さあ、今日はお前たちがその歴史を変える番だ。",
                            color=0x6E6636)
        embed_m5.add_field(name="Enemy:", value="警備員x8\n武装警官x3", inline=True)
        embed_m5.add_field(name="Reward:", value="12,500 - 50,000G", inline=True)
        embed_m5.add_field(name="Cost:", value="6,000G", inline=False)
        embed_m5.set_footer(text="6g9f33pfjcmjazb5zsb4zpcfi44bmf.nor")
        embed_m5.set_image(url="https://media.discordapp.net/attachments/1081260969256296528/1081695726498762792/Heist5.png")    

        contents=[embed_m1,embed_m2,embed_m3,embed_m4,embed_m5]

        menu = await ctx.send(embed=embed_title)
        await asyncio.sleep(1)
        message = await ctx.send(embed=embed_m1)
        view = discord.ui.View()  
        view.add_item(TrueButton(style=discord.ButtonStyle.primary,label="依頼を受諾",now_ctx=ctx))
        await ctx.send(view=view)
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=120, check=check)
                if str(reaction.emoji) == "▶️" and cur_page != pages:
                    cur_page += 1
                    selected_mission += 1
                    await message.edit(embed=contents[cur_page -1])
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️" and cur_page > 1:
                    cur_page -=1
                    selected_mission -= 1
                    await message.edit(embed=contents[cur_page -1])
                    await message.remove_reaction(reaction, user)
                else:
                    pass
            except:
                print("Error has confirm")
                print("`一定時間を過ぎたため、自動的に切断します`")
                await message.delete()
                await menu.delete()
                break


@bot.command()
async def heist1(ctx):
    global phase, Bank_TF
    phases = ["A1","A2","A3","A4"]
    if Bank_TF == False:
        await ctx.send("強盗は開始されていません。")
    elif Bank_TF == True and phase <= 3:
        await ctx.send((BANK_HEIST[(phases[phase])].value))
        phase += 1
    elif phase == 4:
        await ctx.send((BANK_HEIST["A6"].value))
        phase += 1
    elif phase == 5:
        await ctx.send((BANK_HEIST["A7"].value))
        phase += 1
    elif phase == 6: #成功
        await ctx.send("```警察車両から逃げ切り、あなた方は無事逃走に成功した。報酬を分けよう```")

@bot.command()
async def heist2(ctx):
    global phase, Bank_TF
    phases = ["A1","A2","A3","A4"]
    if Bank_TF == False:
        await ctx.send("強盗は開始されていません。")
    elif Bank_TF == True and phase <= 3:
        await ctx.send((ART_GALLERY[(phases[phase])].value))
        phase += 1
    elif phase == 4:
        await ctx.send((ART_GALLERY["A6"].value))
        phase += 1
    elif phase == 5:
        await ctx.send((ART_GALLERY["A7"].value))
        phase += 1
    elif phase == 6: #成功
        await ctx.send("```警察車両から逃げ切り、あなた方は無事逃走に成功した。報酬を分けよう```")

@bot.command()
async def heist3(ctx):
    global phase, Bank_TF
    phases = ["A1","A2","A3","A4"]
    if Bank_TF == False:
        await ctx.send("強盗は開始されていません。")
    elif Bank_TF == True and phase <= 3:
        await ctx.send((GO_BANK[(phases[phase])].value))
        phase += 1
    elif phase == 4:
        await ctx.send((GO_BANK["A6"].value))
        phase += 1
    elif phase == 5:
        await ctx.send((GO_BANK["A7"].value))
        phase += 1
    elif phase == 6: #成功
        await ctx.send("```警察車両から逃げ切り、あなた方は無事逃走に成功した。報酬を分けよう```")

@bot.command()
async def heist4(ctx):
    global phase, Bank_TF
    phases = ["A1","A2","A3","A4"]
    if Bank_TF == False:
        await ctx.send("強盗は開始されていません。")
    elif Bank_TF == True and phase <= 3:
        await ctx.send((JEWERLY_STORE[(phases[phase])].value))
        phase += 1
    elif phase == 4: #銀行外
        await ctx.send((JEWERLY_STORE["A6"].value))
        phase += 1
    elif phase == 5: #カーチェイス
        await ctx.send((JEWERLY_STORE["A7"].value))
        phase += 1
    elif phase == 6: #成功
        await ctx.send("```警察車両から逃げ切り、あなた方は無事逃走に成功した。報酬を分けよう```")


@bot.command()
async def heist5(ctx):
    global phase, Bank_TF
    phases = ["A1","A2","A3","A4"]
    if Bank_TF == False:
        await ctx.send("強盗は開始されていません。")
    elif Bank_TF == True and phase <= 3:
        await ctx.send((THE_BIG_BANK[(phases[phase])].value))
        phase += 1
    elif phase == 4:
        await ctx.send((THE_BIG_BANK["A5"].value))
        phase += 1
    elif phase == 5:
        await ctx.send((THE_BIG_BANK["A6"].value))
        phase += 1
    elif phase == 6:
        await ctx.send((THE_BIG_BANK["A7"].value))
        phase += 1
    elif phase == 7:
        await ctx.send("```警察車両から逃げ切り、あなた方は無事逃走に成功した。報酬を分けよう```")


@bot.command()
async def end(ctx):
    global Bank_TF
    usr_id = str(ctx.author.id)
    if Bank_TF == True and usr_id in User:
        await ctx.send("帰還します。")
        Bank_TF = False
    else:
        await ctx.send("強盗は開始されていません。")

@bot.command()
async def vault(ctx, skill:int):
    result = 0
    global selected_mission, Bank_TF
    dice = random.randrange(1,101,1)
    if Bank_TF == True:
        if dice <= skill:
            for i in range(valt[selected_mission]["num"]):
                result += random.randrange(1,valt[selected_mission]["gold"],1)
            await ctx.reply("> **" + str(result) + "Gを入手した**")
        else:
            await ctx.reply("> **ドリルがエラーを吐いた**")
    else:
        await ctx.send("強盗は開始されていません。")

async def loading(ctx):
    global selected_mission
    await asyncio.sleep(0.5)
    prog_bar = await ctx.send("`[     ]`")
    await prog_bar.edit(content="`[=    ]`")
    await asyncio.sleep(0.6)
    await prog_bar.edit(content="`[==   ]`")
    await asyncio.sleep(0.6)
    await prog_bar.edit(content="`[===  ]`")
    await asyncio.sleep(0.6)
    await prog_bar.edit(content="`[==== ]`")
    await asyncio.sleep(0.6)
    await prog_bar.edit(content="`[=====]`")
    await asyncio.sleep(0.6)
    await prog_bar.edit(content="`[complete]`")
    await ctx.send("`> ロード完了`")
    if selected_mission == 0:
        await BankHeist(ctx)
    elif selected_mission == 1:
        await ArtGallery(ctx)
    elif selected_mission == 2:
        await GoBank(ctx)
    elif selected_mission == 3:
        await JewelryStore(ctx)
    elif selected_mission == 4:
        await TheBigBank(ctx)
    else:
        await ctx.send("Error: No Data")

async def BankHeist(ctx):
    await ctx.send("```強盗名: BANK HEIST\n部屋数: 4\n最大報酬: 20,000G\n難易度: ☆```")
    await ctx.send("全員の準備が完了したら、?heist1と入力してください。")

async def ArtGallery(ctx):
    await ctx.send("```強盗名: ART GALLERY\n部屋数: 5\n最大報酬: 15,000G\n難易度: ☆```")
    await ctx.send("全員の準備が完了したら、?heist2と入力してください。")

async def GoBank(ctx):
    await ctx.send("```強盗名: GO BANK\n部屋数: 5\n最大報酬: 30,000G\n難易度: ☆☆```")
    await ctx.send("全員の準備が完了したら、?heist3と入力してください。")

async def JewelryStore(ctx):
    await ctx.send("```強盗名: JEWELRY STORE\n部屋数: 5\n最大報酬: 35,000G\n難易度: ☆☆```")
    await ctx.send("全員の準備が完了したら、?heist4と入力してください。")

async def TheBigBank(ctx):
    await ctx.send("```強盗名: THE BIG BANK\n部屋数: 5\n最大報酬: 50,000G\n難易度: ☆☆☆```")
    await ctx.send("全員の準備が完了したら、?heist5と入力してください。")

    
bot.run("MTA3MjEwODcxNDAxNTg3MTAzNw.G6Tqbr.OQkLB7Gsm7VOohETEzBKGNq7OdmRDfaoTVfJmY")