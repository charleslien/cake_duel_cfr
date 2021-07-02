#!/usr/bin/python3

from dataclasses import dataclass
import random
from typing import Mapping, Tuple

import action, card, turn_state, utils

HAND_SIZE = 4

PLAYER_0_WIN = object()
PLAYER_1_WIN = object()

WIN = (PLAYER_0_WIN, PLAYER_1_WIN)

@dataclass(frozen=True)
class BoutState:
  claimable: Mapping[card.Card, int]
  ordered_deck: Tuple[card.Card, ...]
  cakes: Tuple[int, int]
  attacker: int
  attack: action.Action
  defense: action.Action
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

  def playAction(self, played_action):
    if self.turn_state == turn_state.TurnState.ATTACK:
      return self._playActionDuringAttack(played_action)
    if self.turn_state == turn_state.TurnState.DEFEND:
      return self._playActionDuringDefend(played_action)
    if self.turn_state == turn_state.TurnState.LAST:
      return self._playActionDuringLast(played_action)

    raise ValueError(f'internal error: {self.turn_state} is not a valid turn state')

  def _playActionDuringAttack(self, played_action):
    if played_action.main_action == action.MainAction.PASS:
      if self.previous_turn_skipped:
        if self.cakes[0] > self.cakes[1]:
          return PLAYER_0_WIN
        else:
          return PLAYER_1_WIN

      return BoutState(
          claimable=self.claimable,
          ordered_deck=self.ordered_deck,
          cakes=self.cakes,
          attacker=1 - self.attacker,
          attack=None,
          defense=None,
          turn_state=turn_state.TurnState.ATTACK,
          previous_turn_skipped=True,
          hands=self.hands
      )

    if played_action.main_action == action.MainAction.CLAIM:
      attacker_hand = action.handAfterClaim(played_action, self.hands[self.attacker])
      hands = ((attacker_hand, self.hands[1]) if
               self.attacker == 0 else
               (self.hands[0], attacker_hand))

      return BoutState(
          claimable=self.claimable,
          ordered_deck=self.ordered_deck,
          cakes=self.cakes,
          attacker=self.attacker,
          attack=played_action,
          defense=None,
          turn_state=turn_state.TurnState.DEFEND,
          previous_turn_skipped=self.previous_turn_skipped,
          hands=hands
      )

    raise ValueError(f'internal error: {played_action.main_action} is not a valid action for ' +
                     f'turn state {self.turn_state}')
  
  def _playActionDuringDefend(self, played_action):
    defender = 1 - self.attacker

    if played_action.main_action == action.MainAction.PASS:
      new_cakes = list(self.cakes)
      cakes_stolen = self.attack.count * card.CAKE_VALUE[self.attack.card]
      new_cakes[self.attacker] += cakes_stolen
      new_cakes[defender] -= cakes_stolen

      if new_cakes[defender] <= 0:
        return WIN[self.attacker]

      hands = list(self.hands)
      attacker_hand, deck = utils.drawCards(
          self.ordered_deck,
          HAND_SIZE - sum(self.hands[self.attacker].values()),
          self.hands[self.attacker])
      hands[self.attacker] = utils.frozendict(attacker_hand)

      return BoutState(
          claimable=self.claimable,
          ordered_deck=deck,
          cakes=new_cakes,
          attacker=defender,
          attack=None,
          defense=None,
          turn_state=turn_state.TurnState.ATTACK,
          previous_turn_skipped=False,
          hands=tuple(hands)
      )
    if played_action.main_action == action.MainAction.CHALLENGE:
      if action.claimIsBluff(self.attack): return WIN[defender]
      else:
        return WIN[self.attacker]
    if played_action.main_action == action.MainAction.CLAIM:
      defender_hand = action.handAfterClaim(played_action, self.hands[defender])
      hands = ((defender_hand, self.hands[1]) if
               defender == 0 else
               (self.hands[0], defender_hand))

      return BoutState(
          claimable=self.claimable,
          ordered_deck=self.ordered_deck,
          cakes=self.cakes,
          attacker=self.attacker,
          attack=self.attack,
          defense=played_action,
          turn_state=turn_state.TurnState.LAST,
          previous_turn_skipped=self.previous_turn_skipped,
          hands=hands
      )

    raise ValueError(f'internal error: {played_action.main_action} is not a valid action for ' +
                     f'turn state {self.turn_state}')

  def _playActionDuringLast(self, played_action):
    defender = 1 - self.attacker

    if played_action.main_action == action.MainAction.PASS:
      new_cakes = list(self.cakes)
      cakes_stolen = (self.attack.count * card.CAKE_VALUE[self.attack.card] -
                      self.defense.count * card.CAKE_VALUE[self.defense.card])
      new_cakes[self.attacker] += cakes_stolen
      new_cakes[defender] -= cakes_stolen

      if new_cakes[defender] <= 0:
        return WIN[self.attacker]

      hands = list(self.hands)
      attacker_hand, deck = utils.drawCards(
          self.ordered_deck,
          HAND_SIZE - sum(self.hands[self.attacker].values()),
          self.hands[self.attacker]
      )
      defender_hand, deck = utils.drawCards(
          deck,
          HAND_SIZE - sum(self.hands[defender].values()),
          self.hands[defender]
      )
      hands = ((attacker_hand, defender_hand) if
               self.attacker == 0 else
               (defender_hand, attacker_hand))

      return BoutState(
          claimable=self.claimable,
          ordered_deck=deck,
          cakes=new_cakes,
          attacker=defender,
          attack=None,
          defense=None,
          turn_state=turn_state.TurnState.ATTACK,
          previous_turn_skipped=False,
          hands=hands
      )
    if played_action.main_action == action.MainAction.CHALLENGE:
      if action.claimIsBluff(self.defense):
        return WIN[self.attacker]
      else:
        return WIN[defender]

    raise ValueError(f'internal error: {played_action.main_action} is not a valid action for ' +
                     f'turn state {self.turn_state}')

def newBoutState(decklist, active_player=0):
  claimable = decklist.copy()
  claimable[card.Card.SIR_WOLFY] = 0
  claimable = utils.frozendict(claimable)

  deck = utils.countDictToList(decklist)
  utils.shuffleList(deck)

  hand_0, deck = utils.drawCards(deck, HAND_SIZE)
  hand_1, deck = utils.drawCards(deck, HAND_SIZE)

  deck = tuple(deck)

  cakes = (3 + active_player, 4 - active_player)

  return BoutState(
      claimable=claimable,
      ordered_deck=deck,
      cakes=cakes,
      attacker=active_player,
      attack=None,
      defense=None,
      turn_state=turn_state.TurnState.ATTACK,
      previous_turn_skipped=False,
      hands=(utils.frozendict(hand_0), utils.frozendict(hand_1))
  )
