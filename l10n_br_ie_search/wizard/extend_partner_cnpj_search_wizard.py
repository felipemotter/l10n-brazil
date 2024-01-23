from odoo import api, models


class ExtendPartnerCnpjSearchWizard(models.TransientModel):
    _inherit = "partner.search.wizard"

    def _get_partner_ie(self):
        webservice = self.env["l10n_br_cnpj_search.webservice.abstract"]
        response = None

        if self._provider() == "sefaz":
            response = webservice.sefaz_search(self.state_id.code, self.cnpj_cpf, None)
        elif self._provider() == "sintegraws":
            response = webservice.sintegraws_search(self.cnpj_cpf)

        if response is not None:
            data = webservice.validate(response)
            inscr_est_dict = webservice._sefaz_import_data(data)
            inscr_est = inscr_est_dict.get("inscr_est", "")
            return inscr_est

    @api.model
    def _provider(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_br_ie_search.ie_search")
        )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res["inscr_est"] = self._get_partner_ie()
        return res
