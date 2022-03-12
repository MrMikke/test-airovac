# -*- coding: utf-8 -*-
import datetime
from odoo.exceptions import UserError

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class purchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    e_mult_std =  fields.Float(digits=(1,4), string="Mult STD", help="Multiplicador solicitado al proveedor" )
    #fields.Float(digits=(1,4), string="Mult STD", help="Multiplicador solicitado al proveedor")
    e_precio_lista = fields.Monetary(digits=(10, 2),string="P.L", help="Precio de Lista X Mult STD")


    @api.onchange('e_mult_std','e_precio_lista')
    def _onchange_mult_std(self):
        self.write({'price_unit': (self.e_mult_std * self.e_precio_lista) })

    @api.onchange('product_qty','e_mult_std','e_precio_lista')
    def _onchange_product_std(self):
        self.write({'price_subtotal':(self.e_mult_std * self.e_precio_lista*self.product_qty)})


    @api.onchange('product_id')
    def _default_mult(self):
        if not self.order_id.currency_id:
            raise UserError(
                'ELIJA UNA TARIFA')
        #print(self.order_id.currency_id.name)

        moneda_usar = self.order_id
        convertido = 0

        if moneda_usar.currency_id.name == 'USD':
            convertido = self.product_id.e_precio_de_lista
            print('Son usd')
        if moneda_usar.currency_id.name == 'MXN':
            dolars = self.env['res.currency'].search(
                [('name', '=', 'USD')],
                limit=1)
            convertido = self.product_id.e_precio_de_lista / (dolars.rate * 1)
        else:
            dolars = self.env['res.currency'].search(
                [('name', '=', 'USD')],
                limit=1)

            otra_moneda = self.env['res.currency'].search(
                [('name', '=', self.order_id.currency_id.name)],
                limit=1)

            pesos = self.product_id.e_precio_de_lista / (dolars.rate * 1)
            convertido = pesos * otra_moneda.rate

        #print("convertido bebe",convertido)

        self.write({'e_precio_lista': convertido,
                    'e_mult_std':self.product_id.e_mult_std})

        #print(self.e_precio_lista)
        return




class productSupplierinfoInherit(models.Model):
    _inherit = 'product.supplierinfo'

    efecto_mult_std = fields.Float(Default=1, digits=(2,4), string="Mult STD",
                              help="Multiplicador solicitado al proveedor por marca")

    efecto_price_list = fields.Monetary(Default=1,
                                        string="Precio de lista",
                                        readonly="1",
                                        force_save="1",
                                help="Precio de lista obtenido del producto")


    @api.onchange('product_tmpl_id','currency_id')
    def _efecto_oncahgue_precio_lista(self):
        convertido = 0
        moneda_usar = self.currency_id
        if moneda_usar.name == 'USD':
            convertido = self.product_tmpl_id.e_precio_de_lista
            #print(convertido,'USD')
        if moneda_usar.name == 'MXN':
            dolars = self.env['res.currency'].search(
                [('name', '=', 'USD')],
                limit=1)
            convertido = self.product_tmpl_id.e_precio_de_lista / dolars.rate
            #print(convertido, 'MXN')
        else:
            dolars = self.env['res.currency'].search(
                [('name', '=', 'USD')],
                limit=1)

            otra_moneda = self.env['res.currency'].search(
                [('name', '=', moneda_usar.name)],
                limit=1)

            pesos = self.product_tmpl_id.e_precio_de_lista / (dolars.rate * 1)
            convertido = pesos * otra_moneda.rate
            #print(convertido, 'OTRA MONEDA')

        self.efecto_price_list = convertido
        self.efecto_mult_std = self.product_tmpl_id.e_mult_std

    @api.onchange('efecto_mult_std','efecto_price_list')
    def _efecto_oncahgue_mult_std(self):
        self.price = self.efecto_price_list \
                     * self.efecto_mult_std

