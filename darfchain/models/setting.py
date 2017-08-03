from openerp import models, fields, api
from openerp.tools.translate import _
import logging
from dateutil import relativedelta
from datetime import datetime as dt
from dateutil import parser
import xlsxwriter
import StringIO
from io import BytesIO
import base64
from math import modf
from lxml import etree

_logger = logging.getLogger(__name__)

class SettingConnect(models.Model):
    
    _name = 'setting.connect'
    _defaluts = {'import_export' : 'export',}

    
    import_export = fields.Selection([('export', 'Export'), ('import', 'Import')],  string='Import/Export', default='export')
    export_node_address = fields.Char(string="Export Node Address")
    export_privat_key = fields.Text(string="Export Privat Key")
    export_asset = fields.Text(string="Export Asset")
    import_node = fields.Char(string="Import Node Address")
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

    
    @api.onchange('import_export')
    def change_export(self):
        _logger.info(self.import_export)
        if self.import_export != 'export' and self.import_export != 'import':
            self.import_export = 'import'
    
    @api.multi
    def synchronaze_button(self):
        _logger.info('test of button')
        root = etree.Element("data")
        if self.all_models:
            _logger.info('test all models')
        else:
            for item in self.models:
                model = etree.SubElement(root, 'model')
                model.set('name',item.model_id.model)
                # search records from model and put this records by field in XML
                record_of_models = self.env[str(item.model_id.model)].search([])
                if record_of_models:
                    for record in record_of_models:
                        record = etree.SubElement(model,'record')
                        model_fields = self.env['ir.model'].search([('model','=',item.model_id.model)])
                        for model_field in model_fields.fild_id:
                            etree.SubElement(record,'field').text = str(record.model_field.name)
                            print model_field
        self.xml_for_synchronization = etree.tostring(root, pretty_print=True)
                        
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
    
    date_of_export = fields.Date(string="Date of export")
    export_models = fields.One2many('export.models','journal_export_id')

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
    
    
    