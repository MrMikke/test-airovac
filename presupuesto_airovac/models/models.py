# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class presupuesto_airovac(models.Model):
#     _name = 'presupuesto_airovac.presupuesto_airovac'
#     _description = 'presupuesto_airovac.presupuesto_airovac'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
