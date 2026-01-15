from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Mapping of project_type to project template XML IDs
    PROJECT_TYPE_TEMPLATE_MAP = {
        'new_device': 'proxton.project_template_new_device',
        'modular_device': 'proxton.project_template_modular_device',
        'modify_device': 'proxton.project_template_modify_device',
        'automation': 'proxton.project_template_automation',
        'documentation': 'proxton.project_template_documentation',
        'service': 'proxton.project_template_service',
        'consultation': 'proxton.project_template_consultation',
        'spare_part': 'proxton.project_template_spare_part',
    }

    def _get_project_template_from_lead(self):
        """Get the project template based on linked CRM lead's project_type."""
        self.ensure_one()
        lead = self.order_id.opportunity_id
        if not lead or not lead.project_type:
            return self.env['project.project']

        template_xmlid = self.PROJECT_TYPE_TEMPLATE_MAP.get(lead.project_type)
        if not template_xmlid:
            return self.env['project.project']

        return self.env.ref(template_xmlid, raise_if_not_found=False) or self.env['project.project']

    def _timesheet_create_project(self):
        """Override to use project template based on CRM lead's project_type.

        Priority: CRM lead's project_type template > product's template > no template
        """
        self.ensure_one()

        # Get template from CRM lead's project_type (takes priority)
        project_template = self._get_project_template_from_lead()

        if project_template and project_template.is_template:
            # Create project from CRM lead's project_type template
            values = self._timesheet_create_project_prepare_values()
            values['name'] = "%s - %s" % (values['name'], project_template.name)

            project = project_template.action_create_from_template(values)
            project.tasks.write({
                'sale_line_id': self.id,
                'partner_id': self.order_id.partner_id.id,
            })
            project.tasks.filtered('parent_id').write({
                'sale_line_id': self.id,
                'sale_order_id': self.order_id.id,
            })

            # Avoid new tasks to go to 'Undefined Stage'
            if not project.type_ids:
                project.type_ids = self.env['project.task.type'].create([{
                    'name': name,
                    'fold': fold,
                    'sequence': sequence,
                } for name, fold, sequence in [
                    (self.env._('To Do'), False, 5),
                    (self.env._('In Progress'), False, 10),
                    (self.env._('Done'), False, 15),
                    (self.env._('Cancelled'), True, 20),
                ]])

            self.write({'project_id': project.id})
            project.reinvoiced_sale_order_id = self.order_id
            return project

        # Fall back to standard behavior (uses product's template if set)
        return super()._timesheet_create_project()
