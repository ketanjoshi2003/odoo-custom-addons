from odoo import fields, models


class RetailSaleTag(models.Model):
    _name = 'retail.sale.tag'
    _description = 'Retail Sale Tag'

    name = fields.Char(
        string='Tag Name',
        required=True,
    )

    color = fields.Integer(
        string='Color',
    )

    sale_ids = fields.Many2many(
        'retail.sale',
        'retail_sale_tag_rel',
        'tag_id',
        'sale_id',
        string='Sales',
    )