aiopentdb
=========
.. image:: https://img.shields.io/github/license/1Prototype1/aiopentdb
    :alt: GitHub - License

**aiopentdb** is an async Python wrapper that implements the entire OpenTDB API.

Note
----
This is the restored repo from the release packages.

Major credit goes to ``CyCanCode``

Features
--------
- Full API coverage
- Caching

Installing
----------

Python **3.6** or **higher** is required

.. code-block:: shell

    pip install git+https://github.com/1Prototype1/aiopentdb.git

or download the repo and run

.. code-block:: shell

    python setup.py install

Quickstart
----------

.. code-block:: python3

    import asyncio
    import aiopentdb

    async def main():
        try:
            client = aiopentdb.Client()
            async for question in client.fetch_questions(amount=5):
                print(question.content)
        finally:
            await client.close()

    asyncio.run(main())
