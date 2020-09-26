import pytest
from pytest import raises
from bs4 import BeautifulSoup
import tennisrules as tennis

import tscraper as t

# Import testing material
titlefile = open('testmatch/title.txt', 'r')
title = titlefile.read()
titlefile.close()

matchfile = open('testmatch/match.txt', 'r')
body = matchfile.read()
matchfile.close()


def test_mergerows():
    list1 = ['a', 'b', 'c', 'd']
    list2 = [1, 2, 3, 4]
    list3 = [1, 2, 3]
    longlist = [1,2,3,4,5,6,7,8]

    expected12 = ['a', 1, 'b', 2, 'c', 3, 'd', 4]
    expected13 = ['a', 1, 'b', 2, 'c', 3, 'd']

    assert t.mergerows(list1, list2) == expected12
    assert t.mergerows(list1, list3) == expected13

    with pytest.raises(Exception):
        assert t.mergerows(longlist, list2)
        assert t.mergerows(list3, list1)

def test_players():
    p1, p2 = t.parse_players(title)
    assert p1.First == 'Alexander'
    assert p1.Last == 'Zverev'
    assert p2.First == 'Dominic'
    assert p2.Last == 'Thiem'
