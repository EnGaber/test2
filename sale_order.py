from odoo import models, fields, api



class SalesOrder(models.Model):
    _inherit = 'sale.order'

    note_des = fields.Char(string="Description Note")

    # products_notes_id = fields.Many2one('sale.order.line')



    def action_confirm(self):
        res = super(SalesOrder, self).action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.note_des = order.note_des
        #         for move in picking.move_lines:  # move_lines refers to stock moves
        #             # Ensure purchase.order.line field Desc_Notes is correctly passed
        #             for line in order.order_line:
        #                 if move.sale_line_id == line:
        #                     move.note_desc = line.note_desc  # Copy value from purchase order l
        # res.update({'note_des': self.note_des})
        print("Test picking res", res)
        return res

  

    # def export_selected_orders(self):
    #     order_ids = ','.join(map(str, self.ids))
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/sale_order/export_excel?order_ids={order_ids}',
    #         'target': 'new',
    #     }





class SalesOrderLine(models.Model):
    _inherit ='sale.order.line'

    # products_notes = fields.Char(string="Description Note", required=True)

    note_desc = fields.Char(string="Desc Note")



    # def _prepare_procurement_values(self, group_id=False):
    #     res = super(SalesOrderLine, self)._prepare_procurement_values(group_id)
    #     # I am assuming field name in both sale.order.line and in stock.move are same and called 'YourField'
    #     res.update({'note_desc': self.note_desc})
    #     print("test ",res)
    #     return res




    # def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
    #     # Call the original method to get the standard move values
    #     vals = super(SalesOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
    #
    #     # Add the custom field's value to the stock move values dictionary
    #     vals.update({
    #         'note_desc': self.note_desc,  # Transfer the custom field value
    #     })
    #     return vals


