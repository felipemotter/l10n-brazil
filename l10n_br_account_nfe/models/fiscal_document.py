from odoo import models


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"

    def _eletronic_document_send(self):
        super(FiscalDocument, self)._eletronic_document_send()
        for rec in self:
            rec.nfe40_detPag = [
                (5, 0, 0),
                (0, 0, rec._prepare_amount_financial("1", "02", 10.00)),
            ]
            rec.nfe40_detPag.__class__._field_prefix = "nfe40_"
