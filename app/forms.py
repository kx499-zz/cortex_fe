from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectMultipleField, FileField
from wtforms.validators import DataRequired, Optional, Length
from config import VALIDATE
import re


class IocForm(Form):
    value = StringField('IOC', validators=[DataRequired()])
    analyzers = SelectMultipleField('Source', validators=[DataRequired()])
    message = StringField('Message',
                          validators = [Optional(), Length(max = 100)],
                          filters = [lambda x: x or None])
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        rex = VALIDATE.get(self.data_type)
        field = self.value
        if rex and not re.search(rex, field.data):
            field.errors.append("Value doesn't match data_type")
            return False
        return True


class FileForm(Form):
    value = FileField('Upload File', validators=[DataRequired()])
    analyzers = SelectMultipleField('Source', validators=[DataRequired()])
    message = StringField('Message',
                          validators = [Optional(), Length(max = 100)],
                          filters = [lambda x: x or None])