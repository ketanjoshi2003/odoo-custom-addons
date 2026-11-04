from odoo import models, fields,api
from odoo.exceptions import ValidationError

class Sale(models.Model):
    _name = 'retail.sale'
    _description = 'Retail Sale'

    @api.constrains('quantity', 'price', 'discount')
    def _check_sale_values(self):
        for sale in self:
            if sale.quantity <= 0:
                raise ValidationError(
                    'Sale quantity must be greater than zero.'
                )

            if sale.price < 0:
                raise ValidationError(
                    'Sale price cannot be negative.'
                )

            if sale.discount < 0 or sale.discount > 100:
                raise ValidationError(
                    'Discount must be between 0 and 100 percent.'
                )
    name = fields.Char(
    string='Sale Number',
    required=True,
    copy=False,
    readonly=True,
    default='New',
    )

    product_id = fields.Many2one(
    'retail.product',
    string='Product',
    required=True,
    domain=[('active', '=', True)],
    ondelete='restrict',
    )

    customer_id = fields.Many2one(
    'res.partner',
    string='Customer',
    required=True,
    ondelete='restrict',
    )

    date = fields.Date(
    string='Date', required=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.sale_price
        else:
            self.price = 0.0
    
    discount = fields.Float(
    string='Discount (%)',
    default=0.0,
    )

    price = fields.Monetary(
    string='Price', required=True
    )
    quantity = fields.Integer(
    string='Quantity', required=True
    )

    total_amount = fields.Monetary(
    string='Total Amount',
    compute='_compute_total_amount',
    store=True,
    )

    currency_id = fields.Many2one(
    'res.currency',
    string='Currency',
    required=True,
    default=lambda self: self.env.company.currency_id,
    )

    state = fields.Selection(
    [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ],
    string='Status',
    default='draft',
    required=True,
    )


    def action_confirm(self):
        for sale in self:
            if sale.state != 'draft':
                raise ValidationError(
                    'Only draft sales can be confirmed.'
                )
            if sale.product_id.available_quantity < sale.quantity:
                raise ValidationError(
                    'Not enough stock available for this product.'
                )

            sale.state = 'confirmed'



    def action_cancel(self):
        for sale in self:
            if sale.state == 'cancelled':
                raise ValidationError(
                    'Sale is already cancelled.'
                )

            sale.state = 'cancelled'


    def action_reset_to_draft(self):
        for sale in self:
            if sale.state != 'cancelled':
                raise ValidationError(
                    'Only cancelled sales can return to draft.'
                )

            sale.state = 'draft'

    @api.depends('quantity', 'price', 'discount')
    def _compute_total_amount(self):
        for sale in self:
            gross_amount = sale.quantity * sale.price
            discount_amount = gross_amount * sale.discount / 100
            sale.total_amount = gross_amount - discount_amount
