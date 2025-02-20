from marshmallow import Schema, fields, ValidationError, validates


class CreateCommentSchema(Schema):
    post_id = fields.String(required=True)
    content = fields.String(required=True)
    replied_comment_id = fields.String(required=False, allow_none=True)

    @validates('content')
    def validate_content(self, value):
        if not isinstance(value, str):
            raise ValidationError("Invalid type for content. Expected a string.")

    @validates('post_id')
    def validate_post_id(self, value):
        if not isinstance(value, str):
            raise ValidationError("Invalid type for post_id. Expected a string.")


class FetchCommentsSchema(Schema):
    post_id = fields.String(required=True)
    page = fields.Int(required=True, validate=lambda x: x > 0)
    size = fields.Int(required=True, validate=lambda x: x > 0)

    @validates("post_id")
    def validate_post_id(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("post_id must be a non-empty string.")