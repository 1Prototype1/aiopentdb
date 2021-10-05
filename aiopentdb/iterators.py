"""
    aiopentdb.iterators
    ~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import base64
import html
from urllib import parse

from .enums import EncodingType
from .objects import Question

__all__ = ()

class _QuestionsIterator:
    __slots__ = (
        '_client', '_questions', '_amount', '_category_type', '_difficulty_type', '_question_type',
        '_consume', '_current'
    )

    def __init__(
        self, client, *,
        amount=10,
        category=None,
        difficulty=None,
        type=None,
        consume=False
    ):
        self._client = client
        self._questions = iter(client.questions)

        self._amount = amount
        self._category_type = category
        self._difficulty_type = difficulty
        self._question_type = type
        self._consume = consume

        self._current = 0

    def _is_valid(self, question):
        if self._category_type is not None and question.category.type is not self._category_type:
            return False
        if self._difficulty_type is not None and question.difficulty is not self._difficulty_type:
            return False
        if self._question_type is not None and question.type is not self._question_type:
            return False
        return True

    def _get_question(self):
        if self._current >= self._amount:
            raise StopIteration()

        while True:
            question = next(self._questions)
            if not self._is_valid(question):
                continue

            if self._consume:
                self._client._questions.remove(question)
            self._current += 1
            return question

    def flatten(self):
        questions = []
        while True:
            try:
                questions.append(self._get_question())
            except StopIteration:
                return questions

    def __iter__(self):
        return self

    def __next__(self):
        return self._get_question()

class _AsyncQuestionsIterator:
    __slots__ = ('_client', '_amounts', '_decoder', '_fetched', '_params')

    _DECODERS = {
        None: html.unescape,
        EncodingType.url: parse.unquote,
        EncodingType.base64: lambda decodable: base64.b64decode(decodable).decode()
    }

    def __init__(
        self, client, *,
        amount=10,
        category=None,
        difficulty=None,
        type=None,
        encoding=None,
        token=None
    ):
        self._client = client

        repeat, remainder = divmod(amount, 50)
        self._amounts = iter((*(50,) * repeat, remainder))
        self._decoder = self._DECODERS[encoding]
        self._fetched = iter(())

        self._params = {}
        if category is not None:
            self._params['category'] = category.value
        if difficulty is not None:
            self._params['difficulty'] = difficulty.value
        if type is not None:
            self._params['type'] = type.value
        if encoding is not None:
            self._params['encoding'] = encoding.value
        if token is not None:
            self._params['token'] = token

    def _create_questions(self, payload):
        questions = []
        for data in payload:
            data['name'] = data.pop('category')
            questions.append(Question(self._client, data, self._decoder))
        return questions

    async def _fetch_questions(self):
        try:
            amount = next(self._amounts)
        except StopIteration:
            raise StopAsyncIteration()
        else:
            if amount == 0:
                raise StopAsyncIteration()
            self._params['amount'] = amount

        payload = await self._client._request('GET', 'api.php', params=self._params)
        return self._create_questions(payload['results'])

    async def flatten(self):
        questions = []
        while True:
            try:
                questions.extend(await self._fetch_questions())
            except StopAsyncIteration:
                return questions

    def __aiter__(self):
        return self

    async def __anext__(self):
        while True:
            try:
                return next(self._fetched)
            except StopIteration:
                self._fetched = iter(await self._fetch_questions())
