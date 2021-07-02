#!/usr/bin/python3

from dataclasses import dataclass
from frozendict import frozendict
import random
from typing import Mapping, Tuple

import action, card, turn_state, utils

HAND_SIZE = 4

@dataclass(frozen=True)
class BoutState:
  claimable: Mapping[card.Card, int]
  ordered_deck: Tuple[card.Card, ...]
  attacker: int
  attack: action.Action
  turn_state: turn_state.TurnState
  previous_turn_skipped: bool
  hands: Tuple[Mapping[card.Card, int], Mapping[card.Card, int]]

  def getAvailableActions(self):
    if self.turn_state == turn_state.TurnState.ATTACK:
      active_player = self.attacker
      return action.getAttackingActions(
          active_player,
          self.hands[active_player],
          self.claimable
      )
    if self.turn_state == turn_state.TurnState.DEFEND:
      active_player = 1 - self.attacker
      return action.getDefendingActions(
          active_player,
          self.hands[active_player],
          self.attack,
          self.claimable
      )
    if self.turn_state == turn_state.TurnState.LAST:
      return action.getLastActions(self.attacker)

    raise ValueError(f'internal error: {self.turn_state} is not a valid turn state')

  def playAction(self, action):
    # TODO implement this
    pass

def newBoutState(decklist, active_player=0):
  claimable = decklist.copy()
  claimable[card.Card.SIR_WOLFY] = 0
  claimable = frozendict(claimable)

  deck = utils.countDictToList(decklist)
  utils.shuffleList(deck)

  hand_0, deck = utils.drawCards(deck, HAND_SIZE)
  hand_1, deck = utils.drawCards(deck, HAND_SIZE)

  deck = tuple(deck)

  return BoutState(
      claimable=claimable,
      ordered_deck=deck,
      attacker=active_player,
      attack=None,
      turn_state=turn_state.TurnState.ATTACK,
      previous_turn_skipped=False,
      hands=(frozendict(hand_0), frozendict(hand_1))
  )
