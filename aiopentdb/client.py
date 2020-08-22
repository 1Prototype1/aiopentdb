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
import collections
import html
import urllib.parse
from typing import Dict, List, Optional, Union

import aiohttp
import yarl

from .enums import CategoryType, Encoding, Difficulty, QuestionType
from .errors import InvalidParameter, NoResults, RequestError, TokenEmpty, TokenNotFound
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


class Client:
    """Represents an OpenTDB client.

    Parameters
    ----------
    session: `Optional[aiohttp.ClientSession]`
        Session to use for HTTP requests. If not set, a new session will be created instead.

    Attributes
    ----------
    session: `aiohttp.ClientSession`
        Session to use for HTTP requests.
    """

    _BASE_URL = yarl.URL('https://opentdb.com')

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None
    ) -> None:

        self.session = session or aiohttp.ClientSession(raise_for_status=True)
        self.__token = None
        self.__questions = collections.deque(maxlen=50)
        self.__categories = {}
        self.__category_count = {}
        self.__global_count = {}

    async def populate_cache(self) -> None:
        """Populates the internal cache."""

        methods = (
            self.populate_token,
            self.populate_questions,
            self.populate_categories,
            self.populate_all_category_count,
            self.populate_global_count
        )
        for method in methods:
            await method()

    # Session

    async def _fetch(self, endpoint, *args, **kwargs):
        async with self.session.get(self._BASE_URL / endpoint, *args, **kwargs) as response:
            data = await response.json()
        if data is None:
            raise RequestError('Unable to fetch')

        response_code = data.pop('response_code', 0)
        if response_code != 0:
            raise _errors[response_code]
        return data

    async def close(self) -> None:
        """Closes the internal session."""

        await self.session.close()

    # Token

    @property
    def token(self) -> Optional[str]:
        """Current session token.

        Returns
        ----------
        `Optional[str]`
            Current session token.
        """

        return self.__token

    async def fetch_token(self) -> str:
        """Fetches a new session token.

        Returns
        ----------
        `str`
            New session token.
        """

        parameters = {'command': 'request'}
        data = await self._fetch('api_token.php', params=parameters)
        return data['token']

    async def populate_token(self) -> None:
        """Populates the internal token."""

        if self.__token is None:
            self.__token = await self.fetch_token()

    async def reset_token(
        self,
        token: Optional[str] = None
    ) -> str:
        """Resets a session token.

        Parameters
        ----------
        token: `Optional[str]`
            Session token to reset. If not set, the internal session token will be used instead.

        Returns
        ----------
        `str`
            New session token.
        """

        parameters = {
            'command': 'reset',
            'token': token or self.__token
        }
        data = await self._fetch('api_token.php', params=parameters)

        new_token = data['token']
        if token is None:
            self.__token = new_token
        return new_token

    # Question

    @property
    def questions(self) -> List[Question]:
        """List of cached questions.

        Returns
        ----------
        `List[Question]`
            List of cached questions.
        """

        return list(self.__questions)

    async def fetch_questions(
        self,
        amount: int = 10,
        category_type: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None,
        question_type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None,
        token: Optional[str] = None
    ) -> List[Question]:
        """Fetches new questions.

        Parameters
        ----------
        amount: `int`
            Amount of question to fetch. Must be between 1 and 50. Defaults to 10.
        category_type: `Optional[CategoryType]`
            Type of question's category to fetch.
        difficulty: `Optional[Difficulty]`
            Difficulty of question to fetch.
        question_type: `Optional[QuestionType]`
            Type of question to fetch.
        encoding: `Optional[Encoding]`
            Encoding of response to be used when fetching.
        token: `Optional[str]`
            Session token to be used when fetching.

        Returns
        ----------
        `List[Question]`
            List of new questions.
        """

        if amount < 1 and amount > 50:
            raise ValueError("'amount' must be between 1 and 50")

        parameters = {'amount': amount}
        if category_type is not None:
            parameters['category'] = category_type.value
        if difficulty is not None:
            parameters['difficulty'] = difficulty.value
        if question_type is not None:
            parameters['type'] = question_type.value
        if encoding is not None:
            parameters['encode'] = encoding.value
        if token is None and self.__token is not None:
            parameters['token'] = self.__token
        else:
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

    async def populate_questions(
        self,
        category_type: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None,
        question_type: Optional[QuestionType] = None,
        encoding: Optional[Encoding] = None,
        token: Optional[str] = None
    ) -> None:
        """Populates the internal question cache.

        Parameters
        ----------
        category_type: `Optional[CategoryType]`
            Type of question's category to fetch.
        difficulty: `Optional[Difficulty]`
            Difficulty of question to fetch.
        question_type: `Optional[QuestionType]`
            Type of question to fetch.
        encoding: `Optional[Encoding]`
            Encoding of response to be used when fetching.
        token: `Optional[str]`
            Session token to be used when fetching.
        """

        questions = self.__questions
        amount = questions.maxlen - len(questions)
        if amount < 1:
            return

        new_questions = await self.fetch_questions(
            amount, category_type, difficulty, question_type, encoding, token
        )
        questions.extend(new_questions)

    def get_questions(
        self,
        amount: int = 10,
        category_type: Optional[CategoryType] = None,
        difficulty: Optional[Difficulty] = None,
        question_type: Optional[QuestionType] = None,
    ) -> List[Question]:
        """Retrieves questions from the internal cache. This method also removes
        retrieved questions from the cache, allowing new questions to be cached.

        Parameters
        ----------
        amount: `int`
            Amount of question to fetch. Must be between 1 and 50. Defaults to 10.
        category_type: `Optional[CategoryType]`
            Type of question's category to fetch.
        difficulty: `Optional[Difficulty]`
            Difficulty of question to fetch.
        question_type: `Optional[QuestionType]`
            Type of question to fetch.

        Returns
        ----------
        `List[Question]`
            List of cached questions.
        """

        actual_questions = self.__questions
        retrieved_questions = []
        count = 0
        for question in self.questions:
            if count >= amount:
                break

            if (
                category_type is not None
                and question.category.type != category_type
            ):
                continue

            if (
                difficulty is not None
                and question.difficulty != difficulty
            ):
                continue

            if (
                question_type is not None
                and question.type != question_type
            ):
                continue

            actual_questions.remove(question)
            retrieved_questions.append(question)
            count += 1
        return retrieved_questions

    # Category

    @property
    def categories(self) -> List[Category]:
        """List of cached categories.

        Returns
        ----------
        `List[Category]`
            List of cached categories.
        """

        return list(self.__categories.values())

    async def fetch_categories(self) -> Dict[CategoryType, Category]:
        """Fetches all categories.

        Returns
        ----------
        `Dict[CategoryType, Category]`
            Dict of fetched categories.
        """

        data = await self._fetch('api_category.php')

        categories = {}
        for entry in data['trivia_categories']:
            type = CategoryType(entry['id'])
            entry['type'] = type
            categories[type] = Category(**entry)
        return categories

    async def populate_categories(self) -> None:
        """Populates the internal category cache."""

        if not self.__categories:
            self.__categories = await self.fetch_categories()

    def get_category(
        self,
        category_type: CategoryType
    ) -> Optional[Category]:
        """Retrieves a category from the internal cache.

        Parameters
        ----------
        category_type: `CategoryType`
            Type of category to retrieve.

        Returns
        ----------
        `Optional[Category]`
            Cached category.
        """

        return self.__categories.get(category_type)

    # Category Count

    @property
    def category_count(self) -> List[CategoryCount]:
        """List of cached category's question count.

        Returns
        ----------
        `List[CategoryCount]`
            List of cached category's question count.
        """

        return list(self.__category_count.values())

    async def fetch_category_count(
        self,
        category_type: CategoryType
    ) -> CategoryCount:
        """Fetches a category's question count.

        Parameters
        ----------
        category_type: `CategoryType`
            Type of category to fetch.

        Returns
        ----------
        `CategoryCount`
            Fetched category's question count.
        """

        parameters = {'category': category_type.value}
        data = await self._fetch('api_count.php', params=parameters)

        count = data['category_question_count']
        return CategoryCount(
            _category_by_ids[category_type.value],
            count['total_question_count'],
            count['total_easy_question_count'],
            count['total_medium_question_count'],
            count['total_hard_question_count']
        )

    async def populate_category_count(
        self,
        category_type: CategoryType
    ) -> None:
        """Populates the internal category's question count.

        Parameters
        ----------
        category_type: `CategoryType`
            Type of category to populate.
        """

        count = self.__category_count
        if not count.get(category_type):
            count[category_type] = await self.fetch_category_count(category_type)

    async def fetch_all_category_count(self) -> Dict[CategoryType, CategoryCount]:
        """Fetches all category's question count.

        Returns
        ----------
        `Dict[CategoryType, CategoryCount]`
            Dict of fetched category's question count.
        """

        count = {}
        for enum in _category_enums:
            count[enum] = await self.fetch_category_count(enum)
        return count

    async def populate_all_category_count(self) -> None:
        """Populates all of the the internal category's question count."""

        if not self.__category_count:
            self.__category_count = await self.fetch_all_category_count()

    def get_category_count(
        self,
        category_type: CategoryType
    ) -> Optional[CategoryCount]:
        """Retrieves a category's question count from the internal cache.

        Parameters
        ----------
        category_type: `CategoryType`
            Type of category to retrieve.

        Returns
        ----------
        `Optional[CategoryCount]`
            Cached category question's count.
        """

        return self.__category_count.get(category_type)

    # Global Count

    @property
    def global_count(self) -> List[GlobalCount]:
        """List of cached global category's question count.

        Returns
        ----------
        `List[GlobalCount]`
            List of cached global category's question count.
        """

        return list(self.__global_count.values())

    async def fetch_global_count(self) -> Dict[Union[CategoryType, str], GlobalCount]:
        """Fetches all global category's question count.

        Returns
        ----------
        `Dict[Union[CategoryType, str], GlobalCount]`
            Dict of fetched global category's question count.
        """

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
        """Populates the internal global category's question count cache."""

        if not self.__global_count:
            self.__global_count = await self.fetch_global_count()

    def get_global_count(
        self,
        category_type: Union[CategoryType, str]
    ) -> Optional[GlobalCount]:
        """Retrieves a global category's question count from the internal cache.

        Parameters
        ----------
        category_type: `Union[CategoryType, str]`
            Type category to retrieve.

        Returns
        ----------
        `Optional[GlobalCount]`
            Cached global category's question count.
        """

        return self.__global_count.get(category_type)
