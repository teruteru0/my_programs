#! python3
# -＊- coding: utf-8 -＊-

#--------用途-----------
#　楽天の懸賞広場に自動的に応募してくれるプログラム


import webbrowser
import time
import pprint
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class kennsyouhiroba:

    def __init__(self,mail_address, password):

        self.rak_url = 'https://prize.travel.rakuten.co.jp/frt/search.do?f_large=staying_ticket'
        self.driver = webdriver.Chrome(executable_path = (r'C:\Users\jubea\Downloads\chromedriver_win32\chromedriver.exe')) #chromeで開く

        # 変更可能変数----------------------------------------------------------------------------------------
        self.count = 0    #hotelタグのインデックスに使う変数　　　変更可能：0~29
        self.page_num = 0 # 現在のページ数  　　　　　　　　　　変更可能：0~13(最終ページ)
        self.error_total = 20 # エラーの回数を指定します    　　　変更可能：１～
        # -----------------------------------------------------------------------------------------------------

        # 時間設定
        self.enter_cnt = 0.5 #入力時間
        self.low_cnt  = 1.2 #少なめの時間
        self.high_cnt = 3 #多めの時間

        # そのほかの変数
        self.error_count = 0
        self.recruit_index = 0 # 応募ページのインデックスを表示
        self.url_set = set() # 同じurlかを確認する


        self.mail_address = mail_address
        self.password = password

        self.driver.get(self.rak_url)
        time.sleep(self.low_cnt)



    def url_confirm(self):
        '''
        ホテルのurlを確認する関数です。
        ホテルのurlをurl_setに保存し、同じところをループしないようにします。
        '''

        driver = self.driver
        hotel_url = driver.current_url # ホテルのurlを格納
        if hotel_url in self.url_set:
            print('エラー：すでに検索済みです。次のページに移行します。')
            kennsyouhiroba.plus_count(self) 
        else:
            self.url_set.add(hotel_url)


    def rakuten(self):

        '''
        ホテルをクリックして応募する関数。
        １．ページにあるホテルの要素をすべて検出
        ２．:try:　そのうちの一つをクリック、ページが存在しない場合は終了
        ３．url_setにurlを保存する
        ４．応募ボタンの個数を検出
        ５．要素順にクリックして、IDとパスワードを入力、クリック
        ６．応募済みならerror_count += 1、それ以外なら応募完了をクリック
        ７．次のホテルへ
        '''

        driver = self.driver
        driver.get(self.rak_url)
        kennsyouhiroba.next_url(self, self.page_num) # ページ数を指定する
        home = driver.find_elements_by_class_name('hotel') # 30件の中から順に検出する
        print('\n現在のホテルindex：' + str(self.count))


        try:
            home[self.count].click() #　クリック
        except IndexError:
            if driver.find_element_by_class_name('pagingNext') == None:
                print('最後尾まで達しました。')
                print('seleniumを終了します。')
                time.sleep(self.low_cnt)
                kennsyouhiroba.quit(self)

        recruit_pages = driver.find_elements_by_class_name('imgover') #応募するを探す

        if self.recruit_index == 0: #最初の時点でurlを取得
            kennsyouhiroba.url_confirm(self)


        print('応募ページの要素の個数：' + str(len(recruit_pages)))
        time.sleep(self.low_cnt)
        print('応募ページindex：' + str(self.recruit_index + 1))
        recruit_pages[self.recruit_index].click() # index = 0から順にクリック
        time.sleep(self.low_cnt)


        enter = driver.find_element_by_name('u') # usernameを入力
        enter.send_keys(self.mail_address)
        time.sleep(self.enter_cnt)
        password = driver.find_element_by_name('p') # passwordを入力
        password.send_keys(self.password)
        time.sleep(self.enter_cnt)
        next_process = driver.find_element_by_xpath('//*[@id="l_submit"]/a') #ログインボタンを押す
        next_process.click()


        try:
            final_recruit = driver.find_element_by_xpath('//form[@method="POST"]/input[@type="submit"]')
            # 応募済みかどうかを検出
        except NoSuchElementException:
            kennsyouhiroba.error_solve(self)

        else:
            final_recruit.click() # 最終の「応募する」をクリック

            try:
                final_error = driver.find_element_by_xpath('//*[@id="presentBt"]/li[1]/a/img')
                # エラー画面かどうかを判断

            except NoSuchElementException:
                kennsyouhiroba.error_solve(self)
            else:
                print('応募完了！！')


        finally:
            time.sleep(self.low_cnt)
            print('\n')
            if len(recruit_pages) - 1 == self.recruit_index:
                self.recruit_index = 0
            else:
                self.recruit_index += 1
                time.sleep(self.low_cnt)
                driver.get(self.rak_url)
                kennsyouhiroba.rakuten(self) # もしrecruit_pagesが複数ならホテルのindexをそのままにして次に行く

        kennsyouhiroba.plus_count(self)


    def error_solve(self):
        print('\nエラー：')
        print('要素が検出されませんでした。')
        self.error_count += 1
        print('ただいまのエラー回数：', self.error_count)
        if self.recruit_index != 0:
            print('このページはすべて応募完了しました。次のページに移行します。')
        if self.error_count == self.error_total:
            print('{}回エラーになりました。プログラムを終了します。'.format(self.error_count))
            kennsyouhiroba.quit_program(self)
        
    def plus_count(self):

        '''
        ホテルのインデックスをカウントする関数
        '''

        if self.count >= 29: # ホテルのインデックスが２９以上ならリセット
            self.page_num += 1
            self.count = 0
            print('\n最大まで到達しました。')
            print('インデックスをリセットします。')
            pprint.pprint(self.url_set)

        else:
            self.count += 1
            print('次へ移行します。')
            print('------------------------------------')
        kennsyouhiroba.rakuten(self)



    def next_url(self, page_num):

        '''
        ページ数をカウントする
        '''

        driver = self.driver
        if page_num != 0: # もしpageが０でないなら
            for num in range(page_num): # page_numまでページを進む
                try:
                    time.sleep(self.low_cnt)
                    page_next = driver.find_element_by_class_name('pagingNext')

                except NoSuchElementException:
                    print('selenium を終了します。')
                    kennsyouhiroba.quit_program(self)
                    break

                else:
                    page_next.click()
            print('\n-----------------------------------------\n\
                pageを取得' + str(self.page_num + 1)  + 'ページ目')


        else:
            pass


    def quit_program(self):
        '''
        プログラムを終了する関数
        '''

        driver = self.driver
        print('---------------------------------')
        print('終了')
        driver.close()
        driver.quit()
        sys.exit(0)


# ---------------------------------------------------------------------------------------------------

number = int(input('アカウント番号を入力してください。（１つしかない場合は０を入力\n'))

# ここに自分のアカウントを設定（複数可能） -----------------------------------------------------------------------------------
ID_password = (('アカウントID', 'アカウントパスワード'), ('アカウント２ID', 'アカウント２パスワード'))
#-------------------------------------------------------------------------------------------------------------------------------

gmail = ID_password[[number][0]]
pass_word = ID_password[number][1]
r = kennsyouhiroba(gmail, pass_word)
r.rakuten()