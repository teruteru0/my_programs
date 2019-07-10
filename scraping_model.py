# python3.7.3
# -*- coding: utf-8 -*-

# スクレイピングするときの大体のモデルを作る！
# bs4　静的スクレイピング　
# requests　勉強中、ログインが必要でも行ける
# selenium　遅め　rakutenプログラム参考

import re #re.compile(検索ワード)
import time
import requests # urllibよりもこちらのほうが高性能...?
from bs4 import BeautifulSoup as b
import openpyxl as px

#--------------------------------------------------
url = "url_link"
# requestsを使ってwebからhtmlを取得
r = requests.get(url)
# 要素を抽出
soup = b(r.text, 'lxml')

#htmlファイルとして保存したい場合はファイルオープンにして保存
with open('target.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify()) # 整形して文字列を出力できるprettify

# soup.find_allを用いて該当タグの要素をすべて取得
elems = soup.find_all(tag='target_elem') # リスト保存する
# cssセレクタを使ったタグの取得
elems = soup.select()

for elem in elems:
    print(elem.getText()) #テキストを取得

#--------------------------------------------------
'''
ログインが必要なページのhtml取得またはスクレイピング方法
またはseleniumで検索して取得する。
必要な情報
#---------------------------------
1. ログインフォームのパラメータ名
(inputタグのnameとvalueを見つける)
2. フォーム送信時のリンク
#---------------------------------
手順
1.requests.session()で何かする
2.loginに必要な情報を紐づけた変数を用意

user = 'user_name'
pass = 'pass_word'

# セッションを開始
session = requests.session()


# ログイン
login_info = {
    'user_param' : user, # name='user_param'とuserを紐づけ
    'pass_param' : pass, 
    'other_input_name' : 'value_tag'
}

詳細url 'https://qiita.com/shunyooo/items/36af8bcb501baf8c7014'

#アクション
url_login = 'form送信リンク'
res = session.post(url_login, data=login_info)
res.raise_for_status() # エラーならここで例外を発生させる

print(res.text) # ログインページのhtmlを取得できる
'''