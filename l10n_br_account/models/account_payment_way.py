# Copyright 2022 Engenere
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models


class AccountPaymentWay(models.Model):
    """Account Payment Way"""

    _name = "account.payment.way"
    _description = "Account Payment Way"

    PAYMENT_WAY_DOMAIN = [
        ("ted", _("TED")),
        ("pix_transfer", _("PIX Transfer")),
    ]

    name = fields.Char()
    domain = fields.Selection(string="Payment Way Domain", selection=PAYMENT_WAY_DOMAIN)
