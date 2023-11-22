import json


def load_questions(location='questions.json'):
    try:
        with open(location, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data


def save_questions(questions: list, location='questions.json'):
    with open(location, "w", encoding="utf-8") as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)


def prepare_readable_questions():
    questions = load_questions()
    questions = sorted(questions, key=lambda x: x["question"])

    with open("easy to read.txt", "w") as file:
        for question in questions:
            text = question['question'] + '\n'

            for answer in question['correct']:
                text += '\t' + answer + '\n'

            text += '\n'

            file.write(text)


if __name__ == '__main__':
    prepare_readable_questions()
