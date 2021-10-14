import logging

from django.core.management import BaseCommand

from accounts.models import EducationalInstitute, User

cities = {
    '264': "نهاوند",
    '417': "نهبندان",
    '37': "نور",
    '38': "نوشهر",
    '382': "نیر",
    '190': "نیشابور",
    '239': "نیک شهر",
    '98': "هرسین",
    '62': "هریس",
    '57': "هشترود",
    '265': "همدان",
    '119': "هندیجان",
    '362': "ورامین",
    '68': "ورزقان",
    '379': "پارس آباد",
    '355': "پارسیان",
    '151': "پاسارگاد",
    '366': "پاکدشت",
    '90': "پاوه",
    '372': "پردیس",
    '287': "پلدختر",
    '85': "پلدشت",
    '72': "پیرانشهر",
    '228': "چادگان‌",
    '67': "چاراویماق",
    '84': "چالدران",
    '42': "چالوس",
    '234': "چابهار",
    '191': "چناران",
    '128': "کارون",
    '138': "کازرون",
    '218': "کاشان",
    '424': "کرج",
    '89': "کرمانشاه",
    '50': "کلاردشت",
    '61': "کلیبر",
    '10': "کمیجان",
    '94': "کنگاور",
    '156': "کوار",
    '285': "کوهدشت",
    '121': "گتوند",
    '330': "گرمسار",
    '411': "گرمه",
    '378': "گرمی",
    '395': "گرگان",
    '44': "گلوگاه",
    '219': "گلپایگان",
    '188': "گناباد",
    '315': "گناوه",
    '396': "گنبدکاووس",
    '95': "گیلانغرب",
    '303': "گچساران",
    '430': "یزد"
}
provinces = {'4': "آذربایجان شرقی",
             '5': "آذربایجان غربی",
             '25': "اردبیل",
             '11': "اصفهان",
             '31': "البرز",
             '17': "ایلام",
             '19': "بوشهر",
             '24': "تهران",
             '30': "خراسان جنوبی",
             '10': "خراسان رضوی",
             '29': "خراسان شمالی",
             '7': "خوزستان",
             '20': "زنجان",
             '21': "سمنان",
             '12': "سیستان وبلوچستان",
             '8': "فارس",
             '27': "قزوین",
             '26': "قم",
             '13': "کردستان",
             '9': "کرمان",
             '6': "کرمانشاه",
             '18': "کهگیلویه و بویراحمد",
             '28': "گلستان",
             '2': "گیلان",
             '16': "لرستان",
             '3': "مازندران",
             '1': "مرکزی",
             '23': "هرمزگان",
             '14': "همدان",
             '15': "چهارمحال و بختیاری",
             '22': "یزد"}

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'renames cities'

    def handle(self, *args, **options):
        for inst in EducationalInstitute.objects.all():
            if inst.city and cities.get(inst.city):
                inst.city = cities.get(inst.city)
            if inst.province and provinces.get(inst.province):
                inst.province = provinces.get(inst.province)
            inst.save()
        for user in User.objects.all():
            if user.city and cities.get(user.city):
                user.city = cities.get(user.city)
            if user.province and provinces.get(user.province):
                user.province = provinces.get(user.province)
            user.save()
        self.stdout.write(self.style.SUCCESS('Successfully renamed cities'))
