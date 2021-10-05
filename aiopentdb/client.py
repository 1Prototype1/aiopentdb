"""
    aiopentdb.client
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import collections

import aiohttp
import attr
import yarl

from .enums import CategoryType
from .errors import InvalidParameter, NoResults, TokenEmpty, TokenNotFound
from .iterators import _AsyncQuestionsIterator, _QuestionsIterator
from .objects import Category, Count, GlobalCount

__all__ = ('Settings', 'Client')

@attr.s(slots=True)
class Settings:
    """Dataclass representing a cache settings for :class:`.Client`.

    This dataclass is used to configure how the client's internal cache should be populated.

    Attributes
    ----------
    token: :class:`bool`
        Denotes whether to populate :class:`.Client` internal token cache or not.
    questions: :class:`bool`
        Denotes whether to populate :class:`.Client` internal question cache or not.
    counts: :class:`bool`
        Denotes whether to populate :class:`.Client` internal count cache or not.
    global_counts: :class:`bool`
        Denotes whether to populate :class:`.Client` internal global count cache or not.
    overwrite: :class:`bool`
        Denotes whether to replace :class:`.Client` current cached entries with the new
        entries when the internal cache has already been populated or not.

        This also changes how the internal question cache should be populated. When this is set to
        ``True``, populating the cache will replace all the cached questions with the new
        questions. When this is set to ``False``, only empty slots of the cache will be populated
        with the new questions.
    category: Optional[:class:`.CategoryType`]
        Category of the questions to be cached.
    difficulty: Optional[:class:`.DifficultyType`]
        Difficulty of the questions to be cached.
    question: Optional[:class:`.QuestionType`]
        Type of the questions to be cached.
    encoding: Optional[:class:`.EncodingType`]
        Encoding of the API responses to be used.
    """

    token = attr.ib(False, kw_only=True)
    questions = attr.ib(False, kw_only=True)
    categories = attr.ib(False, kw_only=True)
    counts = attr.ib(False, kw_only=True)
    global_counts = attr.ib(False, kw_only=True)

    overwrite = attr.ib(False, kw_only=True)

    category = attr.ib(None, kw_only=True)
    difficulty = attr.ib(None, kw_only=True)
    question = attr.ib(None, kw_only=True)
    encoding = attr.ib(None, kw_only=True)

class Client:
    """Class representing an OpenTDB client.

    This class is used to interact with the API and handle cache.

    Parameters
    ----------
    session: Optional[:class:`aiohttp.ClientSession`]
        Session to be used when performing HTTP requests.

        Defaults to ``None``.
    max_questions: :class:`int`
        Number of questions to be cached.

        Defaults to ``50``.
    settings: Optional[:class:`.Settings`]
        Settings to be used when populating the internal cache.

        Defaults to ``Settings()``.

    Attributes
    ----------
    session: Optional[:class:`aiohttp.ClientSession`]
        Session to be used when performing HTTP requests.

        If ``None``, a new session will be created automatically when performing HTTP requests.
    settings: :class:`.Settings`
        Settings to be used when populating the internal cache.
    """

    _BASE_URL = yarl.URL('https://opentdb.com/')
    _ERRORS = {
        None: None,
        0: None,
        1: NoResults,
        2: InvalidParameter,
        3: TokenNotFound,
        4: TokenEmpty
    }

    def __init__(
        self, *,
        session=None,
        max_questions=50,
        settings=None
    ):
        if max_questions < 0:
            raise ValueError('max_questions must be non-negative')

        self.session = session
        self.settings = settings or Settings()

        self._token = None
        self._questions = collections.deque(maxlen=max_questions)
        self._categories = {}
        self._counts = {}
        self._global_counts = {}

    @property
    def token(self):
        """Optional[:class:`str`]: Cached session token. ``None`` when not populated."""

        return self._token

    @property
    def questions(self):
        """List[:class:`.Question`]: List of cached questions. Empty when not populated."""
        return list(self._questions)

    @property
    def categories(self):
        """List[:class:`.Category`]: List of cached categories. Empty when not populated."""

        return list(self._categories.values())

    @property
    def counts(self):
        """List[:class:`.Count`]: List of cached counts. Empty when not populated."""

        return list(self._counts.values())

    @property
    def global_counts(self):
        """List[:class:`.GlobalCount`]: List of cached global counts. Empty when not populated."""

        return list(self._global_counts.values())

    async def _request(self, method, endpoint, **options):
        if self.session is None:
            self.session = aiohttp.ClientSession(raise_for_status=True)

        async with self.session.request(method, self._BASE_URL / endpoint, **options) as response:
            payload = await response.json()

        error_type = self._ERRORS[payload.pop('response_code', None)]
        if error_type is not None:
            raise error_type()
        return payload

    # token

    async def fetch_token(self):
        """Fetches a new session token.

        Returns
        -------
        :class:`str`
            New session token.
        """

        params = {
            'command': 'request'
        }
        payload = await self._request('GET', 'api_token.php', params=params)
        return payload['token']

    async def reset_token(self, token=None):
        """Resets a session token.

        Parameters
        ----------
        token: Optional[:class:`str`]
            Token to be reset.

            If ``None``, :attr:`~.Client.token` will be used. If no cached token exist,
            :class:`ValueError` will be raised.

            Defaults to ``None``.

        Returns
        -------
        :class:`str`
            New session token.
        """

        is_internal = token is None
        token = self._token if is_internal else token
        if token is None:
            raise ValueError('token must be supplied')

        params = {
            'command': 'reset',
            'token': token
        }
        payload = await self._request('GET', 'api_token.php', params=params)
        new_token = payload['token']

        if is_internal:
            self._token = new_token
        return new_token

    # question

    def fetch_questions(
        self, *,
        amount=10,
        category=None,
        difficulty=None,
        type=None,
        encoding=None,
        token=None
    ):
        """Returns an async iterator for handling questions fetching for the client.

        The iterator can be used in 2 different ways:

        .. code-block:: python3

            # quick fetch
            ... = await client.fetch_questions(...).flatten()

            # cancelable fetch
            async for ... in client.fetch_questions(...):
                ...

        Parameters
        ----------
        amount: :class:`int`
            Amount of questions to be fetched.

            Defaults to ``10``.
        category: Optional[:class:`.CategoryType`]
            Category of the questions to be fetched.

            Defaults to ``None``.
        difficulty: Optional[:class:`.DifficultyType`]
            Difficulty of the questions to be fetched.

            Defaults to ``None``.
        type: Optional[:class:`.QuestionType`]
            Type of the questions to be fetched.

            Defaults to ``None``.
        encoding: Optional[:class:`.EncodingType`]
            Encoding of the API response to be used.

            Defaults to ``None``.
        token: Optional[:class:`str`]
            Session token to be used.

            Defaults to :attr:`~.Client.token`.

        Yields
        ------
        :class:`.Question`
            Fetched question.
        """

        if amount < 1:
            raise ValueError('amount must be above 0')

        return _AsyncQuestionsIterator(
            self,
            amount=amount,
            category=category,
            difficulty=difficulty,
            type=type,
            encoding=encoding,
            token=token or self._token
        )

    def get_questions(
        self, *,
        amount=10,
        category=None,
        difficulty=None,
        type=None,
        consume=False
    ):
        """Returns an iterator for handling questions retrieving for the client.

        The iterator can be used in 2 different ways:

        .. code-block:: python3

            # quick get
            ... = client.get_questions(...).flatten()

            # cancelable get
            for ... in client.get_questions(...):
                ...

        Parameters
        ----------
        amount: :class:`int`
            Amount of questions to be retrieved.

            Defaults to ``10``.
        category: Optional[:class:`.CategoryType`]
            Category of the questions to be retrieved.

            Defaults to ``None``.
        difficulty: Optional[:class:`.DifficultyType`]
            Difficulty of the questions to be retrieved.

            Defaults to ``None``.
        type: Optional[:class:`.QuestionType`]
            Type of the questions to be retrieved.

            Defaults to ``None``.
        consume: :class:`bool`
            Denotes whether to remove retrieved questions from the internal question cache or not.

            Defaults to ``False``.

        Yields
        ------
        :class:`.Question`
            Retrieved question.
        """

        if amount < 1:
            raise ValueError('amount must be above 0')

        return _QuestionsIterator(
            self,
            amount=amount,
            category=category,
            difficulty=difficulty,
            type=type,
            consume=consume
        )

    # category

    def _create_categories(self, payload):
        return [Category(data) for data in payload]

    async def fetch_categories(self):
        """Fetches all categories.

        Returns
        -------
        List[:class:`.Category`]
            List of fetched categories.
        """

        payload = await self._request('GET', 'api_category.php')
        return self._create_categories(payload['trivia_categories'])

    def get_category(self, type):
        """Retrieves a category from the internal category cache.

        Parameters
        ----------
        type: :class:`.CategoryType`
            Type of the category to be retrieved.

        Returns
        -------
        Optional[:class:`.Category`]
            Cached category. ``None`` when not cached.
        """

        return self._categories.get(type.value)

    # count

    def _create_count(self, payload):
        return Count(self, payload)

    async def fetch_count(self, category):
        """Fetches a specific count.

        Parameters
        ----------
        category: :class:`.CategoryType`
            Category type of the count to be fetched.

        Returns
        -------
        :class:`.Count`
            Fetched count.
        """

        params = {
            'category': category.value
        }
        payload = await self._request('GET', 'api_count.php', params=params)

        actual_payload = payload['category_question_count']
        actual_payload['id'] = payload['category_id']
        return self._create_count(actual_payload)

    def get_count(self, category):
        """Retrieves a specific count from the internal count cache.

        Parameters
        ----------
        category: :class:`.CategoryType`
            Category type of the count to be retrieved.

        Returns
        -------
        Optional[:class:`.Count`]
            Cached count. ``None`` when not cached.
        """

        return self._counts.get(category.value)

    # global count

    def _create_global_counts(self, payload):
        global_counts = [GlobalCount(self, payload['overall'])]
        for id, data in payload['categories'].items():
            data['id'] = int(id)
            global_counts.append(GlobalCount(self, data))
        return global_counts

    async def fetch_global_counts(self):
        """Fetches all global counts.

        Returns
        -------
        List[:class:`.GlobalCount`]
            List of fetched global counts.
        """

        payload = await self._request('GET', 'api_count_global.php')
        return self._create_global_counts(payload)

    def get_global_count(self, category):
        """Retrieves a specific global count from the internal global count cache.

        Parameters
        ----------
        category: :class:`.CategoryType`
            Category type of the global count to be retrieved.

        Returns
        -------
        Optional[:class:`.GlobalCount`]
            Cached global count. ``None`` when not cached.
        """

        return self._global_counts.get(category.value if category is not None else None)

    # tools

    async def populate(self, settings=None):
        """Populates the internal cache.

        Parameters
        ----------
        settings: Optiona[:class:`.Settings`]
            Settings to be used.

            Defaults to :attr:`~.Client.settings`.
        """

        settings = settings or self.settings

        if settings.token:
            if self._token is None or settings.overwrite:
                self._token = await self.fetch_token()

        if settings.questions:
            if settings.overwrite:
                questions_amount = self._questions.maxlen
            else:
                questions_amount = self._questions.maxlen - len(self._questions)

            if questions_amount > 0:
                questions_iterator = self.fetch_questions(
                    amount=questions_amount,
                    category=settings.category,
                    difficulty=settings.difficulty,
                    type=settings.question,
                    encoding=settings.encoding
                )
                self._questions.extend(await questions_iterator.flatten())

        if settings.categories:
            if not self._categories or settings.overwrite:
                for category in await self.fetch_categories():
                    self._categories[category.type.value] = category

        if settings.counts:
            if not self._counts or settings.overwrite:
                for category_id in Category._VALUE_MAPPING:
                    category_type = CategoryType(category_id)
                    self._counts[category_type.value] = await self.fetch_count(category_type)

        if settings.global_counts:
            if not self._global_counts or settings.overwrite:
                for global_count in await self.fetch_global_counts():
                    category_type = getattr(global_count.category, 'type', None)
                    category_value = category_type.value if category_type is not None else None
                    self._global_counts[category_value] = global_count

    async def close(self):
        """Closes the internal session if exist."""

        if self.session is None:
            return
        await self.session.close()
