

import json
import requests

from kamva_backend.settings.base import get_environment_var

url = get_environment_var(
    'CORRECTOR_API', 'http://localhost:9000/api/corrector/correct/')


def correct_answer(question, given_answer):
    correct_answer = question.correct_answer
    if not question.correct_answer:
        raise Exception("no correct answer provided")
    body = {
        'correct_answer': {
            'answer_type': question.correct_answer.answer_type,
            'text': correct_answer.string_answer,
        },
        'given_answer': {
            'answer_type': given_answer.answer_type,
            'text': given_answer.string_answer,
        }
    }
    response = requests.post(url, json=body)
    result = json.loads(response.text)
    correctness_percentage = result.get('correctness_percentage')
    comment = result.get('comment')
    return [correctness_percentage, comment]
