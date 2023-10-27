from io import BytesIO

import arabic_reshaper
from PIL import Image, ImageFont, ImageDraw
from bidi.algorithm import get_display
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError, PermissionDenied

from errors.error_codes import serialize_error
from apps.fsm.models import Font, CertificateTemplate
from apps.fsm.permissions import is_form_modifier


class FontSerializer(serializers.ModelSerializer):

    class Meta:
        model = Font
        fields = ['id', 'font_file', 'name']
        read_only_fields = ['id', 'name']

    def to_representation(self, instance):
        representation = super(
            FontSerializer, self).to_representation(instance)
        font_file = representation['font_file']
        if font_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['font_file'] = domain + font_file
        return representation


class CertificateTemplateSerializer(serializers.ModelSerializer):
    font = serializers.PrimaryKeyRelatedField(
        queryset=Font.objects.all(), allow_null=False, required=True)

    class Meta:
        model = CertificateTemplate
        fields = '__all__'
        read_only_fields = ['id']

    def validate(self, attrs):
        registration_form = attrs.get('registration_form', None)
        template_file = attrs.get('template_file', None)
        if 'image' in template_file.content_type:
            width, height = Image.open(template_file.file).size
        # elif 'pdf' in template_file.content_type:
        #     pdf_file = Pdf.open(template_file.file)
        #     if len(pdf_file.pages) == 1:
        #         width, height = tuple(pdf_file.pages.p(1).mediabox.as_list()[2:])
        #     else:
        #         raise ParseError(serialize_error('4092'))
        else:
            raise ValidationError(serialize_error('4093'))
        name_X_percentage = attrs.get('name_X_percentage', None)
        name_Y_percentage = attrs.get('name_Y_percentage', None)
        if name_X_percentage > width or name_Y_percentage > height:
            raise ParseError(serialize_error('4094'))
        user = self.context.get('user', None)
        if not is_form_modifier(registration_form, user):
            raise PermissionDenied(serialize_error('4091'))
        elif not registration_form.has_certificate:
            raise ParseError(serialize_error('4097'))
        return super(CertificateTemplateSerializer, self).validate(attrs)

    def save(self, **kwargs):
        instance = super(CertificateTemplateSerializer, self).save(**kwargs)
        registration_form = instance.registration_form
        registration_form.certificates_ready = True
        registration_form.save()
        return instance

    def to_representation(self, instance):
        representation = super(CertificateTemplateSerializer,
                               self).to_representation(instance)
        template_file = representation['template_file']
        if template_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['template_file'] = domain + template_file
        representation['font'] = instance.font.name if instance.font and instance.font.name else None
        return representation


def create_certificate(certificate_template, name: str):
    template_file_extension = _get_file_extension(
        certificate_template.template_file.name)
    if template_file_extension in ['png', 'jpg', 'jpeg', 'gif']:
        if certificate_template.font:
            font_file = certificate_template.font.font_file.file
        else:
            raise ParseError(serialize_error('4096'))

        template_file = certificate_template.template_file
        return _create_certificate(name, certificate_template.name_X_percentage, certificate_template.name_Y_percentage,
                                   font_file, certificate_template.font_size, template_file.file, f'{template_file.name}-{name}.{template_file_extension}')

    elif template_file_extension == 'pdf':
        raise ParseError(serialize_error('4099'))
    else:
        raise ParseError(serialize_error('4093'))


def _create_certificate(name, name_X_percentage, name_Y_percentage, font_file, font_size, template_file, certificate_file_name):
    font = ImageFont.truetype(font_file, font_size)
    image = Image.open(template_file)

    name_X = _get_text_X_position_on_image(
        name, name_X_percentage, image, font)
    name_Y = _get_text_Y_position_on_image(
        name, name_Y_percentage, image, font)

    draw = ImageDraw.Draw(image)
    draw.text((name_X, name_Y), name, '#000000', direction='rtl', font=font)

    return _save_image_to_file(image, certificate_file_name)


def _get_text_X_position_on_image(text: str, text_X_position_percentage: float, image, font):
    image_width, _ = image.size
    return text_X_position_percentage * image_width - font.getsize(text)[0]


def _get_text_Y_position_on_image(text: str, text_Y_position_percentage: float, image, font):
    _, image_height = image.size
    return text_Y_position_percentage * image_height


def _save_image_to_file(image, file_name: str):
    image_io = BytesIO()
    image.save(image_io, format='png')
    return InMemoryUploadedFile(image_io, None, file_name, f'image/{_get_file_extension(file_name)}', image_io.tell(), None)


def _get_file_extension(file_name: str):
    return file_name.split('.')[1].lower()
