from odoo import fields, models

class StockMove(models.Model):
    _name = 'retail.stock.move'
    _description = 'Stock movements'
    _order = 'date desc, id desc'

    product_id = fields.Many2one('retail.product',required=True,ondelete='restrict', index=True)
    quantity = fields.Integer(string='Quantity (signed)',required=True)
    move_type = fields.Selection([
        ('in', 'Stock In'),
        ('out','Sale'),
        ('return','Sale Cancelled'),
    ], required=True)
    date = fields.Datetime(default=fields.Datetime.now,required=True)
    sale_id = fields.Many2one('retail.sale',ondelete='set null')
    stock_id = fields.Many2one('retail.stock',ondelete='set null')
    reference = fields.Char(string='Reference',help='Sale number / Stock record name')