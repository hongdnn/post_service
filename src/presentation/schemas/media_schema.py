from marshmallow import Schema, fields, validates, ValidationError
from src.data.models.media_model import MediaType



class CreateMediaSchema(Schema):
    media_type = fields.Integer(required=True)
    media_url = fields.String(required=True)
    file_size = fields.Float(required=True)
    file_name = fields.String(required=True)
    mime_type = fields.String(required=True)
    created_date = fields.DateTime(allow_none=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)
    video_duration = fields.Float(allow_none=True)
    video_frame_rate = fields.Float(allow_none=True)

    @validates('media_type')
    def validate_media_type(self, value):
        if value not in [MediaType.IMAGE.value, MediaType.VIDEO.value]:
            raise ValidationError("Invalid media_type. Must be 0 (IMAGE) or 1 (VIDEO).")

    @validates('media_url')
    def validate_media_url(self, value):
        if not isinstance(value, str):
            raise ValidationError("Invalid type for media_url. Expected a string.")

    @validates('file_size')
    def validate_file_size(self, value):
        if not isinstance(value, (float, int)):
            raise ValidationError("Invalid type for file_size. Expected a number.")

    @validates('video_duration')
    def validate_video_duration(self, value):
        if value is not None and not isinstance(value, (float, int)):
            raise ValidationError("Invalid type for video_duration. Expected a number or null.")

    @validates('video_frame_rate')
    def validate_video_frame_rate(self, value):
        if value is not None and not isinstance(value, (float, int)):
            raise ValidationError("Invalid type for video_frame_rate. Expected a number or null.")
