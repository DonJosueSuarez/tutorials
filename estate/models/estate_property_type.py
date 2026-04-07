from odoo import  models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'

    name = fields.Char(required=True)

    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id', string='Properties', readonly=True)

    _check_unique_type = models.Constraint('UNIQUE(name)', 'El tipo debe ser único')