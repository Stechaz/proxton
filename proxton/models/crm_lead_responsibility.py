from odoo import fields, models


class CrmLeadResponsibility(models.Model):
    _name = 'crm.lead.responsibility'
    _description = 'CRM Lead Responsibility'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead',
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
