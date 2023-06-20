# Copyright 2017 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class FiscalDocument(models.Model):
    _inherit = "l10n_br_fiscal.document"

    sending_job_ids = fields.Many2many(
        comodel_name="queue.job",
        column1="fiscal_document_id",
        column2="job_id",
        string="Send Fiscal Document Jobs",
        copy=False,
    )

    def _send_document_job(self):
        for record in self:
            record._eletronic_document_send()

    def _document_send(self):
        queue_obj = self.env["queue.job"]
        no_electronic = self.filtered(lambda d: not d.document_electronic)
        no_electronic._no_eletronic_document_send()
        electronic = self - no_electronic

        send_now = electronic.filtered(
            lambda documento: documento.fiscal_operation_id.queue_document_send
            == "send_now"
        )
        send_later = electronic - send_now

        if send_now:
            _logger.info(_("Sending fiscal document now: %s", send_now.ids))
            send_now._send_document_job()

        for document in send_later:
            if document.sending_job_ids.filtered(
                lambda x: x.state in {"pending", "enqueued", "started"}
            ):
                # not send because already in queue
                return
            description = _(f"Sending fiscal document {document.name}")
            new_delay = document.with_delay(
                description=description, max_retries=0
            )._send_document_job()
            job = queue_obj.search([("uuid", "=", new_delay.uuid)])
            document.write({"sending_job_ids": [(4, job.id)]})
