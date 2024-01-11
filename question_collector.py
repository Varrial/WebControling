from time import sleep

from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from data import *


class QuestionCollector:
    def __init__(self, questions: list, headless=True, disable_gpu=True, safe_user_data=False, no_sandbox=False):
        self._known_questions = questions.copy()

        options = Options()

        if headless:
            options.add_argument('--headless')

        if disable_gpu:
            options.add_argument('--disable-gpu')

        if safe_user_data:
            options.add_argument('--user-data-dir=web_user_data')

        if no_sandbox:
            options.add_argument('--no-sandbox')

        self.driver = webdriver.Chrome(options=options)

    def go_to_page(self, adres: str):
        self.driver.get(adres)

    def login_to_cez2(self):
        self.go_to_page(links['cez'])

        # Login
        self.driver \
            .find_element(by='id', value='username') \
            .send_keys(passwords['login'])

        # Password
        self.driver \
            .find_element(by='id', value='password') \
            .send_keys(passwords['password'])

        # Login button
        self.driver. \
            find_element(by='css selector', value='#boxForm > div > form > div.sign-up-btn > button') \
            .click()

    def _start_exam(self):
        # Go to exam
        self.driver.get(links['exam'])

        # Test begin button
        self.driver.find_elements('css selector', '.btn.btn-secondary')[0] \
            .click()

        # Test password
        try:
            self.driver \
                .find_element(by='id', value='id_quizpassword') \
                .send_keys(passwords['exam_password'])
        except NoSuchElementException:
            pass

        # Test password submit
        try:
            self.driver \
                .find_element(by='id', value='id_submitbutton') \
                .click()
        except NoSuchElementException:
            pass

    def process_exam(self):
        self._start_exam()
        self._solve_exam()
        self._learn_from_exam()

        return self.get_known_questions()

    def get_known_questions(self):
        return self._known_questions.copy()

    def learn_from_solved_exams(self):
        for i in range(self._get_solved_exams_amount()):
            self.driver.get(links['exam'])
            self.driver.find_elements(by='css selector', value='td.lastcol')[i].click()
            self._learn_from_exam()

    def _get_solved_exams_amount(self):
        self.driver.get(links['exam'])
        return len(self.driver.find_elements(by='css selector', value='td.lastcol'))

    def _solve_exam(self):
        while True:
            self._process_question()
            self._click_next_page_button()
            if self._all_question_answered():
                break
        self._click_finish_exam()

    def _learn_from_exam(self):
        question_boxes = self._get_question_boxes()

        for question_box in question_boxes:
            question = self._read_question(source=question_box)
            is_single = self._is_single_answer(source=question_box)
            answer_boxes = self._read_answers(source=question_box, return_text=False)
            answers_texts = self._read_correct_answers(source=question_box)

            answer_options = []
            for answer in answer_boxes:
                answer_options.append(answer.text[3:])

            if isinstance(answers_texts, str):
                answers_texts = self._list_from_answers_texts(answers_texts, answer_options)

            known_question = self._get_known_question_if_exist(question, is_single)

            if known_question:
                # self._append_answers(known_question, answers_texts)
                # self._fill_correct_incorrect_fields(known_question, answer_boxes, delete_duplicates=True)
                pass

            else:
                question_dict = self._prepare_dict(
                    question=question,
                    is_single=is_single,
                    answers_texts=answer_options,
                    correct=answers_texts
                )
                # self._fill_correct_incorrect_fields(question_dict, answer_boxes)
                self._known_questions.append(question_dict)

    def _decide_question(self):
        pass

    def _fill_correct_incorrect_fields(self, source: dict, answer_boxes, delete_duplicates=False):
        for answer_box in answer_boxes:
            question_class = answer_box.get_attribute("class").split()
            if "correct" in question_class:
                source['correct'].append(self._read_answers(source=answer_box)[0])
            if "incorrect" in question_class:
                source['incorrect'].append(self._read_answers(source=answer_box)[0])

        if delete_duplicates:
            source["correct"] = list(set(source['correct']))
            source["incorrect"] = list(set(source['incorrect']))

    def _prepare_dict(self, question="", is_single=True, answers_texts=None, correct=None, incorrect=None):
        if answers_texts is None:
            answers_texts = []

        if correct is None:
            correct = []

        if incorrect is None:
            incorrect = []

        return {
            "question": question,
            "type": self._is_single_to_type(is_single),
            "answers": answers_texts,
            "correct": correct,
            "incorrect": incorrect,
        }

    def _get_question_boxes(self) -> list:
        return self.driver.find_elements(by="css selector", value="div.formulation.clearfix")

    def _process_question(self):
        question = self._read_question()
        is_single = self._is_single_answer()
        answers = self._read_answers()

        known_question = self._get_known_question_if_exist(question, is_single)

        if known_question is not None:
            chosen_answer = self._choose_answer(known_question, answers)
        else:
            if not answers:
                return
            chosen_answer = answers[0]

        if chosen_answer:
            self._click_chosen_answers(chosen_answer)

    def _click_finish_exam(self):
        # Zatwierdź wszystkie i zakończ
        self.driver.find_elements(by="css selector", value="button.btn.btn-secondary")[-1].click()

        # Potwierdzenie
        sleep(.2)
        try:
            self.driver.find_element(by="css selector", value="input.btn.btn-primary").click()
        except NoSuchElementException:
            pass

    def _click_next_page_button(self):
        self.driver.find_element(by="css selector", value="input.mod_quiz-next-nav").click()

    def _all_question_answered(self) -> bool:
        last_question_selector = self.driver.find_elements(by='css selector', value='.qnbutton')[-1]
        classes_of_last_question = last_question_selector.get_attribute('class').split()

        return 'answersaved' in classes_of_last_question

    def _read_question(self, source=None) -> str:
        if not source:
            source = self.driver

        element = source.find_element(by='css selector', value='div.qtext')
        question = element.text

        return question

    def _is_single_answer(self, source=None) -> bool:
        if not source:
            source = self.driver

        elements = source.find_elements(by='css selector', value='div.answer > div > input')
        try:
            answer_type = elements[0].get_attribute('type')
        except IndexError:
            # open question
            return False

        if answer_type == 'hidden':
            answer_type = elements[1].get_attribute('type')

        if answer_type == 'radio':
            return True

        if answer_type == 'checkbox':
            return False

        raise Exception("unsupported type")

    def _read_answers(self, source=None, return_text=True) -> list:
        if not source:
            source = self.driver

        elements = source.find_elements(by='css selector', value='label.ml-1')
        answers = list()

        for element in elements:
            if return_text:
                text = element.text
                number = element.find_element(by='css selector', value='span').text

                text = text.replace(number, "", 1).strip()
                answers.append(text)
            else:
                element = element.find_element(by='xpath', value='..')
                answers.append(element)

        return answers

    def _read_correct_answers(self, source=None):
        if not source:
            source = self.driver

        element = source.find_element(by='xpath', value='..')
        answer = element.find_element(by='css selector', value='.outcome .feedback .rightanswer').text

        if answer.startswith('Poprawna odpowiedź to: '):
            answer = answer[23:]
            return [answer]
        elif answer.startswith('Prawidłowymi odpowiedziami są: '):
            answer = answer[31:]

        return answer


    @staticmethod
    def _choose_answer(known_question, answers):
        if known_question['correct']:
            return known_question['correct']

        # usunięcie nieprawidłowych odpowiedzi
        answers = [element for element in answers if element not in known_question['incorrect']]

        if len(answers) == 0:
            return
            # raise Exception("no correct answer")

        return answers[0]

    def _get_known_question_if_exist(self, question, is_single):
        for known_question in self._known_questions:
            if known_question['question'] == question and known_question['type'] == self._is_single_to_type(is_single):
                return known_question

        return None

    @staticmethod
    def _is_single_to_type(is_single):
        return "single" if is_single else "multi"

    @staticmethod
    def _append_answers(known_question, answers):
        known_question['answers'] = list(set(known_question['answers'] + answers))

    def _click_chosen_answers(self, chosen_answers):
        options = self.driver.find_elements(by="css selector", value=".answer > *")

        for option in options:
            if not isinstance(chosen_answers, list):
                chosen_answers = [chosen_answers]

            for chosen_answer in chosen_answers:
                if option.text[1:].strip() == f'. {chosen_answer}':
                    try:
                        option.find_element(by="css selector", value="input").click()
                    except ElementNotInteractableException:
                        option.find_element(by="css selector", value="label").click()
                    return

        raise Exception(f"Cannot find Chosen Answer: {chosen_answers}")

    def __del__(self):
        self.driver.close()

    def _list_from_answers_texts(self, answers_texts, options):
        # GPT
        # Twoja lista odpowiedzi
        odpowiedzi = options

        # String z prawidłowymi odpowiedziami
        prawidlowe_str = answers_texts

        # Sortowanie odpowiedzi od najdłuższej do najkrótszej
        posortowane_odpowiedzi = sorted(odpowiedzi, key=len, reverse=True)

        # Lista do przechowywania indeksów prawidłowych odpowiedzi
        prawidlowe_indeksy = []

        for odpowiedz in posortowane_odpowiedzi:
            if odpowiedz in prawidlowe_str:
                prawidlowe_indeksy.append(odpowiedzi.index(odpowiedz))
                # Usuwanie wystąpienia odpowiedzi z tekstu
                prawidlowe_str = prawidlowe_str.replace(odpowiedz, '')

        odpowiedzi = list()
        for index in sorted(prawidlowe_indeksy):
            odpowiedzi.append(options[index])

        return odpowiedzi

