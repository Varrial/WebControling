from datetime import datetime
from time import sleep

from question_collector import QuestionCollector
from questions_helper import get_no_answer_amount, load_questions, save_questions


TYLKO_NAUKA = False


if __name__ == '__main__':
    while True:
        questions = load_questions()

        collector = QuestionCollector(questions, headless=True)
        collector.login_to_cez2()

        if TYLKO_NAUKA:
            collector.learn_from_solved_exams()
        else:
            collector.process_exam()

        save_questions(collector.get_known_questions())
        print(
            f"{datetime.now().strftime('%H:%M:%S')} - zaktualizowano pytania. Znane odpowiedzi: {get_no_answer_amount()}")

        del collector

        if TYLKO_NAUKA:
            break
