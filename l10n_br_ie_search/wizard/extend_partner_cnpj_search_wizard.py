from erpbrasil.assinatura import certificado as cert
from erpbrasil.edoc.nfe import NFe as edoc_nfe
from erpbrasil.transmissao import TransmissaoSOAP
from requests import Session, get

from odoo import _, api, models
from odoo.exceptions import UserError

SINTEGRA_URL = "https://www.sintegraws.com.br/api/v1/execute-api.php"


class ExtendPartnerCnpjSearchWizard(models.TransientModel):
    _inherit = "partner.search.wizard"

    def _get_partner_ie(self, state_code, cnpj, mockresponse=False):
        webservice = self.env["l10n_br_cnpj_search.webservice.abstract"]
        if self._provider() == "sefaz":
            processo = self._processador()
            response = (
                webservice.sefaz_search(state_code, cnpj, processo)
                if not mockresponse
                else mockresponse
            )
            data = webservice.sefaz_validate(response)
            values = webservice._sefaz_import_data(data)
            return values
        elif self._provider() == "sintegraws":
            response = (
                get(
                    SINTEGRA_URL,
                    data="",
                    params=webservice._get_query(cnpj, webservice._get_token()),
                )
                if not mockresponse
                else mockresponse
            )

            data = webservice.sintegra_validate(response)
            values = webservice._sintegra_import_data(data)
            return values

    @api.model
    def _provider(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("l10n_br_ie_search.ie_search")
        )

    @api.model
    def _get_partner_values(self, cnpj_cpf):
        values = super()._get_partner_values(cnpj_cpf)
        state_id = self.env["res.country.state"].browse(values["state_id"])
        ie_values = self._get_partner_ie(state_code=state_id.code, cnpj=cnpj_cpf)
        values.update(ie_values)
        return values

    @api.model
    def _processador(self):
        company = self.env.company
        if not company.certificate_ecnpj_id:
            raise UserError(_("Certificate not found"))

        certificado = cert.Certificado(
            arquivo=company.certificate_ecnpj_id.file,
            senha=company.certificate_ecnpj_id.password,
        )
        session = Session()
        session.verify = False
        transmissao = TransmissaoSOAP(certificado, session)
        return edoc_nfe(
            transmissao,
            company.state_id.ibge_code,
            versao=company.nfe_version,
            ambiente=company.nfe_environment,
        )
