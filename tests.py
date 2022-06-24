import os

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import pandas as pd

login = "kl602286217"
password = "Mistgund12391005"
current_Page = 1
database_fileName = "BDM_Data"
csv_file = database_fileName + ".csv"
xlsx_file = database_fileName + ".xlsx"
driver = webdriver.Firefox()

def login_account(login, password):
    driver.get("https://www.bdm.pl/")
    driver.find_element(By.XPATH, "//a[@href='https://e.bdm.pl']").click();
    driver.find_element(By.ID, "logLogin").send_keys(login)
    driver.find_element(By.ID, "logHaslo").send_keys(password)
    driver.find_element(By.ID, "btnLogin").click()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "x-auto-60")))
    driver.find_element(By.ID, "x-auto-60").click()
    time.sleep(4)

    pageSource = driver.page_source
    file_To_Write = open("Page_source_" + "Main " + ".html", 'w', encoding='utf-8')
    file_To_Write.write(pageSource)

def page_up(current_Page):
    try:
        driver.find_element(By.XPATH,
                                  "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-next epm-paging-toolbar-button x-component']").click()
        current_Page += 1
    except:
        try:
            driver.find_element(By.XPATH,
                                      "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component  epm-paging-toolbar-next']").click()
            current_Page += 1
        except:
            pass
    return current_Page

def page_down(current_Page):
    try:
        driver.find_element(By.XPATH,
                                  "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component epm-paging-toolbar-prev']").click()
        current_Page -= 1
    except:
        try:
            driver.find_element(By.XPATH,
                                  "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component  epm-paging-toolbar-prev']").click()
            current_Page -= 1
        except:
            pass
    return current_Page

# def nowe_Zlecenie(walor,)

def pulpit_1():
    driver.find_element(By.PARTIAL_LINK_TEXT, "Pulpit 1").click()

def pulpit_2():
    driver.find_element(By.PARTIAL_LINK_TEXT, "Pulpit 2").click()

def download_table_info(bdm_Dict):
    tableWalletNumber = 1
    current_Page = 1
    data = {}
    print(bdm_Dict)
    for div in bdm_Dict:
        build_Dict = []
        for number in range(tableWalletNumber):
            table = driver.find_element(By.XPATH, "//div[@class='x-grid-group-body']")
            elements_row = table.find_elements(By.XPATH, bdm_Dict[div])
            for element in elements_row:
                build_Dict.append(element.text.strip("PLN"))
            if current_Page != tableWalletNumber:
                current_Page = page_up(current_Page)
        data[div] = (build_Dict)
        while current_Page != 1:
            current_Page = page_down(current_Page)

    return pd.DataFrame.from_dict(data)

def insert_row(
               df_price=pd.DataFrame({"Date": [],
                                      "Wycena": []}),
               df=0):
    current_time = driver.find_element(By.XPATH, "//div[@id='epmNtw-quotesTime']").text.strip(
        "Czas notowań:")[0:10]
    pulpit_2()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.XPATH, "//div[@class='x-grid3-cell-inner x-grid3-col-WYCENA_CALKOWITA']")))
    wycena = driver.find_element(By.XPATH,
                                       "//div[@class='x-grid3-cell-inner x-grid3-col-WYCENA_CALKOWITA']").text.replace(
        "PLN", '')
    pulpit_1()
    index = len(df_price) - 1
    if df_price["Date"].empty == True:
        data_info = {"Date": current_time,
                     "Wycena": wycena}
        for (stock_name, price) in zip(df["stock_names"], df['valuation']):
            data_info[stock_name] = price
        df_price = df_price.append(data_info, True)
    elif df_price["Date"].iloc[index] == current_time:
        data_info = {"Date": current_time,
                     "Wycena": wycena}
        for keys1 in data_info.keys():
            if keys1 not in df_price.keys():
                df_price[keys1] = ''
        for (stock_name, price) in zip(df["stock_names"], df['valuation']):
            data_info[stock_name] = price
            df_price.at[index, stock_name] = data_info[stock_name]
        df_price.at[index, "Date"] = current_time
        df_price.at[index, "Wycena"] = wycena
    else:
        data_info = {"Date": current_time,
                     "Wycena": wycena}
        for (stock_name, price) in zip(df["stock_names"], df['valuation']):
            data_info[stock_name] = price
        df_price = df_price.append(data_info, True).drop('', 1)
    return df_price

bdm_Dict = {'stock_names': "//div[@class='x-grid3-cell-inner x-grid3-col-SKROT']",
            'number_to_shares': "//div[@class='x-grid3-cell-inner x-grid3-col-ILOSC_DO_SPRZEDAZY']",
            'blocked under an order': "//div[@class='x-grid3-cell-inner x-grid3-col-BLOKOWANE_POD_ZLECENIA']",
            'current_price': "//div[@class='x-grid3-cell-inner x-grid3-col-KURS_BIEZACY']",
            'average_purchase_rate': "//div[@class='x-grid3-cell-inner x-grid3-col-SREDNI_KURS_NABYCIA']",
            'profit/loss': "//div[@class='x-grid3-cell-inner x-grid3-col-ZYSK_STRATA_PROCENTOWA']",
            'valuation': "//div[@class='x-grid3-cell-inner x-grid3-col-WYCENA_W_WALUCIE_NOTOWANIA']", }


class stooq():
    NotImplementedError


def _check_file():
    if os.path.exists(csv_file):
        df_price = pd.read_csv(csv_file)
        for key in df_price.keys():
            if 'Unnamed' in key:
                df_price = df_price.drop(key, 1)
    else:
        df_price = pd.DataFrame({"Date": [],
                                 "Wycena": []})


#
# bdm_page = self._driver.current_window_handle
# self._driver.switch_to.new_window()
# stooq = self._driver.current_window_handle
# self._driver.get('https://stooq.pl/')
# self._driver.switch_to.window(stooq)
#
# self._driver.find_element(By.CLASS_NAME,'fc-button-label').click()
# self._driver.find_elements(By.ID,"f13")
# # self._driver.quit()
# self._driver.current_window_handle

# self._driver.find_elements()
#
# class Solution:
#     def romanToInt(self, s: str) -> int:
#         dict = {"I": 1,
#                "V": 5,
#                "X": 10,
#                "L": 50,
#                "C": 100,
#                "D": 500,
#                "M": 1000,}
#         value = 0
#         previous_value = 1
#         for x in s:
#             for key in dict.keys():
#                 if x == key:
#                     s_value = dict[key]
#                     if previous_value <= s_value:
#                         value = value + s_value
#                     else:
#                         value = value - s_value
#                     break
#         print(value)
#         return value
# x = Solution()
# print(x.romanToInt("IV"))

login_account(login, password)

# df_price = download_table_info(bdm_Dict)


# try:
#     tableWalletNumber = driver.find_element(By.XPATH, "//div[@class=' x-grid-panel x-component']").text
#     tableWalletNumber = int(re.search(r'\d+', tableWalletNumber).group())
# except:

# return pd.DataFrame.from_dict(data)

df_price = pd.DataFrame({"Date": [],
                                 "Wycena": []})

df = download_table_info(bdm_Dict)
df_price= insert_row(df_price, df=df)

df_price.to_csv(csv_file)
df_price.to_excel(xlsx_file)