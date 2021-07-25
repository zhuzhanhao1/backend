from api.models import MailConfig
from rest_framework import serializers

class MailConfigListSer(serializers.ModelSerializer):

    class Meta:
        model = MailConfig
        fields = "__all__"
