# @ 2021 KMEE - kmee.com.br
#   Luis Felipe Mileo <mileo@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestPaymentOrder(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Get Invoice for test
        cls.invoice_customer_without_paymeny_mode = cls.env.ref(
            "l10n_br_account_payment_order." "demo_invoice_no_payment_mode"
        )

    def test_cancel_invoice_no_payment_mode_pay(self):
        """ Test Pay Invoice without payment mode in cash"""

        # I check that the invoice state is "Open"
        self.assertEqual(
            self.invoice_customer_without_paymeny_mode.invoice_payment_state, "not_paid"
        )

        # TODO testar colocar valor de pagamento
        register_payments = (
            self.env["account.payment.register"]
            .with_context(active_ids=self.invoice_customer_without_paymeny_mode.id)
            .create(
                {
                    "journal_id": self.env["account.journal"]
                    .search([("type", "=", "cash")], limit=1)
                    .id
                }
            )
        )
        register_payments.create_payments()

        # I verify that invoice is now in Paid state
        self.assertEqual(
            self.invoice_customer_without_paymeny_mode.invoice_payment_state,
            "paid",
            "Invoice is not in Paid state",
        )

    def test_cancel_invoice_no_payment_mode_cancel(self):
        """ Test Cancel Invoice Without Payment Mode """
        self.invoice_customer_without_paymeny_mode.button_cancel()

        # I check that the invoice state is "Cancel"
        self.assertEqual(self.invoice_customer_without_paymeny_mode.state, "cancel")
