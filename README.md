# aiopentdb

![GitHub](https://img.shields.io/github/license/CyCanCode/aiopentdb?color=blue)
![Python](https://img.shields.io/badge/python-3.7%20%7C%203.8-blue)
![PyPI](https://img.shields.io/pypi/v/aiopentdb?color=blue)

Async Python wrapper for OpenTDB API

# Installing

**Python 3.7 or higher is required**

```sh
pip install -U aiopentdb
```

# Examples

## Basic

```py
import asyncio
from aiopentdb import Client, Difficulty

async def main():
    client = Client()
    try:
        questions = await client.fetch_questions(difficulty=Difficulty.easy)
        # do something...
    finally:
        await client.close()

asyncio.run(main())
```

## Cache

```py
import asyncio
from aiopentdb import Client, Difficulty

async def main():
    client = Client()
    try:
        await client.populate_questions()
        questions = client.get_questions(difficulty=Difficulty.easy)
        # do something...
    finally:
        await client.close()

asyncio.run(main())
```
