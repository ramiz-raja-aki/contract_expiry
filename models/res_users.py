from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    id_expire_notification = fields.Boolean(
        string='Contract Expiry Notification',
        default=False,
        help='If enabled, this user will receive an activity notification '
             '15 days before any employee contract expires.',
    )
