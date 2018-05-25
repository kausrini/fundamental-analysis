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
        self.uri = None

    # Strips down hypens in the accession number and returns the numeric value only
    def get_accession_number(self):
        return self.accession_number_str.replace('-', '')
