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

import random

import attr

from .enums import CategoryType, Difficulty, QuestionType

__all__ = (
    'Category',
    'Count',
    'GlobalCount',
    'Question'
)


@attr.s(slots=True, init=False)
class Category:
    """|dataclass| an OpenTDB category object.

    .. note::

        This class is read-only and not meant to be instantiated by users.

    Attributes
    ----------

    name: :class:`str`
        Name of the category object.

    id: :class:`int`
        ID of the category object.

    type: :class:`.CategoryType`
        Type of the category object.
    """

    name = attr.ib()
    id = attr.ib()
    type = attr.ib()

    def __init__(self, data):
        self.name = data['name']
        self.id = data['id']
        self.type = CategoryType(data['id'])


@attr.s(slots=True, init=False)
class Count:
    """|dataclass| an OpenTDB count object.

    .. note::

        This class is read-only and not meant to be instantiated by users.

    Attributes
    ----------

    category: :class:`.Category`
        Category that owns the count object.

    total: :class:`int`
        Total question count.

    easy: :class:`int`
        Easy question count.

    medium: :class:`int`
        Medium question count.

    hard: :class:`int`
        Hard question count.
    """

    category = attr.ib()
    total = attr.ib()
    easy = attr.ib()
    medium = attr.ib()
    hard = attr.ib()

    def __init__(self, client, data):
        self.category = client._CATEGORY_BY_IDS[data['category']]
        self.total = data['total_question_count']
        self.easy = data['total_easy_question_count']
        self.medium = data['total_medium_question_count']
        self.hard = data['total_hard_question_count']


@attr.s(slots=True, init=False)
class GlobalCount:
    """|dataclass| an OpenTDB global count object.

    .. note::

        This class is read-only and not meant to be instantiated by users.

    Attributes
    ----------

    category: Union[:class:`.Category`, :class:`str`]
        Category that owns the global count object.

    total: :class:`int`
        Total question count.

    pending: :class:`int`
        Pending question count.

    verified: :class:`int`
        Verified question count.

    rejected: :class:`int`
        Rejected question count.
    """

    category = attr.ib()
    total = attr.ib()
    pending = attr.ib()
    verified = attr.ib()
    rejected = attr.ib()

    def __init__(self, client, data):
        self.category = client._CATEGORY_BY_IDS.get(data.get('category'), 'overall')
        self.total = data['total_num_of_questions']
        self.pending = data['total_num_of_pending_questions']
        self.verified = data['total_num_of_verified_questions']
        self.rejected = data['total_num_of_rejected_questions']


@attr.s(slots=True, init=False)
class Question:
    """|dataclass| an OpenTDB question object.

    .. note::

        This class is read-only and not meant to be instantiated by users.

    Attributes
    ----------

    type: :class:`.QuestionType`
        Type of the question object.

    category: :class:`.Category`
        Category of the question object.

    difficulty: :class:`.Difficulty`
        Difficulty of the question object.

    content: :class:`str`
        Content of the question object.

    correct_answer: :class:`str`
        Correct answer for the question content.

    incorrect_answers: List[:class:`str`]
        List of incorrect answers.
    """

    type = attr.ib()
    category = attr.ib()
    difficulty = attr.ib()
    content = attr.ib()
    correct_answer = attr.ib()
    incorrect_answers = attr.ib()

    def __init__(self, client, data, decoder):
        self.type = QuestionType(decoder(data['type']))
        self.category = client._CATEGORY_BY_NAMES[decoder(data['category'])]
        self.difficulty = Difficulty(decoder(data['difficulty']))
        self.content = decoder(data['question'])
        self.correct_answer = decoder(data['correct_answer'])
        self.incorrect_answers = [decoder(answer) for answer in data['incorrect_answers']]

    @property
    def mixed_answers(self):
        """List[:class:`str`]: List of mixed answers.

        .. note::

            The answers are shuffled.
        """

        answers = [self.correct_answer, *self.incorrect_answers]
        random.shuffle(answers)
        return answers
