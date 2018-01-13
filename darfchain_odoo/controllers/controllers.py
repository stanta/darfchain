# -*- coding: utf-8 -*-
from odoo import http

class Darfchain(http.Controller):
    @http.route('/darfchain/darfchain/', auth='public')
     def index(self, **kw):
         return "Hello, world"

     @http.route('/darfchain/darfchain/objects/', auth='public')
     def list(self, **kw):
         return http.request.render('darfchain.listing', {
             'root': '/darfchain/darfchain',
             'objects': http.request.env['darfchain.darfchain'].search([]),
         })

     @http.route('/darfchain/darfchain/objects/<model("darfchain.darfchain"):obj>/', auth='public')
     def object(self, obj, **kw):
         return http.request.render('darfchain.object', {
             'object': obj
         })

     def darf_waves(self):

        import pywaves as pw
        from models import darf_addr

        myAddress = pw.Address(privateKey='CtMQWJZqfc7PRzSWiMKaGmWFm4q2VN5fMcYyKDBPDx6S')
        otherAddress = pw.Address('3PNTcNiUzppQXDL9RZrK3BcftbujiFqrAfM')
        myAddress.sendWaves(otherAddress, 10000000)
        myToken = myAddress.issueAsset('Token1', 'My Token', 1000, 0)
        while not myToken.status():
            pass
        myAddress.sendAsset(otherAddress, myToken, 50)

    def save_status(self):
        # get saves changes
        # archive with encription with password
        # to save status

    def collect_status(self):
        #1. get list of objects
        #2. extract status changes for each
        #3. make

    def load_changes (self):
        #1. load transaction form API
        #2. recompress/decrypt
        #3. import to odoo
