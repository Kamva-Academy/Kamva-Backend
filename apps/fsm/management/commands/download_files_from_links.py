from fsm.utils import get_django_file
from apps.fsm.models import Image, Video

from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'download files from links'

    def handle(self, *args, **options):
        images = Image.objects.all()
        videos = Video.objects.all()
        all_count = len(images) + len(videos)
        done_count = 0
        for image in images:
            try:
                if not image.file:
                    link_file = get_django_file(image.link)
                    image.file = link_file
                    image.save()
            except:
                pass
            finally:
                done_count += 1
                print(f'{done_count}/{all_count}')

        for video in videos:
            try:
                if not video.file:
                    link_file = get_django_file(video.link)
                    video.file = link_file
                    video.save()
            except:
                pass
            finally:
                done_count += 1
                print(f'{done_count}/{all_count}')
