# -*- coding: utf-8 -*-
from odoo import http

# class Darfchain(http.Controller):
#     @http.route('/darfchain/darfchain/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/darfchain/darfchain/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('darfchain.listing', {
#             'root': '/darfchain/darfchain',
#             'objects': http.request.env['darfchain.darfchain'].search([]),
#         })

#     @http.route('/darfchain/darfchain/objects/<model("darfchain.darfchain"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('darfchain.object', {
#             'object': obj
#         })