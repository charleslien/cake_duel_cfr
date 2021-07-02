#!/usr/bin/python3

from dataclasses import dataclass
from typing import Mapping, Tuple

import card as cd, utils
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
  played_cards: Mapping[cd.Card, int] = None

  def __str__(self):
    if self.main_action == MainAction.CLAIM:
      return (f'({self.player},' +
              f'{self.main_action.value},' +
              f'{self.count},' +
              f'{self.card.value},' +
              ','.join(str(c.value) for c in self.played_cards) +
              ')')
    return f'({self.player},{self.main_action.value})'

def claimIsBluff(action):
  for c in cd.Card:
    if c == action.card:
      if action.played_cards.get(c, 0) != action.count:
        return True
    else:
      if action.played_cards.get(c, 0) != 0:
        return True

  return False

def handAfterClaim(claim, hand):
  hand = dict(hand)
  for c in cd.Card:
    num_cards_played = claim.played_cards.get(c, 0)
    if hand.get(c, 0) < num_cards_played:
      raise ValueError(f'invalid action: tried to play {claim.played_cards[c]} cards when there ' +
                       f'is only {hand[c]}')
    hand[c] = hand.get(c, 0) - num_cards_played

  return utils.frozendict(hand)

def getAttackingActions(active_player, hand, claimable):
  all_actions = [Action(active_player, MainAction.PASS)]

  for c in cd.getCardsByType(cd.ActionType.ATTACK):
    max_claim_num = min(
        sum(hand.values()),
        claimable.get(c, 0)
    )
    for num_cards_to_claim in range(1, max_claim_num + 1):
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

  for c in cd.getCardsByType(
      cd.ActionType.DEFEND,
      damage_type=cd.getDamageType(attack.card)
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
