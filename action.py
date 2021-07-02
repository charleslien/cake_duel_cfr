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

def getAttackingActions(active_player, hand, claimable):
  all_actions = Action(active_player, MainAction.PASS)

  for c in card.getCardsByType(card.ActionType.ATTACK):
    max_claim_num = min(
        sum(hand.values()),
        claimable.get(c, 0)
    )
    for num_cards_to_claim in range(1, max_claim_num):
      for cards_to_claim in utils.getAllUniqueCombinationsOfCards(
          hand, num_cards_to_claim
      ):
        all_actions.append(Action(
            active_player,
            MainAction.CLAIM,
            num_cards_to_claim,
            c,
            cards_to_claim
        ))

  return all_actions

def getDefendingActions(active_player, hand, attack, claimable):
  all_actions = [
      Action(active_player, MainAction.PASS),
      Action(active_player, MainAction.CHALLENGE)
  ]

  for c in card.getCardsByType(
      card.ActionType.DEFEND,
      damage_type=card.getDamageType(attack.card)
  ):
    max_claim_num = min(
        sum(hand.values()),
        claimable.get(c, 0),
        attack.count
    )
    for num_cards_to_claim in range(1, max_claim_num + 1):
      for cards_to_claim in utils.getAllUniqueCombinationsOfCards(
          hand, num_cards_to_claim):
        all_actions.append(Action(
            active_player,
            MainAction.CLAIM,
            count=num_cards_to_claim,
            card=c,
            played_cards=cards_to_claim
        ))

  return all_actions

def getLastActions(active_player):
  return [
      Action(active_player, MainAction.PASS),
      Action(active_player, MainAction.CHALLENGE)
  ]
