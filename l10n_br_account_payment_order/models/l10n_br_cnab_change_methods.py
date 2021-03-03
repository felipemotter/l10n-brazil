# Copyright (C) 2021-Today - Akretion (<http://www.akretion.com>).
# @author Magno Costa <magno.costa@akretion.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class L10nBrCNABChangeMethods(models.Model):
    _name = 'l10n_br_cnab.change.methods'
    _description = 'Methods used to make changes in CNAB Movement.'

    def _create_cnab_change(
        self, change_type, new_date, rebate_value, discount_value,
        reason='', **kwargs):
        """
        CNAB - Alterações possíveis
        :param change_type:
        :param new_date: Nova Data de Vencimento
        :param rebate_value: Valor do Abatimento
        :param discount_value: Valor do Desconto
        :param reason: Justificatica de alteração
        :param kwargs:
        :return:
        """
        # Checar se existe uma Instrução de CNAB ainda a ser enviada
        self._check_cnab_instruction_to_be_send()

        payorder, new_payorder = self._get_payment_order(self.invoice_id)

        if change_type == 'change_date_maturity':
            self._change_cnab_date_maturity(
                new_date, reason, payorder, new_payorder)
        elif change_type == 'change_payment_mode':
            self._change_payment_mode(reason, **kwargs)
        elif change_type == 'baixa':
            self._create_baixa(reason, **kwargs)
        elif change_type == 'not_payment':
            self._create_cnab_not_payment(reason, payorder, new_payorder)
        elif change_type == 'protest_tittle':
            self._create_cnab_protest_tittle(reason, payorder, new_payorder)
        elif change_type == 'suspend_protest_keep_wallet':
            self._create_cnab_suspend_protest_keep_wallet(
                reason, payorder, new_payorder)
        elif change_type == 'suspend_protest_writte_off':
            self._create_cnab_suspend_protest_writte_off(
                reason, payorder, new_payorder)
        elif change_type == 'grant_rebate':
            self._create_cnab_grant_rebate(
                rebate_value, reason, payorder, new_payorder)
        elif change_type == 'cancel_rebate':
            self._create_cnab_cancel_rebate(reason, payorder, new_payorder)
        elif change_type == 'grant_discount':
            self._create_cnab_grant_discount(
                discount_value, reason, payorder, new_payorder)
        elif change_type == 'cancel_discount':
            self._create_cnab_cancel_discount(reason, payorder, new_payorder)

    def _get_payment_order(self, invoice):
        """
        CNAB - Obtem a Ordem de Pagamento a ser usada e se é uma nova
        :param invoice:
        :return: Orderm de Pagamento, E se é uma nova
        """

        # Verificar Ordem de Pagto
        apo = self.env['account.payment.order']
        # Existe a possibilidade de uma Fatura ter diferentes
        # Modos de Pagto nas linhas no caso CNAB ?
        payorder = apo.search([
            ('payment_mode_id', '=', invoice.payment_mode_id.id),
            ('state', '=', 'draft')], limit=1)
        new_payorder = False
        if not payorder:
            payorder = apo.create(
                invoice._prepare_new_payment_order(invoice.payment_mode_id)
            )
            new_payorder = True

        return payorder, new_payorder

    def _check_cnab_instruction_to_be_send(self):
        """
        CNAB - Não pode ser enviada uma Instrução
         de CNAB se houver uma pendente.
        :return: Mensagem de Erro caso exista
        """
        payment_line_to_be_send = self.payment_line_ids.filtered(
            lambda t: t.order_id.state in ('draft', 'open', 'generated'))
        if payment_line_to_be_send:
            raise UserError(_(
                'There is a CNAB Payment Order %s in status %s'
                ' related to invoice %s created, the CNAB file'
                ' should be sent to bank, because only after'
                ' that it is possible make another CNAB Instruction.'
            ) % (payment_line_to_be_send.order_id.name,
                 payment_line_to_be_send.order_id.state, self.invoice_id.number))
        pass

    def _msg_cnab_payment_order_at_invoice(self, new_payorder, payorder):
        """
        CNAB - Registra a mensagem de alteração na Fatura para rastreabilidade.
        :param new_payorder: Se é uma nova Ordem de Pagamento/Debito
        :param payorder: Objeto Ordem de Pagamento/Debito
        :return:
        """

        cnab_instruction = self.mov_instruction_code_id.code + ' - ' + \
                           self.mov_instruction_code_id.name
        if new_payorder:
            self.invoice_id.message_post(body=_(
                'Payment line added to the the new draft payment '
                'order %s which has been automatically created,'
                ' to send CNAB Instruction %s for OWN NUMBER %s.'
            ) % (payorder.name, cnab_instruction, self.own_number))
        else:
            self.invoice_id.message_post(body=_(
                'Payment line added to the existing draft '
                'order %s to send CNAB Instruction %s for OWN NUMBER %s.'
            ) % (payorder.name, cnab_instruction, self.own_number))

    def _msg_error_cnab_missing(self, payment_mode_name, missing):
        """
        CNAB - Não é possível fazer a alteração pois falta algo
        :param payment_mode_name: Nome do Modo de Pagamento
        :param missing: descrição do que falta
        :return: Mensagem de Erro
        """
        raise UserError(_(
            "Payment Mode %s don't has %s for making CNAB change,"
            " check if should have."
        ) % (payment_mode_name, missing))

    def _change_cnab_date_maturity(
            self, new_date, reason, payorder, new_payorder):
        """
        CNAB - Instrução de Alteração da Data de Vencimento.
        :param new_date: nova data de vencimento
        :param reason: descrição do motivo da alteração
        :return: deveria retornar algo ? Uma mensagem de confirmação talvez ?
        """

        if new_date == self.date_maturity:
            raise UserError(_(
                'New Date Maturity %s is equal to actual Date Maturity %s'
            ) % (new_date, self.date_maturity))

        # Modo de Pagto usado precisa ter o codigo de alteração do vencimento
        if not self.invoice_id.payment_mode_id.cnab_code_change_maturity_date_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Date Maturity Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_change_maturity_date_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Request to'
            ' Change Maturity Date.'))
        self.create_payment_line_from_move_line(payorder)
        self.cnab_state = 'added'

        self.write({
            'date_maturity': new_date,
            'last_change_reason': reason,
        })

        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_not_payment(self, reason, payorder, new_payorder):
        """
        CNAB - Não Pagamento/Inadimplencia.
        :param reason: descrição do motivo da alteração
        :return: deveria retornar algo ? Uma mensagem de confirmação talvez ?
        """
        # Modo de Pagto usado precisa ter a Conta Contabil de
        # Não Pagamento/Inadimplencia
        if not self.invoice_id.payment_mode_id.not_payment_account_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'the Account to Not Payment')

        if not self.invoice_id.payment_mode_id.cnab_write_off_code_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Writte Off Code')

        # TODO: O codigo usado seria o mesmo do writte off ?
        #  Em todos os casos?
        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_write_off_code_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Request to'
            ' Write Off, because not payment.'))
        self.create_payment_line_from_move_line(payorder)
        self.cnab_state = 'added'

        # Reconciliação e Baixa do Título
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        journal = self.payment_mode_id.fixed_journal_id
        move = move_obj.create({
            'name': 'CNAB - Banco ' + journal.bank_id.short_name + ' - Conta '
                    + journal.bank_account_id.acc_number + '- Inadimplência',
            'date': fields.Datetime.now(),
            # TODO  - Campo está sendo preenchido em outro lugar
            'ref': 'CNAB Baixa por Inadimplêcia',
            # O Campo abaixo é usado apenas para mostrar ou não a aba
            # referente ao LOG do CNAB mas nesse caso não há.
            # 'is_cnab': True,
            'journal_id': journal.id,
        })
        # Linha a ser conciliada
        counterpart_values = {
            'credit': self.amount_residual,
            'debit': 0.0,
            'account_id': self.account_id.id,
        }
        # linha referente a Conta Contabil de Inadimplecia
        move_not_payment_values = {
            'debit': self.amount_residual,
            'credit': 0.0,
            'account_id': self.invoice_id.
                payment_mode_id.not_payment_account_id.id,
        }

        commom_move_values = {
            'move_id': move.id,
            'partner_id': self.partner_id.id,
            'already_completed': True,
            'ref': self.own_number,
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'company_currency_id': self.company_id.currency_id.id,
        }

        counterpart_values.update(commom_move_values)
        move_not_payment_values.update(commom_move_values)

        moves = move_line_obj.with_context(
            check_move_validity=False).create(
            (counterpart_values, move_not_payment_values)
        )

        move_line_to_reconcile = moves.filtered(
            lambda m: m.credit > 0.0)
        (self + move_line_to_reconcile).reconcile()

        self.write({
            'last_change_reason': reason,
            'payment_situation': 'nao_pagamento',
        })

        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_writte_off(self):
        """
        CNAB - Instrução de Baixar de Título.
        """
        if not self.invoice_id.payment_mode_id.cnab_write_off_code_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Writte Off Code')

        # Checar se existe uma Instrução de CNAB ainda a ser enviada
        self._check_cnab_instruction_to_be_send()

        payorder, new_payorder = self._get_payment_order(self.invoice_id)

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_write_off_code_id
        self.payment_situation = 'baixa_liquidacao'
        self.message_post(body=_(
            'Movement Instruction Code Updated for Request to'
            ' Write Off, because payment done in another way.'))
        self.create_payment_line_from_move_line(payorder)
        self.cnab_state = 'added_paid'

        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_change_tittle_value(self):
        """
        CNAB - Alteração do Valor do Título.
        """
        if not self.payment_mode_id.cnab_code_change_title_value_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Tittle Value Code')

        # Checar se existe uma Instrução de CNAB ainda a ser enviada
        self._check_cnab_instruction_to_be_send()

        payorder, new_payorder = self._get_payment_order(self.invoice_id)

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_change_title_value_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Request to'
            ' Change Title Value, because partial payment'
            ' of %d done.') % (self.debit - self.amount_residual))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'

        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_protest_tittle(self, reason, payorder, new_payorder):
        """
        CNAB - Protestar Título.
        """
        if not self.payment_mode_id.cnab_code_protest_title_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Protest Tittle Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_protest_title_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Request to Protest Title'))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_suspend_protest_keep_wallet(
            self, reason, payorder, new_payorder):
        """
        CNAB - Sustar Protesto e Manter em Carteira.
        """
        if not self.payment_mode_id.cnab_code_suspend_protest_keep_wallet_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name,
                'Suspend Protest and Keep in Wallet Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_suspend_protest_keep_wallet_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Suspend'
            ' Protest and Keep in Wallet.'))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_suspend_protest_writte_off(
            self, reason, payorder, new_payorder):
        """
        CNAB - Sustar Protesto e Baixar Titulo.
        """
        # TODO: Deveria chamar a função de Não
        #  Pagamento( _create_cnab_not_payment ) ?

        if not self.payment_mode_id.cnab_code_suspend_protest_write_off_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name,
                'Suspend Protest and Writte Off Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_suspend_protest_write_off_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Suspend'
            ' Protest and Writte Off Tittle.'))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_grant_rebate(
            self, rebate_value, reason, payorder, new_payorder):
        """
        CNAB - Conceder Abatimento.
        :param rebate_value: Valor do Abatimento
        :param reason: Descrição sobre alteração
        """
        if not self.payment_mode_id.cnab_code_grant_rebate_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Grant Rebate Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_grant_rebate_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Grant'
            ' Rebate for Tittle.'))
        self.with_context(
            rebate_value=rebate_value). \
            create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_cancel_rebate(
            self, reason, payorder, new_payorder):
        """
        CNAB - Cancelar Abatimento.
        :param reason: Descrição sobre alteração
        """
        if not self.payment_mode_id.cnab_code_cancel_rebate_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Cancel Rebate Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_cancel_rebate_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Cancel'
            ' Rebate for Tittle.'))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_grant_discount(
            self, discount_value, reason, payorder, new_payorder):
        """
        CNAB - Conceder Desconto.
        :param discount_value: Valor do Desconto
        :param reason: Descrição sobre alteração
        """
        if not self.payment_mode_id.cnab_code_grant_discount_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Grant Discount Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_grant_discount_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Grant'
            ' Rebate for Tittle.'))
        self.with_context(
            discount_value=discount_value). \
            create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_cnab_cancel_discount(self, reason, payorder, new_payorder):
        """
        CNAB - Cancelar Desconto.
        :param reason: Descrição sobre alteração
        """
        if not self.payment_mode_id.cnab_code_cancel_discount_id:
            self._msg_error_cnab_missing(
                self.payment_mode_id.name, 'Cancel Discount Code')

        self.mov_instruction_code_id = \
            self.payment_mode_id.cnab_code_cancel_discount_id
        self.message_post(body=_(
            'Movement Instruction Code Updated for Cancel'
            ' Discount for Tittle.'))
        self.create_payment_line_from_move_line(payorder)

        self.cnab_state = 'added'
        self.last_change_reason = reason
        # Registra as Alterações na Fatura
        self._msg_cnab_payment_order_at_invoice(new_payorder, payorder)

    def _create_payment_order_change(self, **kwargs):
        self.ensure_one()
        # TODO:

    def _change_payment_mode(self, reason, new_payment_mode_id, **kwargs):
        moves_to_sync = self.filtered(
            lambda m: m.payment_mode_id != new_payment_mode_id)
        moves_to_sync._create_payment_order_change(
            new_payment_mode_id=new_payment_mode_id, **kwargs)
        moves_to_sync.write({
            'payment_mode_id': new_payment_mode_id.id,
            'last_change_reason': reason,
        })

    def _create_baixa(self, reason, **kwargs):
        moves_to_sync = self.filtered(lambda m: True)
        # TODO: Verificar restrições possíveis
        moves_to_sync._create_payment_order_change(baixa=True, **kwargs)
        moves_to_sync.write({
            'last_change_reason': reason,
            'payment_situation': 'baixa',  # FIXME: Podem ser múltiplos motivos
        })
