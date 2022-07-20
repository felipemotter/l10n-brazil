from odoo import fields, models


class PaymentMode(models.Model):
    _inherit = "account.payment.mode"

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
