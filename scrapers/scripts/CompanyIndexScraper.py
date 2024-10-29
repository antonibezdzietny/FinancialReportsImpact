"""
Scraper values of the company's indicators based on 
https://www.biznesradar.pl/
"""

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from enum import Enum

class CompanyIndexScraper:
    class IndexType(Enum):
        COMPANY     = 0,
        SECTOR      = 1,
        COMPANY_YY  = 2,
        SECTOR_YY   = 3,
        COMPANY_QQ  = 4,
        SECTOR_QQ   = 5,
    
    SKELETON_URL = "https://www.biznesradar.pl"
    INDEXES_TO_SCRAP = {
        "wskazniki-wartosci-rynkowej" : [
            "Cena / Wartość księgowa",
            "Cena / Wartość księgowa Grahama",
            "Cena / Przychody ze sprzedaży",
            "Cena / Zysk",
            "Cena / Zysk operacyjny",
            "EV / Przychody ze sprzedaży",
            "EV / EBIT",
            "EV / EBITDA",
        ],
        "wskazniki-rentownosci" : [
            "ROE",
            "ROA",
            "Marża zysku operacyjnego",
            "Marża zysku netto",
            "Marża zysku ze sprzedaży",
            "Marża zysku brutto",
            "Marża zysku brutto ze sprzedaży",
            "Rentowność operacyjna aktywów",
        ],
        "wskazniki-przeplywow-pienieznych" : [
            "Udział zysku netto w przepływach operacyjnych",
            "Wskaźnik źródeł finansowania inwestycji",
        ],
        "wskazniki-zadluzenia" : [
            "Zadłużenie ogólne",
            "Zadłużenie kapitału własnego",
            "Zastosowanie kapitału obcego",
            "Wskaźnik ogólnej sytuacji finansowej",
        ],
        "wskazniki-plynnosci" : [
            "I stopień pokrycia",
            "Płynność gotówkowa",
            "Płynność szybka",
            "Płynność bieżąca",
            "Pokrycie zobowiązań należnościami",
        ],
    }

    def __init__(self):
        self.dates_header_ = None
        self.html_table_   = None
        self.data_array_   = None
        self.columns_name_ = sum(CompanyIndexScraper.INDEXES_TO_SCRAP.values(), [])


    def __generate_url_address(self, indexes_type : str, ticker : str) -> str:
        return f"{CompanyIndexScraper.SKELETON_URL}/{indexes_type}/{ticker}"
    

    def __download_http_response(self, url : str) -> BeautifulSoup:
        request = requests.get(url, allow_redirects=False)
        # If ticker is different or if it is shortcuts
        if request.status_code == 301:
            url = f"{CompanyIndexScraper.SKELETON_URL}{request.headers['Location']}"
            request = requests.get(url)
        # If some error with request raise exception
        if request.status_code != 200:
            raise Exception(f"Download http response error code: {request.status_code} on address {url}")
        return BeautifulSoup(request.content, 'html.parser')


    def __download_and_prepare_html_table(self, indexes_key : str, ticker : str) -> None:
        url = self.__generate_url_address(indexes_key, ticker)
        html_response = self.__download_http_response(url)
        self.html_table_ = html_response.find("table", attrs={"class":"report-table"}) 


    def __scrap_header_date(self):
        header_row = self.html_table_.find("tr")
        self.dates_header_ = {"Date": ["".join(date.text.split()).split('(')[0] for date in header_row.find_all("th", attrs={"class":"thq h"})]}


    def __prepare_data_space(self) -> None:
        # Before use dates_header_ should be initialized 
        self.data_array_ = np.empty((len(CompanyIndexScraper.IndexType), len(self.columns_name_), len(self.dates_header_["Date"])))
        self.data_array_[:] = np.nan
    

    def __scrap_data_table(self, index_key : str) -> None:
        data_rows = self.html_table_.find_all("tr")[1:] # Omit header line
        for row in data_rows:
            self.__scrap_data_row(index_key, row) 


    def __scrap_data_row(self, index_key : str, row : BeautifulSoup) -> None:
        # Check is row to scrap 
        row_header = row.find("td", attrs={"class":"f"}).text
        # If row not in INDEXES_TO_SCRAP omit row
        if row_header not in CompanyIndexScraper.INDEXES_TO_SCRAP[index_key]:
            return
        
        cells = row.find_all("td", attrs={"class":"h"})[:-1]
        n_row = self.columns_name_.index(row_header)
        for n_col, cell in enumerate(cells):
            self.__scrap_data_cell(cell, n_row, n_col) 
    
    
    def __scrap_data_cell(self, cell : BeautifulSoup, n_row : int, n_col : int) -> None:
        # Index company value
        raw_section = cell.find("span", attrs={"class": "value"})
        if raw_section:
            self.data_array_[0, n_row, n_col] = float(raw_section.find("span", attrs={"class":"pv"})
                                                      .text.replace("%", "").replace(" ", ""))
        # Index sector value
        raw_section = cell.find("span", attrs={"class": "sectorv"})
        if raw_section:
            self.data_array_[1, n_row, n_col] = float(raw_section.find("span", attrs={"class":"pv"})
                                                      .text.replace("%", "").replace(" ", ""))
        # Change Q/Q
        raw_section = cell.find("div", attrs={"class": "changeqq"})
        if raw_section:
            self.data_array_[2, n_row, n_col] = float(raw_section.find("span", attrs={"class":"pv"})
                                                      .text.replace("%", "").replace(" ", ""))
            self.data_array_[3, n_row, n_col] = float(raw_section.find("span", attrs={"class":"sectorv"})
                                                    .find("span", attrs={"class":"pv"}).text.replace("%", "").replace(" ", ""))
        # Change Y/Y
        raw_section = cell.find("div", attrs={"class": "changeyy"})
        if raw_section:
            self.data_array_[4, n_row, n_col] = float(raw_section.find("span", attrs={"class":"pv"})
                                                      .text.replace("%", "").replace(" ", ""))
            self.data_array_[5, n_row, n_col] = float(raw_section.find("span", attrs={"class":"sectorv"})
                                                  .find("span", attrs={"class":"pv"}).text.replace("%", "").replace(" ", ""))


    def scrap_data(self, ticker : str):
        is_first = True
        for index_key in CompanyIndexScraper.INDEXES_TO_SCRAP.keys():
            self.__download_and_prepare_html_table(index_key, ticker)
            if is_first:
                is_first = False
                self.__scrap_header_date()
                self.__prepare_data_space()
            self.__scrap_data_table(index_key)
            
    def get_report_index(self, report_type : IndexType) -> pd.DataFrame:
        return pd.DataFrame(data = self.data_array_[report_type.value], 
                            index=self.columns_name_, 
                            columns=self.dates_header_["Date"]).T

