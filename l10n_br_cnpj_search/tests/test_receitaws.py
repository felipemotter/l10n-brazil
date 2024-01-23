# Copyright 2022 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time  # You can't send multiple requests at the same time in trial version

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.l10n_br_cnpj_search.tests.common import TestCnpjCommon


@tagged("post_install", "-at_install")
class TestReceitaWS(TestCnpjCommon):
    def setUp(self):
        super().setUp()

        self.set_param("cnpj_provider", "receitaws")

    def test_receita_ws_fail(self):
        invalido = self.model.create({"name": "invalido", "cnpj_cpf": "00000000000000"})
        invalido._onchange_cnpj_cpf()

        time.sleep(2)  # Pause
        with self.assertRaises(ValidationError):
            invalido.search_cnpj()

    def test_receita_ws_multiple_phones(self):
        isla = self.model.create({"name": "Isla", "cnpj_cpf": "92.666.056/0001-06"})
        isla._onchange_cnpj_cpf()

        time.sleep(2)  # Pause
        isla.search_cnpj()

        self.assertEqual(isla.name.strip(), "Isla Sementes Ltda.")
        self.assertEqual(isla.phone.strip(), "(51) 9852-9561")
        self.assertEqual(isla.mobile.strip(), "(51) 2136-6600")
