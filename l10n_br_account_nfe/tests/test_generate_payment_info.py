from odoo.tests.common import TransactionCase


class TestGeneratePaymentInfo(TransactionCase):
    def setUp(self):
        super(TestGeneratePaymentInfo, self).setUp()

        self.company = self.env.ref("l10n_br_base.empresa_lucro_presumido")
        payment_mode = self.env["account.payment.mode"].create(
            {
                "name": "Money",
                "company_id": self.company.id,
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "fiscal_payment_mode": "18",
                "bank_account_link": "variable",
            }
        )
        payment_mode.fiscal_payment_mode = "18"

        invoice_account_id = (
            self.env["account.account"]
            .create(
                {
                    "company_id": self.company.id,
                    "user_type_id": self.env.ref(
                        "account.data_account_type_receivable"
                    ).id,
                    "code": "RECTEST",
                    "name": "Test receivable account",
                    "reconcile": True,
                }
            )
            .id
        )

        self.invoice = self.env["account.invoice"].create(
            {
                "company_id": self.company.id,
                "partner_id": self.env.ref("l10n_br_base.res_partner_cliente1_sp").id,
                "payment_mode_id": payment_mode.id,
                "document_type_id": self.env.ref("l10n_br_fiscal.document_55").id,
                "fiscal_operation_id": self.env.ref("l10n_br_fiscal.fo_venda").id,
                "issuer": "company",
                "document_serie_id": self.env.ref(
                    "l10n_br_fiscal.empresa_lc_document_55_serie_1"
                ).id,
                "account_id": invoice_account_id,
            }
        )

        invoice_line_account_id = (
            self.env["account.account"]
            .create(
                {
                    "company_id": self.company.id,
                    "user_type_id": self.env.ref(
                        "account.data_account_type_expenses"
                    ).id,
                    "code": "EXPTEST",
                    "name": "Test expense account",
                }
            )
            .id
        )

        self.env["account.invoice.line"].create(
            {
                "product_id": self.env.ref("product.product_product_4").id,
                "quantity": 1,
                "price_unit": 100,
                "invoice_id": self.invoice.id,
                "name": "something",
                "fiscal_operation_id": self.env.ref("l10n_br_fiscal.fo_venda").id,
                "fiscal_operation_line_id": self.env.ref(
                    "l10n_br_fiscal.fo_venda_venda"
                ).id,
                "account_id": invoice_line_account_id,
            }
        )

    def test_generate_payment_info(self):
        self.invoice.action_invoice_open()
