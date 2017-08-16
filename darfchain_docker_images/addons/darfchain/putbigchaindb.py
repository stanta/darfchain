#!/usr/bin/python3.5 -E
import argparse
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from time import sleep
from sys import exit
import xmltodict, json
import base58
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--xml', help='get export xml from Odoo')
args = parser.parse_args()
args = vars(args)

file_xml = open(args['xml'],'r')
attachment = file_xml.read()
attachment = str(attachment)
print(attachment)
odoo = generate_keypair()

bdb_root_url = 'http://172.18.0.1:32782'  

bdb = BigchainDB(bdb_root_url)
json_data = {}
json_data_xml = json.loads(json.dumps(xmltodict.parse(attachment)))
print(json_data_xml['data'])

#print(json_data['data'])
odoo_asset = json_data_xml

odoo_asset_metadata = {
    'info': '2017-08-04 10:28:04.173090//4'
}

prepared_creation_tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=odoo.public_key,
    asset=odoo_asset,
    metadata=odoo_asset_metadata
)

fulfilled_creation_tx = bdb.transactions.fulfill(
    prepared_creation_tx,
    private_keys=odoo.private_key
)

sent_creation_tx = bdb.transactions.send(fulfilled_creation_tx)

txid = fulfilled_creation_tx['id']
print(txid)

