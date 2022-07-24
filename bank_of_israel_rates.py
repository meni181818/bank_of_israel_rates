import urllib.request
import urllib.parse
from socket import timeout
from datetime import date
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List

# config:
boi_xml_end_point: str = r'https://www.boi.org.il/currency.xml'
request_timeout_sec: int = 3

_CURRENCIES_CODES: Dict[str, str] = {
    'USD': '01',
    'GBP': '02',
    'SEK': '03',
    'CHF': '05',
    'CAD': '06',
    'DKK': '12',
    'ZAR': '17',
    'AUD': '18',
    'EUR': '27',
    'NOK': '28',
    'JPY': '31',
    'JOD': '69',
    'LBP': '70',
    'EGP': '79'
}

def get_currencies_codes_list() -> List[str]:
    return list(_CURRENCIES_CODES)


class CurrencyRate:
    def __init__(self, currency_xml_element, last_update):
        self._xml_element = currency_xml_element
        self.last_update = last_update
        self.name = self._xml_element[0].text
        self.unit = int(self._xml_element[1].text)
        self.currency_code = self._xml_element[2].text
        self.country = self._xml_element[3].text
        self.rate = float(self._xml_element[4].text)
        self.change = float(self._xml_element[5].text)
    
    def as_dict(self) -> Dict[str, str]:
        return {
            'last_update': self.last_update,
            'name': self.name,
            'unit': self.unit,
            'currency_code': self.currency_code,
            'country': self.country,
            'rate': self.rate,
            'change': self.change
        }

    def __str__(self) -> str:
        return f'CurrencyRate({self.currency_code}, {self.rate})'

    def __repr__(self) -> str:
        return f'<CurrencyRate model: ({self.currency_code}, {self.last_update})>'

class CurrenciesRates:
    def __init__(self, xml_root) -> None:
        self._xml_root = xml_root
        self.last_update = self._xml_root[0].text

        self.USD = CurrencyRate(self.extract_curr_el('USD'), self.last_update)
        self.GBP = CurrencyRate(self.extract_curr_el('GBP'), self.last_update)
        self.JPY = CurrencyRate(self.extract_curr_el('JPY'), self.last_update)
    
    def extract_curr_el(self, currency_code: str) -> ET.Element:
        return self._xml_root.find(f"./CURRENCY/[CURRENCYCODE='{currency_code}']")


def get_xml(
        currency_code: Optional[str] = None,
        rdate: Optional[str] = None,
    ) -> str:
    """
    :optional param: currency_code: valid currency code which the Bank of Israel api accepts.
    'USD', 'GBP' etc. default: all.
    :optional param: _date: iso format date. str. '2021-20-10'. default: today.
    :return: xml as string

    except for: ValueError with 'invalid currency code' arg in,
    socket.timeout and (if you are not catching it) urllib.error.URLError,
    ValueError with 'invalid date format' in
    """
    params: Dict[str, str] = {}
    
    if currency_code:
        try:
            params['curr'] = _CURRENCIES_CODES[currency_code]
        except KeyError:
            raise ValueError(
                f'invalid currency code: "{currency_code}".\n valid codes are: {get_currencies_codes_list()}',
                'invalid currency code'
            ) from None

    if rdate:
        try:
            params['rdate'] = date.fromisoformat(rdate).strftime('%Y%m%d')
        except ValueError as e:
            e.args += 'invalid date format'
            raise

    encoded_params:str = urllib.parse.urlencode(params)
    request_url: str = f'{boi_xml_end_point}?{encoded_params}'
    
    req = urllib.request.Request(request_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=request_timeout_sec) as f:
        return f.read().decode('utf-8')
        
# one currency
def get_rate(
        currency_code: str,
        rdate: Optional[str] = None,
        req_fail_silently: bool = False # request or server fail only
    ) -> CurrencyRate: # is that OK?
    """
    fetch the official bank of israel xml file, and return it as parsed
    object (CurrencyRate).
    :param currency_code: str, valid one like 'USD', 'GBP' etc.
    you can get the list by calling 'get_currencies_codes_list()'.
    :param rdate: optional. iso format date. if no actual rates for the date =>
    InvalidDate error will be raised. so 'except' for it. default=today
    :param req_fail_silently: return None if server/request failed. (still raise errors on client side errors)
    :return: CurrencyRate object initilize with the properties from boi xml api.
    if timeout = socket.timeout and urllib.error.URLError will raised, so 'except' for it.
    """
    try:
        rate_xml: str = get_xml(currency_code, rdate)
    except timeout:
        if req_fail_silently:
            return None
        raise

    root = ET.fromstring(rate_xml)

    # error checking
    if root.find('ERROR1'):
        raise ValueError(
            f'Requested date is invalid or No exchange rate published for this date ATTENTION: Date should be in format YYYYMMDD: "{rdate}"',
            'invalid date'
        )
    
    currency_xml_element = root[1]
    last_update = root[0].text
    return CurrencyRate(currency_xml_element, last_update)

# multiple currencies (all available)
def get_rates(
        currencies_codes: List[str],
        rdate: Optional[str] = None,
        req_fail_silently: bool = False
    ) -> CurrenciesRates:
    pass


def main():
    cr = get_rate('USD', '2021-12-10')
    print(cr)
    print(cr.as_dict())
    input('...')

if __name__ == '__main__':
    main()