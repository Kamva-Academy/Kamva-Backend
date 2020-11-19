from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from .models import Member, Participant, Team


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # TODO Add custom claims
        token['is_mentor'] = user.is_mentor
        token['is_participant'] = user.is_participant
        if user.is_participant:
            token['name'] = user.first_name
            # token['team'] = str(user.participant.team_id)
            token['uuid'] = str(user.uuid)
        return token


class MemberSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    email = serializers.EmailField(
        required=True
    )
    username = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Member
        fields = ('email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class TeamMembetListField(serializers.RelatedField):
    def to_representation(self, value):
        return value.member.first_name


class TeamSerializer(serializers.ModelSerializer):
    # histories = TeamHistorySerializer(many=True)
    # p_type = serializers.Field(source="team")
    team_members = TeamMembetListField(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['player_type', 'id', 'uuid', 'group_name', 'score', 'team_members']


class PlayerSerializer(serializers.Serializer):
    @classmethod
    def get_serializer(cls, model):
        try:
            model.team
            return TeamSerializer
        except:
            return ParticipantSerializer

    def to_representation(self, instance):
        try:
            instance.team
            serializer = TeamSerializer
            return serializer(instance.team).data
        except:
            try:
                instance.participant
                serializer = ParticipantSerializer
                return serializer(instance.participant).data
            except:
                return {}


class ParticipantSerializer(serializers.Serializer):
    # player_type = serializers.CharField(source='player_type()', read_only=True)
    # customField = serializers.Field(source='get_absolute_url')
    class Meta:
        model = Participant

    def to_representation(self, instance):
        return {
            'player_type': instance.player_type,
            'name': instance.member.first_name,
            'id': instance.id,
            'score': instance.score,
            'uuid': instance.member.uuid
        }
