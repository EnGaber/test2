from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _description = 'Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Request Name', required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', required=True, default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.today)
    end_date = fields.Date(string='End Date')
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)
    orderlines = fields.One2many('purchase.request.line', 'purchase_request_id', string='Order Lines')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    note = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Be Approved'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', readonly=True, tracking=True)

    @api.depends('orderlines.total')
    def _compute_total_price(self):
        for request in self:
            request.total_price = sum(line.total for line in request.orderlines)

    def action_submit_for_approval(self):
        self.write({'state': 'to_approve'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    #def action_approve(self):
      #  self.write({'status': 'approved'})
      #  self.send_approval_email()

    def action_approve(self):
        self.write({'state': 'approved'})
        self.send_approval_email()


    def send_approval_email(self):
        users = self.env["res.users"].search([])
        purchase_manager_users = [user for user in users if user.has_group('Task_purchase.group_purchase_request_manager')]
        emails = [user.login for user in purchase_manager_users if user.login]
        ctx = {}
        if emails:
            ctx['email_to'] = ','.join(emails)
            ctx['email_from'] = self.env.user.company_id.email
            ctx['send_email'] = True
            template = self.env.ref('Task_purchase.email_template_purchase_request_approved')
            template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

       # template = self.env.ref('Task_purchase.email_template_purchase_request_approved')
       # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    #def send_approval_email(self):
     #   group_purchase_manager = self.env.ref('Task_purchase.group_purchase_request_manager')
       # users = group_purchase_manager.users
      #  template = self.env.ref('Task_purchase.email_template_purchase_request_approved')
     #   for user in users:
     #       template.with_context(user=user).send_mail(self.id, force_send=True)

        #self.write({'status': 'approved'})
        # Send email to purchase manager group
        #group_purchase_manager = self.env.ref('purchase.group_purchase_manager')
        #for user in group_purchase_manager.users:
           # template = self.env.ref('purchase_request_module.email_template_purchase_request_approved')
           # self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Purchase Request',
            'res_model': 'purchase.request.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_request_id': self.id},
        }

