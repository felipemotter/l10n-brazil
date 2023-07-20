from odoo.exceptions import UserError
from odoo.tests import SavepointCase, tagged

from ..constants.fiscal import FINAL_CUSTOMER_NO, FINAL_CUSTOMER_YES, TAX_DOMAIN_ICMS


@tagged("icms")
class TestICMSRegulation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("l10n_br_base.res_partner_akretion")
        cls.company = cls.env.ref("base.main_company")
        cls.product = cls.env.ref("product.product_product_1")
        cls.nbm = cls.env["l10n_br_fiscal.nbm"]
        cls.icms_regulation = cls.env.ref("l10n_br_fiscal.tax_icms_regulation")

        cls.sc_state_id = cls.env.ref("base.state_br_sc")
        cls.sp_state_id = cls.env.ref("base.state_br_sp")
        cls.venda_operation_line_id = cls.env.ref("l10n_br_fiscal.fo_venda_venda")
        cls.ncm_48191000_id = cls.env.ref("l10n_br_fiscal.ncm_48191000")
        cls.ncm_energia_id = cls.env.ref("l10n_br_fiscal.ncm_27160000")

    def test_icms_sc_sc_ind_final_yes_default(self):
        tax_icms = self.find_icms_tax(
            in_state_id=self.sc_state_id,
            out_state_id=self.sc_state_id,
            ncm_id=self.ncm_48191000_id,
            ind_final=FINAL_CUSTOMER_YES,
        )
        self.assertEqual(tax_icms.percent_amount, 17.00)

    def test_icms_sc_sc_ind_final_no_default(self):
        tax_icms = self.find_icms_tax(
            in_state_id=self.sc_state_id,
            out_state_id=self.sc_state_id,
            ncm_id=self.ncm_48191000_id,
            ind_final=FINAL_CUSTOMER_NO,
        )
        self.assertEqual(tax_icms.percent_amount, 12.00)

    def test_icms_sc_sc_ind_final_yes_ncm_energia(self):
        tax_icms = self.find_icms_tax(
            in_state_id=self.sc_state_id,
            out_state_id=self.sc_state_id,
            ncm_id=self.ncm_energia_id,
            ind_final=FINAL_CUSTOMER_YES,
        )
        self.assertEqual(tax_icms.percent_amount, 25.00)

    def test_icms_sc_sp_ind_final_yes_default(self):
        tax_icms = self.find_icms_tax(
            in_state_id=self.sc_state_id,
            out_state_id=self.sp_state_id,
            ncm_id=self.ncm_48191000_id,
            ind_final=FINAL_CUSTOMER_YES,
        )
        self.assertEqual(tax_icms.percent_amount, 12.00)

    def find_icms_tax(self, in_state_id, out_state_id, ncm_id, ind_final):

        self.partner.state_id = in_state_id
        self.company.state_id = out_state_id
        self.product.ncm_id = ncm_id

        tax_icms, _ = self.icms_regulation.map_tax(
            company=self.company,
            partner=self.partner,
            product=self.product,
            nbm=self.nbm,
            operation_line=self.venda_operation_line_id,
            ind_final=ind_final,
        )
        return tax_icms.filtered(lambda t: t.tax_domain == TAX_DOMAIN_ICMS)

    def test_state_difal_base_duplicity(self):

        demo_state = self.env.ref("base.state_br_sc")

        with self.assertRaises(UserError):
            self.env["l10n_br_fiscal.icms.difal.regulation"].create(
                {
                    "name": "Difal Test",
                    "unique_base_state_ids": [(4, demo_state.id, 0)],
                    "double_base_state_ids": [(4, demo_state.id, 0)],
                }
            )
