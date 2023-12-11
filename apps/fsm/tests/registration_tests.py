from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import User

registration_form_creation_test_case = {
    "min_grade": 0,
    "max_grade": 0,
    "conditions": "string",
    "event": 4,
    "deadline": "2022-08-11T23:14:07.934000+04:30",
    "accepting_status": "CorrectAccept",
    "paper_type": "RegistrationForm",
    "widgets": [
        {
            "name": "p0",
            "text": "mcp1",
            "widget_type": "MultiChoiceProblem",
            "max_choices": 2,
            "choices": [
                "1",
                "2",
                "3",
                "4"
            ],
            "solution": [
                0,
                1
            ]
        },
        {
            "name": "p1",
            "text": "text1",
            "widget_type": "SmallAnswerProblem",
            "solution": {
                "answer_type": "SmallAnswer",
                "text": "abc"
            }
        },
        {
            "name": "name2",
            "text": "text2",
            "widget_type": "TextWidget"
        },
        {
            "name": "p1",
            "text": "text1",
            "widget_type": "UploadFileProblem",
            "solution": 15
        },
    ]
}
registration_form_creation_test_case_response = {
    "id": 51,
    "min_grade": 0,
    "max_grade": 0,
    "conditions": "string",
    "widgets": [
        {
            "id": 140,
            "name": "p0",
            "paper": 51,
            "widget_type": "MultiChoiceProblem",
            "creator": 2,
            "duplication_of": None,
            "text": "mcp1",
            "max_choices": 2,
            "choices": [
                {
                    "id": 157,
                    "text": "1",
                    "problem": 140
                },
                {
                    "id": 158,
                    "text": "2",
                    "problem": 140
                },
                {
                    "id": 159,
                    "text": "3",
                    "problem": 140
                },
                {
                    "id": 160,
                    "text": "4",
                    "problem": 140
                }
            ],
            "solution": {
                "id": 89,
                "answer_type": "MultiChoiceAnswer",
                "answer_sheet": None,
                # "submitted_by": 2,
                # "created_at": None,
                "is_final_answer": True,
                "is_correct": True,
                "problem": 140,
                "choices": [
                    157,
                    158
                ]
            }
        }
    ],
    "event": 4,
    "fsm": None,
    "paper_type": "RegistrationForm",
    "creator": 2
}

register_test_case = {
    "answer_sheet_type": "RegistrationReceipt",
    "answers": [
        {
            "answer_type": "SmallAnswer",
            "text": "far",
            "problem": 175
        },
        {
            "answer_type": "BigAnswer",
            "text": "far",
            "problem": 176
        },
        {
            "answer_type": "UploadFileAnswer",
            "upload_file_answer": 17,
            "problem": 7
        },
        {
            "answer_type": "MultiChoiceAnswer",
            "choices": [
                1,
                2,
                3,
            ],
            "problem": 178
        },
    ]
}
register_test_case_response = {
    "id": 12,
    "user": 2,
    "answer_sheet_type": "RegistrationReceipt",
    "answer_sheet_of": 62,
    "answers": [
        {
            "id": 123,
            "answer_type": "SmallAnswer",
            "answer_sheet": 12,
            "submitted_by": 2,
            "created_at": None,
            "is_final_answer": False,
            "is_correct": False,
            "problem": 175,
            "text": "far"
        }
    ],
    "is_accepted": False
}

factory = APIRequestFactory()
user = User.objects.get(username='admin')
request = factory.post('/registration_form', registration_form_creation_test_case, format='json')
force_authenticate(request, user=user)
