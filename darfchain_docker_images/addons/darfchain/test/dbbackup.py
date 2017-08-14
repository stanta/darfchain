import base64

import xmlrpclib

sock = xmlrpclib.ServerProxy('http://goldsoft:8071/xmlrpc/db') 
all_database = sock.list()
print all_database
# for database in all_database:
# 
#     file_path = "/home/sergey/git/darfchain/chain/backup/" 
#     
#     file_path += database
#     
#     file_path += ".dump"
#     
#     backup_db_file = open(file_path, 'wb')
#     
#     backup_db_file.write(base64.b64decode(sock.dump('admin', database))) #admin is master password in my case
#     
#     backup_db_file.close()