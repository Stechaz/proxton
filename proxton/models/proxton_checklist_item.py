from odoo import fields, models


class ProxtonChecklistItem(models.Model):
    _name = 'proxton.checklist.item'
    _description = 'Proxton Checklist Item'

    name = fields.Char(string='Name', required=True, translate=True)
    category = fields.Selection([
        ('mechanics', 'Mechanika'),
        ('electrical', 'Elektrika'),
        ('automation', 'Automatizácia'),
        ('quality', 'Kvalita'),
        ('energy', 'Energie a médiá'),
        ('documentation', 'Dokumentácia'),
        ('delivery_scope', 'Rozsah dodávky'),
        ('time_and_process_constraints', 'Časové a procesné obmedzenia'),
        ('risks', 'Riziká'),
        ('attachments', 'Prílohy'),
    ], string='Category', required=True)
    active = fields.Boolean(default=True)
