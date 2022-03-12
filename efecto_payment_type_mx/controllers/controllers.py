# -*- coding: utf-8 -*-
# from odoo import http


# class EfectoPatmentType(http.Controller):
#     @http.route('/efecto_patment_type/efecto_patment_type/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/efecto_patment_type/efecto_patment_type/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('efecto_patment_type.listing', {
#             'root': '/efecto_patment_type/efecto_patment_type',
#             'objects': http.request.env['efecto_patment_type.efecto_patment_type'].search([]),
#         })

#     @http.route('/efecto_patment_type/efecto_patment_type/objects/<model("efecto_patment_type.efecto_patment_type"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('efecto_patment_type.object', {
#             'object': obj
#         })
