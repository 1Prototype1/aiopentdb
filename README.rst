aiopentdb
=========
.. image:: https://img.shields.io/github/license/1Prototype1/aiopentdb
    :alt: GitHub - License

**aiopentdb** is an async Python wrapper that implements the entire OpenTDB API.

Note
----
This is the restored repo from the release packages.

Major credit goes to ``CyCanCode``

Installing
----------

**Python 3.6+ is required.**

.. code:: sh

    pip install git+https://github.com/1Prototype1/aiopentdb.git

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

Links
-----
- `OpenTDB API <https://opentdb.com/api_config.php>`_