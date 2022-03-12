from odoo import models, fields, _
import tempfile
import base64
from lxml import objectify
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    xml_filename = fields.Char(
        string="Nombre XML",
    )

    xml_file = fields.Binary(
        string="XML",
    )

    xml_import_id = fields.Many2one(
        comodel_name="xml.import.invoice",
        string="XML import",
        required=False,
    )

    def action_post(self):
        if self.xml_file:
            precision = self.currency_id.decimal_places
            result = self.xml_file
            data = base64.decodestring(result)
            fobj = tempfile.NamedTemporaryFile(delete=False)
            fname = fobj.name
            fobj.write(data)
            fobj.close()
            file_xml = open(fname, "r")
            tree = objectify.fromstring(file_xml.read().encode())
            # TODO: check if attachment field is xml type
            # if data_file.mimetype == 'application/xml':
            # 	raise UserError(
            # 		_('File %s is not xml type, please remove from list') % (
            # 			data_file.display_name))

            if self.partner_id.vat != tree.Emisor.get('Rfc'):
                raise UserError(
                    _("The provider's RFC (%s) does not match the RFC (%s) of the "
                      "attached xml") % (self.partner_id.vat, tree.Emisor.get('Rfc'))
                )

            if self.company_id.vat != tree.Receptor.get('Rfc'):
                raise UserError(
                    _("The company RFC (%s) does not match the RFC (%s) of the attached"
                      " xml") % (self.company_id.vat, tree.Receptor.get('Rfc'))
                )

            sub_total = float(tree.get('SubTotal')) - (
                float(tree.get('Descuento')) if tree.get('Descuento') else 0)

            if not float_is_zero(self.amount_untaxed - sub_total,
                                 precision_digits=precision):
                raise UserError(
                    _("The sub-total amount (%s) of the invoice does not match the "
                      "sub-total amount (%s) of the attached xml") %
                    (str(self.amount_untaxed), sub_total)
                )

            if not float_is_zero(self.amount_total - float(tree.get('Total')),
                                 precision_digits=precision):
                raise UserError(
                    _("The total amount (%s) of the invoice does not match the total "
                      "amount (%s) of the attached xml") %
                    (str(self.amount_total), tree.get('Total'))
                )

            if self.currency_id.name != tree.get('Moneda'):
                raise UserError(
                    _("The invoice currency (%s) does not match the currency (%s) the "
                      "attached xml") % (self.currency_id.name, tree.get('Moneda'))
                )
            date = tree.get('Fecha')[:10]
            if str(self.invoice_date) != date:
                raise UserError(
                    _("The invoice date (%s) does not match the date of the XML "
                      "attachment (%s)") % (str(self.invoice_date), date,)
                )

        return super(AccountMove, self).action_post()
