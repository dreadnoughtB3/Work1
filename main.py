import discord
import japanize_matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timezone, timedelta
from discord.ext import tasks
from discord.ext.commands import Bot
import random
import asyncio

addment = 0
addment_F = 0
plus = 0
base = 0
event = False
Crisis = False
current_event = 0
after_event = 0
target_ID = "0"
target_me = "0"
blacklist = ["1076422611325702236","1093041645114622004","1032532645655105536","931562992041099275","1081170888063459368","872546782700273694","1066977490339373076","883332312484446229"]

E = [-25,0,25,50,75,100,125]
eventEffect = [1,2,3,4]
day = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
price = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
economy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
price_F = [43, 48, 52, 58, 65, 71, 87, 54, 49, 43, 58, 62, 79, 92, 46, 49, 105, 90, 62, 43, 114, 58, 81, 76,42]
economy_F = [25, 25, 50, 50, 50, 25, 25, 50, 75, 25, 50, 75, 50, 25, 75, 50, 75, 75, 75, 75, 50,75, 50, 50, 50]
event_list = {1:{"text":"金融引き締め政策の修正","add":20},
              5:{"text":"新興企業のIPO","add":15},
              8:{"text":"大規模公共事業の開始","add":15},
              10:{"text":"石油業界での不況","add":-20},
              15:{"text":"大手銀行での強盗","add":-35},
              20:{"text":"軍需業界での不況","add":-20},
              30:{"text":"住宅業界での不況","add":-20},
              40:{"text":"半導体の値上がり","add":-30},
              50:{"text":"都市銀行の信用不安","add":-20},
              60:{"text":"政策金利の引き上げ","add":-30},
              70:{"text":"政策金利の引き下げ","add":30},
              100:{"text":"投資銀行の危機","add":-50},
              101:{"text":"投資銀行の破綻","add":-90}}

data = [[100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [100,100,100,100,100,100],
        [10,10,10,10,10,10]]

proverb = ["> ***`“君はただ眼で見るだけで、観察ということをしない。見る事と観察する事は大違いなのだよ”`***\n> `――シャーロック・ホームズ、探偵`",
           "> ***`“Hope for the best, but prepare for the worst.`***\n> ***`最高を目指して希望を持ち、最悪に備えて準備せよ“`***\n> `――英国の諺`",
           "> ***`“幸せと賢明さ、この2つの違いは、自分が最も幸せだと思っている人間は本当に幸せだが、自分が最も賢いと思っている人間は大抵、大馬鹿であるという点である。“`***\n> `――チャールズ・カレブ・コルトン、牧師`",
           "> ***`“究極の希望は、究極の苦難から生まれる。“`***\n> `――バートランド・ラッセル、哲学者`",
           "> ***`“楽しい、楽しいクリスマス！子ども時代の幸せな記憶を蘇らせ、また老人は若き日の喜びを思い出す。そして旅人たちは、それぞれの穏やかな家へと帰ってゆく。“`***\n> `――チャールズ・ディケンズ、作家`",
           "> ***`“幸福とは、巧みに騙されている状態が万年続いていることである。“`***\n> `――ジョナサン・スウィフト、随筆家`",
           "> ***`“友情とは翼のない愛である。“`***\n> `――バイロン卿、詩人`",
           "> ***`“自由への愛は他者への愛であり、力への愛は自身への愛である。“`***\n> `――ウィリアム・ハズリット、評論家`",
           "> ***`“全力で国への義務を果たします。“`***\n> `――ヴィクトリア、女王`",
           "> ***`“愚者は経験に学び、賢者は歴史に学ぶ。“`***\n> `――オットー・フォン・ビスマルク、政治家`",
           "> ***`“考慮に入れなくていいことなどひとつもありません。もしある事実が推理と一致しなかったら、そのときはその推理を捨てることです。“`***\n> `――エルキュール・ポアロ、探偵`",
           "> ***`“良兵の少数は多兵に勝る。“`***\n> `――オリバー・クロムウェル、革命家`",
           "> ***`“撃っていいのは撃たれる覚悟のあるやつだけだ。“`***\n> `――フィリップ・マーロウ、探偵`",
           "> ***`“どんなことにも教訓はある。君がそれを見つけられるかどうかさ。“`***\n> `――ルイス・キャロル、作家`",
           "> ***`“あなた方は進歩し続けない限りは退歩していることになるのです。目的を高く掲げなさい。“`***\n> `――フローレンス・ナイチンゲール、看護師`",
           "> ***`“正直は常に最善の策である。“`***\n> `――ジョージ・ワシントン、政治家`",
           "> ***`“一頭の狼に率いられた百頭の羊の群れは、一頭の羊に率いられた百頭の狼の群れにまさる。“`***\n> `――ナポレオン・ボナパルト、軍人`",
           "> ***`“歴史は繰り返す。“`***\n> `――カール・マルクス、思想家`",
           "> ***`“運命は我々の行動の半分を支配し、残りの半分を我々自身にゆだねている。“`***\n> `――ニッコロ・マキャヴェッリ、思想家`",
           "> ***`“皇国の興廃この一戦に在り、各員一層奮励努力せよ。“`***\n> `――東郷平八郎、軍人`",
           "> ***`“天気晴朗なれども波高し。“`***\n> `――秋山真之、軍人`",
           "> ***`“学習は之を終生の事業として為さざるべからず。“`***\n> `――秋山好古、軍人`",
           "> ***`“生き残る種とは最も強いものではない。最も知的なものでもない。それは、変化に最もよく適応したものである。“`***\n> `――チャールズ・ダーウィン、自然科学者`",
           "> ***`“いま正しい事も、数年後間違っていることもある。逆にいま間違っていることも、数年後正しいこともある。“`***\n> `――ライト兄弟、発明家`",
           "> ***`“天才とは、1%のひらめきと99%の努力である。“`***\n> `――トーマス・エジソン、発明家`",
           "> ***`“ある者が「神」と呼ぶものを、他の者は「物理法則」と呼ぶ。“`***\n> `――ニコラ・テスラ、発明家`",
           "> ***`“私は、今こそ我らの時代に平和を求める時であると信じている。“`***\n> `――ネヴィル・チェンバレン、政治家`",
           "> ***`“規律は勝利の母である。“`***\n> `――アレクサンドル・スヴォーロフ、軍人`",
           "> ***`“大胆な者は大胆でない者に対して、つねに勝つ。“`***\n> `――カール・フォン・クラウゼヴィッツ、軍人`",
           "> ***`“計画することがすべてだ。 立てた計画はどうでもいい。“`***\n> `――大モルトケ、軍人`",
           "> ***`“樹木にとって最も大切なものは何かと問うたら、それは果実だと誰もが答えるだろう。しかし実際には種なのだ。„`***\n> `――フリードリヒ・ニーチェ、哲学者`",
           "> ***`“But Who watches the watchmen?`***\n> ***`しかし、誰が見張り役を見張るのか？„`***\n> `――風刺詩第6歌『女性への警告』より`",
            "> ***`“明日花開くのに唯一邪魔になるのは、今日についての疑念だけだ。„`***\n> `――フランクリン・ルーズヴェルト、政治家`",
            "> ***`“強大な力を行使する主権国家が存在する限り、戦争は避け得ない。„`***\n> `――アルバート・アインシュタイン、科学者`",
            "> ***`“成功とは、 失敗に失敗を重ねても、 情熱を失わない能力のことだ。„`***\n> `――ウィンストン・チャーチル、政治家`",
            "> ***`“完璧な計画を来週実行するぐらいなら、次善の計画を今、断固として実行すべきだ。„`***\n> `――ジョージ・S・パットン、軍人`",
            "> ***`“銀行資本は武装した軍隊よりも恐ろしい。„`***\n> `――トーマス・ジェファーソン、政治家`",
            "> ***`“他者を信じるのは良いことだが、そうしないのはもっと良い。„`***\n> `――ベニート・ムッソリーニ、政治家`",
            "> ***`“あなたの名前はわからない。あなたが成した行いは、不滅である。„`***\n> `――無名戦士の墓標`",
            "> ***`“自分に向かって返って来る矢を放ってはならない 。„`***\n> `――クルディスタンの諺`",
            "> ***`“剣によって立つ者、剣によって倒れる。„`***\n> `――マタイによる福音書26章52節`",
            "> ***`“地球は人類の揺籠である。しかし、誰も揺籠の中で永遠に生きられはしない 。„`***\n> `――コンスタンチン・ツィオルコフスキー、科学者`",
            "> ***`“自分の面が曲がっているのに、鏡を責めてなんになる。„`***\n> `――『検察官』`",
            "> ***`“人に噂されるより悪いことが一つだけある。それは噂にされないことだ。„`***\n> `――オスカー・ワイルド、作家`",
            "> ***`“人間に危害を加えない条件下において、自らの存在を維持せよ。„`***\n> `――ロボット工学三原則、第三条`",
            "> ***`“シーザーを理解するのにシーザーである必要はない。„`***\n> `――『理解社会学のカテゴリー』`",
            "> ***`“人は概ね、自分で思うほどには幸福でも不幸でもない。肝心なのは自分で望んだり生きたりするのに飽きないことだ。„`***\n> `――『ジャン・クリストフ』`",
            "> ***`“威厳とは、名誉を得ているという事ではなく、名誉に値するという事から成る。„`***\n> `――アリストテレス、哲学者`",
            "> ***`“世界は偉人達の水準で生きることはできない。„`***\n> `――『金枝篇』`",
            "> ***`“信義に二種あり。秘密を守ると正直を守ると也。両立すべきことにあらず。„`***\n> `――『緑雨警語』`",
            "> ***`“ロバが旅に出たところで馬になって帰ってくるわけではない。„`***\n> `――西洋の諺`",
            "> ***`“幸運が姿を三度現すように、不運もまた三度兆候を示す。„`***\n> `――西洋の諺`",
            "> ***`“愛がなくても人は生きられるが、水がなくても生きられる人はいない。„`***\n> `――W・H・オーデン、詩人`",
            "> ***`“嘘で塗り固められたプロパガンダというのは、それがニセの大義であることの証である。長期的には必ず失敗するものなのだ。„`***\n> `――ヨーゼフ・ゲッベルス、政治家`",
            "> ***`“我は死なり、世界の破壊者なり。„`***\n> `――ロバート・オッペンハイマー、科学者`",
            "> ***`“垣根は相手がつくっているのではなく、自分がつくっている。„`***\n> `――アリストテレス、哲学者`",
            "> ***`“We choose to go to the moon.`***\n> ***`我々は月へ行くと決めた„`***\n> `――ジョン・F・ケネディ、政治家`",
            "> ***`“人に従うことを知らないものは、よき指導者になりえない。„`***\n> `――アリストテレス、哲学者`",
           ]

description = '''テスト用botです'''
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
daytime = now.strftime('%Y/%m/%d %H:%M:%S')

intents = discord.Intents.all() #デフォルトのインテンツオブジェクトを生成
bot = Bot(command_prefix='?',  help_command = None, description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'stock.pyをログインしました: {bot.user} (ID: {bot.user.id})')
    print(daytime)
    loop1.start()
    loop2.start()
    loop3.start()
    print('------')

@tasks.loop(seconds=60)
async def loop1():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_HM = now.strftime('%H:%M')
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    if now_HM != "00:00" and now_HM != "00:01" and now_HM != "12:00" and now_HM != "12:01":
        return
    
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    channel = bot.get_channel(992623803291144244) #チャンネルを指定

    for i in range(6):
        data[0][i] = random.randrange(1,300,1)
        data[1][i] = random.randrange(1,300,1)
        data[2][i] = random.randrange(1,300,1)
        data[3][i] = random.randrange(1,300,1)
        data[4][i] = random.randrange(1,300,1)
        data[5][i] = random.randrange(1,300,1)
        data[6][i] = random.randrange(1,300,1)
        data[7][i] = random.randrange(1,300,1)
        data[8][i] = random.randrange(1,300,1)
        data[9][i] = random.randrange(1,300,1)
        gang = random.randrange(1,100,1)
        if gang <= 30:
            data[10][i] = "X"
        else:
            data[10][i] = "O"

    axis1 = ["AIL", "AME", "L.L.L", "INA", "RUZ", "N.U"]
    axis2 = [">衣類", ">酒類", ">機械", ">資源", ">武器", ">装飾", ">食料", ">書籍", ">絵画", ">宝石", "[ギャング]"]
    
    # ここから表作成----------------------------------------
    # fig準備
    fig = plt.figure(facecolor="white",figsize=(6,2.7), dpi=150)
    ax1 = fig.add_subplot(111)
    
    # 表の定義
    ax1.axis('off')
    ax1.table(cellText=data, cellLoc = "center", colLabels=axis1, rowLabels=axis2, loc="center",colColours=['#ffe278', '#ffe278', '#ffe278','#ffe278', '#ffe278', '#ffe278'])
    
    # レイアウト設定
    fig.tight_layout()
    ax1.set_title("ノクターン - 国際市場:", loc="left",fontsize=23, color="red")
    ax1.set_title(daytime,loc="right", fontsize=11, color="black")
    plt.savefig('economy.png', bbox_inches='tight')
    
    # 表示
    await channel.send(file=discord.File('economy.png'))
    # ---------------------------------------------------
    await asyncio.sleep(120)

@tasks.loop(seconds=60)
async def loop2():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_HM = now.strftime('%H:%M')
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    
    if now_HM != "00:00" and now_HM != "00:01":
        return
    #グローバル変数宣言
    global addment, E, price, economy, day, event, Crisis, current_event, after_event

    #株価
    x = day
    y = price

    #経済状態
    x2 = day
    y2 = economy

    channel = bot.get_channel(946667883168153610) #チャンネルを指定

    #イベント管理
    event_num = random.randrange(1,150,1)
    print(event_list.keys())
    if event_num in event_list.keys() and event == False:
        event = True
        current_event = event_num #イベントIDを保存
        after_event += 1 #イベントが発生してから経過した時間を1に設定
        event_text = event_list[event_num]["text"]
        addment = event_list[event_num]["add"]
    elif event_num == 100 and event == False: #もしイベント番号が100なら
        event = True
        Crisis = True
        current_event = event_num #イベントIDを保存
        after_event += 1 #イベントが発生してから経過した時間を1に設定
        event_text =event_list[event_num]["text"]
        addment = event_list[event_num]["add"]
    elif event == True and Crisis == True and after_event in eventEffect: #もしクライシスがTrueなら
        addment = event_list[101]["add"]
        event_text = event_list[101]["text"]
        after_event += 1
    elif event == True and Crisis == False and after_event in eventEffect: #もしクライシスがFalseなら
        addment = event_list[current_event]["add"]
        event_text = "なし"
        after_event += 1
    else:
        event_text = "なし"
        event = False
        after_event = 0 #イベントが発生してから経過した時間を初期化
        current_event = 0 #現在のイベントIDを初期化
        

    #現在時刻
    if True:
        base = int(random.randrange(25,70,1) + addment) #まず基礎値を決定

        if base>=95:    #基礎値が95以上であれば
            plus = 50   #補正を+50
            keiki = "高度経済成長"  #景気を高度経済成長に
            prices = "+30%"
            addment = 50    #次回基礎値の補正を+50
            economy_lat = 125 #景気値を設定

        elif 75<=base<95:
            plus = 35
            keiki = "バブル"
            prices = "+20%"
            addment = 30
            economy_lat = 100

        elif 60<=base<75:
            plus = 20
            keiki = "好景気"
            prices = "+10%"
            addment = 15
            economy_lat = 75

        elif 30<=base<60:
            plus = 5
            keiki = "通常"
            prices = "なし"
            addment = 5
            economy_lat = 50

        elif 15<base<30:
            plus = -15
            keiki = "不景気"
            prices = "-10%"
            addment = -10
            economy_lat = 25

        elif 5<base<=15:
            plus = -35
            keiki = "暴落"
            prices = "-20%"
            addment = -25
            economy_lat = 0

        elif base<=5:   #基礎値が5以下であれば
            plus = -50
            keiki = "大恐慌"
            prices = "-30%"
            addment = -50
            economy_lat = -25

        Stock = int(random.randrange(15,101,1)) + plus   #株価を決定

        price_lat = Stock
        price.append(price_lat) #株価配列の最後尾に現在の株価を追加
        economy.append(economy_lat) #経済値配列の最後尾に現在の経済値を追加
        del price[0]    #株価配列の最初を削除
        del economy[0]  #経済値配列の最初を削除

        plt.figure(figsize=(9,5)) #図のサイズを指定
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        plt.title("ノクターン - NCSE総合指数",size = 20, color = "red")#グラフタイトル
        plt.title(daytime,loc="right", size = 10)#グラフタイトル
        plt.grid()  # グリッド線の表示 

        plt.text(24.5, 125, '高度経済成長', ha='left', va='center', fontweight="bold") #高度経済用文字列
        plt.text(24.5, 100, 'バブル', ha='left', va='center') #バブル用文字列
        plt.text(24.5, 75, '好景気', ha='left', va='center') #好景気用文字列
        plt.text(24.5, 50, '通常', ha='left', va='center') #通常用文字列
        plt.text(24.5, 25, '不景気', ha='left', va='center') #不景気用文字列
        plt.text(24.5, 0, '暴落', ha='left', va='center') #暴落用文字列
        plt.text(24.5, -25, '恐慌', ha='left', va='center') #大恐慌文字列

        plt.plot(x,y,label="株価",lw=1) #グラフ作成
        plt.fill_between(x, y,-75,alpha=0.2)
        plt.plot(x2,y2,label="経済",lw=1,markersize=3,marker="o") #グラフ作成
        plt.xticks([24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0],
                    ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"]) #x軸の数値を設定
        plt.yticks(range(-75, 175, 25)) #y軸の数値を設定
        plt.tick_params(axis="y", colors="r", labelsize=12)
        plt.legend(loc='lower left', bbox_to_anchor=(1, 1)) #ラベルを表示
        plt.savefig('kabu.png', bbox_inches='tight')
        plt.clf()
        plt.close()

        file = discord.File("kabu.png", filename="kabu.png")
        embed=discord.Embed(title="New Cent Stock Exchange - Report",
                    description="**NCSE総合指数:**\n`――――――――――――――――――――――――――――`",
                    color=0x6E6636)
        embed.set_footer(text="Made by mayonaka | " + daytime)
        embed.add_field(name="`経済情勢:`", value=keiki, inline=True)
        embed.add_field(name="`現在株価:`", value=f"{Stock}G", inline=True)
        embed.add_field(name="`物価変動:`", value=prices, inline=True)
        embed.add_field(name="`ニュース:`", value=event_text, inline=True)
        await channel.send(file=file,embed=embed)
        await asyncio.sleep(120)

@tasks.loop(seconds=60)
async def loop3():
    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    now_HM = now.strftime('%H:%M')
    daytime = now.strftime('%Y/%m/%d %H:%M:%S')
    
    if now_HM != "00:00" and now_HM != "00:01":
        return
    #グローバル変数宣言
    global addment_F, E, day, price_F, economy_F
    #株価
    x = day
    y = price

    #経済状態
    x2 = day
    y2 = economy

    channel = bot.get_channel(992086009061843056) #チャンネルを指定

    #現在時刻
    if True:
        base = int(random.randrange(25,70,1) + addment_F) #まず基礎値を決定

        if base>=95:    #基礎値が95以上であれば
            plus = 50   #補正を+50
            keiki = "経済革命"  #景気を高度経済成長に
            prices = "+30%"
            addment_F = 50    #次回基礎値の補正を+50
            economy_lat = 125 #景気値を設定

        elif 75<=base<95:
            plus = 35
            keiki = "バブル"
            prices = "+20%"
            addment_F = 30
            economy_lat = 100

        elif 60<=base<75:
            plus = 20
            keiki = "好景気"
            prices = "+10%"
            addment_F = 15
            economy_lat = 75

        elif 30<=base<60:
            plus = 5
            keiki = "通常"
            prices = "なし"
            addment_F = 5
            economy_lat = 50

        elif 15<base<30:
            plus = -15
            keiki = "不景気"
            prices = "-10%"
            addment_F = -10
            economy_lat = 25

        elif 5<base<=15:
            plus = -35
            keiki = "暴落"
            prices = "-20%"
            addment_F = -25
            economy_lat = 0

        elif base<=5:   #基礎値が5以下であれば
            plus = -50
            keiki = "大恐慌"
            prices = "-30%"
            addment_F = -50
            economy_lat = -25

        Stock = int(random.randrange(15,101,1)) + plus   #株価を決定

        price_lat = Stock
        price_F.append(price_lat) #株価配列の最後尾に現在の株価を追加
        economy_F.append(economy_lat) #経済値配列の最後尾に現在の経済値を追加
        del price_F[0]    #株価配列の最初を削除
        del economy_F[0]  #経済値配列の最初を削除

        plt.figure(figsize=(9,5)) #図のサイズを指定
        mpl.rcParams['axes.xmargin'] = 0
        mpl.rcParams['axes.ymargin'] = 0
        plt.title("ファンタジア - アスガリア証券取引所",size = 20, color = "red",x=0.42, y=1)#グラフタイトル
        plt.title(daytime,loc="right", size = 10)#グラフタイトル
        plt.grid()  # グリッド線の表示 

        plt.text(24.5, 125, '経済革命', ha='left', va='center', fontweight="bold") #高度経済用文字列
        plt.text(24.5, 100, 'バブル', ha='left', va='center') #バブル用文字列
        plt.text(24.5, 75, '好景気', ha='left', va='center') #好景気用文字列
        plt.text(24.5, 50, '通常', ha='left', va='center') #通常用文字列
        plt.text(24.5, 25, '不景気', ha='left', va='center') #不景気用文字列
        plt.text(24.5, 0, '暴落', ha='left', va='center') #暴落用文字列
        plt.text(24.5, -25, '恐慌', ha='left', va='center') #大恐慌文字列

        plt.plot(x,y,label="株価",lw=1) #グラフ作成
        plt.fill_between(x, y,-75,alpha=0.2)
        plt.plot(x2,y2,label="経済",lw=1,markersize=3,marker="o") #グラフ作成
        plt.xticks([24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0],
                    ["0","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"]) #x軸の数値を設定
        plt.yticks(range(-75, 175, 25)) #y軸の数値を設定
        plt.tick_params(axis="y", colors="r", labelsize=12)
        plt.legend(loc='lower left', bbox_to_anchor=(1, 1)) #ラベルを表示
        plt.savefig('kabu_F.png', bbox_inches='tight')
        plt.clf()
        plt.close()

        file = discord.File("kabu_F.png", filename="kabu_F.png")
        embed=discord.Embed(title="Asgaria Stock Exchange - Report",
                    description="**アスガリア証券取引所:**\n`――――――――――――――――――――――――――――`",
                    color=0x6E6636)
        embed.set_footer(text="Made by mayonaka | " + daytime)
        embed.add_field(name="`経済情勢:`", value=keiki, inline=True)
        embed.add_field(name="`現在株価:`", value=f"{Stock}G", inline=True)
        embed.add_field(name="`物価変動:`", value=prices, inline=True)
        await channel.send(file=file,embed=embed)
        await asyncio.sleep(120)

#CS自動作成機能
@bot.command()
async def auto(ctx):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    """自動作成"""
    pedig = [0,0,0,0,0] #家柄格納
    stat = [0,0,0,0] #ステータスTemp
    #ステータス基礎
    status = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    Zok = {0:"地属性", 1:"花属性", 2:"雪属性", 3:"氷属性", 4:"水属性", 5:"風属性", 6:"炎属性", 7:"雷属性", 8:"光属性", 9:"夜属性", 10:"双属性"}
    Past_Zero = {0:"凡庸", 1:"生存", 2:"悲哀", 3:"愚行", 4:"才能", 5:"血統", 6:"復讐", 7:"不要"}
    Past_One = {0:"孤独", 1:"平凡", 2:"愛情", 3:"禁断", 4:"特別", 5:"苦痛"}
    Past_Two = {0:"暴力", 1:"矜持", 2:"無法", 3:"勤勉", 4:"失意", 5:"憧憬"}
    zokusei = [0,0]

    target = str(ctx.author.id)
    numberauto = 0
    member_mention = f"<@{ctx.author.id}>"
    global target_ID,target_me
    #---家柄---
    if target == target_ID:
    #もしターゲットなら
        if numberauto == 1: #もしターゲットで、かつ振った回数が2回以上なら
            for i in range(5): #家柄算出
                pedig[i] = (random.randrange(15,71,1))          
        else:
            for i in range(5): #家柄算出
                pedig[i] = (random.randrange(15,70,1))  
            pedig[1] = 65
            numberauto = 1
    #もし家柄を100にしたい相手なら
    elif target == target_me:
            for i in range(5): #家柄算出
                pedig[i] = (random.randrange(1,101,1))  
            pedig[2] = 100
    else: #もしターゲット以外なら
        for i in range(5): #家柄算出
            pedig[i] = (random.randrange(1,94,1))
        colum = random.randrange(0,5,1)
        pedig[colum] = random.randrange(81,95,1)

    #---属性---
    for i in range(2):
        att_temp = random.randrange(100)
        if 1 <= att_temp <= 9:
            zokusei[i] = 0
        elif 10 <= att_temp <= 19:
            zokusei[i] = 1
        elif 20 <= att_temp <= 29:
            zokusei[i] = 2
        elif 30 <= att_temp <= 39:
            zokusei[i] = 3
        elif 40 <= att_temp <= 49:
            zokusei[i] = 4
        elif 50 <= att_temp <= 59:
            zokusei[i] = 5
        elif 60 <= att_temp <= 69:
            zokusei[i] = 6
        elif 70 <= att_temp <= 79:
            zokusei[i] = 7
        elif 80 <= att_temp <= 89:
            zokusei[i] = 8
        elif 90 <= att_temp <= 99:
            zokusei[i] = 9
        else:
            zokusei[i] = 10

    Elem1 = zokusei[0]
    Elem2 = zokusei[1]

    #---過去---
    Zero_1 = random.randrange(8)
    Zero_2 = random.randrange(8)
    Zero_3 = random.randrange(8)
    One_1 = random.randrange(6)
    One_2 = random.randrange(6)
    One_3 = random.randrange(6)
    Two_1 = random.randrange(6)
    Two_2 = random.randrange(6)
    Two_3 = random.randrange(6)
    #もし自分なら
    if target == target_me:
        Zero_1 = 2
        One_3 = 4
        Two_3 = 5

    #---基礎値---
    if target == target_ID:
        for u in range(8): #STR~BUSまで8回4d45を振る
            for i in range(4): #それぞれの4d45を振って格納、一番高い数値を採用
                stat[i] = random.randrange(25,33,1)
                stat_h = max(stat)
            status[u] = stat_h + 5
    #もし自分なら
    elif target == target_me:
        for u in range(8): #STR~BUSまで8回4d45を振る
            for i in range(4): #それぞれの4d45を振って格納、一番高い数値を採用
                stat[i] = random.randrange(35,46,1)
                stat_h = max(stat)
            status[u] = stat_h + 5
    else:
        for u in range(8): #STR~BUSまで8回4d45を振る
            for i in range(4): #それぞれの4d45を振って格納、一番高い数値を採用
                stat[i] = random.randrange(1,46,1)
                stat_h = max(stat)
            status[u] = stat_h + 5

    #基礎欄
    base_info = (f"使用者:{member_mention}\n```" + 
                "\n名前:" + 
                "\nレベル:0" + 
                "\n家柄:" +
                str(pedig) +
                "\n種族:" +
                "\n性別:" +
                "\n属性:" + Zok[Elem1] + " or " + Zok[Elem2] +
                "\n人種:" + 
                "\n[過去]" +
                "\n0章:" + Past_Zero[Zero_1] + " or " + Past_Zero[Zero_2] + " or " + Past_Zero[Zero_3] +
                "\n1章:" + Past_One[One_1] + " or " + Past_One[One_2] + " or " + Past_One[One_3] +
                "\n2章:" + Past_Two[Two_1] + " or " + Past_Two[Two_2] + " or " + Past_Two[Two_3] + 
                "\n```")


    #ステータス欄
    final_stat = ("```" +
                "\n筋力:" + str(status[0]) +
                "\n知力:" +  str(status[1]) +
                "\n敏捷:" +  str(status[2]) +
                "\n精神:" +  str(status[3]) +
                "\n体格:" +  str(status[4]) +
                "\n生命:" +  str(status[5]) +
                "\n容姿:" +  str(status[6]) +
                "\n商才:" +  str(status[7]) + 
                "\n```")

    #幸運算出
    luck = 0
    point = 0
    for i in status.values():
        point += i
    luck = (point - status[7]) // 10

    #依存技能値
    Direct_stat = ("```" +
                "\nHP:" + str((status[4] + status[5]) // 5) +
                "\nMP:" + str((status[2] + status[3]) // 5) +
                "\n幸運:" + str(luck) +
                "\nスタミナ:" + str((status[2] + status[5]) // 10) +
                "\n気絶点:" + str((status[4] + status[5]) // 10) +
                "\n依存点:" + str((status[1] + status[3]) // 10) +
                "\n魅力:" + str(status[6]) +
                "\n知識:" + str(status[1]) +
                "\nSAN:" + str(status[3]) +
                "\n基礎技能P:" + str(point) +
                "\nAB:" +
                "\n白兵: " +
                "魔法: " +
                "\n```") 

    #サブステータス
    substat = ("```" + "\nサブステータス:" + "\n膂力:" + "\n叡智:" + "\n体力:" + "\n持久力:" + "\n技量:" + "\n```")
    await ctx.send(base_info)
    await ctx.send(final_stat)
    await ctx.send(Direct_stat)
    await ctx.send(substat)
    print(">>誰かがautoを降りました")

@bot.command()
async def settarget(ctx,target_id:str,mode:str="enemy"):
    global target_ID,target_me
    if mode == "enemy":
        target_ID = target_id
        await ctx.send("エネミーターゲットを設定しました")
    elif mode == "me":
        target_me = target_id
        await ctx.send("味方ターゲットを設定しました")
    else:
        await ctx.send("引数エラー")        

#クリティカル自動表示機能
@bot.command()
async def ct(ctx):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    dice = random.randrange(2)
    if(dice == 0):
        await ctx.reply("```\n" + "①重撃\n└ ダメージ2倍" + "\n```") 

    if(dice == 1):
        await ctx.reply("```\n" + "②連撃\n└即時追加ターン（追加ターンなのでアイテム使用なども行えます）" + "\n```", mention_author=True)

#ファンブル自動表示機能
@bot.command()
async def fn(ctx):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    dice = random.randrange(3)
    if(dice == 0):
        await ctx.reply("```\n" + "①深傷\n└1ターン行動不能、敵からの被ダメージ2倍" + "\n```") 

    if(dice == 1):
        await ctx.reply("```\n" + "②破損\n└武器の耐久値-2、3ターン攻撃不可（攻撃不可になるのは事前に行使していた攻撃手段となる。魔法・格闘も含まれる）" + "\n```", mention_author=True)
    
    if(dice == 2):
        await ctx.reply("```\n" + "③挫折\n└2ターン全行動不可能" + "\n```")


#修理コマンド
@bot.command()
async def repair(ctx, num:int, skill:int, current:int = 0,max:int = 0):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    suc = 0
    fail = 0
    crit = 0
    fanb = 0
    hitpoint = 0
    for i in range(num):
        rolled = random.randrange(1,101,1)
        if rolled < skill-5: #成功
            suc += 1
            hitpoint += 1
        elif skill < rolled < 96: #失敗
            fail += 1
            hitpoint -= 0
        elif skill-5 <= rolled <= skill:
            crit += 1
            hitpoint += 2
        elif rolled >= 96:
            fanb += 1
            hitpoint -= 2

    await ctx.reply(f"> {num}回修理を行いました\n`成功:{suc}回 失敗:{fail}回 クリティカル:{crit}回 ファンブル:{fanb}回`\n`耐久変動: {hitpoint}`")
    if max != 0:
        current += hitpoint
        await ctx.send(f"`現在の装備耐久:{current}/{max}`")

#ブラックリストコマンド
@bot.command()
async def black(ctx, mode:str = "表示", ID:str=""):
    global blacklist
    if mode == "追加":
        blacklist.append(ID)
    elif mode == "削除":
        blacklist.remove(ID)
    elif mode == "表示":
        intel = ""
        for i in range(len(blacklist)):
            usr_id = int(blacklist[i])
            user = await bot.fetch_user(usr_id)
            intel += f"stock - {i}. ユーザー名:{user.name}{user.discriminator}\n "
        await ctx.send(intel)

#名言集
@bot.command()
async def saying(ctx):
    if str(ctx.author.id) in blacklist:
        #await ctx.send("discord.ext.error:The user is Persona non grata by faithlessness")
        return
    lengs = len(proverb)
    ran = random.randrange(lengs)
    await ctx.send(proverb[ran])

bot.run('MTA3MjEwODcxNDAxNTg3MTAzNw.G6Tqbr.OQkLB7Gsm7VOohETEzBKGNq7OdmRDfaoTVfJmY')
