
#必要なライブラリをインポート
import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import random, dice, asyncio
import numpy as np

blacklist = ["1076422611325702236","1093041645114622004","1032532645655105536","931562992041099275","1081170888063459368"]


#ボス戦用配列
current_battle = {} #現在戦闘しているチャンネル
current_party = {} #パーティーメンバー
current_party_loc = {} #メンバーの位置
current_party_react = {} #リアクション型管理用
current_turn = {} #現在ターン
tower_floar = {} #現在の階層
show_turn = {} #表示用ターン

gimmick_prog = False #ギミックが進行中かどうか
act = False
rest = False
battle = False

selc_id = ["a","b","c","d","e","f","g"]
tower_boss = {1:"d1", 2:"d2", 3:"d3", 4:"d4", 5:"d5"}
square_xy = {"NW":[1,3],"N":[2,3],"NE":[3,3],
               "W":[1,2],"Center":[2,2],"E":[3,2],
               "SW":[1,1],"S":[2,1],"SE":[3,1]}
streaming_P0 = False
streaming_P1 = False

#ボス戦用クラス
class Actor:
    def __init__(self, name, hp, max_hp):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp

class Enemy(Actor):
    def __init__(self, name, max_hp):
        super().__init__(name, max_hp, max_hp)
        self.enemy = self.__class__.__name__
      
    # NEW METHOD
    def rehydrate(self, name, hp, max_hp):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp

#---1層ボス---
class d1(Enemy):
    floar_name = "魔導研究所セクターA『魔導キマイラII型』"
    gimmick_name_list = {1:["ヘヴィー・クロウ","ハウル・インパクト","突進","両翼開放","ヘヴィー・クロウ"]}
    phase = 1
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 20
    attack_selc = 6
    Bhp = 250
    Bname = "魔導キマイラII型"

    #時間切れ
    timeup = {1:{"name":"ハウル・インパクト", "type":"all", "damage":"2d15+5", "text":"〈キマイラが咆哮を上げる〉","desc":"無属性/ 魔法/ 全体"}}
    timeup_name = {1:["ハウル・インパクト"]}

    #ここから攻撃選択
    p1 = {1:{"name":"ヘヴィー・クロウ", "type":"role", "damage":"3d20+7", "target":"tank", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 回避不可/ 単体"},
          2:{"name":"ハウル・インパクト", "type":"all", "damage":"2d15+5", "text":"〈キマイラが咆哮を上げる〉","desc":"無属性/ 魔法/ 全体"},
          3:{"name":"突進", "type":"locate", "damage":"2d30+7", "danger_locate":["N","Center","S"], "text":"〈キマイラが突進体勢を取る〉","desc":"無属性/ 物理/ 回避不可/ 複数"},
          4:{"name":"両翼開放", "type":"locate", "damage":"2d30+7", "danger_locate":["NW","W","SW","NE","E","SE"], "text":"〈キマイラの両翼が開く〉","desc":"無属性/ 魔法/ 回避不可/ 複数"},
          5:{"name":"ヘヴィー・クロウ", "type":"role", "damage":"3d20+7", "target":"tank", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 回避不可/ 単体"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold

#---2層ボス---
class d2(Enemy):
    floar_name = "魔導研究所セクターB『実験体7号』"
    gimmick_name_list = {1:["マギカ・クラッシャー","フォーリング・スピア","突進","デス・サークル","フィアレス・スピア"]}
    phase = 1
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 20
    attack_selc = 6
    Bhp = 300
    Bname = "実験体7号"

    #時間切れ
    timeup = {1:{"name":"フォーリング・スピア", "type":"all", "damage":"2d20+5", "text":"〈絡繰騎士が攻撃を準備している〉","desc":"無属性/ 物理/ 回避不可/ 全体"}}
    timeup_name = {1:["フォーリング・スピア"]}

    #ここから攻撃選択
    p1 = {1:{"name":"マギカ・クラッシャー", "type":"role", "damage":"3d20+10", "target":"tank", "text":"〈実験体7号が攻撃を準備している〉","desc":"無属性/ 物理/ 回避不可/ 単体"},
          2:{"name":"フォーリング・スピア", "type":"all", "damage":"2d20+5", "text":"〈絡繰騎士が攻撃を準備している〉","desc":"無属性/ 物理/ 回避不可/ 全体"},
          3:{"name":"突進", "type":"locate", "damage":"2d35+7", "danger_locate":["N","Center","S"], "text":"〈実験体七号が突進の姿勢を取る〉","desc":"無属性/ 物理/ 回避不可/ 複数"},
          4:{"name":"デス・サークル", "type":"locate", "damage":"2d35+7", "danger_locate":["E","W","S","N","SW","NW","SE","NE"], "text":"〈ドーナツ型の魔法陣が浮かび上がる〉","desc":"無属性/ 魔法/ 回避不可/ 複数"},
          5:{"name":"フィアレス・スピア", "type":"stack", "damage":"2d10+3", "text":"に対して強力な攻撃が放たれようとしている〉","desc":"無属性/ 物理/ 回避不可/ 複数"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold

#---3層ボス---
class d3(Enemy):
    floar_name = "魔導の塔第三層『絡繰魔導兵』"
    gimmick_name_list = {1:["ミニメテオ","魔導レーザー","マギカレイン","マギカインパクト"]}
    phase = 1
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 25
    attack_selc = 6
    Bhp = 300
    Bname = "絡繰魔導兵"
    #ここから攻撃選択

    p1 = {1:{"name":"ミニメテオ", "type":"tower", "damage":"2d25+7", "tower_damage":"2d10+5","tower_locate":["Center"], "text":"〈魔法陣が開き、中心部へ隕石が近づく〉","desc":"血属性/ 物理/ 回避不可/ 複数"},
          2:{"name":"魔導レーザー", "type":"stack", "damage":"2d10+3", "text":"に対して強力な魔導攻撃が放たれようとしている〉","desc":"血属性/ 魔法/ 回避不可/ 複数"},
          3:{"name":"マギカレイン", "type":"spread", "damage":"2d10+3", "text":"〈魔導攻撃があなた方を狙っている〉","desc":"血属性/ 魔法/ 回避不可/ 複数"},
          4:{"name":"マギカインパクト", "type":"distance", "damage":"6d10+10", "attack_cord":"NW","text":"〈強力な攻撃が北東部へ降ろうとしている〉","desc":"血属性/ 魔法/ 回避不可/ 複数"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold

#Bot関連設定
description = "Emeth V1.3"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=None, intents=intents)

#Botログイン時処理
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")

#塔開始進行用コマンド
@bot.command(name="lab")
async def lab(ctx):
    if str(ctx.author.id) in blacklist:
        await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    global rest, battle,gimmick_prog
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #既に突入しているパーティーがあれば
    if channelID in current_battle:
        await ctx.send("`現在別のパーティーが突入中です`")
        return
    #タワーに突入しており、戦闘が終わっている場合
    if channelID in tower_floar and battle == False:
        #現在休憩フロアである場合は次の戦闘を開始
        #もし休憩フロアであり、かつ2層をクリアしていれば
        if rest == True and tower_floar[channelID] == 2:
            await ctx.send("`3層以降は制作中です。帰還します`")
            battle = False
            rest = False
            gimmick_prog = False
            del current_battle[channelID]
            del current_party[channelID]
            del current_turn[channelID]
            del current_party_loc[channelID]
            current_party_react.clear()
            return
        if rest == True:
            rest = False
            tower_floar[channelID] += 1 #階層を上げる
            show_turn[channelID] = 0
            floar = tower_floar[channelID] #現在階層を取得
            battle = True
            #---クラス処理関連---
            battle = tower_boss[floar] 
            cls = globals()[battle] #クラスを追加
            bossData = cls()
            current_battle[channelID] = bossData #専用配列にチャンネルIDとボスIDを紐付けて登録
            #---辞書への初期値関連---
            show_turn[channelID] = 0 #現在ターンをリセット
            current_turn[channelID] = 0 #現在ターンを0に設定
            await ctx.send(f"**`クエスト名: {bossData.floar_name}`**\n`チャンネル: {ctx.channel.name}`\nロールと現在地は継続の為、準備が整ったら`?trait 開始`で戦闘開始")
            embedPhase1=discord.Embed(title=f"［―――{bossData.floar_name}―――］",
                                    description=" ",
                                    color=0x6E6636)
            await ctx.send(embed=embedPhase1) #ヘッダー表示
        #戦闘が終了した直後で、休憩フロアでない場合
        else:
            floar = tower_floar[channelID]
            await ctx.send(f"`{floar}区画を突破したあなた方は、次の区画に移動するまでの間で休息が行える。準備が整ったら次の区画へ向かおう。`")
            rest = True
            return
    #戦闘がまだ終わっていない場合
    elif channelID in tower_floar and battle == True:
        await ctx.send("`戦闘中です`")
        return
    #タワーに突入していない場合
    elif channelID not in tower_floar:
        battle = True
        #---クラス処理関連---
        cls = globals()["d1"]
        bossData = cls()
        current_battle[channelID] = bossData #専用配列にチャンネルIDとボスIDを紐付けて登録
        #---辞書への初期値関連---
        show_turn[channelID] = 0
        current_party[channelID] = {str(ctx.author.display_name):"front"} #パーティー用の専用配列を作成
        tower_floar[channelID] = 1 #チャンネルの階層を1層に設定
        current_turn[channelID] = 0 #現在ターンを0に設定
        current_party_loc[channelID] = {str(ctx.author.display_name):"S"} #メンバー位置の専用配列を作成

        await ctx.send(f"**`クエスト名: {bossData.floar_name}`**\n`チャンネル: {ctx.channel.name}`\n`?trait [ロール]`でロールを宣言後、戦闘を開始")
        embedPhase1=discord.Embed(title="［―――魔導研究所―――］",
                                description=" ",
                                color=0x6E6636)
        await ctx.send(embed=embedPhase1) #ヘッダー表示

#ギミック型レイド用コマンド
@bot.command(name="trait", help="?trait [内容]")
async def trait(ctx, msg:str = "NaN"):
    if str(ctx.author.id) in blacklist:
        await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    global gimmick_prog, act, battle, rest
    channelID = str(ctx.channel.id) #コマンドが実行されたチャンネルIDを取得
    #もしmsgが入力されていなければ
    if msg == "NaN":
        await ctx.reply("`> 内容を入力してください`")
        return
    #チャンネルIDが辞書に登録されていなければ
    if channelID not in current_battle:
        await ctx.reply("`> 戦闘を開始していません`")
        return
    usr_name = ctx.author.display_name #ニックネームを取得
    bossData = current_battle[channelID] #ボスインスタンスを取得
    counted_turn = show_turn[channelID]
    if msg != "ターン":
        await ctx.send(f"`現在ターン:{counted_turn}`")
    if msg == "ターン":
        act = True
        current_turn[channelID] += 1
        show_turn[channelID] += 1
        counted_turn = show_turn[channelID]
        await ctx.send(f"`現在ターン:{counted_turn}`")
        if current_turn[channelID] == bossData.attack_selc:
            current_turn[channelID] = 1
        await gimmick(ctx)
    elif msg == "北東":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "NE"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 北東に移動しました`")
    elif msg == "南東":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "SE"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 南東に移動しました`")
    elif msg == "北西":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "NW"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 北西に移動しました`")
    elif msg == "南西":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "SW"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 南西に移動しました`")
    elif msg == "東":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "E"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 東に移動しました`") 
    elif msg == "西":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "W"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 西に移動しました`") 
    elif msg == "南":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "S"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 南に移動しました`")  
    elif msg == "北":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "N"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 北に移動しました`")    
    elif msg == "中央":
        update_dict = current_party_loc[channelID]  
        update_dict[usr_name] = "Center"
        current_party_loc[channelID].update(update_dict)
        await ctx.send("`> 中央に移動しました`")          

    elif "ダメージ" in msg:
        dmg = msg.split("ダ")
        print("ダメージ判定")
        print(dmg)
        #DPSチェック中の判定
        if bossData.dps_check == True:
            if int(dmg[0]) > 200:
                fix_damage = (int(dmg[0]) * 0.5) - bossData.armor
            else:
                fix_damage = int(dmg[0]) - bossData.armor    
            bossData.dps_check_hp -= fix_damage
            await ctx.send(f"> **`{usr_name}`**は対象に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.dps_check_hp}`")
            print(bossData.dps_check_hp)     
            if bossData.dps_check_hp <= 0:
                current_turn[channelID] += 1
                await gimmick(ctx)
                bossData.dps_check = False
        #---ここまでDPSチェック判定---
        else:
            #ダメージが100から200の間なら
            if 200 >= int(dmg[0]) > 100:
                fix_damage = (int(dmg[0]) * 0.5) - bossData.armor
            #ダメージが200以下なら
            elif int(dmg[0]) < 200:
                fix_damage = (int(dmg[0]) * 0.6) - bossData.armor
            #ダメージが200以上なら
            elif int(dmg[0]) > 200:
                fix_damage = (int(dmg[0]) * 0.3) - bossData.armor
            #ダメージが100以下なら
            else:
                fix_damage = int(dmg[0]) - bossData.armor
            bossData.Bhp -= fix_damage
            await ctx.send(f"> **`{usr_name}`**は**`{bossData.Bname}`**に`{fix_damage}ダメージを与えた！`\n`残りHP:{bossData.Bhp}`")
            print(bossData.Bhp)
            if bossData.Bhp <= 0:
                await ctx.send(f"`>{usr_name}が{bossData.Bname}へ一撃を加えるのと同時、その体が地に崩れ墜ちる。戦いの末、あなた方は勝利を掴み取ることができた。`")
                await ctx.send("`>戦闘終了`")
                battle = False
                del current_battle[channelID]
                #del current_party[channelID] ロール設定は保持
                del current_turn[channelID]
                #del current_party_loc[channelID]
                del show_turn[channelID]
                #current_party_react.clear()
    elif msg == "中断":
        await ctx.send("中断します")
        battle = False
        rest = False
        gimmick_prog = False
        del current_battle[channelID], current_party[channelID], current_turn[channelID], current_party_loc[channelID]
        current_party_react.clear()
    elif msg == "完了":
        act = True
        await ctx.send(f">`{usr_name}の手番を完了した`")
        await ctx.send("全員の手番が終わったのであれば`?trait ターン`を。その他の場合は2分以内に手番を完了してください。")
        await asyncio.sleep(2)
        act = False
        for i in range(120):#120秒待つ
            await asyncio.sleep(1) 
            if act == True:
                return
        if gimmick_prog == False: #ギミック処理中ではなく、対象が未行動であれば
            current_turn[channelID] += 1
            if current_turn[channelID] == bossData.attack_selc:
                current_turn[channelID] = 1
            await gimmick(ctx,"yes")
    elif msg == "開始":
        await ctx.send(">開始します。一人2分以内に手番を終えてください。完了したら`?trait 完了`と入力してください。")
        for i in range(120):
            await asyncio.sleep(1)
            if act == True:
                return
        if gimmick_prog == False: #ギミック処理中ではなく、対象が未行動であれば
            current_turn[channelID] += 1
            await gimmick(ctx,"yes")
    elif msg == "タンク": #タンクロール設定
        #<--リアクション初期値-->
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        #<--位置初期値-->
        update_dict_L = current_party_loc[channelID]  
        update_dict_L[usr_name] = "Center"
        current_party_loc[channelID].update(update_dict_L)

        if "tank" in update_dict.values():
            await ctx.reply("`> 既にタンクが存在します`")   
            return         
        
        update_dict[usr_name] = "tank"
        current_party.update(update_dict)
        await ctx.reply("`> タンクに設定しました`")
    elif msg == "ヒーラー": #ヒーラーロール設定
        #<--リアクション初期値-->
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        #<--位置初期値-->
        update_dict_L = current_party_loc[channelID]  
        update_dict_L[usr_name] = "Center"
        current_party_loc[channelID].update(update_dict_L)

        if "healer" in update_dict.values():
            await ctx.reply("`> 既にヒーラーが存在します`")   
            return         
        
        update_dict[usr_name] = "healer"
        current_party.update(update_dict)
        await ctx.reply("`> ヒーラーに設定しました`")
    elif msg == "アタッカー": #アタッカーロール設定
        #<--リアクション初期値-->
        current_party_react[usr_name] = "F"
        update_dict = current_party[channelID]
        #<--位置初期値-->
        update_dict_L = current_party_loc[channelID]  
        update_dict_L[usr_name] = "Center"
        current_party_loc[channelID].update(update_dict_L)

        if list(update_dict.values()).count('dps') == 2:
            await ctx.reply("`> 既にアタッカーが二人存在します`")   
            return         
        
        update_dict[usr_name] = "dps"
        current_party.update(update_dict)
        await ctx.reply("`> アタッカーに設定しました`")
    else:
        await ctx.reply("`>不正なコマンドです`")

#時間カウンター用関数
@commands.command()
async def counter(ctx,time:int):
    msg = await ctx.send(f"`発動まで{time}...`")
    for i in reversed(range(time)):
        await asyncio.sleep(1)
        refr = f"`発動まで{i}...`"
        await msg.edit(content=refr)
    await msg.edit(content="`>ギミック発動`")

#ギミック処理用関数
@commands.command()
async def gimmick(ctx,timesup:str = "none"):
    target_selcs = []
    global gimmick_prog
    gimmick_prog = True
    channelID = str(ctx.channel.id) #チャンネルIDを取得
    turn_count = current_turn[channelID]
    now_turn = turn_count- 1 #現在のターンを取得
    bossData = current_battle[channelID] #ボスインスタンスを取得
    #普通にターンが来た場合
    if timesup == "none":
        name_list = bossData.gimmick_name_list[bossData.phase] #ギミック名のリストを取得
        gimmick_data = bossData.p1[turn_count] #辞書から現在ターンに対応したギミックデータを取得
    #時間切れの場合
    else:
        name_list = bossData.timeup_name[bossData.phase]
        now_turn = 0
        gimmick_data = bossData.timeup[0]


    desc = gimmick_data["desc"]
    atk_dmg = gimmick_data["damage"]
    texts = gimmick_data["text"]
    atk_rst = dice.roll(atk_dmg) #攻撃ダメージを取得

    #<---ロール選択攻撃--->
    if gimmick_data["type"] == "role":
        target_roles = [k for k, v in current_party[channelID].items() if v == gimmick_data["target"]]  
        list_form = ''.join(map(str, target_roles))
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    #<---全体攻撃--->
    elif gimmick_data["type"] == "all":
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
    #<---リアクション選択攻撃--->
    elif gimmick_data["type"] == "select":
        stopper = False
        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        embedPhase1=discord.Embed(title="移動先を選択",
                                description=":regional_indicator_a: - 上\n:regional_indicator_b: - 下\n:regional_indicator_c: - 右\n:regional_indicator_d: - 左",
                                color=0x6E6636)
        select_msg = await ctx.send(embed=embedPhase1) #ヘッダー表示
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter A}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter B}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter C}')
        await select_msg.add_reaction('\N{Regional Indicator Symbol Letter D}')
        #リアクション判定部分
        @bot.event
        async def on_reaction_add(reaction, user):
            if stopper == True:
                return
            if str(reaction.emoji) == '\N{Regional Indicator Symbol Letter A}':
                current_party_react[user.display_name] = "A"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter B}':
                current_party_react[user.display_name] = "B"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter C}':
                current_party_react[user.display_name] = "C"
            elif str(reaction.emoji) == '\N{Regional Indicator Symbol Letter D}':
                current_party_react[user.display_name] = "D"
        await counter(ctx,5) 
        stopper = True

        target_selcs = [k for k, v in current_party_react.items() if v != gimmick_data["true_select"]]  
        list_form = '、'.join(map(str, target_selcs))
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    #<---コマンド選択攻撃--->
    elif gimmick_data["type"] == "locate": 
        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        await counter(ctx,10)
        #安置にいないPCをtarget_selcsに追加
        danger_place = gimmick_data["danger_locate"]
        for i in range(len(gimmick_data["danger_locate"])):
            target_selcs += get_keys_from_value(current_party_loc[channelID],danger_place[i])
            print(target_selcs)
        list_form = '、'.join(map(str, target_selcs))
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ダメージの攻撃`") 
    #<---DPSチェック--->
    elif gimmick_data["type"] == "check":
        bossData.dps_check = True
        bossData.dps_check_hp = gimmick_data["target_hp"]
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
    #<---DPSチェック失敗--->
    elif gimmick_data["type"] == "check_fail" and bossData.dps_check == True:
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ダメージの攻撃`") 
    #<---DPSチェック成功--->
    elif gimmick_data["type"] == "check_fail" and bossData.dps_check == False:
        await ctx.send("`>どうにか敵を倒すことができた。`") #ヒントテキストを表示
        bossData.dps_check = False
    #<---タワー攻撃--->
    elif gimmick_data["type"] == "tower":
        fail_tower = []
        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        await counter(ctx,7) #7秒待つ
        #タワー位置とプレイヤー位置を照合し踏んでいる人にダメージ
        tower_locate = gimmick_data["tower_locate"]
        for i in range(len(gimmick_data["tower_locate"])):
            target_selcs += get_keys_from_value(current_party_loc[channelID],tower_locate[i])
            print(target_selcs)
        list_form = '、'.join(map(str, target_selcs))
        if len(target_selcs) != 0:
            suc_dice = gimmick_data["tower_damage"]
            suc_damage = dice.roll(suc_dice)
            await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{suc_damage}ダメージの攻撃`") 
        #タワー位置とプレイヤー位置を照合し、踏まれていないタワーがあれば全体攻撃
        player_locate = list(current_party_loc[channelID].values())
        fail_tower = set(tower_locate) - set(player_locate)
        fail_tower = list(fail_tower)
        fail_num = len(fail_tower)
        if fail_num != 0:
            await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> 全体に{atk_rst}ｘ{fail_num}ダメージの攻撃`") 
    #<---頭割り攻撃--->
    elif gimmick_data["type"] == "stack":
        #頭割り対象を選ぶ
        player_name = list(current_party_loc[channelID].keys())
        stack_target_selc = random.randrange(len(player_name))
        stack_target_name = player_name[stack_target_selc]

        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>〈{stack_target_name}{texts}`") #ヒントテキストを表示
        await counter(ctx,7) #7秒待つ

        stack_target_loc = current_party_loc[channelID][stack_target_name]
        target_selcs = get_keys_from_value(current_party_loc[channelID],stack_target_loc) #頭割り対象と同じ位置にいるプレイヤーを取得
        list_form = '、'.join(map(str, target_selcs))
        stack_num = 5 - len(target_selcs)
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`> {list_form}に{atk_rst}ｘ{stack_num}ダメージの攻撃`") 
    #<---散会攻撃--->  
    elif gimmick_data["type"] == "spread":
        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        await counter(ctx,7) #7秒待つ
        
        player_loc_base = list(current_party_loc[channelID].values()) #プレイヤーの現在地を取得
        player_loc = list(dict.fromkeys(player_loc_base)) #重複を排除したプレイヤー位置を取得
        print(player_loc)

        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`")
        for i in range(len(player_loc)): #重複を排除した位置で個別にダメージを表示
            target_selcs = get_keys_from_value(current_party_loc[channelID],player_loc[i])
            list_form = '、'.join(map(str, target_selcs))
            lap_num = len(target_selcs)
            await ctx.send(f"`> {list_form}に{atk_rst}ｘ{lap_num}ダメージの攻撃`")
    #<---距離減衰--->
    elif gimmick_data["type"] == "distance":
        await ctx.send(f"`>{bossData.Bname}`が`『{name_list[now_turn]}』`を準備している") #ボス名とギミック名を表示
        await ctx.send(f"`>{texts}`") #ヒントテキストを表示
        await counter(ctx,7) #7秒待つ
        
        player_loc_base = list(current_party_loc[channelID].values()) #プレイヤーの現在地を取得
        player_loc = list(dict.fromkeys(player_loc_base)) #重複を排除したプレイヤー位置を取得
        print(player_loc)
        attack_cordinate = np.array(square_xy[gimmick_data["attack_cord"]])
        await ctx.send(f"> **{bossData.Bname}**の**『{name_list[now_turn]}』！**\n`{desc}`")
        for i in range(len(player_loc)):
            player_cordinate = np.array(square_xy[player_loc[i]]) #プレイヤーの座標値を取得
            distance = np.linalg.norm(attack_cordinate - player_cordinate) #距離を算出
            #攻撃値を距離で割る
            atk_real = round((atk_rst / (distance*1.5)),1)  # type: ignore 
            print(atk_rst)
            print(atk_real)
            target_selcs = get_keys_from_value(current_party_loc[channelID],player_loc[i])
            list_form = '、'.join(map(str, target_selcs))
            await ctx.send(f"`> {list_form}に{atk_real}ダメージの攻撃`")

    #<---吹き飛ばし--->
    #<---磁石--->
    #<---フレア--->
    #<---鎖--->
    gimmick_prog = False

#BGMフェードアウトコマンド
async def FadeOut(ctx):
    for i in reversed(range(1,10)):
        volume = i*10
        ctx.voice_client.source.volume = volume / 100
        await asyncio.sleep(0.3)
        print(volume)
    for i in reversed(range(10)):
        volume = i
        ctx.voice_client.source.volume = volume / 100
        await asyncio.sleep(0.2)
        print(volume)
    ctx.voice_client.stop()


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]

#Bot起動
bot.run("MTEwNTMzNzcxMzk1NzI5NDEwMQ.GRHhuN.CpNn8hppr348Q75awUgfMhUMKh7cgaC8JzSTeA")