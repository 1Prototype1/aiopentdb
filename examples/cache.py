import asyncio

import aiopentdb


async def main():
    client = aiopentdb.Client()

    try:
        # populate the internal question cache.
        # this is useful when you dont want to make a lot of API calls when retrieving
        # questions.
        await client.populate_questions()

        # unlike the "basic" example, we retrieve these questions from the cache if exist
        questions = client.get_questions(
            amount=5,
            category_type=aiopentdb.CategoryType.mathematics,
            difficulty=aiopentdb.Difficulty.easy
        )

        for question in questions:
            print(f'Question: {question.content}\nAnswer: {question.correct_answer}', end='\n\n')

    finally:
        await client.close()


asyncio.run(main())
