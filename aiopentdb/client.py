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

import base64
import html
import urllib.parse
from typing import Dict, List, Optional

import aiohttp
import yarl

from .enums import CategoryType, Encoding, Difficulty, QuestionType
from .errors import InvalidParameter, NoResults, TokenEmpty, TokenNotFound
from .objects import Category, CategoryCount, GlobalCount, Question

__all__ = ('Client',)

_category_enums = {
    'General Knowledge': CategoryType.general_knowledge,
    'Entertainment: Books': CategoryType.books,
    'Entertainment: Film': CategoryType.film,
    'Entertainment: Music': CategoryType.music,
    'Entertainment: Musicals & Theatres': CategoryType.musicals_and_theatres,
    'Entertainment: Television': CategoryType.television,
    'Entertainment: Video Games': CategoryType.video_games,
    'Entertainment: Board Games': CategoryType.board_games,
    'Science & Nature': CategoryType.nature,
    'Science: Computers': CategoryType.computers,
    'Science: Mathematics': CategoryType.mathematics,
    'Mythology': CategoryType.mythology,
    'Sports': CategoryType.sports,
    'Geography': CategoryType.geography,
    'History': CategoryType.history,
    'Politics': CategoryType.politics,
    'Art': CategoryType.art,
    'Celebrities': CategoryType.celebrities,
    'Animals': CategoryType.animals,
    'Vehicles': CategoryType.vehicles,
    'Entertainment: Comics': CategoryType.comics,
    'Science: Gadgets': CategoryType.gadgets,
    'Entertainment: Japanese Anime & Manga': CategoryType.anime_and_manga,
    'Entertainment: Cartoon & Animations': CategoryType.cartoon_and_animations
}
_category_objects = {
    enum.value: Category(name, enum.value, enum) for name, enum in _category_enums.items()
}

_decoders = {
    Encoding.url: urllib.parse.unquote, Encoding.base64: lambda s: base64.b64decode(s).decode()
}

_fields = ('category', 'correct_answer')
_enum_fields = (('type', QuestionType), ('difficulty', Difficulty))

_errors = {1: NoResults, 2: InvalidParameter, 3: TokenNotFound, 4: TokenEmpty}


class Client:
    __slots__ = ('session', 'token', 'categories', 'category_count', 'global_count')

    BASE_URL = yarl.URL('https://opentdb.com')

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.session = session or aiohttp.ClientSession(raise_for_status=True)
        self.token: Optional[str] = None
        self.categories: Optional[List[Category]] = None
        self.category_count: Dict[int, CategoryCount] = {}
        self.global_count: Optional[List[GlobalCount]] = None

    async def _fetch(self, endpoint, *args, **kwargs):
        async with self.session.get(self.BASE_URL / endpoint, *args, **kwargs) as response:
            data = await response.json()

        response_code = data.pop('response_code', 0)
        if response_code != 0:
            raise _errors[response_code]
        return data

    # Token

    async def fetch_token(self) -> str:
        parameters = {'command': 'request'}
        data = await self._fetch('api_token.php', params=parameters)
        return data['token']

    async def get_token(self) -> str:
        if self.token is None:
            self.token = await self.fetch_token()
        return self.token

    async def reset_token(self, token: Optional[str] = None) -> str:
        is_internal_token = token is None
        token = token or self.token

        parameters = {'command': 'reset', 'token': token}
        data = await self._fetch('api_token.php', params=parameters)

        token = data['token']
        if is_internal_token:
            self.token = token
        return token

    # Question

    async def fetch_questions(
        self, amount: int = 10, category: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None, type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None, token: Optional[str] = None
    ) -> List[Question]:

        if amount < 1 and amount > 50:
            raise ValueError("'amount' must be between 1 and 50")

        parameters = {'amount': amount}
        if category is not None:
            parameters['category'] = category.value
        if difficulty is not None:
            parameters['difficulty'] = difficulty.value
        if type is not None:
            parameters['type'] = type.value
        if encoding is not None:
            parameters['encode'] = encoding.value
        if token is not None:
            parameters['token'] = token

        data = await self._fetch('api.php', params=parameters)

        questions = []
        decoder = _decoders.get(encoding, html.unescape)
        for entry in data['results']:
            entry['content'] = decoder(entry.pop('question'))
            for field in _fields:
                entry[field] = decoder(entry[field])

            incorrect_answers = entry['incorrect_answers']
            for index, incorrect_answer in enumerate(incorrect_answers):
                incorrect_answers[index] = decoder(incorrect_answer)

            category_enum = _category_enums[entry['category']]
            entry['category'] = _category_objects[category_enum.value]
            for field, enum in _enum_fields:
                entry[field] = enum(decoder(entry[field]))

            questions.append(Question(**entry))
        return questions

    async def get_questions(
        self, amount: int = 10, category: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None, type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None
    ) -> List[Question]:

        while True:
            token = await self.get_token()
            try:
                return await self.fetch_questions(
                    amount, category, difficulty, type, encoding, token
                )
            except TokenEmpty:
                await self.reset_token()

    # Category

    async def fetch_categories(self) -> List[Category]:
        data = await self._fetch('api_category.php')

        categories = []
        for entry in data['trivia_categories']:
            entry['type'] = CategoryType(entry['id'])
            categories.append(Category(**entry))
        return categories

    async def get_categories(self) -> List[Category]:
        if self.categories is None:
            self.categories = await self.fetch_categories()
        return self.categories

    async def fetch_category_count(self, category: CategoryType) -> CategoryCount:
        parameters = {'category': category.value}
        data = await self._fetch('api_count.php', params=parameters)

        category_count = data['category_question_count']
        return CategoryCount(
            _category_objects[category.value], category_count['total_question_count'],
            category_count['total_easy_question_count'],
            category_count['total_medium_question_count'],
            category_count['total_hard_question_count']
        )

    async def get_category_count(self, category: CategoryType) -> CategoryCount:
        if id in self.category_count:
            return self.category_count[category.value]

        category_count = await self.fetch_category_count(category)
        self.category_count[category.value] = category_count
        return category_count

    async def fetch_global_count(self) -> List[GlobalCount]:
        data = await self._fetch('api_count_global.php')

        global_count = []

        overall_count = data['overall']
        global_count.append(
            GlobalCount(
                'overall', overall_count['total_num_of_questions'],
                overall_count['total_num_of_pending_questions'],
                overall_count['total_num_of_verified_questions'],
                overall_count['total_num_of_rejected_questions']
            )
        )

        categories = data['categories']
        for id, count in categories.items():
            global_count.append(
                GlobalCount(
                    _category_objects[int(id)], count['total_num_of_questions'],
                    count['total_num_of_pending_questions'],
                    count['total_num_of_verified_questions'],
                    count['total_num_of_rejected_questions']
                )
            )

        return global_count

    async def get_global_count(self) -> List[GlobalCount]:
        if self.global_count is None:
            self.global_count = await self.fetch_global_count()
        return self.global_count

    # Session

    async def close(self) -> None:
        await self.session.close()
