# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bitcoinlib import wallets, networks #wallet


 class darf_addr (models.Model):
     _name = 'darfchain.darfchain'

     blockchain_name = fields.Char()
     blockchain_address = wallets()
     blockchain_socket = networks()
     description = fields.Text()

     @api.depends('value')
     def _value_pc(self):
         self.value2 = float(self.value) / 100