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
import base64
import html
import urllib.parse
import types
from typing import Dict, List, Mapping, Optional, Union

import aiohttp
import yarl

from .enums import CategoryType, Encoding, Difficulty, QuestionType
from .errors import InvalidParameter, NoResults, TokenEmpty, TokenNotFound
from .objects import Category, CategoryCount, GlobalCount, Question

__all__ = ('Client',)

_category_names = (
    'General Knowledge',
    'Entertainment: Books',
    'Entertainment: Film',
    'Entertainment: Music',
    'Entertainment: Musicals & Theatres',
    'Entertainment: Television',
    'Entertainment: Video Games',
    'Entertainment: Board Games',
    'Science & Nature',
    'Science: Computers',
    'Science: Mathematics',
    'Mythology',
    'Sports',
    'Geography',
    'History',
    'Politics',
    'Art',
    'Celebrities',
    'Animals',
    'Vehicles',
    'Entertainment: Comics',
    'Science: Gadgets',
    'Entertainment: Japanese Anime & Manga',
    'Entertainment: Cartoon & Animations'
)
_category_enums = (
    CategoryType.general_knowledge,
    CategoryType.books,
    CategoryType.film,
    CategoryType.music,
    CategoryType.musicals_and_theatres,
    CategoryType.television,
    CategoryType.video_games,
    CategoryType.board_games,
    CategoryType.nature,
    CategoryType.computers,
    CategoryType.mathematics,
    CategoryType.mythology,
    CategoryType.sports,
    CategoryType.geography,
    CategoryType.history,
    CategoryType.politics,
    CategoryType.art,
    CategoryType.celebrities,
    CategoryType.animals,
    CategoryType.vehicles,
    CategoryType.comics,
    CategoryType.gadgets,
    CategoryType.anime_and_manga,
    CategoryType.cartoon_and_animations
)

_category_by_names = {}
_category_by_ids = {}
for _name, _enum in zip(_category_names, _category_enums):
    _category = Category(_name, _enum.value, _enum)
    _category_by_names[_name] = _category
    _category_by_ids[_enum.value] = _category

_decoders = {
    Encoding.url: urllib.parse.unquote,
    Encoding.base64: lambda s: base64.b64decode(s).decode()
}
_fields = (
    'category',
    'correct_answer'
)
_enum_fields = (
    ('type', QuestionType),
    ('difficulty', Difficulty)
)

_errors = {
    1: NoResults,
    2: InvalidParameter,
    3: TokenNotFound,
    4: TokenEmpty
}


async def _wait():
    await asyncio.sleep(1)


class Client:
    __slots__ = (
        'session',
        '__token',
        '__categories',
        '__category_count',
        '__global_count'
    )

    BASE_URL = yarl.URL('https://opentdb.com')

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None
    ) -> None:

        self.session = session or aiohttp.ClientSession(raise_for_status=True)
        self.__token = None
        self.__categories = {}
        self.__category_count = {}
        self.__global_count = {}

    async def _fetch(self, endpoint, *args, **kwargs):
        async with self.session.get(self.BASE_URL / endpoint, *args, **kwargs) as response:
            data = await response.json()

        response_code = data.pop('response_code', 0)
        if response_code != 0:
            raise _errors[response_code]
        return data

    # Token

    @property
    def token(self) -> Optional[str]:
        return self.__token

    async def fetch_token(self) -> str:
        parameters = {'command': 'request'}
        data = await self._fetch('api_token.php', params=parameters)
        return data['token']

    async def populate_token(self) -> None:
        if self.__token is None:
            self.__token = await self.fetch_token()

    async def reset_token(
        self,
        token: Optional[str] = None
    ) -> str:

        is_internal_token = token is None
        token = token or self.__token

        parameters = {
            'command': 'reset',
            'token': token
        }
        data = await self._fetch('api_token.php', params=parameters)

        new_token = data['token']
        if is_internal_token:
            self.__token = new_token
        return new_token

    # Question

    async def fetch_questions(
        self,
        amount: int = 10,
        category: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None,
        type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None,
        token: Optional[str] = None
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

            entry['category'] = _category_by_names[entry['category']]
            for field, enum in _enum_fields:
                entry[field] = enum(decoder(entry[field]))

            questions.append(Question(**entry))
        return questions

    async def get_questions(
        self,
        amount: int = 10,
        category: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None,
        type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None
    ) -> List[Question]:

        while True:
            try:
                return await self.fetch_questions(
                    amount, category, difficulty, type, encoding, self.__token
                )
            except TokenEmpty:
                await self.reset_token()

    # Category

    @property
    def categories(self) -> Mapping[CategoryType, Category]:
        return types.MappingProxyType(self.__categories)

    async def fetch_categories(self) -> Dict[CategoryType, Category]:
        data = await self._fetch('api_category.php')

        categories = {}
        for entry in data['trivia_categories']:
            type = CategoryType(entry['id'])
            entry['type'] = type
            categories[type] = Category(**entry)
        return categories

    async def populate_categories(self) -> None:
        if not self.__categories:
            self.__categories = await self.fetch_categories()

    def get_category(
        self,
        type: CategoryType
    ) -> Category:

        return self.__categories.get(type)

    # Category Count

    @property
    def category_count(self) -> Mapping[CategoryType, CategoryCount]:
        return types.MappingProxyType(self.__category_count)

    async def fetch_category_count(
        self,
        category: CategoryType
    ) -> CategoryCount:

        parameters = {'category': category.value}
        data = await self._fetch('api_count.php', params=parameters)

        count = data['category_question_count']
        return CategoryCount(
            _category_by_ids[category.value],
            count['total_question_count'],
            count['total_easy_question_count'],
            count['total_medium_question_count'],
            count['total_hard_question_count']
        )

    async def populate_category_count(
        self,
        category: CategoryType
    ) -> None:

        count = self.__category_count
        if not count.get(category):
            count[category] = await self.fetch_category_count(category)

    async def fetch_all_category_count(self) -> Dict[CategoryType, CategoryCount]:
        count = {}
        for enum in _category_enums:
            count[enum] = await self.fetch_category_count(enum)
        return count

    async def populate_all_category_count(self) -> None:
        if not self.__category_count:
            self.__category_count = await self.fetch_all_category_count()

    def get_category_count(
        self,
        category: CategoryType
    ) -> CategoryCount:

        return self.__category_count.get(category)

    # Global Count

    @property
    def global_count(self) -> Mapping[Union[CategoryType, str], GlobalCount]:
        return types.MappingProxyType(self.__global_count)

    async def fetch_global_count(self) -> Dict[Union[CategoryType, str], GlobalCount]:
        data = await self._fetch('api_count_global.php')

        global_count = {}

        overall_count = data['overall']
        global_count['overall'] = GlobalCount(
            'overall',
            overall_count['total_num_of_questions'],
            overall_count['total_num_of_pending_questions'],
            overall_count['total_num_of_verified_questions'],
            overall_count['total_num_of_rejected_questions']
        )

        categories = data['categories']
        for id, count in categories.items():
            category = _category_by_ids[int(id)]
            global_count[category.type] = GlobalCount(
                category,
                count['total_num_of_questions'],
                count['total_num_of_pending_questions'],
                count['total_num_of_verified_questions'],
                count['total_num_of_rejected_questions']
            )

        return global_count

    async def populate_global_count(self) -> None:
        if not self.__global_count:
            self.__global_count = await self.fetch_global_count()

    def get_global_count(
        self,
        category: Union[CategoryType, str]
    ) -> GlobalCount:

        return self.__global_count.get(category)

    # Utility

    async def populate(self) -> None:
        methods = (
            self.populate_token,
            self.populate_categories,
            self.populate_all_category_count,
            self.populate_global_count
        )
        for method in methods:
            await method()
            await _wait()

    # Session

    async def close(self) -> None:
        await self.session.close()
