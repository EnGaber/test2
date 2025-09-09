from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError

from odoo.odoo.api import depends


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order','portal.mixin','mail.thread', 'mail.activity.mixin','utm.mixin']  # Enables chatter


    note_des = fields.Char(string="Description Note", required=False)

    order_id = fields.Char(string='Order ID ', required=True, copy=False, readonly=True,
                           default=lambda self: _('New'))

    receipt_count = fields.Integer(string="Receipts", compute="_compute_receipt_count",store=True)


    #Function to compute number of orders within smart button
    @api.depends('order_line.move_ids')  # Adjust this dependency as needed
    def _compute_receipt_count(self):
        for order in self:
            order.receipt_count = self.env['stock.picking'].search_count([
                ('origin', '=', order.name),
                ('picking_type_id.code', '=', 'incoming')  # Only incoming receipts
            ])

    # def action_view_receipts(self):
    #     self.ensure_one()
    #     # Fetch the default action for pickings
    #     action = self.env.ref('stock.action_picking_tree_all').read()[0]
    #
    #     # Search for related pickings (confirmed ones with 'incoming' type)
    #     pickings = self.env['stock.picking'].search([
    #         ('origin', '=', self.name),  # Match the origin with the purchase order name
    #         ('state', 'in', ['confirmed', 'assigned', 'done']),  # Include only relevant states
    #         ('picking_type_id.code', '=', 'incoming')  # Incoming pickings only
    #     ])
    #
    #     if len(pickings) == 1:
    #         # If only one picking exists, redirect to its form view
    #         action.update({
    #             'view_mode': 'form',
    #             'res_id': pickings.id,  # Set the picking record ID
    #         })
    #     else:
    #         # If multiple pickings exist, show them in the tree view
    #         action.update({
    #             'domain': [('id', 'in', pickings.ids)],  # Restrict to the fetched pickings
    #             'view_mode': 'tree,form',  # Allow switching between tree and form views
    #         })
    #
    #     return action

    def action_view_receipts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
             'name': 'Receipts',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name), ('picking_type_id.code', '=', 'incoming')],
            'context': dict(self._context),
        }



    # Method to update field within purchase.order
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        print("prepare_picking Vals",res)
        res.update({'note_des': self.note_des})
        return  res



    # Create constrains field
    @api.constrains('date_planned')
    def _check_date_order(self):
        # Get today's date
        today= date.today()

        for order in self:
            # Check if the order's date_order is today
            if order.date_planned.date() == today:
                # Raise a validation error or show a notification
                raise ValidationError("The Receipt Date cannot be today's date. Please select another date.")



    # # SQL constraint to ensure the date_planned_date is not today's date
    # _sql_constraints = [
    #     ('check_date_planned_not_today', "CHECK(date_planned.date() != CURRENT_DATE)",
    #      "The Receipt Date cannot be today's date. Please select another date."),
    # ]


# Method to update fields within purchase.order and purchase.order.line
# def button_confirm(self):
    #     res = super(PurchaseOrder, self).button_confirm()
    #
    #     # Iterate through all purchase orders and their picking records
    #     for order in self:
    #         for picking in order.picking_ids:
    #             picking.note_des = order.note_des    # Copy value from purchase order to stock picking
    #             for move in picking.move_lines:  # move_lines refers to stock moves
    #                 # Ensure purchase.order.line field Desc_Notes is correctly passed
    #                 for line in order.order_line:
    #                     if move.purchase_line_id == line:
    #                         move.Desc_Notes = line.Desc_Notes  # Copy value from purchase order line to stock move
    #     return res


    # Create Sequence Field
    @api.model
    def create(self, vals):
        if vals.get('order_id', _('New')) == _('New'):
            # Define the next sequence as "P" followed by zero-padded digits
            last_sequence = self.env['ir.sequence'].next_by_code('purchase.order.sequence') or 'P00001'
            vals['order_id'] = last_sequence
        return super(PurchaseOrder, self).create(vals)



    # Method to print excel sheet within purchase.order
    def export_selected_orders(self):
        order_ids = ','.join(map(str, self.ids))
        return {
            'type': 'ir.actions.act_url',
            'url': f'/purchase_order/export_excel?order_ids={order_ids}',
            'target': 'new',
        }






class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    note_desc = fields.Char(string="Description Note")


    # Method to update field within purchase.order.line and stock.move
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        print("======== line Vals ", res)
        for re in res:
            print("========= Line Vals ", re)
            re['note_desc'] = self.note_desc
        return res






