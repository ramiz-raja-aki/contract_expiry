from odoo import models
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _get_expiry_notification_recipients(self):
        return self.env['res.users'].search([
            ('id_expire_notification', '=', True),
            ('active', '=', True),
        ])

    def _should_notify_for_contract(self, contract):
        if not contract.date_end or contract.state in ['cancel']:
            return False

        today = date.today()
        end_date = today + timedelta(days=15)
        return contract.date_end <= end_date and contract.date_end >= today

    def _create_expiry_notification_for_contract(self, contract):
        if not self._should_notify_for_contract(contract):
            return False

        notify_users = self._get_expiry_notification_recipients()
        if not notify_users:
            _logger.info(
                'Contract Expiry Notification: no users opted-in for notifications.'
            )
            return False

        employee_name = contract.employee_id.name or 'Unknown Employee'
        summary = 'Contract Expiring in 15 Days: %s' % employee_name
        note = (
            'The contract <b>%s</b> for employee <b>%s</b> is expiring on <b>%s</b>. '
            'Please take the necessary action.'
        ) % (contract.name, employee_name, contract.date_end)

        for user in notify_users:
            existing = self.env['mail.activity'].search([
                ('res_model', '=', 'hr.contract'),
                ('res_id', '=', contract.id),
                ('user_id', '=', user.id),
                ('summary', '=', summary),
            ], limit=1)

            if not existing:
                contract.with_context(mail_activity_quick_update=True).activity_schedule(
                    'mail.mail_activity_data_todo',
                    contract.date_end,
                    summary,
                    note=note,
                    user_id=user.id,
                )
                _logger.info(
                    'Contract Expiry Notification: activity created for user %s '
                    'on contract %s (employee: %s, expiry: %s).',
                    user.name, contract.name, employee_name, contract.date_end,
                )
            else:
                _logger.info(
                    'Contract Expiry Notification: activity already exists for user %s '
                    'on contract %s.',
                    user.name, contract.name,
                )
        return True

    def _send_contract_expiry_notifications(self):
        """
        Scheduled action: runs daily and creates activity notifications
        for all users with 'id_expire_notification' enabled, for every
        active contract expiring exactly 15 days from today.
        """
        today = date.today()
        end_date = today + timedelta(days=15)
        expiring_contracts = self.search([
            ('date_end', '>=', today),
            ('date_end', '<=', end_date),
            ('state', 'not in', ['cancel']),
        ])

        if not expiring_contracts:
            _logger.info(
                'Contract Expiry Notification: no contracts expiring within the next 15 days from %s to %s.',
                today,
                end_date,
            )
            return

        for contract in expiring_contracts:
            self._create_expiry_notification_for_contract(contract)

    @staticmethod
    def _get_expiry_warning_date(contract):
        return contract.date_end

    def create(self, vals_list):
        contracts = super().create(vals_list)
        for contract in contracts:
            self._create_expiry_notification_for_contract(contract)
        return contracts

    def write(self, vals):
        result = super().write(vals)
        if 'date_end' in vals or 'state' in vals or 'employee_id' in vals:
            for contract in self:
                self._create_expiry_notification_for_contract(contract)
        return result
