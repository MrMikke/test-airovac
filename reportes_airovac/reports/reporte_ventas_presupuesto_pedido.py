from odoo import api, models


# class ParticularReport(models.AbstractModel):
#     _name = 'report.en_so_report_qweb2.report_so2'
#     _description = 'Presupuesto'
#
#     def get_taxes(self, id):
#         result = set()
#         D = {}
#         print(self)
#         o = self.env['sale.order'].browse(id)
#         for l in o.order_line:
#             for t in l.tax_id:
#                 result.add(t.tax_group_id.name)
#                 print(l.name)
#         for x in result:
#             D[x] = 0
#
#         for li in o.order_line:
#             for t in li.tax_id:
#                 D[t.tax_group_id.name] = ((li.price_unit * li.product_uom_qty) * (t.amount / 100)) + D[t.tax_group_id.name]
#
#         #print(D)
#         return D
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#
#         docs = self.env['sale.order'].browse(docids)
#         for o in docs:
#             print(o.name)
#
#         print("por cada objeto?")
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': 'sale.order',
#             'docs': docs,
#             'taxes': self.get_taxes,
#         }
#         return docargs
