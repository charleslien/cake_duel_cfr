#!/usr/bin/python3

import utils

class ActionType(utils.StrValueEnum):
  ATTACK = 0
  DEFEND = 1

class DamageType(utils.StrValueEnum):
  PHYSICAL = 0
  MAGIC = 1

class Card(utils.StrValueEnum):
  SOLDIER = 0
  ARCHER = 1
  DEFENDER = 2
  WIZARD = 3
  SCIENTIST = 4
  SIR_WOLFY = 5

def getDamageType(card):
  if card in [Card.SOLDIER, Card.ARCHER, Card.DEFENDER]:
    return DamageType.PHYSICAL

  if card in [Card.WIZARD, Card.SCIENTIST]:
    return DamageType.MAGIC

  raise ValueError(f'{card} is not a valid card')

def getCardsByType(action_type, damage_type=None):
  if action_type == ActionType.ATTACK:
    return (
        Card.SOLDIER,
        Card.ARCHER,
        Card.WIZARD
    )
  if action_type == ActionType.DEFEND:
    if damage_type == DamageType.PHYSICAL:
      return (Card.DEFENDER,)
    if damage_type == DamageType.MAGIC:
      return (Card.SCIENTIST,)

    raise ValueError(f'{damage_type} is not a valid damage type')

  raise ValueError(f'{action_type} is not a valid action type')
