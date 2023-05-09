# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

from odoo import tools

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    # logger.debug("START MIGRATE FISCAL NCM")
    # openupgrade.load_data(
    #     env.cr,
    #     "l10n_br_fiscal",
    #     "data/l10n_br_fiscal.ncm.csv",
    # )
    # logger.debug("STOP MIGRATE FISCAL NCM")
    # short_files = {
    #     "load_ncm": "data/l10n_br_fiscal.ncm.csv",
    # }

    # demofiles = []
    # for short_file in short_files.keys():
    #     if tools.config.get(short_file):
    #         demofiles.append(short_files[short_file])

    # for f in demofiles:
    #     tools.convert_file(
    #         env.cr,
    #         "l10n_br_fiscal",
    #         f,
    #         None,
    #         mode="init",
    #         noupdate=True,
    #         kind="demo",
    #     )
    # logger.debug("STOP MIGRATE FISCAL NCM")

    tools.convert_file(
        env.cr,
        "l10n_br_fiscal",
        "data/l10n_br_fiscal.ncm.csv",
        None,
        mode="init",
        noupdate=False,
        kind="init",
    )
