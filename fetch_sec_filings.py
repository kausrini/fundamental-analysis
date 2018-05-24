#!/usr/bin/env python3

import requests
import bs4
import pathlib
from urllib.parse import urlparse
import os

class Company:
    def __init__(self):
        self.ticker = None
        self.cik = None

class Document:
    def __init__(self):
        self.company = None
        self.accession_number_str = None
        self.filing_type = None
        self.name = None
        self.filing_date = None

    # Strips down hypens in the accession number and returns the numeric value only
    def get_accession_number(self):
        return self.accession_number_str.replace('-', '')


# Retrieve all the filing_type documents for the company with stock ticker (upto 100)
def obtain_document_details(stock_ticker, filing_type):
    company = Company()
    company.ticker = stock_ticker
    sec_uri = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb=&owner=include&count=100&output=xml'.format(
        stock_ticker,filing_type)
    response = requests.get(sec_uri)
    page_data = bs4.BeautifulSoup(response.text, "html.parser")
    company.cik = page_data.companyinfo.cik.string
    documents_final = []
    for filing in page_data.find_all('filing'):
        filing_href_string = filing.filinghref.string
        file_name = os.path.basename((urlparse(filing_href_string)).path)
        accession_number_str = file_name.split('-index')[0]

        document = Document()
        document.company = company
        document.filing_date = filing.datefiled.string
        document.filing_type = filing.type.string
        document.accession_number_str = accession_number_str
        documents_final.append(document)
    return documents_final


# Obtain the specified document
def obtain_document(document):
    base_document_uri = 'https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/Financial_Report.xlsx'
    document_uri = base_document_uri.format(cik=document.company.cik, acc_no=document.get_accession_number())
    file_name = document.filing_date + '.xlsx'
    response = requests.get(document_uri)

    current_path = pathlib.Path.cwd()
    company_path = current_path / document.company.ticker.upper()
    company_path.mkdir(exist_ok=True)
    filing_type_path = company_path / document.filing_type
    filing_type_path.mkdir(exist_ok=True)
    document_path = filing_type_path / file_name
    with document_path.open('wb') as output:
        output.write(response.content)


def main():
    stocks = ['pypl', 'amzn', 'aapl']

    for stock in stocks:
        filing_type = '10-K'
        documents = obtain_document_details(stock, filing_type)
        for document in documents:
            obtain_document(document)

main()