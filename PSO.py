#必要なライブラリをインポート
import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import random, dice, asyncio, openpyxl, re
import pandas as pd

dfA = pd.read_excel("data/attack.xlsx")
df = dfA.set_index(["UID","TRIG"])
dfA = dfA.set_index("UID")

#辞書とリスト
#<-- 変動するもの -->
current_raid = {}
current_raid_zako = {}
current_raid_member = {}
current_raid_memstat = {}
total_raid_member = {}
current_round = {}
member_status = {}
boss_round = {}
battle_status = {}
status = {}

#<-- 固定的なもの -->
raid_ids = ["raid1","raid2","raid3"]
yes_no = ["はい","いいえ"]

#Bot関連設定
description = "ABS v1.0"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=None, intents=intents)

#時刻取得
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

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

#---レイド1---
class raid1(Enemy):
    raid_name = "原初の闇『ゴムルスⅠ』"
    gimmick_name_list = {1:["グンネ・ソール","グワナ・ソール","フォルナ・グレア","バース・ソール","予兆1","メガ・グレア"]}
    phase = 1
    phase_num = 1
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 20
    attack_selc = 7
    Bhp = 250
    Bname = "ゴムルスⅠ"

    #ここから攻撃選択
    p1 = {1:{"name":"グンネ・ソール", "type":"random", "damage":"2d8+4", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
          2:{"name":"グワナ・レヴリー", "type":"random", "damage":"1d16+4", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
          3:{"name":"フォルナ・グレア", "type":"all", "damage":"2d10+2", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
          4:{"name":"バース・ソール", "type":"random", "damage":"2d10+4", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
          5:{"name":"予兆1", "type":"announce", "damage":"1d1+1","text":"が強力な攻撃を準備している...。","desc":"none"},
          6:{"name":"メガ・グレア", "type":"all", "damage":"3d10+4", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold
        
#---レイド2---
class raid2(Enemy):
    raid_name = "『エフィシェント・ドラゴン』討伐戦"
    gimmick_name_list = {1:["ファイアーボール","ファイラ","たたかう","フレアスター","レベル3フレア"],
                         2:["サザンクロス","フレア","ファイガ","フレアスター","レベル4フレア"]}
    phase = 1
    phase_num = 2
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 20
    attack_selc = {1:6, 2:6}
    phase_hp = {1:350, 2:300}
    phase_text = {2:"> **「GRRUHHHH……」**",}
    icon_url = "https://media.discordapp.net/attachments/1081260969256296528/1107164639936131092/8aecc3aa-eabd-3149-9697-56364321f5ac.png"
    Bhp = 350
    Bname = "エフィシェント・ドラゴン"
    musics = {1:{"playtime":262,"link":"mp3/kefka1.m4a"},
              2:{"playtime":222,"link":"mp3/kefka2.m4a"},
              }

    #ここから攻撃選択
    actions = {
        1:{1:{"name":"ファイアーボール", "type":"all", "damage":"2d12+2", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 全体"},
            2:{"name":"ファイラ", "type":"random", "damage":"1d20+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法 魔法防護適用/ 単体"},
            3:{"name":"たたかう", "type":"random", "damage":"3d6+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 物理防護適用/ 単体"},
            4:{"name":"フレアスター", "type":"all", "damage":"2d6+5", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ レベルに応じてダメージを乗算/ 全体"},
            5:{"name":"レベル3フレア", "type":"all", "damage":"3d10+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ レベル3のPCのみ"},
            },
        2:{1:{"name":"サザンクロス", "type":"all", "damage":"2d12+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
           2:{"name":"フレア", "type":"random", "damage":"2d20+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},     
           3:{"name":"ファイガ", "type":"random", "damage":"2d10+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法 魔法防護適用/ 単体"},
           4:{"name":"フレアスター", "type":"all", "damage":"2d6+5", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ レベルに応じてダメージを乗算/ 全体"},
           5:{"name":"レベル4フレア", "type":"all", "damage":"3d10+1d4+1", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ レベル4のPCのみ"},
            },
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold
        
#---レイド3---
class raid3(Enemy):
    raid_name = "『エンシェント・メイガス』討伐戦"
    gimmick_name_list = {1:["こころないてんし","はかいのつばさ","トライン","ファイガ","はかいのつばさ","ブリザガ","たたかう","サンダガ"],
                         2:["はかいのつばさ","ミッシング","リベンジャー","トライン"],
                         3:["ハイパードライブ","たたかう","たたかう"],
                         4:["アルテマ","ミッシング","たたかう","ハイパードライブ","メテオ"],}
    phase = 1
    phase_num = 4
    diff = "extreme"
    dps_check = False
    dps_check_hp = 0
    armor = 30
    attack_selc = {1:9, 2:5, 3:4, 4:6}
    phase_hp = {1:350, 2:300, 3:250, 4:200}
    phase_text = {2:"> **「この世界で一番の力を　私は取り込んだ…」**",
                  3:"> **「それもこれもゼ～ンブ ハカイ　ハカイ　ハカイ！ ゼ～ンブ　ハカイだ！！」**",
                  4:"> **「命… 夢… 希望… どこから来て どこへ行く？」**"}
    icon_url = "https://media.discordapp.net/attachments/1081260969256296528/1107164639936131092/8aecc3aa-eabd-3149-9697-56364321f5ac.png"
    Bhp = 350
    Bname = "エンシェント・メイガス"
    musics = {1:{"playtime":262,"link":"mp3/kefka1.m4a"},
              2:{"playtime":222,"link":"mp3/kefka2.m4a"},
              3:{"playtime":200,"link":"mp3/kefka3.m4a"},
              4:{"playtime":365,"link":"mp3/kefka4.m4a"}
              }

    #ここから攻撃選択
    actions = {
        1:{1:{"name":"こころないてんし", "type":"special", "damage":"1d1+0", "text":"全員のHPが1まで減少","desc":"特殊/ 回避・抵抗不可/ 全体"},
            2:{"name":"破壊の翼", "type":"random", "damage":"2d10+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
            3:{"name":"トライン", "type":"all", "damage":"1d20+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
            4:{"name":"ファイガ", "type":"random", "damage":"3d8+3", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
            5:{"name":"破壊の翼", "type":"random", "damage":"2d10+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
            6:{"name":"ブリザガ", "type":"random", "damage":"3d8+3", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
            7:{"name":"たたかう", "type":"random", "damage":"1d16+3", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
            8:{"name":"サンダガ", "type":"random", "damage":"3d8+3", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 単体"},
            },
        2:{1:{"name":"破壊の翼", "type":"random", "damage":"2d10+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
           2:{"name":"ミッシング", "type":"all", "damage":"2d8+1d10+3", "text":"MPが1まで減少","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},     
           3:{"name":"リベンジャー", "type":"special_random", "damage":"1d1+0", "text":"のMPが1まで減少","desc":"特殊/ 回避・抵抗不可/ 単体"},
           4:{"name":"トライン", "type":"all", "damage":"1d20+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
            },
        3:{1:{"name":"ハイパードライブ", "type":"random", "damage":"1d1+59", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗で被ダメ半減/ 単体"},
           2:{"name":"たたかう", "type":"random", "damage":"1d16+6", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
           3:{"name":"たたかう", "type":"all", "damage":"1d12+3", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
        },
        4:{1:{"name":"アルテマ", "type":"all", "damage":"1d1+59", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗で被ダメ半減/ 全体"},
           2:{"name":"ミッシング", "type":"all", "damage":"2d8+1d10+3", "text":"MPが1まで減少","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗不可/ 全体"},
           3:{"name":"たたかう", "type":"random", "damage":"1d16+8", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 物理/ 全防護貫通/ 単体"},
           4:{"name":"ハイパードライブ", "type":"random", "damage":"1d1+59", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 抵抗で被ダメ半減/ 単体"},
           5:{"name":"メテオ", "type":"all", "damage":"1d100+10", "text":"〈キマイラが爪を振り上げる〉","desc":"無属性/ 魔法/ 全防護貫通/ 回避・抵抗不可/ 全体"},
        },
    }

    def __init__(self):
        super().__init__("dummy", 0) # HP, attack, defense, XP, gold
        
#Botログイン時処理
@bot.event
async def on_ready():
    print(f"{bot.user} が起動されました。\n起動時刻:{daytime}")
    
#BGMループ用
@tasks.loop(seconds=1)
async def loop1(ctx,sleeptime,music):
    await asyncio.sleep(sleeptime)
    voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
    ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
    PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1) #可変音源に設定
    voice_client.play(PCMVT) #音楽再生

#辞書の値からキーを取得する関数
def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]
    
#レイド開始コマンド
@bot.command(name="raid")
async def raid_start(ctx, command:str = "0", bgm:str="no"):
    global yes_no
    channelID = str(ctx.channel.id)   # コマンドが実行されたチャンネルIDを取得
    usr_name = ctx.author.display_name #ニックネームを取得
    
    #<-- BGM再生の場合 -->
    if bgm != "no" and channelID not in current_raid:
        
        if command not in raid_ids:
            await ctx.send("`>レイドIDが存在しません`")
            return
        
        if ctx.author.voice is None:
            await ctx.send("`>BGMを再生する場合はボイスチャンネルに参加してください`")
            return     
          
        await ctx.author.voice.channel.connect() #ボイスチャンネルに参加
        voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
        music = "mp3/wait.mp3"
        ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
        PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1) #可変音源に設定
        voice_client.play(PCMVT) #音楽再生
        loop1.start(ctx,124,music)
        
    if channelID not in current_raid: # そのチャンネルでレイドが開始されていない場合
        if command in raid_ids:       # コマンドがレイドIDの指定だった場合
            #---クラス処理関連---
            cls = globals()[command]
            bossData = cls()
            current_raid[channelID] = bossData
            current_raid_member[channelID] = [usr_name]
            current_raid_memstat[channelID] = {usr_name:"生存"}
            print(current_raid_member[channelID])
            print(current_raid_memstat[channelID])
            current_round[channelID] = 1
            boss_round[channelID] = 0
            battle_status[channelID] = "prepare"
            member_status[channelID] = []
            
            await ctx.send(f"**`レイド名: {bossData.raid_name}`**\n`チャンネル: {ctx.channel.name}`\n`?raid join`でレイドに参加後、`?raid start`で戦闘を開始")
            
    else:                             # そのチャンネルでレイドが準備中の場合
        if battle_status[channelID] == "battle":
            await ctx.send("`>戦闘中です`")
            return
        #<-- ユーザー追加 -->
        if command == "join":        
            current_dict = current_raid_member[channelID]
            if usr_name in current_dict:
                await ctx.send("`>既にレイドへ参加しています`")
                return
            current_dict.append(usr_name)
            current_raid_member[channelID] = current_dict
            current_raid_memstat[channelID].update({usr_name:"生存"})
            print(current_raid_memstat[channelID])
            await ctx.send(f"`>{usr_name}を参加者に追加しました`")
            return
            
        elif command in raid_ids:     # ID指定後に再度IDが指定された場合
            await ctx.send("`>既にレイドIDが指定されています`")
            return
        #<-- レイド開始 -->
        elif command == "start":
            # 入力監視用関数
            def check(a):
                return a.channel == ctx.channel and a.author.id != bot.user.id and a.content in yes_no
            
            await ctx.send("`戦闘の準備を開始します。\n確認後、現在の参加者で戦闘が開始されます。\n--------\nよろしいですか？(はい/いいえ)`")
            try:
                a = await bot.wait_for("message", check=check, timeout=120)
            except asyncio.TimeoutError:
                await ctx.send("`>一定時間選択が無かった為、レイドを終了します`")
                del current_raid[channelID], current_raid_member[channelID], current_round[channelID], boss_round[channelID], battle_status[channelID]
                return
            # YES
            else:
                if a.content == "はい":
                    battle_status[channelID] = "battle"
                    total_raid_member[channelID] = current_raid_member[channelID]
                    await ctx.send("`>戦闘を開始します。開始後は以下のコマンドを使用してください`\n`⊖———————————————⊖`\n`?act [数値]ダメージ` - `数値ダメージを与えます`\n`?act 除外` - `死亡した者を除外します`\n`?act 復活` - `蘇生した者を復活させます`\n`?act 完了` - `ターンを完了します。全員が行動後に行ってください`\n`⊖———————————————⊖`")
                    if ctx.message.guild.voice_client != None:
                        loop1.cancel()
                        await FadeOut(ctx)
                    await asyncio.sleep(1)
                    await ctx.send("**3**")
                    await asyncio.sleep(1)
                    await ctx.send("**2**")
                    await asyncio.sleep(1)
                    await ctx.send("**1**")
                    await asyncio.sleep(1)
                    await ctx.send("**START!**")
                    if ctx.message.guild.voice_client != None:
                        bossData = current_raid[channelID]
                        voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
                        music = bossData.musics[bossData.phase]["link"]
                        playtime = bossData.musics[bossData.phase]["playtime"]
                        ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
                        PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1) #可変音源に設定
                        voice_client.play(PCMVT) #音楽再生
                        loop1.start(ctx,playtime,music)
                    await asyncio.sleep(2)
                    await boss_attack(ctx)
                    return
            # NO
                elif a.content == "いいえ":
                    await ctx.send("`>準備を中断します。準備が完了したら再度コマンドを入力してください`")
                    return
                else:
                    print("NaN")
        else:
            await ctx.send("`>コマンドが不正です`")
    
#レイド管理コマンド
@bot.command(name="act")
async def action(ctx, command:str = "0"):
    channelID = str(ctx.channel.id) # コマンドが実行されたチャンネルIDを取得
    # レイドが開始していない場合
    if channelID not in current_raid:
        await ctx.send("`>レイドが開始されていません`")
        return
    
    if battle_status[channelID] == "prepare":
        await ctx.send("`>準備フェーズ中です`")
        return
    
    # 各種値を取得
    usr_name = ctx.author.display_name #ニックネームを取得
    bossData = current_raid[channelID]
    bossName = bossData.Bname
    party_num = len(current_raid_member[channelID])
    
    #<-- レイド参加者名簿に名前がなかった場合 -->
    if usr_name not in total_raid_member[channelID]:
        await ctx.send("`>レイドに参加していません`")
        return
    
    #<-- メンバー除外 -->
    if command == "除外":
        current_dict = current_raid_member[channelID]
        if usr_name not in current_dict:
            await ctx.send(f"`>{usr_name}は既に除外されているか、レイドに参加していません`")
            return
        current_dict.remove(usr_name)
        if len(current_dict) == 0:
            if ctx.message.guild.voice_client != None:
                await loop1.cancel()
                await FadeOut(ctx)
                await ctx.guild.voice_client.disconnect()
            await ctx.send("`>パーティーが全滅した為、レイドを終了します`")
            del current_raid[channelID], current_raid_member[channelID], current_round[channelID], boss_round[channelID], battle_status[channelID], current_raid_memstat[channelID], total_raid_member[channelID]
            return
        current_raid_member[channelID] = current_dict
        current_raid_memstat[channelID].update({usr_name:"死亡"})
        await ctx.send(f"`>{usr_name}を除外しました`")
        return
    
    #<-- メンバー復活 -->
    elif command == "復活":
        current_dict = current_raid_member[channelID]
        if usr_name in current_dict:
            await ctx.send(f"`>{usr_name}は既に復活しています`")
            return
        current_dict.append(usr_name)
        current_raid_member[channelID] = current_dict
        current_raid_memstat[channelID].update({usr_name:"生存"})
        await ctx.send(f"`>{usr_name}を復活させました`")
        return    

    #<-- 行動済みのメンバーだった場合 -->
    if usr_name in member_status[channelID]:
        await ctx.send("`>既に行動を完了しています`")
        return
    
    #<-- ダメージ処理 -->
    if "ダメージ" in command:
        damage_base = int(command.split("ダ")[0])
        #<-- ダメージが100以上200以下の場合、0.7倍 -->
        if 100 < damage_base <= 200:
            damage_base *= 0.7
        #<-- ダメージが200以上400以下の場合、0.5倍 -->
        elif 400 >= damage_base > 200:
            damage_base *= 0.5
        #<-- ダメージが400以上の場合、0.3倍 -->
        elif damage_base > 400:
            damage_base *= 0.3
        final_damage = damage_base - bossData.armor
        if final_damage < 0:
            final_damage = 0
        bossData.Bhp -= final_damage
        await ctx.send(f"`>`**`{usr_name}`**`は`**`{bossName}`**`に`**`{final_damage}`**`ダメージを与えた`\n`残りHP:{bossData.Bhp}`")
        if bossData.Bhp <= 0:
            #<-- 現在フェーズと総フェーズ数が一致すれば -->
            if bossData.phase == bossData.phase_num:
                if ctx.message.guild.voice_client != None:
                    await loop1.cancel()
                    await FadeOut(ctx)
                    await ctx.guild.voice_client.disconnect()
                await asyncio.sleep(1)
                await ctx.send(f"`{usr_name}の一撃により、{bossName}が崩れ落ちる。冒険者たちの勝利だ。`")
                await asyncio.sleep(1)
                await ctx.send("**COMPLETED!**")
                del current_raid[channelID], current_raid_member[channelID], current_round[channelID], boss_round[channelID], battle_status[channelID], current_raid_memstat[channelID], total_raid_member[channelID]
            #<-- 次のフェーズがあれば -->    
            else:
                await asyncio.sleep(1)
                channel = ctx.channel
                bossData.phase += 1
                bossData.Bhp = bossData.phase_hp[bossData.phase]
                boss_round[channelID] = 0
                if ctx.message.guild.voice_client != None:
                    loop1.cancel()
                    await FadeOut(ctx)
                await ctx.send(f"`{usr_name}の一撃が{bossName}に大ダメージを与える。しかし、まだ倒れない。\nそれどころか、より力を増しているようだ...。`")
                await asyncio.sleep(3)
                await ctx.send(f"`>生存している全パーティーメンバーのHP/MPを上限まで回復`")
                #<-- 音楽関係 -->
                if ctx.message.guild.voice_client != None:
                    voice_client = ctx.message.guild.voice_client #ボイスクライアントを指定
                    music = bossData.musics[bossData.phase]["link"] #音楽ファイルを指定
                    playtime = bossData.musics[bossData.phase]["playtime"] #再生時間を指定
                    ffmpeg_audio_source = discord.FFmpegPCMAudio(music) #音源をFFmpegで変換
                    PCMVT = discord.PCMVolumeTransformer(ffmpeg_audio_source, volume=1) #可変音源に設定
                    voice_client.play(PCMVT) #音楽再生
                    loop1.start(ctx,playtime,music)
                
                await asyncio.sleep(3)
                await ctx.send("`――――フェーズ移行――――`")
                await asyncio.sleep(3)
                avatar = bossData.icon_url
                msg_content = bossData.phase_text[bossData.phase]
                webhook = await channel.create_webhook(name="キャラ")
                await webhook.send(content=msg_content, username=bossName, wait=True, avatar_url=avatar)
                await asyncio.sleep(2)
                await webhook.delete()
                await boss_attack(ctx)
                
        return
    
    #<-- ターン完了 -->
    elif command == "完了":
        member_status[channelID].append(usr_name)
        finish_num = len(member_status[channelID])
        await ctx.send(f"`[{finish_num}/{party_num}] {usr_name}がターンを完了した`")
        
        #<-- 全員のターンが完了したら -->
        if finish_num == party_num:
            current_round[channelID] += 1
            latest_round = current_round[channelID]
            member_status[channelID] = []
            await ctx.send(f"`>ラウンド移行`\n**`《ラウンド{latest_round}》`**")
        await boss_attack(ctx)
        return
    
    #<-- 中断処理 -->
    elif command == "中断":
        if ctx.message.guild.voice_client != None:
            await loop1.cancel()
            await FadeOut(ctx)
            await ctx.guild.voice_client.disconnect()
        await ctx.send("`>レイドを中断します`")
        del current_raid[channelID], current_raid_member[channelID], current_round[channelID], boss_round[channelID], battle_status[channelID], current_raid_memstat[channelID], total_raid_member[channelID]
        return
    else:
        await ctx.send("`>コマンドが不正です`")
        return
   
#チャットパレット登録コマンド
@bot.command(name="cr")
async def register(ctx, command:str = "none", trig:str = "none", flavour:str = "なし"):
    global df, dfA
    usr_id = str(ctx.author.id)

    if command == "none":
        await ctx.send("`>コマンドを入力してください`")
        return
    elif trig == "none":
        await ctx.send("`>トリガーを入力してください`")
        return
    
    if re.search(r"[^0-9*.()+-d]",command) != None:
        await ctx.send("正しいコマンドを入力してください")
        return
    
    if int(usr_id) in dfA.index:
        trigger_list = dfA.loc[int(usr_id),"TRIG"]
        if type(trigger_list) != str and type(trigger_list != int):
            trigger_list = trigger_list.values.tolist()
        if trig in trigger_list:
            await ctx.send("`>そのコマンドは既に登録されています`")
            return

    #<-- excelを開く -->
    wb = openpyxl.load_workbook("data/attack.xlsx") 
    ws = wb.worksheets[0]
    rows = int(ws.max_row)+1 #シートの行数
    
    #<-- もし倍率が指定されていれば -->
    if "*" in command:
        reg_com = command.split("*",1)[0]
        reg_com += "+0"
        magni = command.split("*",1)[1]
    else:
        reg_com = command + "+0"
        magni = "none"
        
    #<-- UID/トリガー/コマンド/倍率を登録 -->
    ws.cell(row=rows, column=1).value = usr_id
    ws.cell(row=rows, column=2).value = trig
    ws.cell(row=rows, column=3).value = reg_com
    ws.cell(row=rows, column=4).value = magni
    ws.cell(row=rows, column=5).value = flavour
    wb.save("data/attack.xlsx")

    #<-- データフレームを設定 -->
    dfA = pd.read_excel("data/attack.xlsx")
    df = dfA.set_index(["UID","TRIG"])
    dfA = dfA.set_index("UID")
        
    await ctx.send(f"`>コマンド: {command}をトリガー: {trig}で登録しました`\n`説明: {flavour}`")
    wb.close() #WorkBookをクローズ
    return

#チャットパレット使用コマンド
@bot.command(name="c")
async def chatpaletta(ctx, trigger:str = "none", magni:str = "0", number:int = "1"):
    global df, dfA
    usr_id = str(ctx.author.id)
    sum_list = []
    
    #<-- トリガーが指定されていない場合 -->
    if trigger == "none":
        await ctx.send("`>トリガーを指定してください`")
        return
    
    #<-- UIDが存在しない場合 -->
    if int(usr_id) not in dfA.index:
        await ctx.send("`>コマンドが登録されていません`")
        return
    
    #<-- UIDと紐付いたコマンドが存在しない場合 -->
    trigger_list = dfA.loc[int(usr_id),"TRIG"]
    if type(trigger_list) != str and type(trigger_list != int):
        trigger_list = trigger_list.values.tolist()
        if trigger not in trigger_list:
            await ctx.send("`>そのコマンドは存在しません`")
            return
    
    #<-- 倍率が不正だった場合 -->
    if re.search(r"[^0-9*.]",magni) != None:
        await ctx.send("正しい倍率を入力してください")
        return
    
    #<-- データを取得 -->
    com_body = df.loc[(int(usr_id),trigger),"COM"]
    magni_body = df.loc[(int(usr_id),trigger),"MAGNI"]
    desc = df.loc[(int(usr_id),trigger),"DESC"]
    com = com_body
    final_result = ""
    
    if "++" in com_body:
        separeted = com_body.split("++")
        
    if magni_body != "none":
        com += "ｘ" + str(magni_body)
    if magni != "0" and magni != "1":
        com += "ｘ" + str(magni)
    com = com.replace("+0","")
    
    for i in range(1,int(number)+1):
        #ダイスを振る
        dice_result = str(dice.roll(com_body))
        
        #<-- コマンドに倍率指定があれば -->
        if magni_body != "none":
            magnied = dice_result + "*" + str(magni_body)
            dice_result = round(eval(magnied),2)
        
        #<-- 引数に倍率があれば -->
        if magni != "0":
            dice_magni = str(dice_result) + "*" + str(magni)
            dice_result = round(eval(dice_magni),2)
        sum_list.append(dice_result)
            
        final_result += f"#{i}: ({com}) ＞ {dice_result}\n"
    sum_result = round(sum(sum_list),2)
    await ctx.send(f"`説明:{desc}`\n`コマンド:{com}`\n```\n{final_result}\n```\n`合計:{sum_result}`")
    return

#パーティー確認コマンド
@bot.command(name="party")
async def party_stat(ctx):
    channelID = str(ctx.channel.id) # コマンドが実行されたチャンネルIDを取得
    if channelID not in current_raid_memstat:
        await ctx.send("`>レイドが開始されていません`")
        return
    formated_text = ""
    for k, v in current_raid_memstat[channelID].items():
        formated_text += f"**`{k}`**:**`{v}`**\n"
    await ctx.send(formated_text)

#ステータス登録
@bot.command(name="stat")
async def status_data(ctx):
    usr_id = str(ctx.author.id)
    if usr_id in status:
        status_list = status[usr_id]
        hp = status_list[0]
        mp = status_list[1]
        stamina = status_list[2]
        await ctx.send(f"`現在のステータス:`\n`HP:{hp} | MP:{mp} | スタミナ:{stamina}`")
        return
    else:
        status[usr_id] = [0,0,0]
        await ctx.send(f"`ステータスを登録します。`\n`?hp [数値]` | `?mp [数値]` | `?st [数値]`\nで初期値を入力してください")
        return

#HP変動
@bot.command(name="hp")
async def hitpoint(ctx, num:str = "0"):
    usr_id = str(ctx.author.id)  
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in status:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = status[usr_id]
    if "-" in num:
        stat_list[0] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[0] += int(num.replace("+", ""))
    else:
        stat_list[0] += int(num)
        
    status[usr_id] = stat_list
    current_hp = stat_list[0]
    await ctx.send(f"`HPを{num}変動させました | 現在HP:{current_hp}`")
    return

#MP変動
@bot.command(name="mp")
async def magicpoint(ctx, num:str = "0"):
    usr_id = str(ctx.author.id)  
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in status:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = status[usr_id]
    if "-" in num:
        stat_list[1] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[1] += int(num.replace("+", ""))
    else:
        stat_list[1] += int(num)
    
    status[usr_id] = stat_list
    current_mp = stat_list[1]
    await ctx.send(f"`MPを{num}変動させました | 現在MP:{current_mp}`")
    return

#スタミナ変動
@bot.command(name="st")
async def stamina(ctx, num:str = "0"):
    usr_id = str(ctx.author.id)  
    if re.search(r"[^0-9+-.]",num) != None:
        await ctx.send("`>正しい数値を入力してください`")
        return
    if usr_id not in status:
        await ctx.send("`>ステータスが登録されていません`")
        return
    stat_list = status[usr_id]
    if "-" in num:
        stat_list[2] -= int(num.replace("-", ""))
    elif "+" in num:
        stat_list[2] += int(num.replace("+", ""))
    else:
        stat_list[2] += int(num)
        
    status[usr_id] = stat_list
    current_stmn = stat_list[2]
    await ctx.send(f"`スタミナを{num}変動させました | 現在スタミナ:{current_stmn}`")
    return

#ボス攻撃処理     
@commands.command()
async def boss_attack(ctx):
    channelID = str(ctx.channel.id) # コマンドが実行されたチャンネルIDを取得
    bossData = current_raid[channelID]
    bossName = bossData.Bname
    
    boss_round[channelID] += 1 #現在のラウンドをインクリメント
    #<-- もし攻撃が一巡していたら最初に戻る -->
    if boss_round[channelID] == bossData.attack_selc[bossData.phase]:
        boss_round[channelID] = 1
    turn_count = boss_round[channelID]
    now_turn = turn_count - 1
    
    name_list = bossData.gimmick_name_list[bossData.phase] #ギミック名のリストを取得
    gimmick_data = bossData.actions[bossData.phase][turn_count] #辞書から現在ターンに対応したギミックデータを取得
    desc = gimmick_data["desc"] #攻撃説明
    atk_dmg = gimmick_data["damage"] #ダメージダイス
    texts = gimmick_data["text"] #フレーバーテキスト
    atk_rst = dice.roll(atk_dmg) #攻撃ダメージを取得
    
    #<-- 単体ランダム -->
    if gimmick_data["type"] == "random":
        pc_member = current_raid_member[channelID]
        atk_selc = int(random.randrange(len(pc_member)))
        atk_target = pc_member[atk_selc]
        await ctx.send(f"> **{bossName}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`{atk_target}に{atk_rst}ダメージの攻撃`") 
    #<-- 全体 -->
    elif gimmick_data["type"] == "all":
        await ctx.send(f"> **{bossName}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`全体に{atk_rst}ダメージの攻撃`") 
    #<-- 予兆 -->
    elif gimmick_data["type"] == "announce":
        await ctx.send(f"`>{bossName}{texts}`")
    #<-- 全体特殊攻撃 -->
    elif gimmick_data["type"] == "special":
        await ctx.send(f"> **{bossName}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`{texts}`")
    #<-- 単体特殊攻撃 -->
    elif gimmick_data["type"] == "special_random":
        pc_member = current_raid_member[channelID]
        atk_selc = int(random.randrange(len(pc_member)))
        atk_target = pc_member[atk_selc]
        await ctx.send(f"> **{bossName}**の**『{name_list[now_turn]}』！**\n`{desc}`\n`{atk_target}{texts}`") 

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

@bot.command(name="test")
async def test(ctx):
    channel = ctx.channel
    webhook = await channel.create_webhook(name="試験用")
    await webhook.send(content="テスト",username="テスト",wait=True)

#Bot起動
bot.run("MTEwNTMzNzcxMzk1NzI5NDEwMQ.GRHhuN.CpNn8hppr348Q75awUgfMhUMKh7cgaC8JzSTeA") 