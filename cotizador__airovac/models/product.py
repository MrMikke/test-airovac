# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

class productTemplateInherit(models.Model):
    _inherit = 'product.template'

    e_igi = fields.Float(digits=(3, 4),string="IGI%", help="Porcentaje de IGI")
    e_importation = fields.Float(digits=(3, 4),string="STD Importación%", help="Porcentaje de Importación")
    #e_precio_list = fields.Float(digits=(10,2), string="Precio de Lista", help="Precio de lista")
    e_te_max = fields.Integer(string="T.E MAX",help="Tiempo maximo de entrega en semanas")
    e_te_min = fields.Integer(string="T.E MIN",help="Tiempo minimo de entrega en semanas")
    e_etiqueta_a = fields.Text(string="Etiqueta A")
    e_etiqueta_b = fields.Text(string="Etiqueta B")
    e_mult_min = fields.Float(digits=(10,4),default = 1, string="Mult. Min", help="e_mult_min")
    e_precio_de_lista = fields.Monetary(digits=(10, 2), string="Precio de Lista", help="Precio de lista")
    e_product_class  = fields.Many2one('producte.class',
                                         string="Marca",
                                         )
    e_tiempo_estimado = fields.Char(string="Tiempo Estimado",
                                        help="Tiempo estimado de entrega")

    e_revision_p_l = fields.Char(string="Revisión de P.L")
    e_link_full = fields.Char()
    e_mult_std = fields.Float(digits=(10, 4), default=1, string="Mult Compra",
                              help="e_mult_std")

    @api.onchange('e_te_max')
    def e_change_e_te_max(self):
        if self.e_te_max < self.e_te_min:
            raise UserError(
                     'El tiempo máximo de entrega tiene que ser mayor que el tiempo mínimo')
        if self.e_te_max >= self.e_te_min :
            self.update({'sale_delay': (self.e_te_max * 7)})
        else:
            self.update({'sale_delay': (self.e_te_min * 7)})


    @api.onchange('e_te_min')
    def e_change_e_te_min(self):
        if self.e_te_min > self.e_te_max:
            raise UserError(
                'El tiempo mínimo de entrega tiene que ser menor que el tiempo máximo')




    @api.onchange('e_product_class')
    def _e_product_class(self):
        print('onchangue')
        self.write({'e_mult_min': self.e_product_class.e_mult_min,
                    'e_mult_min': self.e_product_class.e_mult_std})

    @api.onchange('e_mult_min')
    def _change_mult_min(self):
        print('onchangue emult')
        if self.e_mult_min < 0:
            self.write({'e_mult_min': self._origin.e_mult_min})
            return {
                'warning': {
                    'title': "Cuidado",
                    'message': "El multiplicador mínimo debe ser mayor que 0.0",
                }
            }

    @api.onchange('e_mult_std')
    def _change_mult_min(self):
        print('onchangue emult')
        if self.e_mult_std < 0:
            self.write({'e_mult_std': self._origin.e_mult_std})
            return {
                'warning': {
                    'title': "Cuidado",
                    'message': "El multiplicador solicitado debe ser mayor que 0.0",
                }
            }

    @api.onchange('e_precio_de_lista')
    def _onchange_p_l(self):
        # flag = self.env['res.users'].has_group(
        #     'cotizador__airovac.group_nom_options')
        # print(flag, 'cambio precio de lista')
        # if not flag:
        #     raise UserError(
        #         'No tienes los permisos necesarios para hacer esta acción')

        self.write({'list_price':self.e_precio_de_lista})

    @api.onchange('list_price')
    def _onchange_price_sale(self):
        # flag = self.env['res.users'].has_group(
        #     'cotizador__airovac.group_nom_options')
        #
        # print(flag, 'cambio list price')
        # if not flag:
        #     raise UserError(
        #         'No tienes los permisos necesarios para hacer esta acción')

        self.write({'e_precio_de_lista': self.list_price})



    #COMENTARIO
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        print("COMBINATION INFO",pricelist)
        """ Return info about a given combination.

        Note: this method does not take into account whether the combination is
        actually possible.

        :param combination: recordset of `product.template.attribute.value`

        :param product_id: id of a `product.product`. If no `combination`
            is set, the method will try to load the variant `product_id` if
            it exists instead of finding a variant based on the combination.

            If there is no combination, that means we definitely want a
            variant and not something that will have no_variant set.

        :param add_qty: float with the quantity for which to get the info,
            indeed some pricelist rules might depend on it.

        :param pricelist: `product.pricelist` the pricelist to use
            (can be none, eg. from SO if no partner and no pricelist selected)

        :param parent_combination: if no combination and no product_id are
            given, it will try to find the first possible combination, taking
            into account parent_combination (if set) for the exclusion rules.

        :param only_template: boolean, if set to True, get the info for the
            template only: ignore combination and don't try to find variant

        :return: dict with product/combination info:

            - product_id: the variant id matching the combination (if it exists)

            - product_template_id: the current template id

            - display_name: the name of the combination

            - price: the computed price of the combination, take the catalog
                price if no pricelist is given

            - list_price: the catalog price of the combination, but this is
                not the "real" list_price, it has price_extra included (so
                it's actually more closely related to `lst_price`), and it
                is converted to the pricelist currency (if given)

            - has_discounted_price: True if the pricelist discount policy says
                the price does not include the discount and there is actually a
                discount applied (price < list_price), else False
        """
        self.ensure_one()
        # get the name before the change of context to benefit from prefetch
        display_name = self.display_name

        display_image = True
        quantity = self.env.context.get('quantity', add_qty)
        context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
        product_template = self.with_context(context)

        combination = combination or product_template.env['product.template.attribute.value']

        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)

        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)

        if product:
            # We need to add the price_extra for the attributes that are not
            # in the variant, typically those of type no_variant, but it is
            # possible that a no_variant attribute is still in a variant if
            # the type of the attribute has been changed after creation.
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in combination.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )
            list_price = product.price_compute('list_price')[product.id]
            price = product.price if pricelist else list_price
            display_image = bool(product.image_1920)
            display_name = product.display_name
        else:
            product_template = product_template.with_context(current_attributes_price_extra=[v.price_extra or 0.0 for v in combination])
            list_price = product_template.price_compute('list_price')[product_template.id]
            price = product_template.price if pricelist else list_price
            display_image = bool(product_template.image_1920)

            combination_name = combination._get_combination_name()
            if combination_name:
                display_name = "%s (%s)" % (display_name, combination_name)

        if pricelist and pricelist.currency_id != product_template.currency_id:
            list_price = product_template.currency_id._convert(
                list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )

        price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
        has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1

        #print(product.id,display_name, display_image, price, list_price,
        #      has_discounted_price)
        convertido = self._convert_precios_arivocac(product,pricelist)
        #print('salida',convertido)
        #print(display_name,display_image,price,list_price,has_discounted_price)
        return {
            'product_id': product.id,
            'product_template_id': product_template.id,
            'display_name': display_name,
            'display_image': display_image,
            'price': convertido,
            'list_price': list_price,
            'has_discounted_price': has_discounted_price,
        }


    def _convert_precios_arivocac(self, product_id=False , pricelist=False):
        #print('************Convertiendo*************')
        #print(product_id.name,pricelist)
        if product_id:
            moneda_usar = self.env['product.pricelist'].search(
                [('id', '=', pricelist.id)], limit=1)

            #print('************Items*************')
            #print(moneda_usar.item_ids)
            #for p in moneda_usar.item_ids:
                #print(p.applied_on)
                #print(p.product_tmpl_id.name)
            #print('************FIN Items*************')

            if moneda_usar.currency_id.name == 'USD':
                return product_id.e_precio_de_lista
                print('Son usd')
            if moneda_usar.currency_id.name == 'MXN':
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)
                return product_id.e_precio_de_lista / (dolars.rate * 1)
            else:
                dolars = self.env['res.currency'].search(
                    [('name', '=', 'USD')],
                    limit=1)

                otra_moneda = self.env['res.currency'].search(
                    [('name', '=', pricelist.id.currency_id.name)],
                    limit=1)

                pesos = self.product_id.e_precio_de_lista / (dolars.rate * 1)
                return pesos * otra_moneda.rate

class ProductuEClass(models.Model):
    _name = 'producte.class'
    _description = "Marca del producto"

    name = fields.Char(string="Marca del producto", required = True)
    e_mult_min = fields.Float(digits=(1, 4),default=1, string="Multiplicador mínimo", help="Multiplicador, si no existe el multiplicador default 1")
    products_ids = fields.One2many('product.template', 'e_product_class',
                                      string="Productos"
                                      )

    e_num_products = fields.Integer(compute='_calculate_products')
    e_revision_p_l = fields.Char(string="Revisión de P.L")
    e_mult_min = fields.Float(digits=(1, 4),default=1, string="Multiplicador Mínimo", help="Multiplicador, si no existe el multiplicador default 1")
    e_mult_std = fields.Float(digits=(1, 4), default=1,
                              string="Multiplicador Compra",
                              help="Multiplicador solicitado por marca, si no existe el multiplicador default 1")


    @api.onchange('e_mult_min')
    def _onchange_(self):
        if self.e_mult_min < 0:
            self.write({'e_mult_min': self._origin.e_mult_min})
            return {
                'warning': {
                    'title': "Cuidado",
                    'message': "El multiplicador mínimo debe ser mayor que 0.0",
                }
            }

    @api.onchange('e_mult_std')
    def _onchange_(self):
        if self.e_mult_std < 0:
            self.write({'e_mult_std': self._origin.e_mult_std})
            return {
                'warning': {
                    'title': "Cuidado",
                    'message': "El multiplicador solicitado debe ser mayor que 0.0",
                }
            }

    @api.depends('products_ids')
    def _calculate_products(self):
        for record in self:
            record.e_num_products = len(record.products_ids)

        # for clase in self:
        #     print(clase.ids)
        #
        #     print('PRODUCTS',clase.products_ids.ids )
        #     lista = self.env['product.template'].search(
        #         [('id', 'in', clase.products_ids.ids)])
        #
        #     for producto in lista:
        #         print('en lista',producto.name)
        #         producto.write({'e_mult_min': clase.e_mult_min})
        #

