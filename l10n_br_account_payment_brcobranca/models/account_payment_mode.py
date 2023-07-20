# Copyright (C) 2012-Today - KMEE (<http://kmee.com.br>).
#  @author Luis Felipe Miléo - mileo@kmee.com.br
#  @author Renato Lima - renato.lima@akretion.com.br
# Copyright (C) 2021-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountPaymentMode(models.Model):
    """
    Override Account Payment Mode
    """

    _inherit = "account.payment.mode"

    @api.model
    def _selection_cnab_processor(self):
        selection = super()._selection_cnab_processor()
        selection.append(("brcobranca", "BRCobrança"))
        return selection

    brcobranca_modelo = fields.Selection(
        selection=[
            ("rghost", "Padrão 1"),
            ("rghost2", "Padrão 2"),
            ("rghost_carne", "Carne"),
        ],
        string="Modelo do Boleto",
        help="Modelo para impressão do Boleto",
        default="rghost",
    )

