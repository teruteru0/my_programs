#! python3
# -*- coding: utf-8 -*-

'''
手順
１．tkinterをインポート
２．メインウィンドウの作成
３．Widget(ボタンやラベルなど)の作成、設置
４．イベントループ

もしできるならAIに機械学習させてみる
'''

import tkinter as tk
import random


class shogi(tk.Tk):
    def __init__(self):
        super(shogi , self).__init__()
        self.title('はさみ将棋')
        self.geometry("{}x{}+{}+{}".format(400, 400, 300, 100))
        self.resizable(width=0, height=0)
#        self.iconbitmap("hasami_shogi.ico") titleのアイコン設定

        self.flag = False
        self.turn = 1
        self.unpressed = 1 # 自分の駒が選択されているかどうか、選択＝True
        self.previous_tag = None
        self.current_tag = None
        self.tmp = []
        self.candidates = []
        self.retrieves = []
        self.rtmp = []
        self.rflag = False
        self.result = [0, 0]
        self.lock = 0 # 
        self.enlock = 0


        # Canvasの設定
        self.Widgets() #ボタン配置を表示


    def run(self):
        self.mainloop() # 処理待ち状態を作る


    def Widgets(self):
        # 将棋盤を作る---------------------------------------------------------------
        self.board = tk.Canvas(self, width=400, height=400, bg="Peach Puff3")
        self.board.pack() # メインウィンドウに貼り付け


        # 長方形　-------------------------------------------------------------------
        #将棋盤の情報
        # -1 -> 盤の外, 0 -> 空白
        self.board_2_info = [-1] * 11 + [[0, -1][i in [0, 10]]\
            for i in range(11)] * 9 + [-1] * 11
            # [[0, -1][False=0, True=1の判定] for i in range(11)]の内包表記


        # {tag: position}　位置を定義
        self.tag_2_pos = {}


        # 座標からtagの変換 1次元の座標を符号変換する
        self.z_2_tag = {}


        # 符号
        self.numstr = "123456789"
        self.kanstr = "一二三四五六七八九"
        for i , y in zip(self.kanstr, range(20, 380, 40)):
            for j , x in zip(self.numstr[::-1], range(20, 380, 40)):
                pos = (x, y, x+40, y+40) # 枠の大きさ
                tag = j + i #　どの位置にいるかを座標表示
                self.tag_2_pos[tag] = pos[:2] # 位置と座標を辞書定義
                self.board.create_rectangle(pos, fill = "Peach puff3", tags = tag) # サイズ、色、名前タグを設定
                self.z_2_tag[self.z_coordinate(tag)] = tag
        self.get_board_info()


        # 文字を描く ---------------------------------------------------------------
        for turn , i in zip([0, 1] , ["一", "九"]):
            for j in self.numstr[::-1]:
                tag = j + i # 一1～９、九１～9のタグ生成
                self.draw_text(tag, turn)
                self.board_2_info[self.z_coordinate(tag)] = [1, 2][turn] # 1と2を記入
        self.get_board_info()

        self.binding()


    def z_coordinate(self, tag): 
        # タグから１次元の座標に変換
        x, y = self.numstr[::-1].index(tag[0]) + 1 , self.kanstr.index(tag[1]) + 1
        return y*11 + x # １次元表示


    def get_board_info(self, a=None, b=None): # 盤面の情報を取得する
        tags = "" if a is None else "\n{} -> {}".format(a, b)
        board_format = " {:2d} " * 11
        print(tags, *[board_format.format(*self.board_2_info[i:i+11]) \
            for i in range(0, 121, 11)], sep='\n')


    def draw_text(self, tag, turn):
        x , y = self.tag_2_pos[tag]
        self.board.create_text(x + 20, y + 20,\
            font=("Helvetica", 10, "bold") ,\
            angle=[180, 0][turn] ,\
            text=["と", "歩"][turn],\
            tags=tag)


    def binding(self):
        # クリックしたときに指定した関数が呼ばれるようになる。
        # tag_bind(item, event, callback)
        for tag in self.tag_2_pos.keys():
            self.board.tag_bind(tag, "<ButtonPress-1>", self.board_pressed)
            # ButtonPress-1は左クリック


    def board_pressed(self, event):
        # 自分のターン出なければ何もしない
        # itemconfig(item, **options) 長方形の色を変える
        #　after(delay_ms, callback=None, *args)
        # afterを使ってdelay_ms後に実行
        if self.lock:
            return

        _id = self.board.find_closest(event.x, event.y)
        _id = self.board.find_closest(event.x, event.y)
        tag = self.board.gettags(_id[0])[0]
        #print("Tag {} pressed".format(tag))
        #print("Z {} pressed".format(self.z_coordinate(tag)))

        #クリックされた長方形のtagから1次元の座標に変換
        # それをもとに盤面の情報を手に入れる。
        state = self.board_2_info[self.z_coordinate(tag)]


        '''クリックされたのが自分の歩ならば色を変える
        かつ、自分の歩がほかに選択されていないとき
        '''
        if state == 2 and self.unpressed:
            self.board.itemconfig(tag, fill="Peach Puff3")
            # 文字が消えるので再度文字を書く
            self.draw_text(tag, 1)
            # クリックされた状態
            self.unpressed = 0
            self.previous_tag = tag
            # 候補手の探索と表示
            self.show(tag)
        elif state == 2:
            '''
            すでに自分の歩が選択されていて、自分のほかの歩を選択したとき、
            既に選択されているものをもとに戻す。
            その後、新しく選択した歩の色を変える。
            '''
            self.board.itemconfig(self.previous_tag , fill = "Peach Puff3")
            # 文字が消えるので再度文字を書く
            self.draw_text(self.previous_tag, 1)
            self.board.itemconfig(tag, fill="Peach Puff2")
            self.draw_text(tag, 1)
            self.previous_tag = tag

            # 候補手の表示の前に、先の候補手の色をもとに戻す。
            for z in self.candidates:
                ctag = self.z_2_tag[z]
                self.board.itemconfig(ctag, fill="Peach Puff3")
            # 候補手の探索と表示
            self.show(tag)
        elif state == 1 or self.unpressed:
            # 「と」が選択されたとき、もしくは歩が選択されていない
            return
        else:
            '''
            歩が選択されていて、かつ食うハウをクリックしたときの処理
            クリックされたところが、候補手にあるかどうか確認
            '''
            flag = self.click_is_valid(tag)
            if flag == 0:
                return
            self.current_tag = tag
            # クリックされたところが、候補手にあるので盤面の更新。
            self.update_board(tag)


    def update_board(self, tag):
        if self.turn:
            self.lock = 1
        # 候補手の色をもとに戻す
        for z in self.candidates:
            ctag = self.z_2_tag[z]
            self.board.itemconfig(ctag, fill="Peach Puff3")
        self.draw_text(tag, self.turn)

        # 盤面の更新
        self.board_2_info[self.z_coordinate(tag)] = self.turn +1
        self.board_2_info[self.z_coordinate(self.previous_tag)] = 0
        self.board.itemconfig(self.previous_tag, fill="Peach Puff3")
        self.get_board_info(self.previous_tag, tag)
        self.unpressed = 1
        self.previous_tag = None
        self.candidates = []
        # 挟まれているかの確認
        self.after(1000 , self.check)

    def show(self, tag):
        # 候補手の表示
        self.candidates = []
        z = self.z_coordinate(tag)
        self.search(z)
        for z in self.candidates:
            ctag = self.z_2_tag[z]
            self.board.itemconfig(ctag, fill="Peach Puff1")


    def search(self, z):
        # 候補手の探索
        for num in [-11 , 11, 1, -1]:
            self.tmp = []
            self.run_search(z+num, num)
            if self.tmp:
                self.candidates += self.tmp


    def run_search(self, z, num):
        v = self.board_2_info[z]
        if v == 0:
            self.tmp.append(z)
            self.run_search(z+num, num)
        return -1


    def click_is_valid(self, tag):
        # クリックされたところが、候補手にあるかどうか確認
        ans = self.z_coordinate(tag)
        return 1 if ans in self.candidates else 0


    def check(self):
        self.retrieves = []
        z = self.z_coordinate(self.current_tag)
        # 挟んでるかの確認
        self.is_hasami(z)
    # とる
        for z in set(self.retrieves):
            tag = self.z_2_tag[z]
            self.board.itemconfig(tag, fill="skyblue")
            self.draw_text(tag, self.board_2_info[z]-1)
        if len(self.retrieves) > 0:
            self.after(500, self.get_koma)


        if self.turn:
            self.after(1000, self.AI)
        else:
            self.after(1000, self.YOU)
        # find_closestメソッドに発生したイベントの座標を渡し、_idに格納
        # gettagsに_idをわたし出力を返す


    def AI(self):
        if self.enlock:
            return
        self.turn = 0
        self.candidates = []
        while True:
            z = random.choice([i for i, v in enumerate(self.board_2_info) if v == 1])
            # 動かすコマの符号
            self.previous_tag = self.z_2_tag[z]
            self.search(z)
            if self.candidates:
                break

        # 候補手からランダムに選択
        z = random.choice(self.candidates)
        # 動かした後の符号
        self.current_tag = self.z_2_tag[z]
        self.update_board(self.current_tag)

    def YOU(self):
        self.turn = 1
        self.lock = 0



    def is_hasami(self, z):
        # 横と縦のチェック
        for num in [-11, 11 , 1, -1]:
            self.rflag = False
            self.rtmp = [z]
            self.hasami_search(z+num, num)
            if self.rflag:
                self.retrieves += self.rtmp

        # 端の探索
        for edge in [(12, 100, 1, 11), (20, 108, -1, 11), (100, 12, 1, -11), (108, 20, -1, -11)]:
            flag = self.edge_check(*edge)
            if flag:
                break


    def edge_check(self, start, end, interval_0, interval_1):
        source = [2, 1][self.turn]
        target = [1, 2][self.turn]
        tmp = []
        cnt = interval_0
        set_1 = (start, start+cnt, interval_0)
        set_2 = (start, start+cnt+interval_0, interval_0)


        if self.board_2_info[start] != source:
            return
        i = start + interval_0
        while self.board_2_info[i] == source:
            cnt = cnt +  interval_0
            i = i +  interval_0
        if self.board_2_info[i] in [-1, 0]:
            return
        tmp += [j for j  in range(set_2)]
        start += interval_1

        while True:
            flag_0 = \
                all([1 if self.board_2_info[j] == source else 0 for j in range(set_1)])
            if flag_0:
                tmp += [j for j in range(set_2)]
                start += interval_1
                continue
            flag_1 = \
                all([1 if self.board_2_info[j] == target else 0 for j in range(set_1)])
            if flag_1:
                tmp += [j for j in range(set_1)]
            break
        if flag_1:
            self.retrieves += tmp
        return flag_1


    def get_koma(self):
        for z in set(self.retrieves):
            tag = self.z_2_tag[z]
            self.board.itemconfig(tag, fill="Peach Puff3")
            if self.board_2_info[z] == [1, 2][self.turn]:
                self.draw_text(tag, self.board_2_info[z] -1)
            else:
                self.board_2_info[z] = 0
                self.result[self.turn] += 1

        # 結果の確認
        if self.result[self.turn] >= 3:
            self.enlock = 1
            self.end_game()


    def hasami_search(self, z, num):
        v = self.board_2_info[z]
        if v == [2, 1][self.turn]:
            self.rtmp.append(z)
            self.hasami_search(z+num, num)
        if v == [1, 2][self.turn] and len(self.rtmp) > 1:
            self.rtmp.append(z)
            self.rflag = True
        return


    def end_game(self):
        self.board.unbind("<ButtonPress-1>")
        result = self.result[0] < self.result[1]
        print("Result : {} Win". format(["相手", "あなた"][result]))


if __name__ == "__main__":
    shogi = shogi()
    shogi.run()
