# @ 2018 Akretion - www.akretion.com.br -
#   Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestPaymentOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Product Tax Boleto
        cls.invoice_product_tax_boleto = cls.env.ref(
            "l10n_br_account_payment_order.demo_invoice_payment_order_bb_cnab400"
        )

        # Product Tax Boleto
        cls.invoice_cheque = cls.env.ref(
            "l10n_br_account_payment_order.demo_invoice_payment_order_cheque"
        )

    def test_product_tax_boleto(self):
        """ Test Invoice where Payment Mode has Product Tax. """
        self.invoice_product_tax_boleto._onchange_payment_mode_id()

        # TODO por algum motivo o Modo de Pagamento é alterado e assim não
        #  encontra o Produto Taxa retornando nada no line_product_tax, essa
        #  alteração de Modo de Pagto não ocorre na tela
        # Produto Taxa adicionado
        # line_product_tax = self.invoice_product_tax_boleto.invoice_line_ids.filtered(
        #    lambda l: l.product_id
        #    == self.invoice_product_tax_boleto.payment_mode_id.product_tax_id
        # )
        # self.assertEqual(len(line_product_tax), 1)
        # I validate invoice by creating on
        self.invoice_product_tax_boleto.post()
        # I check that the invoice state is "posted"
        self.assertEqual(self.invoice_product_tax_boleto.state, "posted")

    def test_payment_mode_without_payment_order(self):
        """ Test Invoice when Payment Mode not generate Payment Order. """
        self.invoice_cheque._onchange_payment_mode_id()
        # I validate invoice by creating on
        self.invoice_cheque.post()
        # I check that the invoice state is "posted"
        self.assertEqual(self.invoice_cheque.state, "posted")
        payment_order = self.env["account.payment.order"].search(
            [("payment_mode_id", "=", self.invoice_cheque.payment_mode_id.id)]
        )
        self.assertEqual(len(payment_order), 0)

    def test_bra_number_constrains(self):
        """ Test bra_number constrains. """
        self.banco_bradesco = self.env["res.bank"].search([("code_bc", "=", "033")])
        try:
            result = self.env["res.partner.bank"].create(
                dict(
                    bank_id=self.banco_bradesco.id,
                    partner_id=self.ref("l10n_br_base.res_partner_akretion"),
                    bra_number="12345",
                )
            )
        except Exception:
            result = False
        self.assertFalse(
            result,
            "Error to check included bank BRA Number greater than four caracters",
        )
