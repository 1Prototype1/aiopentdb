"""
    aiopentdb.enums
    ~~~~~~~~~~~~~~~

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import types

__all__ = ('CategoryType', 'DifficultyType', 'QuestionType', 'EncodingType')

def _create_enum_type(name):
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return '{0}(name={1.name}, value={1.value})'.format(name, self)

    attributes = {
        '__slots__': __slots__,
        '__init__': __init__,
        '__repr__': __repr__
    }
    return type(name, (), attributes)

def _is_descriptor(object):
    return any(hasattr(object, name) for name in ('__get__', '__set__', '__delete__'))

class _EnumMeta(type):
    def __new__(cls, name, bases, attributes):
        enum_type = _create_enum_type(name)
        name_mapping = {}
        value_mapping = {}

        for attribute_name, attribute_value in attributes.items():
            if _is_descriptor(attribute_value):
                setattr(enum_type, attribute_name, attribute_value)
            else:
                if attribute_name.startswith('_'):
                    continue

                enum = enum_type(attribute_name, attribute_value)
                attributes[attribute_name] = enum
                name_mapping[attribute_name] = enum
                value_mapping[attribute_value] = enum

        attributes['_name_mapping'] = name_mapping
        attributes['_value_mapping'] = value_mapping
        attributes['_enums'] = tuple(name_mapping.values())
        return super().__new__(cls, name, bases, attributes)

    def __getitem__(self, name):
        return self._name_mapping[name]

    def __call__(self, value):
        return self._value_mapping[value]

    def __setattr__(self, name, value):
        raise TypeError(self.__name__ + ' is immutable')

    def __delattr__(self, name):
        raise TypeError(self.__name__ + ' is immutable')

    def __iter__(self):
        return iter(self._enums)

    def __reversed__(self):
        return reversed(self._enums)

    def __contains__(self, enum):
        return enum in self._enums

    def __len__(self):
        return len(self._enums)

    @property
    def __members__(self):
        return types.MappingProxyType(self._name_mapping)

class _Enum(metaclass=_EnumMeta):
    ...

class CategoryType(_Enum):
    """Enum representing an OpenTDB category type.

    This enum is used to denote type of :class:`.Category`.

    Attributes
    ----------
    general
        General knowledge.
    books
        Entertainment: Books.
    film
        Entertainment: Film.
    music
        Entertainment: Music.
    musicals_and_theatres
        Entertainment: Musicals and Theatres.
    television
        Entertainment: Television.
    video_games
        Entertainment: Video Games.
    board_games
        Entertainment: Board Games.
    science_and_nature
        Science and Nature.
    computers
        Science: Computers.
    mathematics
        Mathematics.
    mythology
        Mythology.
    sports
        Sports.
    geography
        Geography.
    history
        History.
    politics
        Politics.
    art
        Art
    celebrities
        Celebrities.
    animals
        Animals.
    vehicles
        Vehicles.
    comics
        Entertainment: Comics.
    gadgets
        Science: Gadgets.
    anime_and_manga
        Entertainment: Japanese Anime and Manga.
    cartoon_and_animations
        Enternainment: Cartoon and Animations.
    """

    general = 9
    books = 10
    film = 11
    music = 12
    musicals_and_theatres = 13
    television = 14
    video_games = 15
    board_games = 16
    science_and_nature = 17
    computers = 18
    mathematics = 19
    mythology = 20
    sports = 21
    geography = 22
    history = 23
    politics = 24
    art = 25
    celebrities = 26
    animals = 27
    vehicles = 28
    comics = 29
    gadgets = 30
    anime_and_manga = 31
    cartoon_and_animations = 32

    def __int__(self):
        return self.value

class DifficultyType(_Enum):
    """Enum representing an OpenTDB difficulty type.

    This enum is used to denote difficulty type of :class:`.Question`.

    Attributes
    ----------
    easy
        Easy question.
    medium
        Medium question.
    hard
        Hard question.
    """

    easy = 'easy'
    medium = 'medium'
    hard = 'hard'

    def __str__(self):
        return self.value

class QuestionType(_Enum):
    """Enum representing an OpenTDB question type.

    This enum is used to denote type of :class:`.Question`.

    Attributes
    ----------
    multiple
        Multiple choice.
    boolean
        True or False.
    """

    multiple = 'multiple'
    boolean = 'boolean'

    def __str__(self):
        return self.value

class EncodingType(_Enum):
    """Enum representing an OpenTDB encoding type.

    This enum is used to denote encoding type of an API response.

    Attributes
    ----------
    url
        URL encoding (RFC 3986).
    base64
        Base64 encoding.
    """

    url = 'url3986'
    base64 = 'base64'

    def __str__(self):
        return self.value
