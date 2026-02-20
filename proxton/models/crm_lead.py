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
    ], string='Typ projektu', tracking=True)

    project_difficulty = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Štruktúra projektu', tracking=True)

    development_type = fields.Selection([
        ('new', 'New'),
        ('variant', 'Variant'),
        ('repeat', 'Repeat'),
    ], string='Typ vývoja', tracking=True)

    specification_level = fields.Selection([
        ('precise', 'Presne špecifikované'),
        ('partial', 'Čiastočne špecifikované'),
        ('open', 'Otvorené riešenie'),
    ], string='Miera špecifikácie', tracking=True)

    environment_ids = fields.Many2many(
        'proxton.environment.tag',
        string='Prostredie',
        tracking=True,
    )
    industry_ids = fields.Many2many(
        'proxton.industry.tag',
        string='Odvetvie',
        tracking=True,
    )

    mechanics_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_mechanics_rel',
        'lead_id', 'item_id',
        string='Mechanika',
        domain=[('category', '=', 'mechanics')],
        tracking=True,
    )
    electrical_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_electrical_rel',
        'lead_id', 'item_id',
        string='Elektrika',
        domain=[('category', '=', 'electrical')],
        tracking=True,
    )
    automation_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_automation_rel',
        'lead_id', 'item_id',
        string='Automatizácia',
        domain=[('category', '=', 'automation')],
        tracking=True,
    )
    quality_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_quality_rel',
        'lead_id', 'item_id',
        string='Kvalita',
        domain=[('category', '=', 'quality')],
        tracking=True,
    )
    energy_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_energy_rel',
        'lead_id', 'item_id',
        string='Energie a médiá',
        domain=[('category', '=', 'energy')],
        tracking=True,
    )
    documentation_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_documentation_rel',
        'lead_id', 'item_id',
        string='Dokumentácia',
        domain=[('category', '=', 'documentation')],
        tracking=True,
    )
    delivery_scope_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_delivery_scope_rel',
        'lead_id', 'item_id',
        string='Rozsah dodávky',
        domain=[('category', '=', 'delivery_scope')],
        tracking=True,
    )

    time_and_process_constraints = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_time_and_process_constraints_rel',
        'lead_id', 'item_id',
        string='Časové a procesné obmedzenia',
        domain=[('category', '=', 'time_and_process_constraints')],
        tracking=True,
    )
    has_fixed_deadline = fields.Boolean(
        string='Has Fixed Deadline',
        compute='_compute_has_fixed_deadline',
    )
    required_delivery_date = fields.Date(
        string='Požadovaný termín',
        tracking=True,
    )

    risk_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_risk_rel',
        'lead_id', 'item_id',
        string='Riziká',
        domain=[('category', '=', 'risks')],
        tracking=True,
    )
    attachment_checklist_ids = fields.Many2many(
        'proxton.checklist.item',
        'crm_lead_attachment_checklist_rel',
        'lead_id', 'item_id',
        string='Prílohy',
        domain=[('category', '=', 'attachments')],
        tracking=True,
    )

    responsibility_ids = fields.One2many(
        'crm.lead.responsibility',
        'lead_id',
        string='Zodpovednosti',
        default=lambda self: self._default_responsibility_ids(),
    )

    @api.model
    def _default_responsibility_ids(self):
        """Prepopulate responsibility_ids with all project roles."""
        roles = self.env['project.role'].search([])
        return [(0, 0, {'role_id': role.id}) for role in roles]

    @api.depends('time_and_process_constraints')
    def _compute_has_fixed_deadline(self):
        for lead in self:
            lead.has_fixed_deadline = any(
                item.name == 'Pevný deadline'
                for item in lead.time_and_process_constraints
            )

    expected_start_date = fields.Date(
        string='Očakávaný termín začiatku realizácie',
        help='Expected start date of implementation',
        tracking=True,
    )
    expected_end_date = fields.Date(
        string='Očakávaný termín konca realizácie',
        help='Expected end date of implementation',
        tracking=True,
    )

    def _prepare_opportunity_quotation_context(self):
        """Extend quotation context with checklist fields from lead."""
        context = super()._prepare_opportunity_quotation_context()
        # Copy checklist fields
        context.update({
            'default_mechanics_ids': [(6, 0, self.mechanics_ids.ids)],
            'default_electrical_ids': [(6, 0, self.electrical_ids.ids)],
            'default_automation_ids': [(6, 0, self.automation_ids.ids)],
            'default_quality_ids': [(6, 0, self.quality_ids.ids)],
            'default_energy_ids': [(6, 0, self.energy_ids.ids)],
            'default_documentation_ids': [(6, 0, self.documentation_ids.ids)],
            'default_delivery_scope_ids': [(6, 0, self.delivery_scope_ids.ids)],
            'default_risk_ids': [(6, 0, self.risk_ids.ids)],
        })
        # Copy responsibility data (hard copy)
        responsibility_vals = [
            (0, 0, {'role_id': resp.role_id.id, 'user_id': resp.user_id.id})
            for resp in self.responsibility_ids
        ]
        context['default_responsibility_ids'] = responsibility_vals
        return context
