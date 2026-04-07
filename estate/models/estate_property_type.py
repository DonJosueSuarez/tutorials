from odoo import  models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'

    name = fields.Char(required=True)

    _check_unique_type = models.Constraint('UNIQUE(name)', 'El tipo debe ser único')