# coding: utf-8

import time
from anki.db import DB
from anki.consts import *
from tests.shared import getEmptyDeck

def test_genCards():
    deck = getEmptyDeck()
    f = deck.newFact()
    f['Front'] = u'1'
    f['Back'] = u'2'
    deck.addFact(f)
    cards = deck.genCards(f, f.model().templates)
    assert len(cards) == 1
    assert cards[0].ord == 1
    assert deck.cardCount() == 2
    assert cards[0].due == f.id
    # should work on random mode too
    deck.qconf['newCardOrder'] = NEW_CARDS_RANDOM
    f = deck.newFact()
    f['Front'] = u'1'
    f['Back'] = u'2'
    deck.addFact(f)
    cards = deck.genCards(f, f.model().templates)
    assert deck.cardCount() == 4
    c = deck.db.list("select due from cards where fid = ?", f.id)
    assert c[0] == c[1]

def test_previewCards():
    deck = getEmptyDeck()
    f = deck.newFact()
    f['Front'] = u'1'
    f['Back'] = u'2'
    # non-empty and active
    cards = deck.previewCards(f, 0)
    assert len(cards) == 1
    assert cards[0].ord == 0
    # all templates
    cards = deck.previewCards(f, 2)
    assert len(cards) == 2
    # add the fact, and test existing preview
    deck.addFact(f)
    cards = deck.previewCards(f, 1)
    assert len(cards) == 1
    assert cards[0].ord == 0
    # make sure we haven't accidentally added cards to the db
    assert deck.cardCount() == 1

def test_delete():
    deck = getEmptyDeck()
    f = deck.newFact()
    f['Front'] = u'1'
    f['Back'] = u'2'
    deck.addFact(f)
    cid = f.cards()[0].id
    deck.reset()
    deck.sched.answerCard(deck.sched.getCard(), 2)
    assert deck.db.scalar("select count() from revlog") == 1
    deck.delCards([cid])
    assert deck.cardCount() == 0
    assert deck.factCount() == 0
    assert deck.db.scalar("select count() from facts") == 0
    assert deck.db.scalar("select count() from cards") == 0
    assert deck.db.scalar("select count() from fsums") == 0
    assert deck.db.scalar("select count() from revlog") == 0
    assert deck.db.scalar("select count() from graves") == 0
    # add the fact back
    deck.addFact(f)
    assert deck.cardCount() == 1
    cid = f.cards()[0].id
    # delete again, this time with syncing enabled
    deck.syncName = "abc"
    deck.lastSync = time.time()
    deck.delCards([cid])
    assert deck.cardCount() == 0
    assert deck.factCount() == 0
    assert deck.db.scalar("select count() from graves") != 0

def test_misc():
    d = getEmptyDeck()
    f = d.newFact()
    f['Front'] = u'1'
    f['Back'] = u'2'
    d.addFact(f)
    c = f.cards()[0]
    assert c.cssClass() == "cm1-0"
    assert c.fact().id == 1
    assert c.model().id == 1
    assert c.template()['ord'] == 0
