from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import User

registration_form_creation_test_case = {
    "min_grade": 0,
    "max_grade": 0,
    "conditions": "string",
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
            "widget_type": "Description"
        }
    ]
}
registration_form_creation_test_case_response = {
    "id": 37,
    "min_grade": 0,
    "max_grade": 0,
    "conditions": "string",
    "widgets": [
        {
            "id": 98,
            "name": "p0",
            "paper": 37,
            "widget_type": "MultiChoiceProblem",
            "creator": 2,
            "duplication_of": null,
            "text": "mcp1",
            "help_text": null,
            "max_score": null,
            "max_choices": 2,
            "choices": [
                {
                    "id": 101,
                    "text": "1",
                    "problem": 98
                },
                {
                    "id": 102,
                    "text": "2",
                    "problem": 98
                },
                {
                    "id": 103,
                    "text": "3",
                    "problem": 98
                },
                {
                    "id": 104,
                    "text": "4",
                    "problem": 98
                }
            ],
            "solution": {
                "id": 61,
                "answer_type": "MultiChoiceAnswer",
                "answer_sheet": null,
                "submitted_by": 2,
                "created_at": null,
                "is_final_answer": true,
                "is_solution": true,
                "problem": 98,
                "choices": [
                    101,
                    102
                ]
            }
        },
        {
            "id": 99,
            "name": "p1",
            "paper": 37,
            "widget_type": "SmallAnswerProblem",
            "creator": 2,
            "duplication_of": null,
            "text": "text1",
            "help_text": null,
            "max_score": null,
            "solution": {
                "id": 62,
                "answer_type": "SmallAnswer",
                "answer_sheet": null,
                "submitted_by": 2,
                "created_at": null,
                "is_final_answer": true,
                "is_solution": true,
                "problem": 99,
                "text": "abc"
            }
        },
        {
            "id": 100,
            "name": "name2",
            "paper": 37,
            "widget_type": "Description",
            "creator": 2,
            "duplication_of": null,
            "text": "text2"
        }
    ]
}

factory = APIRequestFactory()
user = User.objects.get(username='admin')
request = factory.post('/registration_form', registration_form_creation_test_case, format='json')
force_authenticate(request, user=user)
# TODO - configure tests and all
