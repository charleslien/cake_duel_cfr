#!/usr/bin/python3

import enum
from frozendict import frozendict as fd
import random

import card

class frozendict(fd):
  def __repr__(self):
    return repr({
        c: self[c] for c in self if self[c] != 0
    })

  def __str__(self):
    return str({
        c: self[c] for c in self if self[c] != 0
    })

class StrValueEnum(enum.IntEnum):
  def __str__(self):
    return self.value

def countDictToList(count_dict):
  ret = []
  for key in count_dict:
    ret += [key] * count_dict[key]

  return ret

def listToCountDict(lst):
  ret = {}
  for val in lst:
    ret[val] = ret.get(val, 0) + 1
  
  return ret

def shuffleList(lst):
  length = len(lst)
  for i in range(length):
    j = int(random.random() * length)
    tmp = lst[i]
    lst[i] = lst[j]
    lst[j] = tmp

def drawCards(deck, num_cards, original_hand=None):
  original_hand = original_hand or {}
  original_hand = dict(original_hand)
  cards_to_draw = min(num_cards, len(deck))

  for c in deck[-cards_to_draw:]:
    original_hand[c] =  original_hand.get(c, 0) + 1
  
  return frozendict(original_hand), deck[:-cards_to_draw]

def getAllUniqueCombinationsOfCards(count_dict, num_cards):
  ret = []

  stack = [(card.Card(0), {}, num_cards)]
  while stack:
    c, curr, num_left = stack.pop()

    max_num_of_c = min(count_dict.get(c, 0), num_left)
    if count_dict.get(c, 0) >= num_left:
      temp_dict = curr.copy()
      temp_dict[c] = num_left
      ret.append(frozendict(temp_dict))
      max_num_of_c -= 1

    try:
      next_card = card.Card(c.value + 1)
    except ValueError as e:
      continue

    for num_of_c in range(max_num_of_c + 1):
      temp_dict = curr.copy()
      if num_of_c > 0:
        temp_dict[c] = num_of_c
      stack.append((next_card, temp_dict, num_left - num_of_c))

  return ret
