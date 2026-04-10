from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', help='Úselo para ordenar por tipo')

    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id', string='Properties', readonly=True)

    offer_count = fields.Integer(compute='_compute_offer_count')

    _check_unique_type = models.Constraint('UNIQUE(name)', 'El tipo debe ser único')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)