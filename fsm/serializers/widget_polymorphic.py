from rest_polymorphic.serializers import PolymorphicSerializer
from scoring.serializers.scorable_polymorphic import ScorablePolymorphicSerializer
from fsm.serializers.widget_serializers import DescriptionSerializer, ImageSerializer, VideoSerializer, AudioSerializer, AparatSerializer, \
    GameSerializer, SmallAnswerProblemSerializer, BigAnswerProblemSerializer, MultiChoiceProblemSerializer, UploadFileProblemSerializer
from fsm.models import Player, Game, Video, Image, Description, Problem, SmallAnswerProblem, SmallAnswer, BigAnswer, \
    MultiChoiceProblem, Choice, MultiChoiceAnswer, UploadFileProblem, BigAnswerProblem, UploadFileAnswer, State, Hint, \
    Paper, Widget, Team, Aparat, Audio
from scoring.models import Scorable

class WidgetPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        # Widget
        Description: DescriptionSerializer,
        Image: ImageSerializer,
        Video: VideoSerializer,
        Audio: AudioSerializer,
        Aparat: AparatSerializer,
        Game: GameSerializer,
        # Problem,
        SmallAnswerProblem: SmallAnswerProblemSerializer,
        BigAnswerProblem: BigAnswerProblemSerializer,
        MultiChoiceProblem: MultiChoiceProblemSerializer,
        UploadFileProblem: UploadFileProblemSerializer,
        # Scorable
        Scorable: ScorablePolymorphicSerializer,
    }

    resource_type_field_name = 'widget_type'
