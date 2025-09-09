from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description', related='product_id.name')
    quantity = fields.Float(string='Quantity', default=1.0)
    cost_price = fields.Float(string='Cost Price', related='product_id.standard_price', readonly=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)


    @api.depends('quantity', 'cost_price')
    def _compute_total(self):
        for line in self:
            line.total = line.quantity * line.cost_price