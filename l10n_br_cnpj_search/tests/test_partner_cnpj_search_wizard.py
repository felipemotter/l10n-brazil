from odoo.tests.common import TransactionCase


class TestPartnerCnpjSearchWizard(TransactionCase):
    def setUp(self):
        super(TestPartnerCnpjSearchWizard, self).setUp()
        self.partner_model = self.env["res.partner"]

    def test_open_partner_cnpj_search_wizard(self):
        partner = self.partner_model.create(
            {
                "name": "Nubank",
                "cnpj_cpf": "30.680.829/0001-43",
            }
        )
        context = {"default_partner_id": partner.id}

        wizard = self.env["partner.search.wizard"].with_context(context).create({})

        self.assertEqual(
            wizard.legal_name,
            "Nu Financeira S.A. - Sociedade De Credito, Financiamento E Investimento",
        )
        self.assertEqual(
            wizard.name,
            "Nu Financeira S.A. - Sociedade De Credito, Financiamento E Investimento",
        )
        self.assertEqual(wizard.street_name, "Rua Capote Valente")
        self.assertEqual(wizard.street2, "Andar 12 Ao 15")
        self.assertEqual(wizard.street_number, "120")
        self.assertEqual(wizard.zip, "05.409-000")
        self.assertEqual(wizard.district, "Pinheiros")
        self.assertEqual(wizard.phone, "(11) 3064-8969")
        self.assertEqual(wizard.state_id.code, "SP")
        self.assertEqual(wizard.currency_id, self.env.ref("base.BRL"))

        original_legal_name = partner.legal_name
        original_district = partner.district

        wizard.legal_name = ""
        wizard.street_name = "ROD SC 410"
        wizard.district = ""
        wizard.email = "recursoshumanos@macris.com.br"

        wizard.action_update_partner()
        self.assertEqual(partner.legal_name, original_legal_name)
        self.assertEqual(partner.street_name, "ROD SC 410")
        self.assertEqual(partner.district, original_district)
        self.assertEqual(partner.email, "recursoshumanos@macris.com.br")
