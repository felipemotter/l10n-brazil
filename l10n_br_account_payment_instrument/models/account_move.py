# Copyright 2023 Engenere.one
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    payment_instrument_ids = fields.Many2many(
        comodel_name="l10n_br.payment.instrument",
        compute="_compute_payment_instrument_ids",
    )

    @api.depends("line_ids", "line_ids.payment_instrument_id")
    def _compute_payment_instrument_ids(self):
        for move in self:
            move.payment_instrument_ids = move.mapped("line_ids.payment_instrument_id")

    def open_payment_instruments(self):
        self.ensure_one()
        action = {
            "name": _("Payment Instruments"),
            "view_type": "tree",
            "view_mode": "list,form",
            "res_model": "l10n_br.payment.instrument",
            "type": "ir.actions.act_window",
            "res_id": self.id,
        }
        return action
