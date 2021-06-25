#!/usr/bin/python3

import random

import action, card, turn_state, utils

class BoutState:
  HAND_SIZE = 4

  def __init__(self, starting_deck, claim_update=None):
    self.deck_cards = starting_deck.copy()
    self.claim = starting_deck.copy()
    if claim_update is not None:
      self.claim.update(claim_update)
    else:
      self.claim[card.Card.SIR_WOLFY] = 0

    self._getNewShuffledDeck()

    self.hands = [[], []]
    self.discard_piles = [{}, {}]
    self._resetTurn()

  def _getNewShuffledDeck(self):
    self.deck = utils.countDictToList(self.deck_cards)

    # shuffle deck
    num_cards = len(self.deck)
    for i in range(num_cards):
      j = int(random.random() * num_cards)
      if self.deck[i] == self.deck[j]:
        continue
      tmp = self.deck[i]
      self.deck[i] = self.deck[j]
      self.deck[j] = tmp
 
  def _resetTurn(self, previous_active_player=1, previous_turn_passed=False):
    self.attacker = 1 - previous_active_player
    self.active_player = self.attacker

    self.previous_action = None
    self.turn_state = turn_state.TurnState.ATTACK

    self._drawCards(previous_active_player)
    self._drawCards(self.active_player)

    self.previous_turn_passed = previous_turn_passed

  def _drawCards(self, player):
    num_cards = len(self.hands[player])
    cards_to_draw = min(BoutState.HAND_SIZE - num_cards, len(self.deck))

    self.hands[player] += self.deck[-cards_to_draw:]
    self.deck = self.deck[:-cards_to_draw]
    self.hands[player].sort()

  def getAvailableActions(self):
    if self.turn_state == turn_state.TurnState.ATTACK:
      return self._getAttackingActions()
    if self.turn_state == turn_state.TurnState.DEFEND:
      return self._getDefendingActions()
    if self.turn_state == turn_state.TurnState.LAST:
      return self._getLastActions()

    raise ValueError(f'internal error: {self.turn_state} is not a valid turn state')

  def _getAttackingActions(self):
    all_actions = [action.Action(self.active_player, action.MainAction.PASS)]

    for c in card.getCardsByType(card.ActionType.ATTACK):
      max_claim_num = min(
          len(self.hands[self.active_player]),
          self.claim.get(c, 0)
      )
      for num_cards_to_claim in range(1, max_claim_num + 1):
        for cards_to_claim in self._getAllCombinationsOfCardsInHand(
            self.active_player,
            num_cards_to_claim
        ):
          all_actions.append(action.Action(
              self.active_player,
              action.MainAction.CLAIM,
              count=num_cards_to_claim,
              card=c,
              played_cards=cards_to_claim
          ))

    return all_actions

  def _getDefendingActions(self):
    all_actions = [
        action.Action(self.active_player, action.MainAction.PASS),
        action.Action(self.active_player, action.MainAction.CHALLENGE),
    ]

    for c in card.getCardsByType(
        card.ActionType.DEFEND,
        damage_type=card.getDamageType(self.previous_action.card)
    ):
      max_claim_num = min(
          len(self.hands[self.active_player]),
          self.claim.get(c, 0),
          self.previous_action.count
      )
      for num_cards_to_claim in range(1, max_claim_num + 1):
        for cards_to_claim in self._getAllCombinationsOfCardsInHand(
            self.active_player,
            num_cards_to_claim
        ):
          all_actions.append(action.Action(
              self.active_player,
              action.MainAction.CLAIM,
              count=num_cards_to_claim,
              card=c,
              played_cards=cards_to_claim
          ))

    return all_actions

  def _getLastActions(self):
    return [
        action.Action(self.active_player, action.MainAction.PASS),
        action.Action(self.active_player, action.MainAction.CHALLENGE)
    ]

  def _getAllCombinationsOfCardsInHand(self, player, num_cards):
    hand = utils.listToCountDict(self.hands[player])

    ret = []

    stack = [(card.Card(0), {}, 0)]
    while stack:
      c, curr, num_selected = stack.pop()

      max_num_of_c = min(hand.get(c, 0), num_cards - num_selected)
      if hand.get(c, 0) >= num_cards - num_selected:
        temp_dict = curr.copy()
        temp_dict[c] = num_cards - num_selected
        ret.append(tuple(sorted(utils.countDictToList(temp_dict))))
        max_num_of_c -= 1

      try:
        next_card = card.Card(c.value + 1)
      except ValueError as e:
        continue

      for num_of_c in range(max_num_of_c + 1):
        temp_dict = curr.copy()
        temp_dict[c] = num_of_c
        stack.append((next_card, temp_dict, num_selected + num_of_c))

    return ret

  def playAction(self, action):
    # TODO implement this
    pass
