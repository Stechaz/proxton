from odoo import fields, models


class SaleOrderResponsibility(models.Model):
    _name = 'sale.order.responsibility'
    _description = 'Sale Order Responsibility'

    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        required=True,
        ondelete='cascade',
    )
    role_id = fields.Many2one(
        'project.role',
        string='Rola',
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Zodpovedná osoba',
    )
