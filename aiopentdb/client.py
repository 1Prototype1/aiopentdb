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
import itertools
import urllib.parse

import aiohttp
import yarl

from .enums import CategoryType, Encoding
from .errors import InvalidParameter, NoResults, RequestError, TokenEmpty, TokenNotFound
from .objects import Category, Count, GlobalCount, Question

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


class Client:
    """Class for interacting with the OpenTDB API and handling caches.

    Parameters
    ----------

    session: Optional[:class:`aiohttp.ClientSession`]
        Session to use for all HTTP requests.
        Defaults to ``aiohttp.ClientSession(raise_for_status=True)``.

    max_questions: :class:`int`
        Amount of questions to cache.
        Defaults to ``50``.

        .. versionadded:: 0.4.0

    Attributes
    ----------

    session: :class:`aiohttp.ClientSession`
        Session to use for all HTTP requests.
    """

    _BASE_URL = yarl.URL('https://opentdb.com')
    _QUESTION_MAX = 50
    _DECODERS = {
        Encoding.url: urllib.parse.unquote,
        Encoding.base64: lambda decodable: base64.b64decode(decodable).decode()
    }
    _ERRORS = {
        1: NoResults,
        2: InvalidParameter,
        3: TokenNotFound,
        4: TokenEmpty
    }

    _CATEGORY_BY_NAMES = {}
    _CATEGORY_BY_IDS = {}

    for _name, _enum in zip(_category_names, _category_enums):
        _data = {'name': _name, 'id': _enum.value}
        _category = Category(_data)
        _CATEGORY_BY_NAMES[_name] = _category
        _CATEGORY_BY_IDS[_enum.value] = _category

    del _name
    del _enum
    del _data
    del _category

    def __init__(self, session=None, max_questions=50):
        self.session = session or aiohttp.ClientSession(raise_for_status=True)
        self._token = None
        self._questions = collections.deque(maxlen=max_questions)
        self._categories = {}
        self._counts = {}
        self._global_counts = {}

    @property
    def token(self):
        """Optional[:class:`str`]: Current session token."""

        return self._token

    @property
    def questions(self):
        """List[:class:`.Question`]: List of cached questions."""

        return list(self._questions)

    @property
    def categories(self):
        """List[:class:`.Category`]: List of cached categories."""

        return list(self._categories.values())

    @property
    def counts(self):
        """List[:class:`.Count`]: List of cached counts."""

        return list(self._counts.values())

    @property
    def global_counts(self):
        """List[:class:`.GlobalCount`]: List of cached global counts."""

        return list(self._global_counts.values())

    async def populate_cache(self):
        """Populates all internal caches. This method calls every population related methods internally.

        .. warning::

            This method could be spammy for the API as it does not delay each populating process.
        """

        methods = (
            self.populate_token,
            self.populate_questions,
            self.populate_categories,
            self.populate_counts,
            self.populate_global_counts
        )
        for method in methods:
            await method()

    # Session

    async def _fetch(self, endpoint, *args, **kwargs):
        try:
            async with self.session.get(self._BASE_URL / endpoint, *args, **kwargs) as response:
                data = await response.json()
        except aiohttp.ClientResponseError as error:
            raise RequestError(error.message)

        if data is None:
            raise RequestError('Unknown error occured')

        response_code = data.pop('response_code', 0)
        if response_code != 0:
            raise self._ERRORS[response_code]
        return data

    async def close(self):
        """Closes the internal session."""

        await self.session.close()

    # Token

    async def fetch_token(self):
        """Fetches a new session token.

        Returns
        -------

        :class:`str`
            New session token.
        """

        parameters = {'command': 'request'}
        data = await self._fetch('api_token.php', params=parameters)
        return data['token']

    async def populate_token(self):
        """Populates the internal session token. This method calls :meth:`.Client.fetch_token` internally."""

        if self._token is None:
            self._token = await self.fetch_token()

    async def reset_token(self, token=None):
        """Resets a session token.

        Parameters
        ----------

        token: Optional[:class:`str`]
            Session token to reset.
            If not set, defaults to :attr:`.Client.token` and replace it with the new session token.

        Returns
        -------

        :class:`str`
            New session token.
        """

        parameters = {
            'command': 'reset',
            'token': token or self._token
        }
        data = await self._fetch('api_token.php', params=parameters)

        new_token = data['token']
        if token is None:
            self._token = new_token
        return new_token

    # Question

    def _get_amounts(self, amount):
        repeat, remaining = divmod(amount, self._QUESTION_MAX)
        amounts = (*itertools.repeat(self._QUESTION_MAX, repeat),)
        if remaining:
            amounts += (remaining,)
        return amounts

    async def fetch_questions(
        self,
        amount=10,
        category_type=None,
        difficulty=None,
        question_type=None,
        encoding=None,
        token=None
    ):
        """Fetches questions.

        Parameters
        ----------

        amount: :class:`int`
            Amount of question to fetch.
            Defaults to ``10``.

            .. warning::

                Only 50 questions can be fetched per request.

            .. versionchanged:: 0.4.0

                Remove limit of the question amount.

        category_type: Optional[:class:`.CategoryType`]
            Type of the question category to fetch.

        difficulty: Optional[:class:`.Difficulty`]
            Difficulty of the question to fetch.

        question_type: Optional[:class:`.QuestionType`]
            Type of the question to fetch.

        encoding: Optional[:class:`.Encoding`]
            Encoding of the response to use.

            .. note::

                This does not affect result.

        token: Optional[:class:`str`]
            Session token to use.
            Defaults to :attr:`.Client.token` if exist.

        Returns
        -------

        List[:class:`.Question`]
            List of fetched questions.
        """

        questions = []

        for actual_amount in self._get_amounts(amount):
            parameters = {'amount': actual_amount}
            if category_type is not None:
                parameters['category'] = category_type.value
            if difficulty is not None:
                parameters['difficulty'] = difficulty.value
            if question_type is not None:
                parameters['type'] = question_type.value
            if encoding is not None:
                parameters['encode'] = encoding.value

            if token is None:
                if self._token is not None:
                    parameters['token'] = self._token
            else:
                parameters['token'] = token
            data = await self._fetch('api.php', params=parameters)

            decoder = self._DECODERS.get(encoding, html.unescape)
            for entry in data['results']:
                questions.append(Question(self, entry, decoder))

        return questions

    async def generate_questions(
        self,
        amount=10,
        category_type=None,
        difficulty=None,
        question_type=None,
        encoding=None,
        token=None
    ):
        """Generates questions. Unlike :meth:`.Client.fetch_questions`, this method will make requests one by one. The
        following example would only make 2 requests instead of 4 as it stops at 75 questions:

        .. code:: py

            count = 0
            async for question in client.generate_questions(amount=200):
                if count >= 75:
                    break
                count += 1

        .. versionadded:: 0.5.0

        Parameters
        ----------

        amount: :class:`int`
            Amount of question to fetch.
            Defaults to ``10``.

            .. warning::

                Only 50 questions can be generated per request.

        category_type: Optional[:class:`.CategoryType`]
            Type of the question category to fetch.

        difficulty: Optional[:class:`.Difficulty`]
            Difficulty of the question to fetch.

        question_type: Optional[:class:`.QuestionType`]
            Type of the question to fetch.

        encoding: Optional[:class:`.Encoding`]
            Encoding of the response to use.

            .. note::

                This does not affect result.

        token: Optional[:class:`str`]
            Session token to use.
            Defaults to :attr:`.Client.token` if exist.

        Yields
        ------
        :class:`.Question`
            Generated question.
        """

        for actual_amount in self._get_amounts(amount):
            for question in await self.fetch_questions(
                actual_amount, category_type, difficulty, question_type, encoding, token
            ):
                yield question

    async def populate_questions(
        self,
        category_type=None,
        difficulty=None,
        question_type=None,
        encoding=None,
        token=None
    ):
        """Populates the internal question cache. This method calls :meth:`.Client.fetch_questions` internally.

        Parameters
        ----------

        category_type: Optional[:class:`.CategoryType`]
            Type of the question category to fetch.

        difficulty: Optional[:class:`.Difficulty`]
            Difficulty of the question to fetch.

        question_type: Optional[:class:`.QuestionType`]
            Type of the question to fetch.

        encoding: Optional[:class:`.Encoding`]
            Encoding of the response to use.

            .. note::

                This does not affect result.

        token: Optional[:class:`str`]
            Session token to use.
            Defaults to :attr:`.Client.token` if exist.
        """

        questions = self._questions
        amount = questions.maxlen - len(questions)
        if amount < 1:
            return

        new_questions = await self.fetch_questions(amount, category_type, difficulty, question_type, encoding, token)
        questions.extend(new_questions)

    def get_questions(
        self,
        amount=10,
        category_type=None,
        difficulty=None,
        question_type=None,
    ):
        """Retrieves questions from the internal cache. This also removes them from the cache.

        Parameters
        ----------

        amount: :class:`int`
            Amount of question to fetch.
            Defaults to ``10``.

            .. versionchanged:: 0.4.0

                Remove limit of the question amount.

        category_type: Optional[:class:`.CategoryType`]
            Type of the question category to fetch.

        difficulty: Optional[:class:`.Difficulty`]
            Difficulty of the question to fetch.

        question_type: Optional[:class:`.QuestionType`]
            Type of the question to fetch.

        Returns
        -------

        List[:class:`.Question`]
            List of cached questions.
        """

        questions = self._questions
        retrieved_questions = []

        count = 0
        for question in self.questions:
            if count >= amount:
                break

            if category_type is not None and question.category.type != category_type:
                continue
            if difficulty is not None and question.difficulty != difficulty:
                continue
            if question_type is not None and question.type != question_type:
                continue

            questions.remove(question)
            retrieved_questions.append(question)
            count += 1

        return retrieved_questions

    # Category

    async def fetch_categories(self):
        """Fetches all categories.

        Returns
        -------

        Dict[:class:`.CategoryType`, :class:`.Category`]
            Dict of fetched categories.
        """

        data = await self._fetch('api_category.php')

        categories = {}
        for entry in data['trivia_categories']:
            categories[type] = Category(entry)
        return categories

    async def populate_categories(self):
        """Populates the internal category cache. This method calls :meth:`.Client.fetch_categories` internally."""

        if not self._categories:
            self._categories = await self.fetch_categories()

    def get_category(self, category_type):
        """Retrieves a :class:`.Category` from the internal cache.

        Parameters
        ----------

        category_type: :class:`.CategoryType`
            Type of the category to retrieve.

        Returns
        -------

        Optional[:class:`.Category`]
            Cached category.
        """

        return self._categories.get(category_type)

    # Count

    async def fetch_count(self, category_type):
        """Fetches a :class:`.Count`.

        Parameters
        ----------

        category_type: :class:`.CategoryType`
            Type of the category to fetch.

        Returns
        -------

        :class:`.Count`
            Fetched count.
        """

        parameters = {'category': category_type.value}
        data = (await self._fetch('api_count.php', params=parameters))['category_question_count']
        data['category'] = category_type.value
        return Count(self, data)

    async def populate_count(self, category_type):
        """Populates the internal count cache. This method calls :meth:`.Client.fetch_count` internally.

        Parameters
        ----------

        category_type: :class:`.CategoryType`
            Type of the category to populate.
        """

        counts = self._counts
        if not counts.get(category_type):
            counts[category_type] = await self.fetch_count(category_type)

    async def fetch_counts(self):
        """Fetches all counts.

        .. warning::

            This method could be spammy for the API as it calls :meth:`.Client.fetch_counts` on every category types.

        Returns
        -------

        Dict[:class:`.CategoryType`, :class:`.Count`]
            Dict of fetched counts.
        """

        counts = {}
        for enum in _category_enums:
            counts[enum] = await self.fetch_count(enum)
        return counts

    async def populate_counts(self):
        """Populates all internal count caches. This method calls :meth:`.Client.fetch_counts` internally."""

        if not self._counts:
            self._counts = await self.fetch_counts()

    def get_count(self, category_type):
        """Retrieves a :class:`.Count` from the internal cache.

        Parameters
        ----------

        category_type: :class:`.CategoryType`
            Type of the category to retrieve.

        Returns
        -------

        Optional[:class:`.Count`]
            Cached count.
        """

        return self._counts.get(category_type)

    # Global Count

    async def fetch_global_counts(self):
        """Fetches all global counts.

        Returns
        -------

        Dict[Union[:class:`.CategoryType`, :class:`str`], :class:`.GlobalCount`]
            Dict of fetched global counts.
        """

        data = await self._fetch('api_count_global.php')
        global_counts = {}

        for id, entry in data['categories'].items():
            entry['category'] = int(id)
            global_count = GlobalCount(self, entry)
            global_counts[global_count.category.type] = global_count

        global_counts['overall'] = GlobalCount(self, data['overall'])
        return global_counts

    async def populate_global_counts(self):
        """Populates the internal global count cache. This method calls :meth:`.Client.fetch_global_counts` internally."""

        if not self._global_counts:
            self._global_counts = await self.fetch_global_counts()

    def get_global_count(self, category_type):
        """Retrieves a :class:`.GlobalCount` from the internal cache.

        Parameters
        ----------

        category_type: Union[:class:`.CategoryType`, :class:`str`]
            Type of the category to retrieve.

        Returns
        -------

        Optional[:class:`.GlobalCount`]
            Cached global count.
        """

        return self._global_counts.get(category_type)
