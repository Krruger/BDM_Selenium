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


class BDM():

    def __init__(self, login, password):
        self._current_Page = 1
        self._driver = webdriver.Firefox()
        self._driver.get("https://www.bdm.pl/")
        self._driver.find_element(By.XPATH, "//a[@href='https://e.bdm.pl']").click();
        self._driver.find_element(By.ID, "logLogin").send_keys(login)
        self._driver.find_element(By.ID, "logHaslo").send_keys(password)
        self._driver.find_element(By.ID, "btnLogin").click()
        WebDriverWait(self._driver, 20).until(EC.presence_of_element_located((By.ID, "x-auto-60")))
        self._driver.find_element(By.ID, "x-auto-60").click()
        time.sleep(4)

        pageSource = self._driver.page_source
        file_To_Write = open("Page_source_" + "Main " + ".html", 'w', encoding='utf-8')
        file_To_Write.write(pageSource)

    def page_up(self):
        try:
            self._driver.find_element(By.XPATH,
                                      "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-next epm-paging-toolbar-button x-component']").click()
        except selenium.common.exceptions.NoSuchElementException:
            self._driver.find_element(By.XPATH,
                                      "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component  epm-paging-toolbar-next']").click()
        self._current_Page += 1

    def page_down(self):
        try:
            self._driver.find_element(By.XPATH,
                                      "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component epm-paging-toolbar-prev']").click()
        except selenium.common.exceptions.NoSuchElementException:
            self._driver.find_element(By.XPATH,
                                      "//div[@class=' x-icon-btn x-nodrag epm-paging-toolbar-button x-component  epm-paging-toolbar-prev']").click()
        self._current_Page -= 1

    def pulpit_1(self, ):
        self._driver.find_element(By.PARTIAL_LINK_TEXT, "Pulpit 1").click()

    def pulpit_2(self, ):
        self._driver.find_element(By.PARTIAL_LINK_TEXT, "Pulpit 2").click()

    def download_table_info(self):

        bdm_Dict = {'stock_names': "//div[@class='x-grid3-cell-inner x-grid3-col-SKROT']",
                    'number_to_shares': "//div[@class='x-grid3-cell-inner x-grid3-col-ILOSC_DO_SPRZEDAZY']",
                    'blocked under an order': "//div[@class='x-grid3-cell-inner x-grid3-col-BLOKOWANE_POD_ZLECENIA']",
                    'current_price': "//div[@class='x-grid3-cell-inner x-grid3-col-KURS_BIEZACY']",
                    'average_purchase_rate': "//div[@class='x-grid3-cell-inner x-grid3-col-SREDNI_KURS_NABYCIA']",
                    'profit/loss': "//div[@class='x-grid3-cell-inner x-grid3-col-ZYSK_STRATA_PROCENTOWA']",
                    'valuation': "//div[@class='x-grid3-cell-inner x-grid3-col-WYCENA_W_WALUCIE_NOTOWANIA']", }

        def _download_function():
            data = {}
            for div in bdm_Dict:
                build_Dict = []
                for number in range(tableWalletNumber):
                    table = self._driver.find_element(By.XPATH, "//div[@class='x-grid-group-body']")
                    elements_row = table.find_elements(By.XPATH, bdm_Dict[div])
                    for element in elements_row:
                        build_Dict.append(element.text.strip("PLN"))
                    if current_Page != tableWalletNumber:
                        current_Page = page_up(current_Page)
                data[div] = (build_Dict)
                while current_Page != 1:
                    current_Page = page_down(current_Page)
            return pd.DataFrame.from_dict(data)

        tableWalletNumber = self._driver.find_element(By.XPATH, "//div[@class='my-paging-text x-component']").text
        tableWalletNumber = int(re.search(r'\d+', tableWalletNumber).group())
        self._df = _download_function(bdm_Dict)

    def insert_row(self,
                   df_price=pd.DataFrame({"Date": [],
                                          "Wycena": []}),
                   df=0):

        # df_price = df_price.drop('ULTGAMES', 1)
        current_time = self._driver.find_element(By.XPATH, "//div[@id='epmNtw-quotesTime']").text.strip(
            "Czas notowań:")[0:10]
        pulpit_2()
        WebDriverWait(self._driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='x-grid3-cell-inner x-grid3-col-WYCENA_CALKOWITA']")))
        wycena = self._driver.find_element(By.XPATH,
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
            df_price = df_price.append(data_info, True)
        self._df_price = df_price.drop('', 1)

    def zlecenie_kupna(self, nazwa_Tickera, cena_Akcji, kwota):
        nowe_zlecenie = driver.find_element(By.XPATH, "//div[@class='epm-gadget-body x-component']")
        x, auto, value = nowe_zlecenie.get_attribute('id').split("-")
        value = int(value)

        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-'{value+25}'']").click()
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 34}-input']").send_keys(f'{nazwa_Tickera}')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, f"//div[@class='x-combo-list-item  x-view-highlightrow x-combo-selected']")))
        self._driver.find_element(By.XPATH,
                            f"//div[contains(@class,'x-combo-list-item x-view-highlightrow x-combo-selected')][contains(text(), f'{nazwa_Tickera}')]").click()
        time.sleep(4)
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 52}-input']").clear()
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 52}-input']").send_keys(f'{int(kwota/cena_Akcji)}')
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 54}-input']").clear()
        time.sleep(0.5)
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 54}-input']").send_keys(f'{cena_Akcji}')

        self._driver.find_element(By.XPATH, "//*[text()='Wyślij']").click()
        try:
            self._driver.find_element(By.XPATH, "//*[text()='Tak']").click()
        except:
            pass
        self._driver.find_element(By.XPATH, "//*[text()='Tak']").click()

    def zlecenie_sprzedaży(self, nazwa_Tickera, cena_Akcji, liczba_akcji):
        nowe_zlecenie = driver.find_element(By.XPATH, "//div[@class='epm-gadget-body x-component']")
        x, auto, value = nowe_zlecenie.get_attribute('id').split("-")
        value = int(value)

        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-'{value+27}'']").click()
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 34}-input']").send_keys(f'{nazwa_Tickera}')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, f"//div[@class='x-combo-list-item  x-view-highlightrow x-combo-selected']")))
        self._driver.find_element(By.XPATH,
                            f"//div[contains(@class,'x-combo-list-item x-view-highlightrow x-combo-selected')][contains(text(), f'{nazwa_Tickera}')]").click()
        time.sleep(4)
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 52}-input']").clear()
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 52}-input']").send_keys(f'{liczba_akcji}')
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 54}-input']").clear()
        time.sleep(0.5)
        self._driver.find_element(By.XPATH, f"//input[@id='x-auto-{value + 54}-input']").send_keys(f'{cena_Akcji}')

        self._driver.find_element(By.XPATH, "//*[text()='Wyślij']").click()
        try:
            self._driver.find_element(By.XPATH, "//*[text()='Tak']").click()
        except:
            pass
        self._driver.find_element(By.XPATH, "//*[text()='Tak']").click()

    def anuluj_zlecenie(self,walor):
        for x in self._driver.find_elements(By.XPATH,
                                      '//div[@class="x-tab-panel-body x-tab-panel-body-top epm-tabPanel-body"]'):
            if 'ID zlecenia' in x.text:
                break
        try:
            x.find_element(By.XPATH, f'//*[text()="{walor}"]').click()
        except selenium.common.exceptions.NoSuchElementException:
            print(f"No such '{walor}' available to sell.")
        x.find_element(By.XPATH, f'//*[text()="Anuluj"]').click()

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

# df_price = insert_row(df_price, df)
# df_price.to_csv("test.csv")
# df_price.to_excel("text.xlsx")

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