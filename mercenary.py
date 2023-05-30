#必要なライブラリをインポート
import discord
from discord import Intents, Client, Interaction, Member, ButtonStyle
from datetime import datetime, timezone, timedelta
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import random, dice, asyncio
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gc as garbage

#スプレッドシート関連
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
json = 'strl-380010-d9b3efdea4a1.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json, scope)
gc = gspread.authorize(credentials)
SPREADSHEET_KEY = '1vXe0TvwhgoOypM4xGF-fkQPYSNaLwTJVN06LmonCfoA'
workbook = gc.open_by_key(SPREADSHEET_KEY)
wolfs = workbook.worksheet("傭兵会社")
wolfsU = workbook.worksheet("部隊マスター")

blacklist = ["1048913629187166248","1076422611325702236","1081170888063459368","827536336130932748","861519462183206921","1032532645655105536"]

operations = {"ops1":{"ops_name":"`現地武装組織排除`","enemy_name":"ローグ・コヨーテ","units":["unit_infsqd_ery"],
            "reward":10},
              "ops2":{"ops_name":"`対応部隊撃破`","enemy_name":"ローグ・コヨーテ","units":["unit_infsqd_mid","unit_infsqd_ery"],
            "reward":15},
              "ops3":{"ops_name":"`哨戒陣地制圧`","enemy_name":"ローグ・コヨーテ","units":["unit_infsqd_mid","unit_artplt_ery"],
            "reward":20},
              "ops4":{"ops_name":"`FOB制圧`","enemy_name":"ローグ・コヨーテ","units":["unit_infsqd_mid","unit_infsqd_mid","unit_artplt_ery","unit_artplt_ery"],
            "reward":40},
              "ops5":{"ops_name":"`輸送車列襲撃`","enemy_name":"ゼロリスク・セキュリティ","units":["unit_motplt_ery","unit_motplt_ery","unit_tankplt_ery"],
            "reward":35},
              "ops6":{"ops_name":"`戦車小隊撃滅`","enemy_name":"ゼロリスク・セキュリティ","units":["unit_tankplt_ery","unit_tankplt_ery"],
            "reward":30},
              "ops7":{"ops_name":"`火箭を制す`","enemy_name":"ゼロリスク・セキュリティ","units":["unit_artplt_ery","unit_artplt_ery","unit_artplt_ery"],
            "reward":30},
              "ops8":{"ops_name":"`ゲリラ殲滅`","enemy_name":"現地武装組織","units":["unit_guerilla_ery","uunit_guerilla_ery","unit_guerilla_apc"],
            "reward":35},
              "opsnz1":{"ops_name":"`所属不明部隊撃破`","enemy_name":"不明","units":["unit_nazi_sqd","unit_nazi_sqd"],
            "reward":20},
            }

in_ops = []

#ユニット用クラス
class unit:
    
    def __init__(self,ID, age, name, fire, range, speed, type, hp, genre):
        self.ID = ID
        self.age = age
        self.name = name
        self.fire = fire
        self.range = range
        self.speed = int(speed)
        self.type = type
        self.hp = int(hp)
        self.genre = genre
        self.status = "alive"

    def under_attack(self,damage,attack_type):
        final_damage = int(damage)
        return_data = []
        #ハードタイプのユニットならダメージを2割軽減
        if self.type == "hard": 
            final_damage *= 0.8
        #距離によるダメージ減少を計算
        if attack_type == "近" and self.range == "中":
            final_damage *= 0.8
        elif attack_type == "近" and self.range == "遠":
            final_damage *= 0.6
        elif attack_type == "中" and self.range == "遠":
            final_damage *= 0.8
        self.hp -= int(final_damage)
        print(f"減少量:{final_damage}")
        #ユニットの生死を判定
        if self.hp <= 0:
            return_data.append("dead")
        else:
            return_data.append("alive")
        return_data.append(final_damage)
        return return_data
    
    def attack(self,target_type):
        damage = 0
        attackpower = self.fire.split("/")
        if target_type == "ground":
            damage = dice.roll(attackpower[0])
        elif target_type == "navy":
            damage = dice.roll(attackpower[1])
        elif target_type == "air":
            damage = dice.roll(attackpower[2])
        return damage
    
    def __del__(self):
        print(f"{self.name}: インスタンス破棄")

#Bot関連設定
description = "Emeth V1.3"
intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?', description=description, help_command=None, intents=intents)

#傭兵会社登録
@bot.command()
async def company(ctx, company_name:str = "NaN", aide_name:str = "副官",aida_tone:str = "1"):
    usr_id = str(ctx.author.id) #ユーザーIDを取得
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #傭兵会社名が入力されていなければ
    if company_name == "NaN":
        await ctx.send("> `エラー:傭兵会社名を入力してください`")
        return
    #UIDが2列目にあれば
    if usr_id in wolfs.col_values(2):
        await ctx.send("> `エラー:既に登録されています`")
        return
    company_id = random.randrange(1,9999,1) #企業IDを生成
    wolfs.append_row([ctx.author.name,usr_id,str(company_id),company_name,"30","1",aide_name,aida_tone,"5"]) #基礎データ登録
    wolfs.append_row([ctx.author.name,str(company_id)+"F","fcl_mb_lv1"]) #初期施設データ登録
    wolfs.append_row([ctx.author.name,str(company_id)+"U","unit_infsqd_ery"]) #初期部隊データ登録
    await ctx.send(f"`傭兵会社名:{company_name}`\n`副官名:{aide_name}`\n`副官の口調:{aida_tone}`\n以上のデータを登録しました。")

#マザーベース確認用コマンド
@bot.command()
async def base(ctx):
    usr_id = str(ctx.author.id) #ユーザーIDを取得
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #表示用リストを定義
    facility_list = []
    unit_list = []
    counter = 0
    #UIDが2列目になければ
    if usr_id not in wolfs.col_values(2):
        await ctx.send("> `エラー:傭兵会社を設立していません`")
        return
    
    #データフレームを生成
    basedf = pd.DataFrame(wolfs.get_all_values()[1:],columns=wolfs.get_all_values()[0])
    basedfA = basedf.set_index("IDs")
    unitdf = pd.DataFrame(wolfsU.get_all_values()[1:],columns=wolfsU.get_all_values()[0])
    unitdfA = unitdf.set_index("ID")
    facilityDF = unitdf.set_index("FID")
    company_name = basedfA.at[usr_id,'傭兵会社名'] #会社名を取得
    company_ID = basedfA.at[usr_id,"傭兵会社ID"] #傭兵会社ID
    skip_name = basedfA.at[usr_id,"識別(ユーザー名)"]
    current_MC = basedfA.at[usr_id,"所持金"] #所持金
    level = basedfA.at[usr_id,"レベル"] #所持金
    sortie = basedfA.at[usr_id, "出撃回数"]
    lv1_in = ["dummy"]
    #---施設を取得---
    facility_body = basedfA.loc[company_ID+"F"] 
    for item in facility_body:
        if item == skip_name or item == "":
            continue
        name = facilityDF.at[item,"施設名"]
        facility_list.append("- "+name)
    #---施設一覧を整形
    if any(s.endswith("LV2") for s in facility_list):
        nored = [i  for i in facility_list if "LV2" in i]
        for i in range(len(nored)):
            name_body = nored[i]
            sliced = name_body[:-3]
            facility_list.remove(sliced+"LV1")
    if any(s.endswith("LV3") for s in facility_list):
        nored = [i  for i in facility_list if "LV3" in i]
        for i in range(len(nored)):
            name_body = nored[i]
            sliced = name_body[:-3]
            facility_list.remove(sliced+"LV2")
    #---ユニットを取得---
    unit_body = basedfA.loc[company_ID+"U"]
    for item in unit_body:
        if item == skip_name or item == "":
            continue
        name = unitdfA.at[item,"部隊名"]
        counter += 1 #カウンターを1増やす
        unit_list.append(f"{counter}:"+name)
    #---不要になったdfを削除---
    del basedf
    del basedfA
    del unitdf
    del unitdfA
    embed=discord.Embed(title="マザーベース",
                    description=f"```民間軍事会社:{company_name}の本拠地\nレベル: {level} | 軍票: {current_MC}MC | 残出撃回数: {sortie}回```",
                    color=0x6E6636)
    embed.add_field(name="`施設:`", value='\n'.join(map(str, facility_list)), inline=True)
    embed.add_field(name="`部隊:`", value='\n'.join(map(str, unit_list)), inline=True)
    embed.set_image(url="https://media.discordapp.net/attachments/1091038645898723458/1091615246298394705/gamesdk_2015-08-27_13-34-30-08.png")  
    await ctx.send(embed=embed) #ヘッダー表示
    #ガーベージコレクションを解放
    garbage.collect()
    
#部隊配備コマンド
@bot.command()
async def deploy(ctx,unit_name:str = "NaN"):
    usr_id = str(ctx.author.id) #ユーザーIDを取得
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #UIDが2列目になければ
    if usr_id not in wolfs.col_values(2):
        await ctx.send("> `エラー:傭兵会社を設立していません`")
        return
    if unit_name == "NaN":
        await ctx.send("> `エラー:部隊名を入力してください`")
        return
    if unit_name not in wolfsU.col_values(3):
        await ctx.send("> `エラー:部隊名が不正です`")
        return
    
    unit_list = []
    facility_list = []
    
    #必要なデータフレームを生成
    basedf = pd.DataFrame(wolfs.get_all_values()[1:],columns=wolfs.get_all_values()[0])
    basedfA = basedf.set_index("IDs")
    unitdf = pd.DataFrame(wolfsU.get_all_values()[1:],columns=wolfsU.get_all_values()[0])
    unitdfA = unitdf.set_index("部隊名")

    company_ID = basedfA.at[usr_id,"傭兵会社ID"] #傭兵会社ID
    skip_name = basedfA.at[usr_id,"識別(ユーザー名)"] #識別名
    current_MC = basedfA.at[usr_id,"所持金"] #所持金

    #保有施設ID一覧を取得
    facility_body = basedfA.loc[company_ID+"F"] 
    for item in facility_body:
        if item == skip_name or item == "":
            continue
        facility_list.append(item)

    #ユニット名からIDと値段と必要施設を取得
    unit_id = unitdfA.at[unit_name,"ID"] #ユニットID
    unit_price = unitdfA.at[unit_name,"値段"] #ユニット価格
    unit_require = unitdfA.at[unit_name,"必要施設"] #ユニット要求施設

    if unit_require not in facility_list:
        await ctx.send("> `エラー:必要な施設がありません`")
        return
    
    latest_MC = int(current_MC) - int(unit_price)

    if latest_MC < 0:
        await ctx.send("> `エラー:軍票が足りません`")
        return        
    
    #保有ユニットID一覧を取得
    unit_body = basedfA.loc[company_ID+"U"]
    for item in unit_body:
        if item == skip_name or item == "":
            continue
        unit_list.append(item)

    unit_target = wolfs.find(company_ID+"U")
    #保有ユニットを一度クリア
    wolfs.batch_clear([f"C{unit_target.row}:L{unit_target.row}"])
    #保有ユニットリストに購入したユニットIDを追加
    unit_list.append(unit_id)
    #更新
    wolfs.append_row(unit_list,table_range=f'C{unit_target.row}')

    target_ind = (basedfA.index.get_loc(usr_id)) + 2
    target_clm = 5
    wolfs.update_cell(target_ind,target_clm,latest_MC)
    await ctx.send(f"> `{unit_name}を配備しました。`\n`残金:{latest_MC}MC`")
    del basedf,basedfA,unitdf,unitdfA

#施設建設コマンド
@bot.command()
async def build(ctx,facility_name:str="NaN"):
    usr_id = str(ctx.author.id) #ユーザーIDを取得
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #UIDが2列目になければ
    if usr_id not in wolfs.col_values(2):
        await ctx.send("> `エラー:傭兵会社を設立していません`")
        return
    if facility_name == "NaN":
        await ctx.send("> `エラー:施設名を入力してください`")
        return
    if facility_name not in wolfsU.col_values(16):
        await ctx.send("> `エラー:施設名が不正です`")
        return
    
    facility_list = []

    #必要なデータフレームを生成
    basedf = pd.DataFrame(wolfs.get_all_values()[1:],columns=wolfs.get_all_values()[0])
    basedfA = basedf.set_index("IDs")
    unitdf = pd.DataFrame(wolfsU.get_all_values()[1:],columns=wolfsU.get_all_values()[0])
    unitdfA = unitdf.set_index("施設名")

    company_ID = basedfA.at[usr_id,"傭兵会社ID"] #傭兵会社ID
    skip_name = basedfA.at[usr_id,"識別(ユーザー名)"] #識別名
    current_MC = basedfA.at[usr_id,"所持金"] #所持金

    #保有施設ID一覧を取得
    facility_body = basedfA.loc[company_ID+"F"] 
    for item in facility_body:
        if item == skip_name or item == "":
            continue
        facility_list.append(item)

    #施設名からIDと値段と必要施設を取得
    facility_id = unitdfA.at[facility_name,"FID"] #ユニットID
    facility_price = unitdfA.at[facility_name,"施設値段"] #ユニット価格
    facility_require = unitdfA.at[facility_name,"前提施設"] #ユニット要求施設
    #もし建設済みなら
    if facility_id in facility_list:
        await ctx.send("> `エラー:既に建設済みです`")
        return  
    #もし前提施設が複数なら
    if "/" in facility_require:
        facility_require_list = facility_require.split("/")     
        for i in range(2):
            if facility_require_list[i] not in facility_list:
                await ctx.send("> `エラー:必要な施設がありません`")
                return
    else:
        if facility_require not in facility_list:
            await ctx.send("> `エラー:必要な施設がありません`")
            return
    
    latest_MC = int(current_MC) - int(facility_price)

    if latest_MC < 0:
        await ctx.send("> `エラー:軍票が足りません`")
        return 
    
    facility_target = wolfs.find(company_ID+"F")
    #保有施設を一度クリア
    wolfs.batch_clear([f"C{facility_target.row}:L{facility_target.row}"])
    #保有施設リストに建設した施設IDを追加
    facility_list.append(facility_id)
    #更新
    wolfs.append_row(facility_list,table_range=f'C{facility_target.row}')

    target_ind = (basedfA.index.get_loc(usr_id)) + 2
    target_clm = 5
    wolfs.update_cell(target_ind,target_clm,latest_MC)
    await ctx.send(f"> `{facility_name}を建設しました。`\n`残金:{latest_MC}MC`")
    del basedf,basedfA,unitdf,unitdfA

#作戦コマンド
@bot.command()
async def ops(ctx,ops_id:str = "NaN",units:str="NaN"):
    usr_id = str(ctx.author.id) #ユーザーIDを取得
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    #UIDが2列目になければ
    if usr_id not in wolfs.col_values(2):
        await ctx.send("> `エラー:傭兵会社を設立していません`")
        return
    if ops_id == "NaN":
        await ctx.send("> `エラー:作戦IDを入力してください")
        return
    if units == "NaN":
        await ctx.send("> `エラー:投入ユニットを入力してください")
        return
    if units.endswith(","):
        await ctx.send("> `エラー:末尾に,を書かないでください`")
        return    
    if usr_id in in_ops:
        await ctx.send("> `エラー:既に作戦を実行中です`")
        return            
    #必要な変数の初期定義
    unit_list = []
    units_splited = []
    player_units_name = []
    enemy_units_name = []
    player_units_class = []
    enemy_units_class = []
    units_ID_list = []
    e_totalspd = 0
    f_totalspd = 0
    enemy_units = operations[ops_id]["units"]
    enemy_name = operations[ops_id]["enemy_name"]
    current_turn = 0
    in_ops.append(usr_id)

    #---投入部隊数が一つの場合    
    if len(units) == 2:
        units_splited.append(units)      
    else:
        units_splited = units.split(",")
        if len(units_splited) > 5:
            await ctx.send("> `エラー:5部隊以上は投入できません`")
            in_ops.remove(usr_id)
            return 

    #必要なデータフレームを生成
    basedf = pd.DataFrame(wolfs.get_all_values()[1:],columns=wolfs.get_all_values()[0])
    basedfA = basedf.set_index("IDs")
    unitdf = pd.DataFrame(wolfsU.get_all_values()[1:],columns=wolfsU.get_all_values()[0])
    unitdfA = unitdf.set_index("ID")

    #不要なデータフレームを削除
    del basedf, unitdf

    #必要なIDを取得
    company_ID = basedfA.at[usr_id,"傭兵会社ID"] #傭兵会社ID
    skip_name = basedfA.at[usr_id,"識別(ユーザー名)"]
    company_name = basedfA.at[usr_id,'傭兵会社名'] #会社名を取得
    sortie = basedfA.at[usr_id, "出撃回数"]

    #保有ユニット一覧を取得
    unit_body = basedfA.loc[company_ID+"U"]
    for item in unit_body:
        if item == skip_name or item == "":
            continue
        unit_list.append(item)
    print(unit_list)

    if int(sortie) == 0:
        await ctx.send("> `エラー:出撃可能回数が0です`")
        in_ops.remove(usr_id)
        return        

    for i in range(len(units_splited)):
        if int(units_splited[i]) > len(unit_list):
            await ctx.send("> `エラー:投入できないユニットが存在します`")
            in_ops.remove(usr_id)
            return

    #ユニットの実態を生成
    for i in range(len(units_splited)):
        class_arg = []
        class_name = company_ID+"F"+str(i)
        unit_num = int(units_splited[i])-1
        data_series = unitdfA.loc[unit_list[unit_num],['時代(U)','部隊名','火力','射程','速度','タイプ','HP(U)','ジャンル']]
        class_arg.append(unit_list[unit_num])
        for item in data_series:
            class_arg.append(item)
        class_name = unit(*class_arg)
        player_units_class.append(class_name)
    ##---投入ユニットのIDを取得---
    for i in range(len(player_units_class)):
        units_ID_list.append(player_units_class[i].ID)
    #敵ユニットの実体を生成
    for d in range(len(enemy_units)):
        class_arg = []
        class_name = company_ID+"E"+str(d) #クラス名を定義
        data_series = unitdfA.loc[enemy_units[d],['時代(U)','部隊名','火力','射程','速度','タイプ','HP(U)','ジャンル']]
        class_arg.append(enemy_units[d]) #ユニットIDを追加
        for item in data_series:
            class_arg.append(item)
        class_name = unit(*class_arg)
        enemy_units_class.append(class_name)
    del unitdfA

    #先行決め
    for i in range(len(units_splited)):
        f_spd = player_units_class[i].speed
        f_totalspd += int(f_spd)
        player_units_name.append(player_units_class[i].name)
    for i in range(len(enemy_units)):
        e_spd = enemy_units_class[i].speed
        e_totalspd += int(e_spd)
        enemy_units_name.append(enemy_units_class[i].name)
    player_base_spd = (random.randrange(1,10,1))+f_totalspd
    enemy_base_spd = random.randrange(1,10,1)+e_totalspd
    await ctx.send(operations[ops_id]["ops_name"])
    await ctx.send(f"> **{company_name}:**\n```\n- "+'\n- '.join(map(str, player_units_name))+"\n```\n　　　VS")
    await ctx.send(f"-\n> **{enemy_name}:**\n```\n- "+'\n- '.join(map(str, enemy_units_name))+"\n```")    
    if player_base_spd > enemy_base_spd:
        await ctx.send("`プレイヤー側先攻`")
        first = "ply"
    else:
        await ctx.send("`エネミー側先攻`")
        first = "eny"

    while True:
        current_turn += 1
        await ctx.send(f"――――――――――――――――――\n**>{current_turn}ターン目:**")
        #プレイヤー側の攻撃処理
        await ctx.send(f"> {company_name}側の攻撃")
        for i in range(len(player_units_class)):
            if first == "eny" and current_turn == 1:
                await ctx.send(">`エネミー側先攻の為スキップ`")
                break
            f_unit_name = player_units_class[i].name
            #攻撃対象を選択(0を出せないので結果に-1)
            target_selc = (random.randrange(1,len(enemy_units_class)+1,1))-1
            #対象のタイプと名前を取得
            target_type = enemy_units_class[target_selc].genre
            target_name = enemy_units_class[target_selc].name
            #攻撃メソッドにタイプを渡して呼び出し、ダメージを計算
            attack_damage = player_units_class[i].attack(target_type)
            print(f"ダメージ:{attack_damage}")
            #攻撃側の射程を取得
            attack_range = player_units_class[i].range
            #攻撃対象の被攻撃メソッドにダメージと射程を渡して呼び出し
            attack_result = enemy_units_class[target_selc].under_attack(attack_damage,attack_range)
            #もし攻撃によって対象が撃破されたらリストから削除
            await asyncio.sleep(3)
            if attack_result[0] == "dead":
                del enemy_units_class[target_selc]
                await ctx.send(f"`{f_unit_name}`：`{target_name}`に攻撃->`{attack_result[1]}`ダメージ\n>`撃破`")
            else:
                await ctx.send(f"`{f_unit_name}`：`{target_name}`に攻撃->`{attack_result[1]}`ダメージ") 
            if len(enemy_units_class) == 0:
                break       
        if len(enemy_units_class) == 0:
            break            
        #敵側の攻撃処理
        await ctx.send(f"> {enemy_name}側の攻撃")
        for i in range(len(enemy_units_class)):
            e_unit_name = enemy_units_class[i].name
            target_selc = (random.randrange(1,len(player_units_class)+1,1))-1
            target_type = player_units_class[target_selc].genre
            target_name = player_units_class[target_selc].name            
            attack_damage = enemy_units_class[i].attack(target_type)
            print(f"ダメージ:{attack_damage}")
            #攻撃側の射程を取得
            attack_range = enemy_units_class[i].range
            #攻撃対象の被攻撃メソッドにダメージと射程を渡して呼び出し
            attack_result = player_units_class[target_selc].under_attack(attack_damage,attack_range)
            #もし攻撃によって対象が撃破されたらリストから削除
            await asyncio.sleep(3)
            if attack_result[0] == "dead":
                del player_units_class[target_selc]
                await ctx.send(f"`{e_unit_name}`：`{target_name}`に攻撃->`{attack_result[1]}`ダメージ\n>`撃破`")
            else:
                await ctx.send(f"`{e_unit_name}`：`{target_name}`に攻撃->`{attack_result[1]}`ダメージ") 
            if len(player_units_class) == 0:
                break   
        if len(player_units_class) == 0:
            break     
    #戦闘終了後処理
    await asyncio.sleep(3)
    if len(player_units_class) == 0:
        await ctx.send(f"――――――――――――――――――\n**戦闘終了**\n`{enemy_name}の勝利`")
        del enemy_units_class
        clear_target = wolfs.find(company_ID+"U")
        #保有ユニットを一度クリア
        wolfs.batch_clear([f"C{clear_target.row}:L{clear_target.row}"])
        #リスト化した保有ユニットから損失ユニットを抜く 
        for i in range(len(units_splited)):
            del_id = units_ID_list[i]
            unit_list.remove(del_id)
        #損失ユニットを抜いたリストで更新
        wolfs.append_row(unit_list,table_range=f'C{clear_target.row}')
    else:
        reward = operations[ops_id]["reward"]
        await ctx.send(f"――――――――――――――――――\n**戦闘終了**\n`{company_name}の勝利`")   
        await ctx.send(f"報酬:{reward}MC") 
        current_MC = int(basedfA.at[usr_id,"所持金"]) #所持金
        current_MC += int(reward)
        target_ind = (basedfA.index.get_loc(usr_id)) + 2
        target_clm = 5
        wolfs.update_cell(target_ind,target_clm,current_MC)
        del player_units_class
    current_sortie = int(sortie) - 1
    target_ind = (basedfA.index.get_loc(usr_id)) + 2
    target_clm = 9
    wolfs.update_cell(target_ind,target_clm,current_sortie)
    in_ops.remove(usr_id)
    del enemy_units_name, enemy_units

#軍票をゴールドに換金
@bot.command()
async def cash(ctx,money:str="NaN"):
    usr_id = str(ctx.author.id)
    if usr_id in blacklist:
        await ctx.send("[ERROR] discord.ext.commands.bot: Ignoring exception in command None")
        return
    if usr_id not in wolfs.col_values(2):
        await ctx.send("> `エラー:傭兵会社を設立していません`")
        return
    #データフレームを生成
    basedf = pd.DataFrame(wolfs.get_all_values()[1:],columns=wolfs.get_all_values()[0])
    basedfA = basedf.set_index("IDs")
    current_MC = basedfA.at[usr_id,"所持金"] #所持金
    latest_MC = int(current_MC) - int(money) #変動後の所持金
    if latest_MC < 0:
        await ctx.send("> `エラー:軍票が足りません`")
        return
    money_change = int(money) * 20 #変換したゴールド
    
    target_ind = (basedfA.index.get_loc(usr_id)) + 2
    target_clm = 5
    wolfs.update_cell(target_ind,target_clm,latest_MC)
    await ctx.reply(f"`> {money}MCを{money_change}Gに変換しました。`\n`残金:{latest_MC}MC`")
    del basedf,basedfA

bot.run("MTA3MjEwODcxNDAxNTg3MTAzNw.G6Tqbr.OQkLB7Gsm7VOohETEzBKGNq7OdmRDfaoTVfJmY")