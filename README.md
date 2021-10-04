aiopentdb
=========
.. image:: https://img.shields.io/github/license/1Prototype1/aiopentdb
    :alt: GitHub - License

Async Python wrapper for OpenTDB API.

Installing
----------

Python 3.7+ is required.

.. code:: sh

    pip git+https://github.com/1Prototype1/aiopentdb.git

or download the repo and run

.. code:: sh

    python setup.py install

Quick Example
-------------

.. code:: py

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
