from openerp import models, fields, api
from openerp.tools.translate import _
import logging
#from fingerprint import Fingerprint
from dateutil import relativedelta
from datetime import datetime as dt
from dateutil import parser
import xlsxwriter
import StringIO
from io import BytesIO
import base64
import hashlib
import xmltodict
from math import modf
from lxml import etree
#from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring
from json import dumps
import pywaves as pw
import requests
import base58
import rethinkdb as r
from subprocess import call
import os
import ast


_logger = logging.getLogger(__name__)

class CryptoCurrency(models.Model):
    
    _inherit = 'res.partner'
    
    bitcoin_balance = fields.Float(string='Bitcoin Balance',compute='_bitcoin_balance')
    bitcoin_address = fields.Char(string='Bitcoin Address')
    waves_balance = fields.Float(string='Waves Balance', compute='_waves_balance')
    waves_address = fields.Char(string='Waves Address')
    ethereum_address = fields.Char(string="Ethereum Address")
    ethereum_balance = fields.Float(string="Ethereum Balance",compute='_ethereum_balance')
    
    
    @api.one
    def _ethereum_balance(self):
        if self.ethereum_address:
            requests_api_ethereum = 'https://api.blockcypher.com/v1/eth/main/addrs/'+self.ethereum_address+'/balance'
            req = requests.get(requests_api_ethereum)
            balance = req.json()['final_balance']
            self.ethereum_balance = balance
        else:
            self.ethereum_balance
    
    
    @api.one
    def _waves_balance(self):
        if self.waves_address:
            address = pw.Address(self.waves_address)
            self.waves_balance = address.balance()
        else:
            self.waves_balance = 0
    
    @api.one
    def _bitcoin_balance(self):
        _logger.info(self.bitcoin_address)
        if self.bitcoin_address:
            request_api = 'https://blockchain.info/rawaddr/'+self.bitcoin_address
            req = requests.get(request_api)
            balance=req.json()['final_balance']
            self.bitcoin_balance = float(balance)/100000000
        else:
            self.bitcoin_balance = 0
            
            