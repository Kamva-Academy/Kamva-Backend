import logging
import csv
import os

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand
from django.shortcuts import get_object_or_404

from accounts.models import User, School, SchoolStudentship, Studentship, AcademicStudentship
from fsm.models import FSM, RegistrationReceipt, Team

logger = logging.getLogger(__file__)

GENDER_MAPPING = {
    'دختر': User.Gender.Female,
    'پسر': User.Gender.Male
}

GRADE_MAPPING = {
    'نهم': 9,
    'دهم': 10,
    'یازدهم': 11,
    'دوازدهم': 12
}

MAJOR_MAPPING = {
    'ریاضی فیزیک': SchoolStudentship.Major.Math,
    'تجربی': SchoolStudentship.Major.Biology,
    'ادبیات': SchoolStudentship.Major.Literature,
    'عمومی': SchoolStudentship.Major.Others
}

def convert(string):
    return string.replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')


class Command(BaseCommand):
    help = 'Create users and teams'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('fsm', nargs='+', type=str)

    def handle(self, *args, **options):
        fsm_name = options['fsm'][0]
        fsm = get_object_or_404(FSM, name=fsm_name)
        filename = options['filename'][0]
        with open(filename, 'r', encoding='utf-8') as file:
            for data in csv.DictReader(file):
                members = [dict(), dict(), dict()]
                for k in data.keys():
                    if k != 'team_code':
                        for i in range(len(members)):
                            if len(data[k]) > 1:
                                members[i][k] = data[k].split('-')[i].strip()
                            if k == 'username':
                                members[i][k] = members[i][k].replace(' ', '_')
                receipts = []
                for member in members:
                    schools = School.objects.filter(name=member['institute'], city=member['city'],
                                                    province=member['province'])
                    if len(schools) > 0:
                        school = schools.first()
                    else:
                        school = School.objects.create(name=member['institute'], institute_type='School',
                                                       city=member['city'], province=member['province'])
                        self.stdout.write(self.style.SUCCESS(f'Successfully created school {school.name}'))
                    if 'phone_number' not in member.keys():
                        continue
                    phone_number = convert(member['phone_number'])
                    user = User.objects.create(
                        phone_number=phone_number,
                        first_name=member['first_name'],
                        last_name=member['last_name'],
                        city=member['city'],
                        password=make_password(phone_number),
                        national_code=member['national_code'],
                        province=member['province'],
                        username=member['username'],
                        gender=GENDER_MAPPING[member['gender']],
                    )
                    school_studentship = SchoolStudentship.objects.create(
                        school=school,
                        studentship_type=Studentship.StudentshipType.School,
                        user=user,
                        major=MAJOR_MAPPING[member['major']] if 'major' in member.keys() else MAJOR_MAPPING['ریاضی فیزیک'],
                        grade=GRADE_MAPPING[member['grade']],
                        is_document_verified=True,
                    )
                    academic_studentship = AcademicStudentship.objects.create(
                        studentship_type=Studentship.StudentshipType.Academic,
                        user=user,
                    )
                    receipts.append(RegistrationReceipt.objects.create(
                        answer_sheet_of=fsm.registration_form,
                        answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                        user=user,
                        status=RegistrationReceipt.RegistrationStatus.Accepted,
                        is_participating=True,
                    ))
                    self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.phone_number}'))
                team = Team.objects.create(name=data['team_code'],
                                           team_head=receipts[0],
                                           registration_form=fsm.registration_form)
                for x in receipts:
                    x.team = team
                    x.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created team {team.name}'))

