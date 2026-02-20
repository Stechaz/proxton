from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    opportunity_description = fields.Html(
        related='opportunity_id.description',
        string='Stručný popis zákazky',
        readonly=False,
    )

    project_type = fields.Selection(
        related='opportunity_id.project_type',
        string='Typ projektu',
        readonly=False,
    )

    project_difficulty = fields.Selection(
        related='opportunity_id.project_difficulty',
        string='Zložitosť',
        readonly=False,
    )

    development_type = fields.Selection(
        related='opportunity_id.development_type',
        string='Typ vývoja',
        readonly=False,
    )

    contractual_delivery_date = fields.Date(
        string='Zmluvný termín dodania',
        tracking=True,
    )

    is_deadline_fixed = fields.Boolean(
        string='Termín pevný?',
        tracking=True,
    )

    # Order comparison fields (CP vs PO)
    total_price_comparison = fields.Monetary(
        string='Cena celkom',
        currency_field='currency_id',
        tracking=True,
    )
    items_check_cp_po = fields.Boolean(
        string='Kontrola položiek v CP vs PO',
        tracking=True,
    )
    pricing_model = fields.Selection(
        selection=[
            ('fixed', 'Fixed price'),
            ('tm', 'T&M'),
        ],
        string='Cenový model',
        tracking=True,
    )
    invoicing_model = fields.Selection(
        selection=[
            ('milestones', 'Milestones'),
            ('delivery', 'Delivery'),
            ('periodic', 'Periodic'),
        ],
        string='Fakturačný model',
        tracking=True,
    )
    advance_invoicing = fields.Text(
        string='Zálohová fakturácia',
        tracking=True,
    )

    # Compliance / Legal fields
    standards_certification = fields.Text(
        string='Normy / certifikácia (CE, ISO, …)',
        tracking=True,
    )
    safety_requirements = fields.Text(
        string='Bezpečnostné požiadavky',
        tracking=True,
    )
    nda_ip_restrictions = fields.Text(
        string='NDA / IP obmedzenia',
        tracking=True,
    )
    penalties_sla = fields.Text(
        string='Penále / SLA',
        tracking=True,
    )

    # Category approval fields
    mechanics_approved = fields.Boolean(string='Mechanika schválená', tracking=True)
    electrical_approved = fields.Boolean(string='Elektrika schválená', tracking=True)
    automation_approved = fields.Boolean(string='Automatizácia schválená', tracking=True)
    quality_approved = fields.Boolean(string='Kvalita schválená', tracking=True)
    energy_approved = fields.Boolean(string='Energie a médiá schválené', tracking=True)
    documentation_approved = fields.Boolean(string='Dokumentácia schválená', tracking=True)
    delivery_scope_approved = fields.Boolean(string='Rozsah dodávky schválený', tracking=True)
    risks_approved = fields.Boolean(string='Riziká schválené', tracking=True)

    # Checklist fields - copied from crm.lead
    mechanics_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_mechanics_rel',
        'order_id', 'item_id',
        string='Mechanika',
        domain=[('category', '=', 'mechanics')],
        tracking=True,
    )

    electrical_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_electrical_rel',
        'order_id', 'item_id',
        string='Elektrika',
        domain=[('category', '=', 'electrical')],
        tracking=True,
    )

    automation_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_automation_rel',
        'order_id', 'item_id',
        string='Automatizácia',
        domain=[('category', '=', 'automation')],
        tracking=True,
    )

    quality_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_quality_rel',
        'order_id', 'item_id',
        string='Kvalita',
        domain=[('category', '=', 'quality')],
        tracking=True,
    )

    energy_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_energy_rel',
        'order_id', 'item_id',
        string='Energie a médiá',
        domain=[('category', '=', 'energy')],
        tracking=True,
    )

    documentation_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_documentation_rel',
        'order_id', 'item_id',
        string='Dokumentácia',
        domain=[('category', '=', 'documentation')],
        tracking=True,
    )

    delivery_scope_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_delivery_scope_rel',
        'order_id', 'item_id',
        string='Rozsah dodávky',
        domain=[('category', '=', 'delivery_scope')],
        tracking=True,
    )

    risk_ids = fields.Many2many(
        'proxton.checklist.item',
        'sale_order_risk_rel',
        'order_id', 'item_id',
        string='Riziká',
        domain=[('category', '=', 'risks')],
        tracking=True,
    )

    # Responsibility fields - hard copy from crm.lead
    responsibility_ids = fields.One2many(
        'sale.order.responsibility',
        'order_id',
        string='Zodpovedné osoby',
    )

    def get_approval_source_info(self, field_name):
        """Get approval source info for any related field from opportunity.

        This is a universal method that returns the source model/record info
        for proper approval tracking of fields related to the opportunity.

        Args:
            field_name: The field name on crm.lead to track approval for

        Returns:
            dict with source_model, source_res_id, and source_field
        """
        self.ensure_one()
        if not self.opportunity_id:
            return {
                'source_model': False,
                'source_res_id': False,
                'source_field': False,
            }
        return {
            'source_model': 'crm.lead',
            'source_res_id': self.opportunity_id.id,
            'source_field': field_name,
        }
