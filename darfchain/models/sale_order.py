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
import json
from openerp.exceptions import UserError
from web3 import Web3, HTTPProvider, IPCProvider
import hashlib

_logger = logging.getLogger(__name__)

class sign_sale_order(models.Model):
    
    _inherit = 'sale.order'
    
    signature_status = fields.Boolean('Sign')
    signature_hash = fields.Char('Signature Hash')
    gas_for_signature = fields.Float('Gas for signature',compute='_gas_for_signature')
    gas_limit = fields.Float('Gas limit',compute='_gas_limit')
    signature_timestamp = fields.Char('Signature timestamp')
    result_of_check = fields.Char(default='Not checked')
    
    @api.one
    def getDocumentMD5(self):
        return hashlib.md5(str(self.incoterm)).hexdigest()
    
    @api.one
    def get_ethereum_addres(self):
        ethereum_address = self.env['setting.connect'].search([('platforma','=','ethereum')])
        result_ethereum_dic = {}
        if ethereum_address:
            result_ethereum_dic.update({'ethereum_address':ethereum_address[0].ethereum_pk,
                                        'ethereum_interface': ethereum_address[0].ethereum_address,
                                        'address_node':ethereum_address[0].ethereum_node_address})
        return result_ethereum_dic
    
    def _gas_for_signature(self):
        ethereum_setting = {}
        if self.get_ethereum_addres()[0].keys() == {}:
            result_of_gas_estimate = 0
        else:
            date_of_synchronization = dt.now()
            ethereum_setting = self.get_ethereum_addres()
            ethereum_setting = ethereum_setting[0]
            web3 = Web3(HTTPProvider(ethereum_setting['address_node']))
            abi_json = ethereum_setting['ethereum_interface']
            ethereum_contract_address = ethereum_setting['ethereum_address']
            contract =  web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
            hash_of_synchronaze = '"'+base58.b58encode(str(date_of_synchronization))+'"'
            md5 = self.getDocumentMD5()
            md5_for_solidity = '"'+md5[0]+'"'
            print hash_of_synchronaze
            try:
                result_of_gas_estimate = contract.estimateGas().setDocumentHash(str(hash_of_synchronaze),md5_for_solidity)
            except:
                result_of_gas_estimate = 0
        self.gas_for_signature = result_of_gas_estimate
        return result_of_gas_estimate
    
    def _gas_limit(self):
        ethereum_setting = {}
        if self.get_ethereum_addres()[0].keys() == {}:
            result_of_gas_limit = 0
        else:
            ethereum_setting = self.get_ethereum_addres()
            ethereum_setting = ethereum_setting[0]
            web3 = Web3(HTTPProvider(ethereum_setting['address_node']))
            abi_json = ethereum_setting['ethereum_interface']
            ethereum_contract_address = ethereum_setting['ethereum_address']
            contract =  web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
            result_of_gas_limit = contract.call().getGasLimit()
            self.gas_limit = result_of_gas_limit
        return result_of_gas_limit
    
    def signature_action(self):
        ethereum_setting = {}
        date_of_synchronization = dt.now()
        ethereum_setting = {}
        ethereum_setting = self.get_ethereum_addres()
        ethereum_setting = ethereum_setting[0]
        web3 = Web3(HTTPProvider(ethereum_setting['address_node']))
        abi_json = ethereum_setting['ethereum_interface']
        ethereum_contract_address = ethereum_setting['ethereum_address']
        contract =  web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
        hash_of_synchronaze = '"'+base58.b58encode(str(date_of_synchronization))+'"'
        print hash_of_synchronaze
        md5 = self.getDocumentMD5()
        md5_for_solidity = '"'+md5[0]+'"'
        TransactionHashEthereum = contract.transact().setDocumentHash(str(hash_of_synchronaze),str(md5_for_solidity))
        self.signature_timestamp = str(date_of_synchronization)
        self.signature_hash = TransactionHashEthereum
        self.signature_status = True
        self.env['journal.signature'].create({'name':self.name,
                                              'checksum':md5[0],
                                              'hash_of_signature':TransactionHashEthereum,
                                              'timestamp_of_document':self.signature_timestamp,
                                              'date_of_signature':date_of_synchronization})
        root = etree.Element("data")
        sale_order_name = etree.SubElement(root,'name')
        sale_order_name.text=self.name
        sale_order_hash = etree.SubElement(root,'transaction_hash')
        sale_order_hash.text=TransactionHashEthereum
        sale_order_md5 = etree.SubElement(root,'md5')
        sale_order_md5.text=md5[0]
        xml_result = etree.tostring(root, pretty_print=False)
        #xml_result = xml_result.replace('"','\\"')
        #-------------------------------------------- write xml to temp file
        file_to_save_with_path = '/tmp/'+self.name+str(date_of_synchronization)
        temp_file = open(file_to_save_with_path,'w')
        temp_file.write(xml_result)
        temp_file.close()
        string = '/usr/bin/putbigchaindb.py --xml="'+file_to_save_with_path+'"'
        os.system(string)
        
    
    def check_signature_action(self):
        date_of_synchronization = dt.now()
        ethereum_setting = self.get_ethereum_addres()
        ethereum_setting = ethereum_setting[0]
        web3 = Web3(HTTPProvider(ethereum_setting['address_node']))
        abi_json = ethereum_setting['ethereum_interface']
        ethereum_contract_address = ethereum_setting['ethereum_address']
        contract =  web3.eth.contract(abi = json.loads(abi_json), address=ethereum_contract_address)
        get_transact = web3.eth.getTransaction(self.signature_hash)
        timestamp = str(contract.call(get_transact).getDocumentHash().replace('"',''))
        md5 = self.getDocumentMD5()
        md5_from_contract = contract.call(get_transact).getDocumentMD5()
        if str(md5_from_contract).replace('"', '') == md5[0]:
            self.result_of_check = 'OK'
        else:
            self.result_of_check = 'Error Checksum'
        
        
    
        
class JournalOfSignature(models.Model):
    _name = 'journal.signature'
    
    name = fields.Char('Document Number')
    hash_of_signature = fields.Char('Hash of signature')
    checksum = fields.Char('Check sum of Document')
    timestamp_of_document = fields.Char('Timestamp')
    date_of_signature = fields.Date('Date of signature')
    
    
     
    