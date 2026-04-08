from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'tag'
    _description = 'Estate Property Tag'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()

    _check_unique_tag = models.Constraint('UNIQUE(name)', 'El nombre de la etiqueta debe ser único')