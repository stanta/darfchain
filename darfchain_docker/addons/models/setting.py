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
from xmljson import badgerfish as bf
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

class SettingConnect(models.Model):
    
    _name = 'setting.connect'
    _defaluts = {'import_export' : 'export',}

    
    import_export = fields.Selection([('export', 'Export'), ('import', 'Import')],  string='Import/Export', default='export')
    export_node_address = fields.Char(string="Export Node Address")
    export_privat_key = fields.Text(string="Export Privat Key")
    export_asset = fields.Text(string="Export Asset")
    import_node = fields.Char(string="Import Node Address")
    import_address = fields.Char(string="Import Waves Address")
    privat_key_import = fields.Text(string="Import Privat Key")
    import_asset = fields.Text(string="Import Asset")
    models = fields.One2many('models_setting','connect_id')
    all_models = fields.Boolean(string="All models")
    #send period
    send_period = fields.Selection([('day', 'Every day'),('week', 'Weekly'),('month','Monthly'),('Period','Time period of synchronization')],string="Period of synchronization")
    week_day = fields.Selection([
            ('0', 'Mn'),
            ('1', 'Tu'),
            ('2', 'We'),
            ('3', 'Th'),
            ('4', 'Fr'),
            ('5', 'Sd'),
            ('6', 'Sun')
        ],
        string="Day of week")
    send_time = fields.Float(string="Time")
    time_period = fields.Float(string="Time period")
    send_date = fields.Integer(string='Day of month')
    last_send_date = fields.Date(string="Date of last synchronization")
    last_send_time = fields.Float(string="Time of last synchronization")
    xml_for_synchronization = fields.Text(string="XML for synchronization")
    import_synchronization = fields.Text(string="Import Data")

    
    @api.onchange('import_export')
    def change_export(self):
        _logger.info(self.import_export)
        if self.import_export != 'export' and self.import_export != 'import':
            self.import_export = 'import'
    
    @api.multi
    def synchronaze_button(self):
        date_of_synchronization = dt.now()
        if self.import_export == 'export':
            res = self.env['journal.of.export'].create({'date_of_export':date_of_synchronization})
            #-------------get general info timestemp for synchronization with waves and than search of this record in bigchaindb
            general_info_text = str(date_of_synchronization)+'_'+str(res.id)
            #------------------------------------------ create main data element with general info
            root = etree.Element("data")
            general_info = etree.SubElement(root,'general_info')
            general_info.text=general_info_text
            #----------------------- create element of model from setting wizard
            control_model_dict = {}
            if self.all_models:
                _logger.info('test all models') #to-do for all model in DB
            else:
                #-------------------- get all models from setting wizard in item
                #==============================================================================================================
                for item in self.models:
                    model = etree.SubElement(root, 'model') #----------------------------------------------create element model
                    model.set('name',str(item.model_id.model)) #-------------------------------------------add name to model
                    model.set('main','True')
                    # search records from model and put this records by field in XML
                    #________________-_________________________________________________________________________________________
                    record_of_models = self.env[str(item.model_id.model)].search([])
                    if record_of_models:
                        records_list = [] #list of records for model in model control dictionary
                        for record in record_of_models:
                            record_xml = etree.SubElement(model,'record')
                            record_xml.set('id',str(record.id)) #get id of record of model
                            #==================================================================================================
                            #-------------------- add current id to records list and write values in control model dictionary
                            records_list.append(record.id)
                            if item.model_id.model in control_model_dict.keys():
                                records_value = control_model_dict[item.model_id.model]
                                list_for_record = records_value+records_list
                                control_model_dict.update({item.model_id.model:list_for_record})
                            else:
                                control_model_dict.update({item.model_id.model:records_list})
                            #==================================================================================================   
                            model_fields = self.env['ir.model'].search([('model','=',item.model_id.model)]) #get object of model
                            for model_field in model_fields.field_id:
                                # create field element without special information
                                res_field = str(getattr(record,str(model_field.name)))
                                if res_field not in ['id','create_date','create_uid','__last_update','message_ids'] and res_field != "" and res_field[res_field.find("(")+1:res_field.find(")")] != "":
                                    field = etree.SubElement(record_xml,'field') #add field element to record
                                    field.set('name',str(model_field.name))
                                    field.set('type',str(model_field.ttype))
                                    current_field_result = getattr(record,str(model_field.name)) #get value of record
                                    if str(model_field.ttype) in ['one2many','many2many','many2one']:
                                        list_of_id = str(res_field[res_field.find("(")+1:res_field.find(")")]).split(",")
                                        list_of_one = list(res_field[res_field.find("(")+1:res_field.find(")")])
                                        if list_of_one[-1] == ',':
                                            list_of_id = list_of_id[0:-1]
                                        list_of_id = map(int,list_of_id)
                                        model_name = str(res_field.split('(')[0])
                                        field.text="{'"+model_name+"':"+str(list_of_id)+"}"
                                        # create model with record accoding to list_of_id
                                        #check if model exist in control dict
                                        if model_name in control_model_dict.keys():
                                            for list_item in control_model_dict[model_name]:
                                                if list_item in list_of_id:
                                                    list_of_id.remove(list_item)
                                        else:
                                            model_rel = etree.SubElement(root, 'model')
                                            model_rel.set('name',model_name)
                                            model_rel.set('main','False')
                                        #----- get all needed records from model
                                        records_of_current_model = self.env[model_name].search([('id','in',list_of_id)])
                                        fields_of_model = self.env['ir.model'].search([('model','=',model_name)])
                                        # create element model for relation models
                                        excepted_fields = ['password_crypt','id','create_date','create_uid','__last_update','message_ids','login_date','message_channel_ids',
                                                            'message_follower_ids','message_is_follower', 'message_last_post','message_needaction','message_needaction_counter',
                                                            'message_partner_ids','message_unread', 'message_unread_counter','logo','logo_web','image','image_medium','image_small']
                                        if records_of_current_model:
                                            for record_c in records_of_current_model:
                                                if model_name in control_model_dict.keys():
                                                    for model_by_attr in root.iter('model'):
                                                        if model_by_attr.attrib['name'] == model_name:
                                                            next_record = etree.SubElement(model_by_attr,'record')
                                                            next_record.set('id',str(record_c.id)) 
                                                else:
                                                    next_record = etree.SubElement(model_rel,'record')
                                                    next_record.set('id',str(record_c.id))
                                                for field_c in fields_of_model.field_id:
                                                    current_field_n_result = getattr(record_c,str(field_c.name))
                                                    res_field = str(current_field_n_result)
                                                    if  field_c.name not in excepted_fields:
                                                        field_n = etree.SubElement(next_record,'field') #add field element to record
                                                        field_n.set('name',str(field_c.name))
                                                        field_n.set('type',str(field_c.ttype))
                                                        if str(field_c.ttype) in ['one2many','many2many','many2one']:
                                                            if res_field is not False:
                                                                list_of_id = str(res_field[res_field.find("(")+1:res_field.find(")")]).split(",")
                                                                list_of_one = list(res_field[res_field.find("(")+1:res_field.find(")")])
                                                                if len(list_of_one) > 0:
                                                                    if list_of_one[-1] == ',' and len(list_of_one)>0:
                                                                        list_of_id = list_of_id[0:-1]
                                                                if len(list_of_one) > 0:
                                                                    list_of_id = map(int,list_of_id)
                                                                model_name_str = str(res_field.split('(')[0])
                                                                if len(list_of_one)==0:
                                                                    field_n.text="False"
                                                                else:
                                                                    field_n.text="{'"+model_name_str+"':"+str(list_of_id)+"}"
                                                            else:
                                                                field_n.text="False"
                                                        else:
                                                            field_n.text=str(current_field_n_result)
                                                    if model_name in control_model_dict.keys():
                                                        records_value = control_model_dict[model_name]
                                                        list_for_record = records_value+list_of_id
                                                        control_model_dict.update({model_name:list_for_record})
                                                    else:
                                                        control_model_dict.update({model_name:list_of_id})
                                        if model_name in control_model_dict.keys():
                                            records_value = control_model_dict[model_name]
                                            list_for_record = records_value+list_of_id
                                            control_model_dict.update({model_name:list_for_record})
                                        else:
                                            control_model_dict.update({model_name:list_of_id})
                                    else:
                                        field.text=str(current_field_result)
                               
            self.xml_for_synchronization = etree.tostring(root, pretty_print=True)
            #self.xml_for_synchronization = etree.tostring(root, pretty_print=False)
            xml_result = etree.tostring(root, pretty_print=False)
            #xml_result = xml_result.replace('"','\\"')
            #-------------------------------------------- write xml to temp file
            file_to_save_with_path = '/tmp/'+general_info_text
            temp_file = open(file_to_save_with_path,'w')
            temp_file.write(xml_result)
            temp_file.close()
            string = '/usr/bin/putbigchaindb.py --xml="'+file_to_save_with_path+'"'
            #------------------------------------- synchronaze with waves blockchain
            pw.setNode(node = self.export_node_address, chain = 'testnet')
            myAddress = pw.Address(privateKey=self.export_privat_key)
            myAddress.sendWaves(myAddress, 110000, attachment=general_info_text,txFee=100000)
            os.system(string)
            
            #call(string, shell=True)
            #self.xml_for_synchronization = dumps(xmltodict.parse(etree.tostring(root, pretty_print=True)))
        else:
            _logger.info('start import')
            url_of_access = self.import_node+'/transactions/address/'+self.import_address+'/limit/100'
            result_waves = requests.get(url_of_access)
  
            attachment = result_waves.json()[0][0]['attachment']
            attachment = base58.b58decode(attachment)
            print attachment
            conn = r.connect('goldsoft.org', 28015).repl()
            get_result = r.db('bigchain').table('assets').filter({'data':{"general_info":  attachment}}).run(conn)
            dict_for_record  = {}
            excepted_fields = ['password_crypt','id','create_date','create_uid','__last_update','message_ids','login_date','mail_followers','write_date','message_last_post','validity_date','message_is_follower']
            for item_import in get_result:
#                 print item_import
                self.import_synchronization = item_import
                test = item_import
                def get_name(json,model_name,record_id):
                    for item in json['data']['model']:
                        if item['@name'] == model_name:
                            if isinstance(item['record'],list):
                                for record in item['record']:
                                    if int(record['@id']) == record_id:
                                        for field in record['field']:
                                            if field['@name'] == 'name':
                                                result = field['#text']
                                                return result
                            else:
                                if int(item['record']['@id']) == record_id:
                                    for field_cur in item['record']['field']:
                                        if field_cur['@name'] == 'name':
                                            result = field_cur['#text']
                                            return result
#                   
                def get_dict_record(json,model_name,record_id):
                    dict_for_record_field = {}
                    result_dict = {}
                    for item in json['data']['model']:
                        if item['@name'] == model_name:
                            if isinstance(item['record'],list):
                                for record in item['record']:
                                    if int(record['@id']) == record_id:
                                        for field in record['field']:
                                            if '#text' in field.keys():
                                                if field['@type'] == 'many2one' and field['#text'] != 'False':
                                                    key = ast.literal_eval(field['#text']).keys()[0]
                                                    list_id =  ast.literal_eval(field['#text'])[key]
                                                    dict_for_record_field.update({field['@name']:list_id[0]})
                                                elif field['@type'] in ['one2many']:
                                                    if str(field['#text']) != 'False':
                                                        key = ast.literal_eval(field['#text']).keys()[0]
                                                        list_id =  ast.literal_eval(field['#text'])[key]
                                                        record_list = []
                                                        for list_record in list_id:
                                                            record_list.append((4,list_record,False))
                                                        if field['@name'] == 'procurement_ids':
                                                            pass
                                                        else:
                                                            dict_for_record_field.update({field['@name']:record_list})
                                                else:
                                                    pass
                                                    #dict_for_record_field.update({field['@name']:field['#text']})
                            else:
                                if int(item['record']['@id']) == record_id:
                                    for field_cur in item['record']['field']:
                                        if '#text' in field_cur.keys():
                                            if field_cur['@type'] == 'many2one' and field_cur['#text'] != 'False':
                                                    key = ast.literal_eval(field_cur['#text']).keys()[0]
                                                    list_id =  ast.literal_eval(field_cur['#text'])[key]
                                                    dict_for_record_field.update({field_cur['@name']:list_id[0]})
                                            elif field_cur['@type'] in ['one2many']:
                                                print field_cur['#text']
                                                if str(field_cur['#text']) != 'False':
                                                    key = ast.literal_eval(field_cur['#text']).keys()[0]
                                                    list_id =  ast.literal_eval(field_cur['#text'])[key]
                                                    record_list = []
                                                    for list_record in list_id:
                                                        record_list.append((4,list_record,False))
                                                    if field_cur['@name'] == 'procurement_ids':
                                                        pass
                                                    else:
                                                        dict_for_record_field.update({field_cur['@name']:record_list})
                                            else:
                                                pass
                                                #dict_for_record_field.update({field_cur['@name']:field_cur['#text']})
                    return dict_for_record_field
                
                for item in test['data']['model']:
                    if item['@main'] == 'True':
                        if isinstance(item['record'],list):
                            for record in item['record']:
                                for field in record['field']:
                                    if field['@type'] not in ['one2many','many2many','many2one'] and item['@name'] == 'sale.order' and field['@name'] not in excepted_fields:
                                        dict_for_record.update({field['@name']:field['#text']})
                                    if field['@type'] == 'one2many'  and field['@name'] not in excepted_fields:
                                        key = ast.literal_eval(field['#text']).keys()[0]
                                        list_id =  ast.literal_eval(field['#text'])[key]
                                        list_of_one2many = []
                                        if key not in ['mail.followers']:
                                            for test_list in list_id:
                                                result = get_name(test,key,test_list)
                                                result_dict = get_dict_record(test,key,test_list)
                                                name_field_current = self.env[key].search([('name','=',result)])
                                                if result == name_field_current.name:
                                                    list_of_one2many.append((4,name_field_current.id,False))
                                                else:
                                                    result_dict = get_dict_record(test,key,test_list)
                                                    #res = self.env[key].create(result_dict)
                                                    list_of_one2many.append((0,False,result_dict))        
                                            dict_for_record.update({field['@name']:list_of_one2many})
                                                
                                    if field['@type'] == 'many2one':
                                        print 'test many2one ++++++++++++++++++++++++++++++++'
                                        key = ast.literal_eval(field['#text']).keys()[0]
                                        list_id =  ast.literal_eval(field['#text'])[key]
                                        list_of_many2one = []
                                        for test_list in list_id:
                                            result = get_name(test,key,test_list)
                                            result_dict = get_dict_record(test,key,test_list)
                                            name_field_current = self.env[key].search([('name','=',result)])
                                            if result == name_field_current.name:
                                                list_of_many2one.append(name_field_current.id)
                                                dict_for_record.update({field['@name']:name_field_current.id})
                                            else:
                                                result_dict = get_dict_record(test,key,test_list)
                                                #res = self.env[key].create(result_dict)
                                                #dict_for_record.update({field['@name']:res.id})
                                                dict_for_record.update({field['@name']:list_id[0]})
                                    if field['@type'] == 'many2many':
                                        print field['@type']
                                        print field['#text']
                        else:
                            for field in item['record']['field']: #record of fields
                                if '#text' in field.keys():
                                    if field['@type'] not in ['one2many','many2many','many2one'] and item['@name'] == 'sale.order' and field['@name'] not in excepted_fields:
                                        dict_for_record.update({field['@name']:field['#text']})
                                    if field['@type'] == 'one2many' and field['@name'] not in excepted_fields:
                                        key = ast.literal_eval(field['#text']).keys()[0]
                                        list_id =  ast.literal_eval(field['#text'])[key]
                                        list_of_one2many = []
                                        if key not in ['mail.followers']:
                                            for test_list in list_id:
                                                result = get_name(test,key,test_list)
                                                result_dict = get_dict_record(test,key,test_list)
                                                name_field_current = self.env[key].search([('name','=',result)])
                                                if result is not None:
                                                    result_dict = get_dict_record(test,key,test_list)
                                                    print result_dict
                                                    if result == name_field_current.name:
                                                        list_of_one2many.append((4,name_field_current.id,False))
                                                    else:
                                                        result_dict = get_dict_record(test,key,test_list)
                                                        #res = self.env[key].create(result_dict)
                                                        list_of_one2many.append((0,False,result_dict))        
                                            dict_for_record.update({field['@name']:list_of_one2many})
                                    if field['@type'] == 'many2one':
                                        print 'test many2one ++++++++++++++++++++++++++++++++'
                                        key = ast.literal_eval(field['#text']).keys()[0]
                                        list_id =  ast.literal_eval(field['#text'])[key]
                                        list_of_many2one = []
                                        for test_list in list_id:
                                            result = get_name(test,key,test_list)
                                            result_dict = get_dict_record(test,key,test_list)
                                            name_field_current = self.env[key].search([('name','=',result)])
                                            if result is not None:
                                                if result == name_field_current.name:
                                                    list_of_many2one.append(name_field_current.id)
                                                    dict_for_record.update({field['@name']:list_of_many2one[0]})
                                                else:
                                                    result_dict = get_dict_record(test,key,test_list)
                                                    if 'procurement_ids' in result_dict.keys() and key == 'procurement.group':
                                                        del result_dict['procurement_ids']
                                                    res = self.env[key].create(result_dict)
                                                    dict_for_record.update({field['@name']:res.id})
                                                    
                                    if field['@type'] == 'many2many':
                                        print field['@type']
                                        print field['#text']
                                        print 'test ----------------- '
                                        print ast.literal_eval(field['#text']).keys()
                                        key = ast.literal_eval(field['#text']).keys()[0]
                                        list_id =  ast.literal_eval(field['#text'])[key]
                                        print list_id[0]
                                        print list_id
                                        for test_list in list_id:
                                            result = get_name(test,key,test_list)
                                            name_field = self.env[key].search([('name','=',result)])
                                            if name_field.name == result:
                                                print 'test of name get'
                                                print name_field
                print dict_for_record
                res_create = self.env['sale.order'].with_context(mail_create_nosubscribe=True).create(dict_for_record)
    @api.multi
    def synchronaze(self,id):
        current_connection = self.env['setting.connect'].search([('id','=',id)])[0]
        if current_connection.all_models:
            _logger.info('test all models')
        else:
            for item in current_connection.models:
                _logger.info(item.model_id.name)
                _logger.info(item.model_id.model)
                for field in item.model_id.field_id:
                    _logger.info(field.type)
                    _logger.info(field.name) 
    
class ModelsSetting(models.Model):
    
    _name = 'models_setting'
    
    connect_id = fields.Many2one('setting.connect',default=lambda self: self._context.get('connect_id', self.env['setting.connect']))
    model_id = fields.Many2one('ir.model')
    
class JournalOfExport(models.Model):
    
    _name = 'journal.of.export'
    
    date_of_export = fields.Char(string="Synchronization date")

class JournalOfImport(models.Model):
    _name = 'journal.of.import'
    
    date_of_imoprt = fields.Char(string="Synchronized date")

class ExportModels(models.Model):
    
    _name = 'export.models'
    
    journal_export_id = fields.Many2one('journal.of.export')
    model_id = fields.Many2one('ir.model')
    record_count = fields.Integer(string="Record count")
    
class NextDispatchDate(models.Model):
    _name = 'dafr.next_dispatches'
    _inherits = {'setting.connect': 'connect_id'}

    next_sending_date = fields.Datetime(string='Next synchronization')

    @api.model
    def get_next_sending_date(self, *args):

        connects = self.env['setting.connect'].search([])
        
        self.update_next_dispatches(connects)
         
        for connect in self.search([]):
            next_hour = int(connect.send_time)
            # Due to the floating separator minute can vary +-1 min
            next_minute = int(modf(connect.send_time)[0] * 60)
            time = dt.now().replace(hour=next_hour, minute=next_minute)
            date_of_run = dt.now().strftime("%Y-%m-%d %H")
            record_to_process = self.env['darf.next_dispatches'].search([('id','=',connect.id)])
            if connect.time_period != 0 and connect.send_priod == 'Period':
                self.env['setting.connect'].synchronaze(connect.connect_id.id)
            if record_to_process and connect.send_priod != 'Period':
                self.env['setting.connect'].synchronaze(connect.connect_id.id)
            if connect.send_period == 'day':
                connect.next_sending_date = time
            elif connect.send_period == 'week':
                if int(time.weekday()) <= int(connect.week_day):
                    time = time + dt.timedelta(
                            days=int(connect.week_day) - time.date().weekday())
                else:
                    time = time + dt.timedelta(
                            days=int(connect.week_day) - time.date().weekday(),
                            weeks=1)
                connect.next_sending_date = time

            elif connect.send_period == 'month':

                if int(time.day) > int(connect.send_date):
                    time = time + relativedelta(months=+1)

                time = time.replace(day=int(connect.send_date))
                connect.next_sending_date = time

    @api.multi
    def update_next_dispatches(self, ids):
        for connect in ids:
            check_of_connect = self.search([('id','=',connect.id)]).id
            if  check_of_connect is False and (connect.send_date or connect.send_time):
                self.env['darf.next_dispatches'].create(
                        {'connect_id': connect.id})
    
    
    