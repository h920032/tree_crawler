#reference website : http://oldtree.tainan.gov.tw/tree0.asp
#implement by H.Y Shih

from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import requests
import re
from progress.bar import Bar
from progress.bar import ChargingBar

start = 0
print("輸入抓取起始編號：")
start = int(input()) - 1

chromedriver = ".\\chromedriver"
driver = webdriver.Chrome(chromedriver)

#起始網址
tree_list_url = 'http://oldtree.tainan.gov.tw/tree0.asp'
print("起始網址：" + tree_list_url)
print("存放位置：" + os.getcwd() + "/tree_data")
#開啟chrome driver
driver.get(tree_list_url)

s1 = Select(driver.find_element_by_name('menu'))
length = len(s1.options)

#列出老樹網址列表
path = ".\\tree_data" #建立資料夾
if not os.path.isdir(path):
    os.mkdir(path)
rows = list()
bar = ChargingBar('抓取樹木清單', max=length, suffix='%(percent)d%%')
for i in range(1,length):
    s1 = Select(driver.find_element_by_name('menu'))
    s1.select_by_index(i)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    a_tags = soup.select('td')
    table = soup.find('table',{'cellspacing': '0'}) #找到表格
    trs = table.find_all('tr')[1:] #取出元素
    for tr in trs:
        temp = [td.text.replace('\n', '').replace('\xa0', '').replace('\t', '') for td in tr.find_all('td')] #取出內容
        url = [a.get('href') for a in tr.find_all('a')] #獨立出網址
        temp.append(url[0])
        rows.append(temp)
    bar.next()
rows = np.array(rows)
rows = np.delete(rows, [3], axis=1)
columns = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
df_tree_index = pd.DataFrame(data=rows,columns=columns)
df_tree_index.to_excel(path + "\\樹木清單.xlsx", sheet_name='tree_index',index=False)
bar.next()
bar.finish()
print("==========樹木清單抓取完成==========")

for i in range(start,df_tree_index['詳看內容'].size):
    print("==========正在抓取樹木編號：" + df_tree_index['編號'].values[i] + "==========")
    single = 'http://oldtree.tainan.gov.tw/' + df_tree_index['詳看內容'].values[i]
    driver.get(single)
    
    file_path = ".\\tree_data\\" + df_tree_index['編號'].values[i]
    if not os.path.isdir(file_path):
        os.mkdir(file_path)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    content = soup.find('div',{'id': 'panes'})
    info = soup.find('div',{'class': 'pane'}).get_text()

    #寫入基本資料
    with open(file_path + "\\" + "基本資料.txt", "w",encoding="utf-8") as f:
        f.write(info)

    h3 = content.find_all('h3')
    #print(info.prettify())
    #print(info)
    
    jpg_list = []
    for a in content.select('li'):
        for j in a.find_all('a'):
            jpg_list.append(j.get('href'))

    #file_path = "./tree_data/" + df_tree_index['編號'].values[i]
    img_path = file_path + '\\treeimgs'
    if not os.path.isdir(img_path):
        os.mkdir(img_path)
    bar = ChargingBar('下載圖片', max=len(jpg_list), suffix='%(percent)d%%')
    for a in jpg_list:
        url = 'http://oldtree.tainan.gov.tw/' + a
        r = requests.get(url)
        with open(file_path + '\\' + a,'wb') as f:
        #將圖片下載下來
            f.write(r.content)
        bar.next()
    bar.finish()
    #print("==========圖片下載完成==========")
    
    bar = ChargingBar('抓取詳細資料網址', max=2, suffix='%(percent)d%%')
    table1_url = 'http://oldtree.tainan.gov.tw/' + 'tree02.asp?' + df_tree_index['詳看內容'].values[i].split('?',1)[1]
    driver.get(table1_url)
    rows = list()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find('table',{'cellspacing': '0'}) #找到表格
    trs = table.find_all('tr')[1:] #取出元素
    for tr in trs:
        temp = [td.text.replace('\n', '').replace('\xa0', '').replace('\t', '') for td in tr.find_all('td')] #取出內容
        url = [a.get('href') for a in tr.find_all('a')] #獨立出網址
        temp.append(url[0])
        rows.append(temp)
    if rows:
        rows = np.array(rows)
        rows = np.delete(rows, [4], axis=1)
    columns = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
    df_treat_index = pd.DataFrame(data=rows,columns=columns)
    df_treat_index.to_excel(file_path + "\\健康檢查.xlsx", sheet_name='tree_index',index=False)
    bar.next()
    
    table2_url = 'http://oldtree.tainan.gov.tw/' + 'tree03.asp?' + df_tree_index['詳看內容'].values[i].split('?',1)[1]
    driver.get(table2_url)
    rows = list()
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find('table',{'cellspacing': '0'}) #找到表格
    trs = table.find_all('tr')[1:] #取出元素
    for tr in trs:
        temp = [td.text.replace('\n', '').replace('\xa0', '').replace('\t', '') for td in tr.find_all('td')] #取出內容
        url = [a.get('href') for a in tr.find_all('a')] #獨立出網址
        temp.append(url[0])
        rows.append(temp)
    if rows:
        rows = np.array(rows)
        rows = np.delete(rows, [3], axis=1)
    columns = [th.text.replace('\n', '') for th in table.find('tr').find_all('th')]
    df_case_index = pd.DataFrame(data=rows,columns=columns)
    df_case_index.to_excel(file_path + "\\診治紀錄.xlsx", sheet_name='tree_index',index=False)
    bar.next()
    bar.finish()
    
    #============================抓取健康檢查內容=====================================
    bar = ChargingBar('抓取健康檢查內容', max=df_treat_index['詳看內容'].size, suffix='%(percent)d%%')
    for j in range(df_treat_index['詳看內容'].size):
        treat_path = file_path + '\\健康檢查'
        if not os.path.isdir(treat_path):
            os.mkdir(treat_path)

        treat_date_path = treat_path + "\\" + df_treat_index['健檢日期'].values[j].replace('/', '-')
        if not os.path.isdir(treat_date_path):
            os.mkdir(treat_date_path)

        treat_url = 'http://oldtree.tainan.gov.tw/' + df_treat_index['詳看內容'].values[j]
        driver.get(treat_url)



        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find('table',{'cellspacing': '5'})
        data = table.find_all('td',{'colspan': '2'})
        #print(table.text.replace('\t', '').replace('\xa0', ''))
        info = ("0,1\n" + table.text.replace('\t', '').replace(',', '\n').replace('其他','\n其他').replace(' ', '').replace('\xa0', '').split("樹木基本狀況樹木健康狀況",1)[0].replace('：', ',')).replace('\n\n', '\n')

        with open(treat_date_path + "\\" + "temp.csv", "w",encoding="utf-8") as f:
            f.write(info)
        base_info = pd.read_csv(treat_date_path + "\\" + 'temp.csv')

        if os.path.isfile(treat_date_path + "\\" + "temp.csv"):
            os.remove(treat_date_path + "\\" + "temp.csv")
        #base_info.to_excel(treat_date_path + "/詳細資料.xlsx", sheet_name='基本資料',index=False,header=False)

        #data[0].text.replace('樹木基本狀況樹木健康狀況','').replace('\t','').replace('\xa0','').replace('：', ',')

        base_data = pd.DataFrame()
        if table.find_all('table',{'class': 'text14'}):
            info = table.find_all('table',{'class': 'text14'})[1].text.replace('\t','').replace('\xa0','').replace('：', ',')
            with open(treat_date_path + "\\" + "temp.csv", "w",encoding="utf-8") as f:
                f.write(info)
            base_data = pd.read_csv(treat_date_path + "\\" + 'temp.csv')

            if os.path.isfile(treat_date_path + "\\" + "temp.csv"):
                os.remove(treat_date_path + "\\" + "temp.csv")

        health_data = pd.DataFrame()
        if table.find_all('td',{'valign': 'top'}):
            health_data = []
            for term in table.find_all('td',{'valign': 'top'})[1].find_all('li'):
                health_data.append(term.text.replace('\xa0','').replace('\t','').replace('\n',''))
            health_data = pd.DataFrame(health_data)

        treat_data = pd.DataFrame()
        if table.find_all('td',{'valign': 'top'}):
            treat_data = []
            for term in table.find_all('td',{'valign': 'top'})[2].find_all('td'):
                treat_data.append(term.text.replace('\xa0','').replace('\t','').replace('\n',''))
            treat_data = pd.DataFrame(treat_data)

        descript_data = pd.DataFrame()
        if table.find_all('td',{'valign': 'top'}):
            descript_data = []
            descript_data.append(table.find_all('td',{'valign': 'top'})[3].text.replace('\xa0','').replace('\t','').replace('\n',''))
            descript_data = pd.DataFrame(descript_data)

        with pd.ExcelWriter(treat_date_path + "\\詳細資料.xlsx") as writer:
            base_info.to_excel(writer, sheet_name='基本資料',index=False,header=False)
            base_data.to_excel(writer, sheet_name='樹木基本狀況',index=False,header=False)
            health_data.to_excel(writer, sheet_name='樹木健康狀況',index=False,header=False)
            treat_data.to_excel(writer, sheet_name='處置建議',index=False,header=False)
            descript_data.to_excel(writer, sheet_name='相關說明',index=False,header=False)

        jpg_list = []
        if table.find('ul') is not None:
            for ul in table.find('ul').find_all('a'):
                jpg_list.append(ul.get('href'))
            for i in jpg_list:
                url = 'http://oldtree.tainan.gov.tw/' + i
                r = requests.get(url)
                with open(treat_date_path + '\\' + i.split('/',1)[1],'wb') as f:
                    #將圖片下載下來
                    f.write(r.content)
        #print(df_treat_index['健檢日期'].values[j].replace('/', '-'))
        bar.next()
    bar.finish()
    #print("==========健康檢查內容抓取完成==========")
        
    #================================抓取診治紀錄內容========================================
    bar = ChargingBar('抓取診治紀錄內容', max=df_case_index['詳看內容'].size, suffix='%(percent)d%%')
    for j in range(df_case_index['詳看內容'].size):

        case_path = file_path + '\\診治紀錄'
        if not os.path.isdir(case_path):
            os.mkdir(case_path)

        case_date_path = case_path + "\\" + df_case_index['診治日期'].values[j].replace('/', '-')
        if not os.path.isdir(case_date_path):
            os.mkdir(case_date_path)

        treat_url = 'http://oldtree.tainan.gov.tw/' + df_case_index['詳看內容'].values[j]
        driver.get(treat_url)


        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find('table',{'cellspacing': '5'})
        data = table.find_all('td',{'colspan': '2'})
        #print(table.text.replace('\t', '').replace('\xa0', ''))
        info = ("0,1\n" + table.text.replace('\t', '').replace(',', '\n').replace(' ', '').replace('\xa0', '').split("樹木基本狀況樹木健康狀況",1)[0].replace('：', ',')).replace('\n\n', '\n')

        with open(case_date_path + "\\" + "temp.csv", "w",encoding="utf-8") as f:
            f.write(info)
        base_info = pd.read_csv(case_date_path + "\\" + 'temp.csv')

        if os.path.isfile(case_date_path + "\\" + "temp.csv"):
            os.remove(case_date_path + "\\" + "temp.csv")

        base_info.to_excel(case_date_path + "/詳細資料.xlsx", sheet_name='基本資料',index=False,header=False)

        jpg_list = []
        if table.find_all('a') is not None:
            for ul in table.find_all('a'):
                jpg_list.append(ul.get('href'))
            for i in jpg_list:
                url = 'http://oldtree.tainan.gov.tw/' + i
                r = requests.get(url)
                with open(case_date_path + '\\' + i.split('/',1)[1],'wb') as f:
                    #將圖片下載下來
                    f.write(r.content)
        #print(df_case_index['診治日期'].values[j].replace('/', '-'))
        bar.next()
    bar.finish()
