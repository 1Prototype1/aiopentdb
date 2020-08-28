aiopentdb
=========

.. image:: https://img.shields.io/travis/com/CyCanCode/aiopentdb
    :alt: Travis (.com)
.. image:: https://img.shields.io/pypi/l/aiopentdb
    :alt: PyPI - License
.. image:: https://img.shields.io/pypi/v/aiopentdb
    :alt: PyPI

Async Python wrapper for OpenTDB API.

Installing
----------

Python 3.7+ is required.

.. code:: sh
    pip install -U aiopentdb

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
