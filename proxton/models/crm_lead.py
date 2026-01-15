from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_type = fields.Selection([
        ('new_device', 'Vývoj nového zariadenia'),
        ('modular_device', 'Výroba modulárneho zariadenia'),
        ('modify_device', 'Úprava existujúceho zariadenia'),
        ('automation', 'Automatizácia procesu'),
        ('documentation', 'Dokumentácia'),
        ('service', 'Servis'),
        ('consultation', 'Konzultácia'),
        ('spare_part', 'Náhradný diel'),
    ], string='Typ projektu')
    
    project_difficulty = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Štruktúra projektu')
    
    development_type = fields.Selection([
        ('new', 'New'),
        ('variant', 'Variant'),
        ('repeat', 'Repeat'),
    ], string='Typ vývoja')

    specification_level = fields.Selection([
        ('precise', 'Presne špecifikované'),
        ('partial', 'Čiastočne špecifikované'),
        ('open', 'Otvorené riešenie'),
    ], string='Miera špecifikácie')

    environment_ids = fields.Many2many(
        'proxton.environment.tag',
        string='Prostredie',
    )
    industry_ids = fields.Many2many(
        'proxton.industry.tag',
        string='Odvetvie',
    )

    mechanics_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_mechanics_rel',
        'lead_id', 'item_id',
        string='Mechanika',
        domain=[('category', '=', 'mechanics')],
    )
    electrical_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_electrical_rel',
        'lead_id', 'item_id',
        string='Elektrika',
        domain=[('category', '=', 'electrical')],
    )
    automation_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_automation_rel',
        'lead_id', 'item_id',
        string='Automatizácia',
        domain=[('category', '=', 'automation')],
    )
    quality_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_quality_rel',
        'lead_id', 'item_id',
        string='Kvalita',
        domain=[('category', '=', 'quality')],
    )
    energy_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_energy_rel',
        'lead_id', 'item_id',
        string='Energie a médiá',
        domain=[('category', '=', 'energy')],
    )
    documentation_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_documentation_rel',
        'lead_id', 'item_id',
        string='Dokumentácia',
        domain=[('category', '=', 'documentation')],
    )
    delivery_scope_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_delivery_scope_rel',
        'lead_id', 'item_id',
        string='Rozsah dodávky',
        domain=[('category', '=', 'delivery_scope')],
    )
    
    time_and_process_constraints = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_time_and_process_constraints_rel',
        'lead_id', 'item_id',
        string='Časové a procesné obmedzenia',
        domain=[('category', '=', 'time_and_process_constraints')],
    )
    has_fixed_deadline = fields.Boolean(
        string='Has Fixed Deadline',
        compute='_compute_has_fixed_deadline',
    )
    required_delivery_date = fields.Date(string='Požadovaný termín')

    risk_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_risk_rel',
        'lead_id', 'item_id',
        string='Riziká',
        domain=[('category', '=', 'risks')],
    )
    attachment_checklist_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_attachment_checklist_rel',
        'lead_id', 'item_id',
        string='Prílohy',
        domain=[('category', '=', 'attachments')],
    )

    @api.depends('time_and_process_constraints')
    def _compute_has_fixed_deadline(self):
        for lead in self:
            lead.has_fixed_deadline = any(
                item.name == 'Pevný deadline'
                for item in lead.time_and_process_constraints
            )

    expected_start_date = fields.Date(
        string='Očakávaný termín začiatku realizácie',
        help='Expected start date of implementation'
    )
    expected_end_date = fields.Date(
        string='Očakávaný termín konca realizácie',
        help='Expected end date of implementation'
    )
