# Copyright (C) 2019 - Raphaël Valyi Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import SUPERUSER_ID, _, api
from odoo.exceptions import UserError
from odoo.tools.sql import column_exists, create_column


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    cr.execute("select demo from ir_module_module where name='l10n_br_account';")
    is_demo = cr.fetchone()[0]
    if is_demo:
        # load convenient COAs that are used in demos and tests
        # without a hard dependency (you don't need all COAs for production)
        coa_modules = env["ir.module.module"].search(
            [
                ("name", "in", ("l10n_br_coa_generic", "l10n_br_coa_simple")),
                ("state", "=", "uninstalled"),
            ]
        )

        if coa_modules:
            raise UserError(
                _(
                    """It looks like your database %s(database) is running with demo
                   data. But the l10n_br_account module will need you to install the
                   l10n_br_coa_simple and l10n_br_coa_generic
                   chart of accounts modules first to load l10n_br_account demo data
                   or run its tests properly (for production, these dependencies are not
                   required, that is why these are not usual explicit
                   module dependencies).
                   Please install the l10n_br_coa_simple and l10n_br_coa_generic modules
                   first and try installing the l10n_br_account module again.
                """,
                    database=cr.dbname,
                )
            )


def load_fiscal_taxes(env, l10n_br_coa_chart):
    companies = env["res.company"].search(
        [("chart_template_id", "=", l10n_br_coa_chart.id)]
    )

    for company in companies:
        taxes = env["account.tax"].search([("company_id", "=", company.id)])

        for tax in taxes:
            if tax.get_external_id():
                tax_ref = tax.get_external_id().get(tax.id)
                ref_module, ref_name = tax_ref.split(".")
                ref_name = ref_name.replace(str(company.id) + "_", "")
                template_source_ref = ".".join(["l10n_br_coa", ref_name])
                template_source = env.ref(template_source_ref)
                tax_source_ref = ".".join([ref_module, ref_name])
                tax_template = env.ref(tax_source_ref)
                tax.fiscal_tax_ids = (
                    tax_template.fiscal_tax_ids
                ) = template_source.fiscal_tax_ids


def post_init_hook(cr, registry):
    """Relate fiscal taxes to account taxes."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    l10n_br_coa_charts = env["account.chart.template"].search(
        [("parent_id", "=", env.ref("l10n_br_coa.l10n_br_coa_template").id)]
    )

    for l10n_br_coa_chart in l10n_br_coa_charts:
        load_fiscal_taxes(env, l10n_br_coa_chart)
