import logging
import csv
import os

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand
from django.db.models import Q
from django.shortcuts import get_object_or_404

from apps.accounts.models import User, School, SchoolStudentship, Studentship, AcademicStudentship
from apps.fsm.models import FSM, RegistrationReceipt, Team, AnswerSheet, RegistrationForm

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
    'ریاضی': SchoolStudentship.Major.Math,
    'تجربی': SchoolStudentship.Major.Biology,
    'ادبیات': SchoolStudentship.Major.Literature,
    'عمومی': SchoolStudentship.Major.Others
}


def convert_with_punctuation_removal(string):
    return string.replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵',
                                                                                                                    '5').replace(
        '۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9').replace(' ', '').replace('-', '').replace('_',
                                                                                                                  '')


class Command(BaseCommand):
    help = 'Create users and teams'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('registration_form', nargs='+', type=str)
        parser.add_argument('admin', nargs='+', type=str)

    def handle(self, *args, **options):
        form_id = options['registration_form'][0]
        registration_form = RegistrationForm.objects.get(id=form_id)
        filename = options['filename'][0]
        admin_user = User.objects.get(username=options['admin'][0])
        older_users = []
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
                                                       city=member['city'], province=member['province'],
                                                       creator=admin_user)
                        self.stdout.write(self.style.SUCCESS(f'Successfully created school {school.name}'))
                    if 'phone_number' not in member.keys():
                        continue
                    phone_number = convert_with_punctuation_removal(member['phone_number'])
                    national_code = convert_with_punctuation_removal(member['national_code'])
                    first_name = member['name'].split()[0]
                    last_name = member['name'][len(first_name):].strip()
                    if len(User.objects.filter(Q(username=national_code) | Q(phone_number=phone_number))) <= 0:
                        user = User.objects.create(
                            phone_number=phone_number,
                            first_name=first_name,
                            last_name=last_name,
                            city=member['city'],
                            password=make_password(national_code),
                            national_code=national_code,
                            province=member['province'],
                            username=national_code,
                            gender=GENDER_MAPPING[member['gender']],
                        )
                    elif len(User.objects.filter(phone_number=phone_number)) > 0:
                        user = User.objects.filter(phone_number=phone_number).first()
                        older_users.append(user)
                    else:
                        user = User.objects.filter(username=national_code).first()
                    if len(SchoolStudentship.objects.filter(user=user)) <= 0:
                        school_studentship = SchoolStudentship.objects.create(
                            school=school,
                            studentship_type=Studentship.StudentshipType.School,
                            user=user,
                            major=MAJOR_MAPPING[member['major']] if 'major' in member.keys() else MAJOR_MAPPING[
                                'ریاضی'],
                            grade=GRADE_MAPPING[member['grade']],
                            is_document_verified=True,
                        )
                    else:
                        school_studentship = SchoolStudentship.objects.filter(school=school, user=user).first()
                    if len(AcademicStudentship.objects.filter(user=user)) <= 0:
                        academic_studentship = AcademicStudentship.objects.create(
                            studentship_type=Studentship.StudentshipType.Academic,
                            user=user,
                        )
                    else:
                        academic_studentship = AcademicStudentship.objects.filter(user=user).first()
                    if len(RegistrationReceipt.objects.filter(answer_sheet_of=registration_form, user=user)) <= 0:
                        receipts.append(RegistrationReceipt.objects.create(
                            answer_sheet_of=registration_form,
                            answer_sheet_type=AnswerSheet.AnswerSheetType.RegistrationReceipt,
                            user=user,
                            status=RegistrationReceipt.RegistrationStatus.Accepted,
                            is_participating=True,
                        ))
                    else:
                        receipts.append(RegistrationReceipt.objects.filter(
                            answer_sheet_of=registration_form, user=user).first())
                    self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.username}'))
                if len(Team.objects.filter(name=data['team_code'])) <= 0:
                    team = Team.objects.create(name=data['team_code'],
                                               team_head=receipts[0],
                                               registration_form=registration_form)
                else:
                    team = Team.objects.filter(name=data['team_code']).first()

                for x in receipts:
                    x.team = team
                    x.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created team {team.name}'))
        self.stdout.write(self.style.SUCCESS('older users include:'))
        for u in older_users:
            self.stdout.write(self.style.SUCCESS(f'{u.phone_number}-{u.national_code}'))
