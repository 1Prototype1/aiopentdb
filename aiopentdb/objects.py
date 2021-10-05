"""
    aiopentdb.objects
    ~~~~~~~~~~~~~~~~~

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import random

import attr

from .enums import CategoryType, DifficultyType, QuestionType

__all__ = ('Category', 'Count', 'GlobalCount', 'Question')

def _bypass_setter(target):
    def new_setter(name, value):
        object.__setattr__(target, name, value)

    return new_setter

def _get_category_mappings():
    names = (
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
    name_mapping = {}
    value_mapping = {}

    for id, name in enumerate(names, 9):
        name_mapping[name] = id
        value_mapping[id] = name

    return name_mapping, value_mapping

@attr.s(frozen=True, slots=True, init=False)
class Category:
    """Dataclass representing an OpenTDB category.

    Attributes
    ----------
    name: :class:`str`
        Name of the category.
    id: :class:`int`
        ID of the category.
    type: :class:`.CategoryType`
        Type of the category.
    """

    name = attr.ib()
    id = attr.ib()
    type = attr.ib()

    _NAME_MAPPING, _VALUE_MAPPING = _get_category_mappings()

    def __init__(self, data):
        new_setter = _bypass_setter(self)
        new_setter('name', data['name'])
        new_setter('id', data['id'])
        new_setter('type', CategoryType(self.id))

    @classmethod
    def _from_partial(cls, client, data):
        name = data.get('name')
        id = data.get('id')

        if name is not None:
            id = id or cls._NAME_MAPPING[name]
        elif id is not None:
            name = name or cls._VALUE_MAPPING[id]
        else:
            return None

        return client._categories.get(id) or cls({'name': name, 'id': id})

@attr.s(frozen=True, slots=True, init=False)
class Count:
    """Dataclass representing an OpenTDB count.

    Attributes
    ----------
    total: :class:`int`
        Total number of all the questions.
    easy: :class:`int`
        Number of easy questions.
    medium: :class:`int`
        Number of medium questions.
    hard: :class:`int`
        Number of hard questions.
    category: :class:`.Category`
        Category that the count belongs to.
    """

    total = attr.ib()
    easy = attr.ib()
    medium = attr.ib()
    hard = attr.ib()
    category = attr.ib()

    def __init__(self, client, data):
        new_setter = _bypass_setter(self)
        new_setter('total', data['total_question_count'])
        new_setter('easy', data['total_easy_question_count'])
        new_setter('medium', data['total_medium_question_count'])
        new_setter('hard', data['total_hard_question_count'])
        new_setter('category', Category._from_partial(client, data))

@attr.s(frozen=True, slots=True, init=False)
class GlobalCount:
    """Dataclass representing an OpenTDB global count.

    Attributes
    ----------
    total: :class:`int`
        Total number of all the questions.
    pending: :class:`int`
        Number of pending questions.
    verified: :class:`int`
        Number of verified questions.
    rejected: :class:`int`
        Number of rejected questions.
    category: Optional[:class:`.Category`]
        Category that the global count belongs to. ``None`` for overall global count.
    """

    total = attr.ib()
    pending = attr.ib()
    verified = attr.ib()
    rejected = attr.ib()
    category = attr.ib()

    def __init__(self, client, data):
        new_setter = _bypass_setter(self)
        new_setter('total', data['total_num_of_questions'])
        new_setter('pending', data['total_num_of_pending_questions'])
        new_setter('verified', data['total_num_of_verified_questions'])
        new_setter('rejected', data['total_num_of_rejected_questions'])
        new_setter('category', Category._from_partial(client, data))

@attr.s(frozen=True, slots=True, init=False)
class Question:
    """Dataclass representing an OpenTDB question.

    Attributes
    ----------
    type: :class:`.QuestionType`
        Type of the question.
    difficulty: :class:`.DifficultyType`
        Difficulty of the question.
    content: :class:`int`
        Actual content of the question.
    correct_answer: :class:`str`
        Correct answer of the question.
    incorrect_answers: List[:class:`str`]
        List of incorrect answers.
    category: :class:`.Category`
        Category that the question belongs to.
    """

    type = attr.ib()
    difficulty = attr.ib()
    content = attr.ib(repr=False)
    correct_answer = attr.ib(repr=False)
    incorrect_answers = attr.ib(repr=False)
    category = attr.ib()

    def __init__(self, client, data, decoder):
        new_setter = _bypass_setter(self)
        new_setter('type', QuestionType(decoder(data['type'])))
        new_setter('difficulty', DifficultyType(decoder(data['difficulty'])))
        new_setter('content', decoder(data['question']))
        new_setter('correct_answer', decoder(data['correct_answer']))
        new_setter('incorrect_answers', [decoder(answer) for answer in data['incorrect_answers']])
        new_setter('category', Category._from_partial(client, data))

    @property
    def answers(self):
        """List[:class:`str`]: List of shuffled answers."""

        answers = [self.correct_answer, *self.incorrect_answers]
        random.shuffle(answers)
        return answers
