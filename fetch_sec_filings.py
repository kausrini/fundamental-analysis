#!/usr/bin/env python3

import requests
import bs4
import pathlib
from urllib.parse import urlparse
import os


from models import Company
from models import Document

# Retrieve all the filing_type documents for the company with the stock_ticker (upto 100 most recent documents)
# The details returned by this method is used to create the EDGAR urls which contain the actual filed document.
def obtain_document_details(stock_ticker, filing_type):
    company = Company()
    company.ticker = stock_ticker
    sec_uri = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type={}&dateb=&owner=include&count=100&output=xml'.format(
        stock_ticker,filing_type)
    response = requests.get(sec_uri)
    page_data = bs4.BeautifulSoup(response.text, "html.parser")
    company.cik = page_data.companyinfo.cik.string
    documents = []
    for filing in page_data.find_all('filing'):
        filing_href_string = filing.filinghref.string
        file_name = os.path.basename((urlparse(filing_href_string)).path)
        accession_number_str = file_name.split('-index')[0]

        document = Document()
        document.company = company
        document.filing_date = filing.datefiled.string
        document.filing_type = filing.type.string
        document.accession_number_str = accession_number_str
        documents.append(document)
    return documents


# Obtain the specified document from EDGAR
def obtain_document(document):

    #base_document_uri = 'https://www.sec.gov/Archives/edgar/data/{cik}/{acc_no}/Financial_Report.xlsx'
    #document_uri = base_document_uri.format(cik=document.company.cik, acc_no=document.get_accession_number())

    company_url = 'https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik}&accession_number={acc_no}'.format(
        cik=document.company.cik, acc_no=document.accession_number_str)
    res = requests.get(company_url)
    soup = bs4.BeautifulSoup(res.text, "html.parser").find_all('a', class_='xbrlviewer',
                                                                                string='View Excel Document')
    if len(soup):
        document_relative_uri = soup[0]['href']
        if not document_relative_uri:
            print('[WARNING] {} document for the company {} for the filing date {} not downloaded'.format(
                document.filing_type, document.company.ticker, document.filing_date))
            return
    else:
        print('[WARNING] {} document for the company {} for the filing date {} not downloaded'.format(
            document.filing_type, document.company.ticker, document.filing_date))
        return

    document_uri = 'https://www.sec.gov' + str(document_relative_uri)
    file_name = document.filing_date + os.path.splitext(document_relative_uri)[1]
    response = requests.get(document_uri)
    downloaded_reports_path = pathlib.Path.cwd() / 'reports' / 'downloaded_filings'
    company_path = downloaded_reports_path / document.company.ticker.upper()
    company_path.mkdir(parents=False, exist_ok=True)
    filing_type_path = company_path / document.filing_type
    filing_type_path.mkdir(parents=False, exist_ok=True)
    document_path = filing_type_path / file_name
    with document_path.open('wb') as output:
        output.write(response.content)


# Accepts a list of stock tickers and filing types as arguments and fetches the sec filings for them from EDGAR database
def fetch_sec_filings(stocks, filing_type):
    for stock in stocks:
        print('[INFO] Fetching the {} documents for the company with stock ticker {}'.format(filing_type,
                                                                                             stock))
        documents = obtain_document_details(stock, filing_type)
        for document in documents:
            obtain_document(document)
        print('[INFO] {} documents for the company with stock ticker {} have been downloaded'.format(filing_type,
                                                                                             stock))

if __name__ == '__main__':
    filing_type = '10-K'
    stocks = ['pypl', 'amzn', 'aapl']
    fetch_sec_filings(stocks, filing_type)
    #res = requests.get('https://www.sec.gov/cgi-bin/viewer?action=view&cik=1018724&accession_number=0001193125-13-028520')
    #page_data = bs4.BeautifulSoup(res.text, "html.parser")
    #url = page_data.find_all('a', class_='xbrlviewer', string='View Excel Document')[0]['href']
