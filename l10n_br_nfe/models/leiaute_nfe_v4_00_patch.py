# Copyright 2021 Akretion (Raphaël Valyi <raphael.valyi@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

# These xsd mixins are overriden to alter the xsd_required attribute
# of some fields. Indeed, unless generateDS, xsdata has no proper
# support for <choice> tags and may fail to set xsd_required properly.
# (all in all this is a minor issue compared to all the pros of xsdata)


class Tipi(models.AbstractModel):
    _inherit = "nfe.40.tipi"

    nfe40_choice3 = fields.Selection(
        [("nfe40_IPITrib", "IPITrib"), ("nfe40_IPINT", "IPINT")], "IPITrib/IPINT"
    )
    nfe40_IPITrib = fields.Many2one(xsd_required=True)
    nfe40_IPINT = fields.Many2one(xsd_required=True)


class Nfref(models.AbstractModel):
    _inherit = "nfe.40.nfref"

    nfe40_refNF = fields.Many2one(xsd_required=True)
    nfe40_refNFP = fields.Many2one(xsd_required=True)
    nfe40_refECF = fields.Many2one(xsd_required=True)


class Prod(models.AbstractModel):
    _inherit = "nfe.40.prod"

    nfe40_veicProd = fields.Many2one(xsd_required=False)  # not required but choice
    nfe40_med = fields.Many2one(xsd_required=False)
    nfe40_arma = fields.One2many()  # only for proper field ordering
    nfe40_comb = fields.Many2one(xsd_required=False)  # not required but choice


class Imposto(models.AbstractModel):
    _inherit = "nfe.40.imposto"

    nfe40_ICMS = fields.Many2one(xsd_required=True)
    nfe40_IPI = fields.Many2one(xsd_required=True)

    # next fields are only repeated to keep proper field ordering:
    nfe40_II = fields.Many2one()
    nfe40_ISSQN = fields.Many2one()
    nfe40_PIS = fields.Many2one()
    nfe40_PISST = fields.Many2one()
    nfe40_COFINS = fields.Many2one()
    nfe40_COFINSST = fields.Many2one()
    nfe40_ICMSUFDest = fields.Many2one()


class Pis(models.AbstractModel):
    _inherit = "nfe.40.pis"

    nfe40_PISAliq = fields.Many2one(xsd_required=True)
    nfe40_PISQtde = fields.Many2one(xsd_required=True)
    nfe40_PISNT = fields.Many2one(xsd_required=True)
    nfe40_PISOutr = fields.Many2one(xsd_required=True)


class Pisoutr(models.AbstractModel):
    _inherit = "nfe.40.pisoutr"

    nfe40_vBC = fields.Monetary(
        xsd_required=True,  # not required but choice
        currency_field="brl_currency_id",
    )
    nfe40_pPIS = fields.Float(xsd_required=True)  # not required but choice


class Cofins(models.AbstractModel):
    _inherit = "nfe.40.cofins"

    nfe40_COFINSAliq = fields.Many2one(xsd_required=True)
    nfe40_COFINSQtde = fields.Many2one(xsd_required=True)
    nfe40_COFINSNT = fields.Many2one(xsd_required=True)
    nfe40_COFINSOutr = fields.Many2one(xsd_required=True)


class Cofinsnt(models.AbstractModel):
    _inherit = "nfe.40.cofinsnt"

    nfe40_vBC = fields.Monetary(
        xsd_required=True,  # not required but choice
        currency_field="brl_currency_id",
    )
    nfe40_pCOFINS = fields.Float(xsd_required=True)  # not required but choice


class Cofinsoutr(models.AbstractModel):
    _inherit = "nfe.40.cofinsoutr"

    nfe40_vBC = fields.Monetary(xsd_required=True)  # not required but choice
    nfe40_pCOFINS = fields.Float(xsd_required=True)  # not required but choice


class Icms(models.AbstractModel):
    _inherit = "nfe.40.icms"

    nfe40_ICMSPart = fields.Many2one(xsd_required=True)
    nfe40_ICMSST = fields.Many2one()  # only for field ordering


class ImpostoDevol(models.AbstractModel):
    _inherit = "nfe.40.impostodevol"

    nfe40_IPI = fields.Many2one(
        comodel_name="nfe.40.tipi"  # "nfe.40.ipi" with generateDS
    )
