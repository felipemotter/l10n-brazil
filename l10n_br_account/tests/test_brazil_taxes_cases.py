# l10n_br_account/tests/test_invoice_taxes.py

from datetime import datetime, timedelta

from odoo.tests.common import Form, TransactionCase


class TestInvoiceTaxes(TransactionCase):
    def setUp(self):
        super(TestInvoiceTaxes, self).setUp()

        self.company_id = self.env.ref("l10n_br_base.empresa_lucro_presumido")
        self.env.user.company_id = self.company_id

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Client",
                "country_id": self.env.ref("base.br").id,
                "state_id": self.env.ref("base.state_br_sp").id,
                "city_id": self.env.ref("l10n_br_base.city_3550308").id,
                "is_company": True,
                "fiscal_profile_id": self.env.ref(
                    "l10n_br_fiscal.partner_fiscal_profile_cnt"
                ).id,
            }
        )

        self.product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "default_code": "PROD001",
                "fiscal_type": "00",
                "ncm_id": self.env.ref("l10n_br_fiscal.ncm_94033000").id,
            }
        )

        self.sale_operation_id = self.env.ref("l10n_br_fiscal.fo_venda")
        self.sale_operation_line_id = self.env.ref("l10n_br_fiscal.fo_venda_venda")
        self.sale_operation_id.deductible_taxes = True

        self.buy_operation_id = self.env.ref("l10n_br_fiscal.fo_compras")
        self.buy_operation_line_id = self.env.ref(
            "l10n_br_fiscal.fo_compras_compras_comercializacao"
        )
        self.buy_operation_id.deductible_taxes = False

        self.bonif_operation_id = self.env.ref("l10n_br_fiscal.fo_bonificacao")
        self.bonif_operation_line_id = self.env.ref(
            "l10n_br_fiscal.fo_bonificacao_bonificacao"
        )

    def create_invoice(self, operation_id, operation_line_id, ind_final=0):
        # Get current date and due date (current date + 1 day)
        current_date = datetime.now().date()
        due_date = current_date + timedelta(days=1)

        # Create the invoice with Form
        with Form(
            self.env["account.move"]
            .with_company(self.company_id)
            .with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.partner
            invoice_form.invoice_date = current_date
            invoice_form.invoice_date_due = due_date
            invoice_form.fiscal_operation_id = operation_id
            invoice_form.document_type_id = self.env.ref("l10n_br_fiscal.document_55")
            invoice_form.document_serie_id = self.env.ref(
                "l10n_br_fiscal.document_55_serie_1"
            )
            invoice_form.ind_final = ind_final

            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product
                line_form.quantity = 1.0
                line_form.price_unit = 1000
                line_form.fiscal_operation_id = operation_id
                line_form.fiscal_operation_line_id = operation_line_id

        invoice = invoice_form.save()

        # Post the invoice
        invoice.action_post()

        return invoice

    def test_deductible_taxes(self):

        self.create_invoice(self.sale_operation_id, self.sale_operation_line_id)
