from rest_polymorphic.serializers import PolymorphicSerializer
from apps.fsm.serializers.widget_serializers import DetailBoxWidgetSerializer, TextWidgetSerializer, ImageSerializer, VideoSerializer, AudioSerializer, AparatSerializer, \
    GameSerializer, SmallAnswerProblemSerializer, BigAnswerProblemSerializer, MultiChoiceProblemSerializer, UploadFileProblemSerializer
from apps.fsm.models import DetailBoxWidget, Player, Game, Video, Image, TextWidget, Problem, SmallAnswerProblem, SmallAnswer, BigAnswer, \
    MultiChoiceProblem, Choice, MultiChoiceAnswer, UploadFileProblem, BigAnswerProblem, UploadFileAnswer, State, Hint, \
    Paper, Widget, Team, Aparat, Audio


class WidgetPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Widget
        TextWidget: TextWidgetSerializer,
        Image: ImageSerializer,
        Video: VideoSerializer,
        Audio: AudioSerializer,
        Aparat: AparatSerializer,
        Game: GameSerializer,
        DetailBoxWidget: DetailBoxWidgetSerializer,
        # Problem,
        SmallAnswerProblem: SmallAnswerProblemSerializer,
        BigAnswerProblem: BigAnswerProblemSerializer,
        MultiChoiceProblem: MultiChoiceProblemSerializer,
        UploadFileProblem: UploadFileProblemSerializer,
    }

    resource_type_field_name = 'widget_type'
