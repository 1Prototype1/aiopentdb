"""
MIT License

Copyright (c) 2020 CyCanCode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import functools

import aiopentdb


async def main() -> None:
    # NOTE: Temporary tests
    try:
        client = aiopentdb.Client()
        wait = functools.partial(asyncio.sleep, 1)

        token = await client.get_token()
        print(token, end='\n\n')
        await wait()

        questions = await client.get_questions()
        print(questions, end='\n\n')
        await wait()

        categories = await client.get_categories()
        print(categories, end='\n\n')
        await wait()

        category_count = await client.get_category_count(aiopentdb.CategoryType.general_knowledge)
        print(category_count, end='\n\n')
        await wait()

        global_count = await client.get_global_count()
        print(global_count, end='\n\n')
        await wait()

    finally:
        await client.close()


asyncio.run(main())
