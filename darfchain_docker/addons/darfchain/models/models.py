from openerp import models, fields, api
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class ModelsXMLExport(models.Model):
    
    _name = 'setting.connect'
    
    node_address = fields.Char(string="Node Address")
    privat_key = fields.Text(string="Privat Key")
    asset = fields.Text(string="Asset")
    import_node = fields.Char(string="Import Node Address")
    privat_key_import = fields.Text(string="Import Privat Key")
    import_assert = fields.Text(string="Import Asset")