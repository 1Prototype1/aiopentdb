import asyncio

import aiopentdb


async def main():
    # instantiate the OpenTDB client
    client = aiopentdb.Client()

    try:
        # fetch 5 questions with category type "mathematics" and difficulty "easy"
        questions = await client.fetch_questions(
            amount=5,
            category_type=aiopentdb.CategoryType.mathematics,
            difficulty=aiopentdb.Difficulty.easy
        )

        # print each question and its correct answer
        for question in questions:
            print(f'Question: {question.content}\nAnswer: {question.correct_answer}', end='\n\n')

    finally:
        # close the internal session
        await client.close()


asyncio.run(main())
