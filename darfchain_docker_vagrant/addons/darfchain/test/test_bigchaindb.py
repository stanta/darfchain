from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from time import sleep
from sys import exit
import base58
import gzip
from io import StringIO
out = StringIO()

odoo = generate_keypair()

bdb_root_url = 'https://goldsoft.org:59984'  

bdb = BigchainDB(bdb_root_url)

odoo_asset = {
    
}

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