from datetime import datetime
from time import sleep

from question_collector import QuestionCollector
from questions_helper import get_no_answer_amount, load_questions, save_questions

if __name__ == '__main__':
    while True:
        questions = load_questions()

        collector = QuestionCollector(questions)
        collector.login_to_cez2()

        # collector.learn_from_solved_exams()
        collector.process_exam()

        save_questions(collector.get_known_questions())
        print(
            f"{datetime.now().strftime('%H:%M:%S')} - zaktualizowano pytania. Znane odpowiedzi: {get_no_answer_amount()}")

        del collector
