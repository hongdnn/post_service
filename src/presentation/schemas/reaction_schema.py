from marshmallow import Schema, fields, ValidationError, validates


class UpdateReactionSchema(Schema):
    post_id = fields.String(required=True)

    @validates('post_id')
    def validate_post_id(self, value):
        if not isinstance(value, str):
            raise ValidationError("Invalid type for post_id. Expected a string.")