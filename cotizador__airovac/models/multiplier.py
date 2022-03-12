# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api

class StepMultiplier(models.Model):
    _name = 'step.multiplier'
    _description = "Etapa de cotizaciónes"

    name = fields.Char(string="Etapa", required = True)
    description = fields.Text(string="Descripción")
    e_step_multiplier_line_ids = fields.One2many(
        'step.multiplier.line', 'e_step_multiplier_id')




class StepMultiplierLine(models.Model):
    _name = 'step.multiplier.line'
    _description = "Etapa de cotización Linea"



    name = fields.Char(string="Multiplicadores por marca")
    e_marca = fields.Many2one('producte.class',
                                ondelete='cascade', string="Marca del producto",
                                required=True)
    e_multiplicador = fields.Float(digits=(10,4),default=1, string="Multiplicador del producto por etapa", help="")
    e_step_multiplier_id = fields.Many2one('step.multiplier',
                                ondelete='cascade', string="Etapa",
                                required=True)



    #Filter the e_marca if this alredy have e_multiplicador asigned
    @api.onchange('e_marca')
    def _onchange_emarca(self):
        in_use = []
        for line in self.e_step_multiplier_id.e_step_multiplier_line_ids:
            if  line.e_marca.id:
                 in_use.append(line.e_marca.id)

        if not in_use:
            return
        print(in_use)
        return {'domain':{'e_marca':
                         [('id', 'not in', in_use)]}}





