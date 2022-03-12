# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    e_etiqueta_title_a = fields.Text(string="Titulo de Etiqueta A", default="Volumen de Aire (CFM’s)")
    e_etiqueta_title_b = fields.Text(string="Titulo de Etiqueta B", default="Caída de Presión (in H2O)")
    e_desciption = fields.Char(string="Descripción")

    e_g_m_p = fields.Float(digits=(1, 3),Default = 0,compute='_compute_e_g_m_p',string="G.M. del Proyecto",readonly="True")
    e_costo_total_obra = fields.Monetary(compute='_compute_e_costo_total_obra',string="Costo Total Obra",readonly="True")
    e_costo_total_imp_obra = fields.Monetary(compute='_compute_e_costo_total_imp',string="Costo Total Imp Obra",readonly="True")

    step_multiplier_id = fields.Many2one('step.multiplier',
                                         ondelete='cascade',
                                         string="Etapa del proyecto",
                                         )

    hide_fields = fields.Boolean(default = True)
    contador = fields.Integer(default = 0, compute = '_compute_contador_paquetes')
    perdidoText = fields.Boolean()
    e_fecha_prevista_cierre = fields.Date(
        string='Fecha prevista de cierre')



    def _dafault_cambio_etapa(self):
        #print("Default cambio de etapa")
        for order in self:
            for line in order.order_line:
                if not line.display_type:
                    if line.mult_is_changed():
                        #print("ubo un cambio",line.mult_is_changed())
                        return True
            #print("No hbo cambio", line.mult_is_changed())
            return False



    cambio_etapa = fields.Boolean(default = _dafault_cambio_etapa,store=True, compute = '_compute_cambio_etapa',string="Hay cambio")
    cambio_etapa_chebox = fields.Boolean(default = False, string="Habilitar cambio de etapa")
    breakdown = fields.Boolean(default=True, string="Imprimir Desglosado")
    perdido = fields.Char(default='')

    @api.onchange('opportunity_id')
    def _e_change_opportunity_id(self):
        print('changue oportunity')
        for order in self:
            if order.opportunity_id:
               order.write({'e_fecha_prevista_cierre':
                                order.opportunity_id.date_deadline })


    def marcar_perido(self):
        for order in self:
            print('perdido')
            order.write({'state': 'cancel','perdido':'Perdido'})





    @api.depends('order_line.e_multiplicador')
    def _compute_cambio_etapa(self):
        #print('_compute_cambio_etapa')
        for order in self:
            #print("cambio_etapa Antes del for lines ",order.cambio_etapa)
            for line in order.order_line:
                if not line.display_type:
                    if line.mult_is_changed():
                        #print("ubo un cambio",line.mult_is_changed())
                        #print("cambio_etapa RETUn True")
                        order.write({'cambio_etapa': True})
                        return
            #print("cambio_etapa RETUn False")
            order.write({'cambio_etapa': False})

    @api.onchange('cambio_etapa')
    def _onchange_cambio_etapa(self):
        #print("onchange cambio etapa")
        for order in self:
            #print('Valor de cambio_etapa',order.cambio_etapa)
            if order.cambio_etapa:
                  order.write({'cambio_etapa_chebox':False})
                  return
        order.write({'cambio_etapa_chebox': True})


    @api.onchange('cambio_etapa_chebox')
    def _onchangue_cambio_etapa_chebox(self):
        for order in self:
            #print(order.cambio_etapa_chebox,order.cambio_etapa)
            if  order.cambio_etapa_chebox and order.cambio_etapa :
                order.write({'cambio_etapa': False})
                return {
                    'warning': {
                        'title': "Cuidado",
                        'message': "Al cambiar de etapa el Multiplicador sera sobre escrito",
                    }
                }

    def mostrar_detalles(self):
        for order in self:
            if not order.hide_fields:
                order.write({'hide_fields': True})
                #print("True",order.hide_fields)
                return
        order.write({'hide_fields': False})
        #print("False", order.hide_fields)


    @api.onchange('step_multiplier_id')
    def _onchange_step_multiplier_id(self):

        for order in self:
            for line in order.order_line:
                if not line.display_type:
                    print(line.product_id.name)
                    #Buscamos el multiplicador
                    mult = self.env['step.multiplier.line'].search([('e_step_multiplier_id','=',order.step_multiplier_id.id),('e_marca','=',line.product_id.e_product_class.id)])

                    #print(mult,mult.e_multiplicador)
                    #Si el multiplicador es maypr que 0
                    if mult.e_multiplicador > 0.0:
                        resul = mult.e_multiplicador * line.e_precio_de_lista * (
                                1 - (line.discount / 100))
                        espe = mult.e_multiplicador * line.e_precio_de_lista
                        #print(resul,espe)
                        if resul < espe :
                            line.write({'e_multiplicador': mult.e_multiplicador,'price_unit' : mult.e_multiplicador * line.e_precio_de_lista * (1 - (line.discount / 100)),'e_por_debajo': 1})
                        else:
                            line.write({'e_multiplicador': mult.e_multiplicador,
                                        'price_unit': mult.e_multiplicador * line.e_precio_de_lista ,
                                        'e_punto_venta':mult.e_multiplicador * line.e_precio_de_lista * (
                                                    1 - (line.discount / 100)),
                                        'e_por_debajo': 0})
                        #print(line)
                    else:
                        #print('multiplicador 0')
                        resul = 1 * line.e_precio_de_lista * (
                                1 - (line.discount / 100))
                        espe = 1 * line.e_precio_de_lista
                        if resul < espe:
                            line.write({'e_multiplicador': 1,
                                        'price_unit': mult.e_multiplicador * line.e_precio_de_lista,
                                        'e_punto_venta': mult.e_multiplicador * line.e_precio_de_lista * (
                                                1 - (line.discount / 100)),
                                        'e_por_debajo': 1})
                        else:
                            line.write({'e_multiplicador': 1,
                                        'price_unit': mult.e_multiplicador * line.e_precio_de_lista,
                                        'e_punto_venta': mult.e_multiplicador * line.e_precio_de_lista * (
                                                1 - (line.discount / 100)),
                                        'e_por_debajo': 0})
                        #print('return multi')
                        return
            order.write({'cambio_etapa': False})





    @api.onchange('amount_untaxed')
    def _onchange_amount_untaxed(self):
        for order in self:
            for line in order.order_line:
                if line.price_subtotal > 0:
                    line.write({'e_estimado_pro_l': (line.price_subtotal * 100) / self.amount_untaxed})
                else:
                    line.write({'e_estimado_pro_l': 0})


    @api.depends('order_line.e_g_m_l')
    def _compute_e_g_m_p(self):
        #print("que pedo carnal")
        for order in self:
            costo_total = 0.0
            total = 0.0
            for line in order.order_line:
                costo_total += line.e_costo_total
                total += line.e_punto_venta * line.product_uom_qty
            #print(e_g_m_p)
            if total != 0:
                order.write({'e_g_m_p': 1 - (costo_total/total)})
                return
            order.write({'e_g_m_p': 0})




    @api.depends('order_line.e_costo_total')
    def _compute_e_costo_total_obra(self):
        #print("compute_e_costo_total")
        for order in self:
            e_costo_total_obra = 0.0
            for line in order.order_line:
                e_costo_total_obra += line.e_costo_total
            #print(e_costo_total_obra)
            order.write({'e_costo_total_obra': e_costo_total_obra})


    @api.depends('order_line.e_costo_total_imp')
    def _compute_e_costo_total_imp(self):
        #print("que pedo carnal")
        for order in self:
            e_costo_total_imp_obra = 0.0
            for line in order.order_line:
                e_costo_total_imp_obra += line.e_costo_total_imp
            #print('costo total impor',e_costo_total_imp_obra)
            order.write({'e_costo_total_imp_obra': e_costo_total_imp_obra})




    @api.depends('order_line.e_asociar','order_line.sequence','order_line.price_subtotal')
    def _compute_contador_paquetes(self):
        #print("**********")
        for order in self:

            contador_one = 0

            for line in order.order_line:
                #print("linea",line.id,line.e_asociar)
                if line.e_asociar:
                    contador_one +=1



            #print("Contador_one",contador_one)
            if contador_one % 2 == 0 :
                contador  = 0
                grupo = 1
                colored = 1
                sigue = False
                total_group = 0
                div = 0
                aux = None
                for line in order.order_line:
                    #print(contador,'A',line.e_asociar,grupo,sigue)

                    if line.e_asociar:
                        contador +=1
                        if contador % 2 != 0 and aux is None:
                            aux = line.id
                            div = line.product_uom_qty
                            #print('Asignando Aux',aux.id,total_group)

                        total_group += line.e_punto_venta * line.product_uom_qty
                        line.write({'grupo': grupo,'colored': colored,'e_p_unit_a': 0,'e_subtotal_no_des':0 })


                        #print(contador, 'B', line.e_asociar, grupo, sigue)

                        if contador % 2 == 0:
                             if div > 0:

                                 order_line = self.env['sale.order.line'].browse([aux])
                                 #print('Antes de operar puc')
                                 #print(order_line.id, total_group,div)
                                 op =  total_group / div
                                 #print('op', op)
                                 order_line.write({'e_p_unit_a': op, 'principal': 1,'e_subtotal_no_des':op * div  })
                             aux = None
                             total_group = 0
                             div = 0
                             sigue = False
                             grupo += 1
                             if grupo % 2 ==0:
                               colored = 2
                             else:
                                colored = 1
                            #print(contador, 'C', line.e_asociar, grupo, sigue)
                        else:
                            sigue = True
                            #total_group += line.price_subtotal
                            #print(aux.grupo,total_group,line.price_subtotal)
                            #print(contador, 'D', line.e_asociar, grupo, sigue)
                    else:
                        if sigue:
                            total_group += line.e_punto_venta * line.product_uom_qty
                            #print('En sige Aux id',aux.id,aux.grupo, total_group, line.price_subtotal)
                            #if line.e_p_unit_a > 0 and line.principal > 0:
                            #    line.write({'grupo': grupo, 'colored': colored})
                            #else:
                            line.write({'grupo': grupo, 'colored' : colored,'e_p_unit_a': 0, 'principal': 0,'e_subtotal_no_des':0})
                            #print(contador, 'E', line.e_asociar, grupo, sigue)
                        else:
                            if line.e_p_unit_a > 0 or line.principal > 0:
                                line.write({'grupo': 0, 'colored': 0,
                                            'e_p_unit_a': line.e_punto_venta, 'principal': 0,'e_subtotal_no_des':line.price_subtotal})
                            else:
                                line.write({'grupo': 0, 'colored': 0,'e_p_unit_a': line.e_punto_venta,'e_subtotal_no_des':line.price_subtotal})
                            #print(contador, 'F', line.e_asociar, grupo, sigue,line.colored)
                    #lista.append(line)

            # lista.reverse()
            # for line_s in lista:
            #     print(line_s.id,line_s.colored)

            order.write({'contador': contador_one})
            #print('Aver we el contador', contador_one)



class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'


    e_igi = fields.Float(digits=(10, 2), string="IGI %",help="Porcentaje de IGI")
    e_importation = fields.Float(digits=(10, 2), string="IMPOR %",help="Porcentaje de Importación")
    e_etiqueta_line_a = fields.Text(string="Et A.")
    e_etiqueta_line_b = fields.Text(string="Et B.")
    e_te_line_max = fields.Integer(string="T.E MAX")
    e_te_line_min = fields.Integer(string="T.E MIN")
    e_precio_de_lista = fields.Monetary(digits=(10, 2),readonly=True,string="P.L.", help="Precio de lista")
    e_multiplicador = fields.Float(digits=(10, 4),default=0, string="Mult.", help="Multiplicador, si no exite 1")
    e_descuento = fields.Integer(string="Des %")
    e_costo_total =fields.Monetary(string="Costo Total",readonly=True)

    e_costo_unitario = fields.Monetary(digits=(10, 2),Default = 0,store=True,readonly=True, string="Costo Unitario", help="(1 + IGI + Impotación) * (PL * Mult. STD)")
    e_costo_total = fields.Float(digits=(10, 3),Default = 0, store=True,readonly=True, string="Costo Total", help="Costo Unitario * Cantidad")
    e_costo_total_imp = fields.Float(digits=(1, 3),Default = 0, store=True,readonly=True, string="C.T Import", help="Importacion * (PL * Mult. STD) * Cantidad")
    e_g_m_l = fields.Float(digits=(10, 3),Default = 0, store=True,readonly=True, string="G . M ", help="COSTO TOTAL / Subtotal")
    e_estimado_pro_l = fields.Float(digits=(10, 3), Default=0,readonly = True, store=True, string="% STP", help="% Sobre total de propuesta")
    e_asociar = fields.Boolean( Default=False,string="G.",help="Asocia productos con accesorios cada dos checkboxes")
    e_p_unit_a = fields.Monetary(Default=0,readonly=True,string="P.U con Accesorios",help="Precio unitario con accesorios")
    e_subtotal_no_des = fields.Monetary(Default=0,string="Subtotal",help="Sub total no desglosado")
    e_t_e = fields.Char(string="T.E.",
                                        help="Tiempo estimado de entrega")
    e_por_debajo = fields.Integer(Default=0)
    #Discount = fields.Integer(Default=0,string = "Descuento %")

    #campos no visibles, usados para el calculo de productos con accesorios :3
    sequence = fields.Integer("Sequence")
    grupo = fields.Integer(default=0)
    colored = fields.Integer(default=0)
    principal = fields.Integer(default=0)
    e_partida = fields.Char(string="P.")
    e_provedor = fields.Many2one('product.supplierinfo', string="Proveedor")
    e_mult_std = fields.Float(digits=(10, 4),default = 1.0, string="Mult Compra",
                              help="Mult Compra por marca")
    e_mult_min = fields.Float(digits=(10, 4),default = 1, string="Mult. Min", help="e_mult_min")
    e_exwork = fields.Monetary( string="Cost Exwork",store=True, help="P.L x Exwork mult")
    e_marca = fields.Char(String='Marca', related='product_id.e_product_class.name')
    e_punto_venta = fields.Monetary(digits=(10, 2),readonly=True, string="P . V",help="P.L * Multiplicador * (1 - Descuento)")

    # price_unit =fields.Float(digits=(10, 2),readonly=True, string="P . V",help="P.L * Multiplicador * (1 - Descuento)")
    #price_subtotal = fields.Monetary(Default=0, string="Subtutal",compute='_compute_subtotal',
     #                                   help="Subtutal")




    # @api.onchange('price_subtotal')
    # def _compute_subtotal(self):
    #     for line in self:
    #         #print("Semurio2?")
    #         line.write({'price_subtotal':line.price_unit * line.product_uom_qty})



    @api.onchange('e_costo_unitario', 'product_uom_qty')
    def compute_costo_total(self):
        return (self.e_costo_unitario * self.product_uom_qty)

    def _set_mul_default(self):
        if self.order_id.step_multiplier_id.id:
            mult = self.env['step.multiplier.line'].search(
                [('e_step_multiplier_id', '=', self.order_id.step_multiplier_id.id),
                 ('e_marca', '=', self.product_id.e_product_class.id)])
            #print(mult,"aquitoy",len(mult))
            if mult.e_multiplicador > 0.0 :
                #print('mult.e_multiplicador > 0')
                return mult.e_multiplicador

        return 1.0

    def mult_is_changed(self):
        #print('Funcion mult is changed')
        if self.order_id.step_multiplier_id.id:
            #print('Nombre de la Etapa',self.order_id.step_multiplier_id.name)
            mult = self.env['step.multiplier.line'].search(
                [('e_step_multiplier_id', '=', self.order_id.step_multiplier_id.id),
                 ('e_marca', '=', self.product_id.e_product_class.id)])


            #print('Multiplicador de etapa',mult.e_multiplicador,'Multiplicador del actual',self.e_multiplicador)
            if (mult.e_multiplicador != self.e_multiplicador) or (mult.e_multiplicador == 0 and self.e_multiplicador != 1):
                #print('Se cumple condicion TRUE')
                return True
        if not self.order_id.step_multiplier_id.id:
            #print('No existe una etapa inicial')
            if self.e_multiplicador != 1:
                return True
        #print('No hubo ningun cambio')
        return False

    @api.onchange('e_multiplicador')
    def change_e_multiplicador(self):
        print("cambia el multiplicador")
        if  self.e_multiplicador < 0:
            raise UserError(
                'El multiplicador no puede ser negativo')

        flag = self.env['res.users'].has_group(
            'cotizador__airovac.group_nom_options')
        resul = self.e_multiplicador * self.e_precio_de_lista * (
                     1 - (self.discount / 100))
        espe =  self.e_mult_min * self.e_precio_de_lista

        if (self.e_multiplicador < self.e_mult_min and not flag) or ((resul < espe)  and not flag) :
            raise UserError(
                'El multiplicador tiene que ser mayor que el multiplicador mínimo')

        if (self.e_multiplicador < self.e_mult_min and flag) or (
                (resul < espe) and flag):
                    print("Ofrece por debajo del minimo")
                    self.update({'price_unit': self.e_multiplicador * self.e_precio_de_lista,
                                     'e_punto_venta': self.e_multiplicador * self.e_precio_de_lista *  (
                     1 - (self.discount / 100)) , 'e_por_debajo' : 1})
                    return {
                        'warning': {
                            'title': "Cuidado",
                            'message': "Has ofrecido el producto por debajo de su precio mínimo",
                            'type': 'notification'
                        }
                    }
        print("Update multiplicador")
        self.update({
            'price_unit': self.e_multiplicador * self.e_precio_de_lista,
            'e_punto_venta': self.e_multiplicador * self.e_precio_de_lista * (
                    1 - (self.discount / 100))
            , 'e_por_debajo': 0
        })

    @api.onchange('discount')
    def change_discount_airovac(self):
        if self.discount > 100:
            raise UserError(
                "El Descuento no puede ser más del 100%")

        flag = self.env['res.users'].has_group(
            'cotizador__airovac.group_nom_options')
        resul = self.e_multiplicador * self.e_precio_de_lista * (
                1 - (self.discount / 100))
        espe = self.e_mult_min * self.e_precio_de_lista

        if (self.e_multiplicador < self.e_mult_min and flag) or (
                (resul < espe) and flag):
            self.update(
                {'price_unit': self.e_multiplicador * self.e_precio_de_lista,
                 'e_punto_venta': self.e_multiplicador * self.e_precio_de_lista * (
                         1 - (self.discount / 100))
                    , 'e_por_debajo': 1})
            return {
                'warning': {
                    'title': "Cuidado",
                    'message': "Has ofrecido el producto  por debajo de su precio mínimo",
                    'type': 'notification'
                }
            }
        if (self.e_multiplicador < self.e_mult_min and not flag) or ((resul < espe)  and not flag) :
            raise UserError(
                'No puedes dar un producto por debajo de su precio mínimo')

        self.update({
            'price_unit': self.e_multiplicador * self.e_precio_de_lista,
            'e_punto_venta': self.e_multiplicador * self.e_precio_de_lista * (
                    1 - (self.discount / 100))
            , 'e_por_debajo': 0
        })


    #
    #         self.update({
    #                         'e_punto_venta': self.price_unit * 1 - (
    #                         self._origin.discount / 100),
    #                         'e_por_debajo': 0,'discount' :self._origin.discount})
    #         return {
    #             'warning': {
    #                 'title': "Cuidado",
    #                 'message': "El Descuento no puede ser más del 100%",
    #                 'type': 'notification'
    #             }
    #         }





    # @api.onchange('e_multiplicador', 'discount','e_precio_de_lista')
    # def asing_punto_venta(self):
    #
    #     # El descuento no puede ser del 100%
    #
    #     if self.discount >= 100:
    #
    #         self.update({
    #                         'e_punto_venta': self.price_unit * 1 - (
    #                         self._origin.discount / 100),
    #                         'e_por_debajo': 0,'discount' :self._origin.discount})
    #         return {
    #             'warning': {
    #                 'title': "Cuidado",
    #                 'message': "El Descuento no puede ser más del 100%",
    #                 'type': 'notification'
    #             }
    #         }
    #
    #     # El multiplicador no puede ser negativo
    #
    #     if self.e_multiplicador < 0:
    #         self.write({
    #                         'e_punto_venta': self._origin.e_multiplicador * self.e_precio_de_lista * (
    #                                 1 - (self.discount / 100)),
    #                         'e_por_debajo': 0,'e_multiplicador' : self._origin.e_multiplicador})
    #         return {
    #             'warning': {
    #                 'title': "Cuidado",
    #                 'message': "El Multiplicador no puede ser menor que 0",
    #                 'type': 'notification'
    #             }
    #         }
    #
    #
    #
    #     flag = self.env['res.users'].has_group('cotizador__airovac.group_nom_options')
    #     resul = self.e_multiplicador * self.e_precio_de_lista * (
    #             1 - (self.discount / 100))
    #     espe =  self.e_mult_min * self.e_precio_de_lista
    #
    #     if (self.e_multiplicador < self.e_mult_min and not flag) or ((resul < espe)  and not flag):
    #
    #             self.write({'e_multiplicador' : self._set_mul_default(),
    #                          'e_por_debajo' : 0,'discount':self._origin.discount
    #                         })
    #             return {
    #                 'warning': {
    #                     'title': "Cuidado",
    #                     'message': "No puedes ofrecer un producto por debajo de su (multiplicador) precio mínimo",
    #                     'type': 'notification'
    #                 }
    #             }
    #
    #     if (self.e_multiplicador < self.e_mult_min and  flag) or  ((resul < espe)  and  flag):
    #
    #             self.write({'price_unit': self.e_multiplicador * self.e_precio_de_lista * (
    #                                     1 - (self.discount / 100)), 'e_por_debajo' : 1})
    #
    #             return {
    #                 'warning': {
    #                     'title': "Cuidado",
    #                     'message': "Has ofrecido el producto  por debajo de su precio mínimo",
    #                     'type': 'notification'
    #                 }
    #             }
    #
    #     #print("cambiando subtotal")
    #     self.write({'price_unit': self.e_multiplicador * self.e_precio_de_lista * (
    #                                 1 - (self.discount / 100)),'e_por_debajo' : 0})

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.order_id.pricelist_id:
            raise UserError(
                'ELIJA UNA TARIFA')
        # SUPER
        res = super(SaleOrderLineInherit, self).product_id_change()

        print(self.order_id.pricelist_id.id)
        moneda_usar = self.env['product.pricelist'].search([('id','=',self.order_id.pricelist_id.id)], limit=1)
        print(self.order_id.pricelist_id.currency_id.name.strip(),'ODI')
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
                [('name', '=', self.order_id.pricelist_id.currency_id.name)],
                limit=1)

            pesos = self.product_id.e_precio_de_lista / (dolars.rate * 1)
            convertido = pesos * otra_moneda.rate

            #print('Otra moneda')

        price_init_f = self.product_id.e_precio_de_lista
        self.write({'e_precio_de_lista': convertido,
                    'e_etiqueta_line_a': self.product_id.e_etiqueta_a,
                    'e_etiqueta_line_b': self.product_id.e_etiqueta_b,
                    'e_te_line_max' : self.product_id.e_te_max,
                    'e_te_line_min' : self.product_id.e_te_min,
                    'e_igi' : (self.product_id.e_igi * 100),
                    'e_importation' : (self.product_id.e_importation * 100),
                    'e_t_e': self.product_id.e_tiempo_estimado,
                    'e_mult_min': self.product_id.e_mult_min,
                    'e_mult_std': self.product_id.e_mult_std,
                    'e_multiplicador' :  self._set_mul_default(),
                    'price_unit': convertido,
                    'e_punto_venta':convertido,
                    'e_exwork': self.product_id.e_mult_std * convertido
                    })
        if self.product_id:
            self.write({'e_partida' : str(len(self.order_id.order_line)-1)})

        return res




    @api.onchange('product_uom_qty')
    def _onchange_quantity(self):
        print('node debe da cambiar')

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            price = self.price_unit
            #print(self.price_unit)
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(price, product.taxes_id, self.tax_id, self.company_id)




    @api.onchange('product_id','e_igi','e_importation','e_exwork')
    def compute_costo_unitario(self):
        self.e_costo_unitario =  (1 + (self.e_igi/100) + (self.e_importation/100)) * self.e_exwork
        #print(self.e_costo_unitario)

    @api.onchange('e_costo_unitario','product_uom_qty')
    def compute_costo_total(self):
        self.e_costo_total = ( self.e_costo_unitario * self.product_uom_qty)
        #print(self.e_costo_total)

    @api.onchange('e_importation','product_uom_qty','e_exwork')
    def compute_costo_total_imp(self):
        self.e_costo_total_imp = (self.e_importation/100) * self.e_exwork  * self.product_uom_qty

    @api.onchange('e_costo_total','e_costo_unitario','product_uom_qty')
    def compute_g_m_l(self):
        if self.e_costo_total == 0 or  self.e_costo_unitario == 0 or  self.product_uom_qty == 0:
            return 0
        #print(self.e_costo_total ,self.price_unit , self.product_uom_qty)
        self.e_g_m_l = 1 - (self.e_costo_total / (self.price_unit * self.product_uom_qty  * (
                    1 - (self.discount / 100))))
        #print(self.e_g_m_l)


    # @api.onchange('e_provedor')
    # def _onchange_e_mult_std(self):
    #     self.write({'e_mult_std' : self.e_provedor.e_mult_std})
    #


    @api.onchange('e_mult_std')
    def _onchange_e_mult_stf(self):
        self.write({'e_exwork': self.e_mult_std * self.e_precio_de_lista})

