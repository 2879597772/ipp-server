import json
import logging
import requests
from collections import namedtuple


class Pc2Paper(namedtuple('Pc2Paper',
        ('username', 'password', 'name', 'address1', 'address2', 'address3', 'address4', 'postcode', 'country', 'postage', 'paper', 'envelope', 'extras'))):
    # 从 https://www.pc2paper.co.uk/downloads/country.csv - From https://www.pc2paper.co.uk/downloads/country.csv
    NUMERIC_COUNTRY_CODES = {
        'UK': 1,
    }

    # 从 http://www.pc2paper.co.uk/datagetpostage.asp?method=getZonesLetterCanBeSentFrom&str=1
    # From http://www.pc2paper.co.uk/datagetpostage.asp?method=getZonesLetterCanBeSentFrom&str=1
    POSTAGE_TYPES = {
        'UK 1st': 3,
        'UK 2nd': 31,
    }

    # 从 http://www.pc2paper.co.uk/datagetpostage.asp?method=getPaperBasedOnZoneAndPrintType&str=3,Colour%20Laser
    # From http://www.pc2paper.co.uk/datagetpostage.asp?method=getPaperBasedOnZoneAndPrintType&str=3,Colour%20Laser
    PAPER_TYPES = {
        '80gsm': 4,
        '100gsm': 17,
        'Conqueror': 5,
        '80gsm double sided': 14,
    }

    ENVELOPE_TYPES = {
        'DL': 1,
        'C5': 10,
        'A4': 11,
    }

    @classmethod
    def from_config_file(cls, filename):
        # 从配置文件加载配置 - Load configuration from config file
        with open(filename) as f:
            data = json.load(f)

        conversions = [
            ('country', cls.NUMERIC_COUNTRY_CODES),
            ('postage', cls.POSTAGE_TYPES),
            ('paper', cls.PAPER_TYPES),
            ('envelope', cls.ENVELOPE_TYPES),
        ]
        for key, lookup in conversions:
            if key in data and not isinstance(data[key], int):
                data[key] = lookup[data[key]]

        return cls(**data)

    def post_pdf_letter(self, filename, pdffile):
        # 上传PDF并投递信件 - Upload PDF and post letter
        pdf_guid = self._upload_pdf(filename, pdffile)
        self._post_letter(pdf_guid)

    def _upload_pdf(self, filename, pdffile):
        # 导入翻译函数 - Import translation function
        try:
            from .translations import t
        except ImportError:
            def t(key, **kwargs):
                return key
        
        logging.info(t('uploading_pdf'))
        post_data = {
            'username': self.username,
            'password': self.password,
            'filename': filename.decode('utf-8') if isinstance(filename, bytes) else filename,
            'fileContent': [byte for byte in pdffile],
        }
        response = requests.post(
            'https://www.pc2paper.co.uk/lettercustomerapi.svc/json/UploadDocument',
            headers={'Content-type': 'application/json'},
            json=post_data)
        response_data = response.json()
        logging.debug(t('upload_response', response=response_data))
        error_messages = response_data['d']['ErrorMessages']
        if error_messages:
            raise ValueError(error_messages)
        return response_data['d']['FileCreatedGUID']

    def _post_letter(self, pdf_guid):
        # 导入翻译函数 - Import translation function
        try:
            from .translations import t
        except ImportError:
            def t(key, **kwargs):
                return key
        
        logging.info(t('posting_letter'))
        post_data = {
            'username': self.username,
            'password': self.password,
            'letterForPosting': {
                'SourceClient' : 'h2g2bob ipp-server',
                'Addresses': [{
                    'ReceiverName': self.name,
                    'ReceiverAddressLine1': self.address1,
                    'ReceiverAddressLine2': self.address2,
                    'ReceiverAddressTownCityOrLine3': self.address3,
                    'ReceiverAddressCountyStateOrLine4': self.address4,
                    'ReceiverAddressPostCode': self.postcode,
                }],
                'ReceiverCountryCode': self.country,
                'Postage': self.postage,
                'Paper': self.paper,
                'Envelope': self.envelope,
                'Extras': self.extras,
                # 'LetterBody' : '',
                'FileAttachementGUIDs': [pdf_guid],
            },
        }
        response = requests.post(
            'https://www.pc2paper.co.uk/lettercustomerapi.svc/json/SendSubmitLetterForPosting',
            headers={'Content-type': 'application/json'},
            json=post_data)
        response_data = response.json()

        logging.debug(t('post_response', response=response_data))
        error_messages = response_data['d']['ErrorMessages']
        if error_messages:
            raise ValueError(error_messages)