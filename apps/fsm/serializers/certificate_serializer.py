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
        representation = super(FontSerializer, self).to_representation(instance)
        font_file = representation['font_file']
        if font_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['font_file'] = domain + font_file
        return representation


class CertificateTemplateSerializer(serializers.ModelSerializer):
    font = serializers.PrimaryKeyRelatedField(queryset=Font.objects.all(), allow_null=False, required=True)

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
        name_X = attrs.get('name_X', None)
        name_Y = attrs.get('name_Y', None)
        if name_X > width or name_Y > height:
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
        representation = super(CertificateTemplateSerializer, self).to_representation(instance)
        template_file = representation['template_file']
        if template_file.startswith('/api/'):
            domain = self.context.get('domain', None)
            if domain:
                representation['template_file'] = domain + template_file
        representation['font'] = instance.font.name if instance.font and instance.font.name else None
        return representation


def create_certificate(certificate_template, full_name):
    extension = certificate_template.template_file.name.split('.')[1].lower()
    if extension in ['png', 'jpg', 'jpeg', 'gif']:
        if certificate_template.font:
            font_file = certificate_template.font.font_file.file
        else:
            raise ParseError(serialize_error('4096'))
        font = ImageFont.truetype(font_file, certificate_template.font_size)
        image = Image.open(certificate_template.template_file.file)

        reshaped_text = arabic_reshaper.reshape(full_name)  # correct its shape
        bidi_text = get_display(reshaped_text)  # correct its direction

        draw = ImageDraw.Draw(image)
        x = certificate_template.name_X - font.getsize(full_name)[0]
        draw.text((x, certificate_template.name_Y), bidi_text, (0, 0, 0), font=font)
        draw = ImageDraw.Draw(image)

        image_io = BytesIO()
        image.save(image_io, format='png')
        certificate_file_name = f'{certificate_template.template_file.name}-{full_name}.{extension}'
        image_file = InMemoryUploadedFile(image_io, None, certificate_file_name, f'image/{extension}', image_io.tell(), None)

        return image_file

    elif extension == 'pdf':
        raise ParseError(serialize_error('4099'))
    else:
        raise ParseError(serialize_error('4093'))