# Copyright (C) 2013  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Account NFe/NFC-e Integration",
    "summary": "Integration between account and NFe",
    "category": "Localisation",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-brazil",
    "version": "12.0.0.0.0",
    "development_status": "Alpha",
    "depends": [
        "l10n_br_nfe",
        "account_payment_mode",
    ],
    "data": [
        "views/account_payment_mode.xml",
    ],
    "demo": [
        # Some demo data is being loaded via post_init_hook in hook file
    ],
}
