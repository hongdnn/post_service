from marshmallow import Schema, fields, validates, ValidationError, validates_schema

from src.presentation.schemas.media_schema import CreateMediaSchema


class CreatePostSchema(Schema):
    content = fields.String(required=True)
    location = fields.String(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    medias = fields.List(fields.Nested(CreateMediaSchema(), required=False))

    @validates_schema
    def validate_location_fields(self, data, **kwargs):
        """Ensure all location-related fields are provided together."""
        location_fields = [data.get('location'), data.get('latitude'), data.get('longitude')]
        if any(field for field in location_fields) and not all(field for field in location_fields):
            raise ValidationError("Missing some location information.")
