from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from fsm.models import CertificateTemplate, Font
from fsm.permissions import IsCertificateTemplateModifier
from fsm.serializers.certificate_serializer import CertificateTemplateSerializer, FontSerializer


class CertificateTemplateViewSet(ModelViewSet):
    serializer_class = CertificateTemplateSerializer
    queryset = CertificateTemplate.objects.all()
    permission_classes = [IsCertificateTemplateModifier, ]
    parser_classes = [MultiPartParser, ]
    my_tags = ['certificates']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsCertificateTemplateModifier]
        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user': self.request.user})
        context.update({'domain': self.request.build_absolute_uri('/api/')[:-5]})
        return context


class FontViewSet(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    serializer_class = FontSerializer
    queryset = Font.objects.all()
    permission_classes = [IsAuthenticated]
    my_tags = ['certificates']