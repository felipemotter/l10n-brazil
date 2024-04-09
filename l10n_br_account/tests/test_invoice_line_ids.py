# Copyright 2024 Engenere.one
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestInvoiceLineIds(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.ref("l10n_br_base.empresa_lucro_presumido")

        self.company.delivery_costs = "total"

        self.invoice_account_id = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "code": "RECTEST",
                "name": "Test receivable account",
                "reconcile": True,
            }
        )

        self.invoice_journal = self.env["account.journal"].create(
            {
                "company_id": self.company.id,
                "name": "Invoice Journal - (test)",
                "code": "INVTEST",
                "type": "sale",
            }
        )

        self.invoice_line_account_id = self.env["account.account"].create(
            {
                "company_id": self.company.id,
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
                "code": "701",
                "name": "Product revenue account (test)",
            }
        )

        self.fiscal_operation_id = self.env.ref("l10n_br_fiscal.fo_venda")
        self.fiscal_operation_id.deductible_taxes = True

        product_id = self.env.ref("product.product_product_7")
        self.partner = self.env["res.partner"].create(
            {
                "name": "Partner (test)",
                "country_id": self.env.ref("base.br").id,
                "company_id": self.company.id,
            }
        )

        invoice_line_vals_1 = [
            (
                0,
                0,
                {
                    "account_id": self.invoice_line_account_id.id,
                    "product_id": product_id.id,
                    "quantity": 1,
                    "price_unit": 1000.0,
                },
            )
        ]

        invoice_line_vals_2 = [
            (
                0,
                0,
                {
                    "account_id": self.invoice_line_account_id.id,
                    "product_id": product_id.id,
                    "quantity": 1,
                    "price_unit": 1000.0,
                },
            ),
            (
                0,
                0,
                {
                    "account_id": self.invoice_line_account_id.id,
                    "product_id": product_id.id,
                    "quantity": 3,
                    "price_unit": 500.0,
                },
            ),
        ]

        self.out_invoice_1 = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": self.company.id,
                    "document_serie_id": self.env.ref(
                        "l10n_br_fiscal.empresa_lc_document_55_serie_1"
                    ).id,
                    "journal_id": self.invoice_journal.id,
                    "invoice_user_id": self.env.user.id,
                    "fiscal_operation_id": self.fiscal_operation_id,
                    "move_type": "out_invoice",
                    "currency_id": self.company.currency_id.id,
                    "invoice_line_ids": invoice_line_vals_1,
                    "amount_freight_value": 100,
                    "amount_insurance_value": 150,
                    "amount_other_value": 50,
                }
            )
        )

        self.out_invoice_2 = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": self.company.id,
                    "document_serie_id": self.env.ref(
                        "l10n_br_fiscal.empresa_lc_document_55_serie_1"
                    ).id,
                    "journal_id": self.invoice_journal.id,
                    "invoice_user_id": self.env.user.id,
                    "fiscal_operation_id": self.fiscal_operation_id,
                    "move_type": "out_invoice",
                    "currency_id": self.company.currency_id.id,
                    "invoice_line_ids": invoice_line_vals_2,
                    "amount_freight_value": 300,
                    "amount_insurance_value": 450,
                    "amount_other_value": 150,
                }
            )
        )

    def test_out_invoice_1_field_by_total(self):
        self.assertTrue(self.out_invoice_1)
        self.out_invoice_1.action_post()

        self.assertEqual(self.out_invoice_1.delivery_costs, "total")
        # Check the invoice_line_ids fields
        self.assertEqual(self.out_invoice_1.invoice_line_ids.fiscal_price, 1000.0)
        self.assertEqual(self.out_invoice_1.invoice_line_ids.freight_value, 100.0)
        self.assertEqual(self.out_invoice_1.invoice_line_ids.insurance_value, 150.0)
        self.assertEqual(self.out_invoice_1.invoice_line_ids.other_value, 50.0)
        self.assertEqual(self.out_invoice_1.invoice_line_ids.amount_total, 1300.0)
        self.assertEqual(self.out_invoice_1.invoice_line_ids.amount_untaxed, 1000.0)

        # Check the financial_move_line_ids fields
        self.assertEqual(
            self.out_invoice_1.financial_move_line_ids.amount_residual, 1300.0
        )
        self.assertEqual(self.out_invoice_1.financial_move_line_ids.debit, 1300.0)
        # Correct here it returns that value but it is returning 1300.0
        self.assertEqual(self.out_invoice_1.amount_total, 1300.0)
        # Correct here it returns that value but it is returning 1000.0

    def test_out_invoice_2_field_by_total(self):
        self.assertTrue(self.out_invoice_2)
        self.out_invoice_2.action_post()

        self.assertEqual(self.out_invoice_2.delivery_costs, "total")
        # Check the invoice_line_ids fields
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].fiscal_price, 1000.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].freight_value, 120.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].insurance_value, 180.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].other_value, 60.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].amount_total, 1360.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[0].amount_untaxed, 1000.0)

        # Check the financial_move_line_ids fields
        self.assertEqual(
            self.out_invoice_1.financial_move_line_ids.amount_residual, 3400.0
        )
        self.assertEqual(self.out_invoice_1.financial_move_line_ids.debit, 3400.0)
        # Correct here it returns that value but it is returning 2500.0
        self.assertEqual(self.out_invoice_2.amount_total, 3400.0)
        # Correct here it returns that value but it is returning 2500.0

        # Check the fiscal_line_ids fields
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].fiscal_price, 500.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].freight_value, 180.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].insurance_value, 270.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].other_value, 90.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].amount_total, 2040.0)
        self.assertEqual(self.out_invoice_2.invoice_line_ids[1].amount_untaxed, 1500.0)
