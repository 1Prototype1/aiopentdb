# aiopentdb

![GitHub](https://img.shields.io/github/license/CyCanCode/aiopentdb?color=blue)
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue)
![PyPI](https://img.shields.io/pypi/v/aiopentdb?color=blue)
![Travis](https://img.shields.io/travis/com/CyCanCode/aiopentdb)

Async Python wrapper for OpenTDB API

# Installing

**Python 3.7 or higher is required**

```sh
pip install -U aiopentdb
```

# Quick Example

```py
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
```

Look at the examples directory for more examples.
