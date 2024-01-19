# Copyright 2022 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from erpbrasil.base.misc import punctuation_rm
from requests import get

from odoo import _, api, models
from odoo.exceptions import UserError


class PartyMixin(models.AbstractModel):
    _inherit = "l10n_br_base.party.mixin"

    def search_cnpj(self):
        """Search CNPJ by the chosen API"""
        if not self.cnpj_cpf:
            raise UserError("Por favor insira o CNPJ")

        if self.cnpj_validation_disabled():
            raise UserError(

                    "It is necessary to activate the option to validate de CNPJ to use this "
                    + "functionality."
            )

        cnpj_cpf = punctuation_rm(self.cnpj_cpf)
        webservice = self.env["l10n_br_cnpj_search.webservice.abstract"]
        response = get(
            webservice.get_api_url(cnpj_cpf), headers=webservice.get_headers()
        )

        data = webservice.validate(response)
        values = webservice.import_data(data)
        values["company_type"] = "company"
        self.write(values)

    def action_open_cnpj_search_wizard(self):
        if not self.cnpj_cpf:
            raise UserError("Please enter your CNPJ")
        # Forces the system to enter a name so the user doesn't have to type
        if not self.name:
            self.name = "/"

        if self.cnpj_validation_disabled():
            raise UserError(
                "It is necessary to activate the option to validate de CNPJ to use this "
                + "functionality."
            )
        return {
            "name": "Search Data by CNPJ",
            "type": "ir.actions.act_window",
            "res_model": "partner.search.wizard",
            "view_type": "form",
            "view_mode": "form",
            "context": {
                "default_partner_id": self.id,
            },
            "target": "new",
        }

    @api.model
    def cnpj_validation_disabled(self):
        cnpj_validation_disabled = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_br_base.disable_cpf_cnpj_validation")
        )
        return cnpj_validation_disabled
