# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.addons.crm.models.digest import Digest


class efecto_patment_type(models.Model):
    _inherit = 'account.payment'



    efecto_payment_type = fields.Float(digits=(3, 5),
                                       default=1,
                                       string="Tipo de cambio",
                                       help="tipo de cambio")

    efecto_payment_type_original = fields.Float(digits=(3, 5),
                                       default=1,
                                       string="Tipo de cambio original",
                                       help="tipo de cambio")

    efecto_base_amount = fields.Monetary(default=1,
                                       string="Importe Original",
                                       help="tipo de cambio")

    efecto_oculta_help = fields.Integer(default=1)






    @api.onchange('amount','currency_id')
    def _efecto_onchange_currency_id(self):
        print(self.currency_id.name,self.amount)
        if self.currency_id.name == 'MXN' and self.payment_difference == 0:
            self.efecto_base_amount = self.amount
            base = self.amount + self.payment_difference
            self.valor = self.amount
            dolars = self.env['res.currency'].search(
                [('name', '=', 'USD')],
                limit=1)
            en_dolares = round(base * dolars.rate,2)
            #print(self.amount,dolars.rate,en_dolares)
            self.efecto_payment_type = base / en_dolares
            #print(self.efecto_payment_type)
            self.efecto_payment_type_original = self.efecto_payment_type
            #print(self.efecto_payment_type)
        if self.currency_id.name != 'MXN':
            self.efecto_oculta_help = 0
            #print('BOLEANO',self.efecto_oculta_help)
        else:
            self.efecto_oculta_help = 1
            #print('BOLEANO', self.efecto_oculta_help)

    @api.onchange('efecto_payment_type')
    def _onchange_efecto_payment_type(self):
        if self.currency_id.name == 'MXN':
           #print('*****************************')
           base = self.amount+self.payment_difference
           #print('Base:',base)
           dolars = self.env['res.currency'].search(
               [('name', '=', 'USD')],
               limit=1)
           en_dolares = round(base * dolars.rate, 2)
           #print('En dolares;',en_dolares,'Paymen type:',self.efecto_payment_type)
           self.amount = en_dolares * self.efecto_payment_type
           #print('amount:', self.amount)
           #print(self.payment_difference,self.amount,(self.amount+self.payment_difference))
           self.efecto_oculta_help = 1
           #print('BOLEANO', self.efecto_oculta_help)
        else:
            self.efecto_oculta_help = 0
            #print('BOLEANO', self.efecto_oculta_help)




        