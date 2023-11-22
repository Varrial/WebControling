import json
from time import sleep

from selenium import webdriver

from data import *


def load_questions(location='questions.json'):
    try:
        with open(location, "r", encoding="utf-8") as file:
            data = json.load(file)
    except:
        data = []
    return data


def save_questions(questions: list, location='questions.json'):
    with open(location, "w", encoding="utf-8") as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)


def login_to_cez2():
    driver.get(links['cez'])

    # Login
    driver \
        .find_element(by='id', value='username') \
        .send_keys(passwords['login'])

    # Password
    driver \
        .find_element(by='id', value='password') \
        .send_keys(passwords['password'])

    # Login button
    driver. \
        find_element(by='css selector', value='#boxForm > div > form > div.sign-up-btn > button') \
        .click()


def start_exam():
    # Go to exam
    driver.get(links['exam'])

    # Test begin button
    driver.find_elements('css selector', '.btn.btn-secondary')[0] \
        .click()

    # Test password
    driver \
        .find_element(by='id', value='id_quizpassword') \
        .send_keys(passwords['exam_password'])

    # Test password submit
    driver \
        .find_element(by='id', value='id_submitbutton') \
        .click()


def end_exam():
    driver \
        .find_element('css selector', '.endtestlink') \
        .click()

    buttons = driver.find_elements('css selector', '.btn.btn-secondary')

    for button in buttons:
        if button.text == 'Zatwierdź wszystkie i zakończ':
            button.click()
            break
    sleep(.3)
    driver \
        .find_elements('css selector', '.btn.btn-primary')[1] \
        .click()


def translate_questions(all_questions):
    answers_box = driver.find_elements(by='css selector', value='.content')[:-1]

    for answer_box in answers_box:
        full_question = dict()
        text_lines = answer_box.text.split('\n')

        full_question['question'] = str()
        full_question['options'] = []
        full_question['correct'] = []
        full_question['type'] = str()

        question = get_question(text_lines)
        options = get_option(text_lines)
        correct = get_correct(text_lines)
        type = get_type(answer_box)

        handle_duplicat(all_questions, question, options, correct, type)

    return all_questions


def get_question(text_lines):
    return text_lines[1]


def get_option(text_lines):
    important_lines = text_lines[3:-3]
    options = []
    for text in important_lines:
        options.append(text[3:])
    return options


def get_correct(text_lines):
    important_line = text_lines[-1]

    if important_line.startswith('Poprawna'):
        return [important_line[23:]]

    if not important_line.startswith('Prawidłowymi'):
        raise Exception("Inny typ odpowiedzi")

    correct = []
    options = get_option(text_lines)
    important_lines = important_line[31:].split(', ')

    for option in options:
        for text in important_lines:
            if option.startswith(text):
                correct.append(option)

    return correct


def get_type(box):
    try:
        type = box.find_elements('css selector', '.answer > div > input')[0].get_attribute('type')
    except :
        return 'other'

    if type == 'radio':
        return 'single'

    if type == 'checkbox':
        return 'multi'

    return 'other'


def handle_duplicat(all_questions, question, options, correct, typ):
    for index, full_question in enumerate(all_questions):

        # znalezienie duplikatu pytania
        if full_question['question'] == question:

            # idealny duplikat, więc można pominąć
            if \
                    sorted(full_question['options']) == sorted(options) and \
                    sorted(full_question['correct']) == sorted(correct) and \
                    full_question['type'] == typ:
                return all_questions

            # inny typ pytania, trzeba dodać nowe
            if full_question['type'] != typ:
                continue

            # duplikaty w wielokrotnym
            if typ == 'multi':

                # uzupełnienie opcji
                if sorted(full_question['options']) != sorted(options):
                    merged_options = list(set(full_question['options'] + options))
                    all_questions[index]['options'] = merged_options

                # uzupełnienie odpowiedzi
                if sorted(full_question['correct']) != sorted(correct):
                    merged_correct = list(set(full_question['correct'] + correct))
                    all_questions[index]['correct'] = merged_correct

                # pominięcie
                return all_questions

            # duplikaty w jednokrotnym
            elif typ == 'single':

                # inna odpowiedź, dodanie
                if sorted(full_question['correct']) != sorted(correct):
                    continue

                # inne opcje, uzupełnienie i pominięcie
                if sorted(full_question['options']) != sorted(options):
                    merged_options = list(set(full_question['options'] + options))
                    all_questions[index]['options'] = merged_options
                    return all_questions

            # błąd
            else:
                print("Error: Nieobsługiwany typ danych")
                print(f'index: {index}')
                print(full_question)
                print(f'New question: {question}')
                print(f'New correct: {correct}')
                print(f'New typ: {typ}')
                print()

    # dodanie nowego pytania
    new_question = {
        'question': question,
        'options': options,
        'correct': correct,
        'type': typ
    }
    all_questions.append(new_question)

    return all_questions


def process_questions():
    questions = len(driver.find_elements(by='css selector', value='.qn_buttons.clearfix.multipages > *')) - 1

    for i in range(questions):
        answers = driver.find_elements(by='css selector', value='.answer > div > input')[::2]
        answers[0].click()
        driver.find_element('css selector', '.mod_quiz-next-nav.btn.btn-primary').click()
    driver \
        .find_element('css selector', '.endtestlink') \
        .click()


driver = webdriver.Chrome()
NUMBER_OF_LOOPS = 10


if __name__ == '__main__':
    questions = load_questions()

    login_to_cez2()

    for _ in range(NUMBER_OF_LOOPS):
        start_exam()
        end_exam()
        questions = translate_questions(questions)

    save_questions(questions)

driver.close()
