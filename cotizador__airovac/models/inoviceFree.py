import base64
from itertools import groupby
import re
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import requests
from pytz import timezone

from lxml import etree
from lxml.objectify import fromstring
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import float_round
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr

from odoo.addons.l10n_mx_edi.tools.run_after_commit import run_after_commit

class AccountMoveFree(models.Model):
    _inherit = 'account.move'

    l10n_mx_edi_cfdi_name = fields.Char(string='CFDI name', copy=False, readonly=False,
                                        help='The attachment name of the CFDI editado.')

class AccountMoveLineEfecto(models.Model):
    _inherit = "account.move.line"



    def _get_computed_price_unit(self):
        self.ensure_one()

        if not self.product_id:
            return self.price_unit
        elif self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.

            if  self.move_id.currency_id.name == "USD":
                price_unit = self.product_id.e_precio_de_lista

            if self.move_id.currency_id.name == "MXN":
                #print("no son dolares")
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)
                price_unit = self.product_id.e_precio_de_lista / (
                            dolars.rate * 1)
            else:
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)

                otra_moneda = self.env['res.currency'].search(
                    [('name', '=',
                      self.move_id.currency_id.name)],
                    limit=1)

                pesos = self.product_id.e_precio_de_lista / (dolars.rate * 1)
                #print("price unit primera parada",pesos, otra_moneda.rate)
                price_unit = pesos * otra_moneda.rate

        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            price_unit = self.product_id.standard_price
            #print("PRICE UNIT")
        else:
            #print("ELSE PRICE UNIT")
            return self.price_unit

        if self.product_uom_id != self.product_id.uom_id:
            price_unit = self.product_id.uom_id._compute_price(price_unit, self.product_uom_id)
            #print("ultimo price unit",price_unit)

        #print("price unit return",price_unit)
        return price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or line.display_type in (
            'line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            line.tax_ids = line._get_computed_taxes()
            line.product_uom_id = line._get_computed_uom()
            line.price_unit = line._get_computed_price_unit()

            # Manage the fiscal position after that and adapt the price_unit.
            # E.g. mapping a price-included-tax to a price-excluded-tax must
            # remove the tax amount from the price_unit.
            # However, mapping a price-included tax to another price-included tax must preserve the balance but
            # adapt the price_unit to the new tax.
            # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
            # 100 as balance but set 120 as price_unit.
            #print("Onchangue id",line.price_unit)
            if line.tax_ids and line.move_id.fiscal_position_id:
                line.price_unit = line._get_price_total_and_subtotal()[
                    'price_subtotal']
                #print("en el if", line.price_unit)
                line.tax_ids = line.move_id.fiscal_position_id.map_tax(
                    line.tax_ids._origin, partner=line.move_id.partner_id)
                accounting_vals = line._get_fields_onchange_subtotal(
                    price_subtotal=line.price_unit,
                    currency=line.move_id.company_currency_id)
                balance = accounting_vals['debit'] - accounting_vals['credit']
                line.price_unit = line._get_fields_onchange_balance(
                    balance=balance).get('price_unit', line.price_unit)

            # Convert the unit price to the invoice's currency.
            company = line.move_id.company_id
            #print('ultimo antes de convertir',line.price_unit)
            if not line.move_id.currency_id.name == "USD":
                convertido = 0
                if line.move_id.currency_id.name == "MXN":
                    #print("no son dolares")
                    dolars = self.env['res.currency'].search(
                        [('name', '=', 'USD')],
                        limit=1)
                    convertido = self.product_id.e_precio_de_lista / (
                            dolars.rate * 1)
                else:
                    dolars = self.env['res.currency'].search(
                        [('name', '=', 'USD')],
                        limit=1)

                    otra_moneda = self.env['res.currency'].search(
                        [('name', '=',
                          line.move_id.currency_id.name)],
                        limit=1)

                    pesos = self.product_id.e_precio_de_lista / (
                                dolars.rate * 1)
                    convertido = pesos * otra_moneda.rate
                    #print("price unit segunda parada", pesos, otra_moneda.rate)

                #print("no son dolares",convertido)

                line.price_unit = company.currency_id._convert(convertido,
                                                           line.move_id.currency_id,
                                                           company,
                                                           line.move_id.date)

            #print("precio unitario",line.price_unit)
        if len(self) == 1:
            return {'domain': {'product_uom_id': [
                ('category_id', '=', self.product_uom_id.category_id.id)]}}

    @api.onchange('product_uom_id')
    def _onchange_uom_id(self):
        ''' Recompute the 'price_unit' depending of the unit of measure. '''
        price_unit = self._get_computed_price_unit()

        # See '_onchange_product_id' for details.
        taxes = self._get_computed_taxes()
        if taxes and self.move_id.fiscal_position_id:
            price_subtotal = \
            self._get_price_total_and_subtotal(price_unit=price_unit,
                                               taxes=taxes)[
                'price_subtotal']
            accounting_vals = self._get_fields_onchange_subtotal(
                price_subtotal=price_subtotal,
                currency=self.move_id.company_currency_id)
            balance = accounting_vals['debit'] - accounting_vals['credit']
            price_unit = self._get_fields_onchange_balance(
                balance=balance).get('price_unit', price_unit)

        # Convert the unit price to the invoice's currency.
        company = self.move_id.company_id

        if not self.move_id.currency_id.name == "USD":

            if self.move_id.currency_id.name == "MXN":
                #print("no son dolares")
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)
                convertido = self.product_id.e_precio_de_lista / (
                        dolars.rate * 1)
                self.price_unit = company.currency_id._convert(convertido,
                                                               self.move_id.currency_id,
                                                               company,
                                                               self.move_id.date)
            else:
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)

                otra_moneda = self.env['res.currency'].search(
                    [('name', '=',
                      self.move_id.currency_id.name)],
                    limit=1)

                pesos = self.product_id.e_precio_de_lista / (
                        dolars.rate * 1)
                convertido = pesos * otra_moneda.rate
                #print("tercera parada", pesos, otra_moneda.rate)
                self.price_unit = company.currency_id._convert(convertido,
                                                       self.move_id.currency_id,
                                                       company,
                                                       self.move_id.date)
        else:
            self.price_unit = price_unit

    # @api.onchange('product_id')
    # def _onchange_oni(self):
    #     # SUPER
    #     #print(self.order_id.currency_id.name)
    #
    #     moneda_usar = self.account_id.currency_id
    #     convertido = 0
    #
    #     if moneda_usar.name == 'USD':
    #         convertido = self.product_id.e_precio_de_lista
    #         print('Son usd')
    #     if moneda_usar.name == 'MXN':
    #         dolars = self.env['res.currency'].search(
    #             [('name', '=', 'USD')],
    #             limit=1)
    #         if(self.product_id.e_precio_de_lista == 0):
    #             convertido = 1
    #         else:
    #             convertido = self.product_id.e_precio_de_lista / (dolars.rate * 1)
    #     else:
    #         dolars = self.env['res.currency'].search(
    #             [('name', '=', 'USD')],
    #             limit=1)
    #
    #         otra_moneda = self.env['res.currency'].search(
    #             [('name', '=', self.account_id.currency_id.name)],
    #             limit=1)
    #
    #         pesos = self.product_id.e_precio_de_lista / (dolars.rate * 1)
    #         convertido = pesos * otra_moneda.rate
    #
    #     print("convertido bebe",convertido)
    #
    #     self.update({'price_unit':10000})
    #
    #     #print(self.e_precio_lista)
    #     return




