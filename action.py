#!/usr/bin/python3

from dataclasses import dataclass
from typing import Tuple

import card as cd
import utils

class MainAction(utils.StrValueEnum):
  CLAIM = 0
  BLOCK = 1
  CHALLENGE = 2
  PASS = 3

@dataclass(frozen=True)
class Action:
  player: int
  main_action: MainAction
  count: int = None
  card: cd.Card = None
  played_cards: Tuple[cd.Card, ...] = None

  def __str__(self):
    if self.main_action == MainAction.CLAIM:
      return (f'({self.player},' +
              f'{self.main_action.value},' +
              f'{self.count},' +
              f'{self.card.value},' +
              ','.join(str(c.value) for c in self.played_cards) +
              ')')
    return f'({self.player},{self.main_action.value})'
