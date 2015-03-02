from copy import copy
from random import seed, randint
import string

SYMBOL_DICE     = "d"
SYMBOL_HITS     = "h"
SYMBOL_EXPLODES = "e"
SYMBOL_FAILS    = "f"

STATE_PREDICE   = 0
STATE_INDICE    = 1
STATE_INHIT     = 2
STATE_INEXPLODE = 3
STATE_INFAIL    = 4

def _roll( sides ) :
  return randint( 1, sides )

def _cap( current_set, data ) :
  if data :
    if data.has_key( "count" ) and data.has_key( "sides" ) :
      current_set.add_dice( Dice( data.get( "count" ), data.get( "sides" ), data.get( "hit", 0 ), data.get( "explodes", 0 ), data.get( "fails", 0 ) ) )
    elif data.has_key( "const" ) :
      current_set.add_const( int( data.get( "const" ) ) )

def parse_expression( expr ) :
  base_set    = DiceSet()
  current_set = [base_set]
  state       = ""
  data        = {}

  expr        += "\n"
  
  for c in expr :
    if c in string.digits :
      if data.has_key( "const" ) :
        data["const"] += str( c )
      else :
        data["const"] = str( c )
      continue

    if state :
      data[state] = int( data.pop( "const" ) )

    if c in (string.whitespace + "+)") :
      _cap( current_set[-1], data )
      if c == ")" and len( current_set ) > 1 :
        current_set.pop()
      data  = {}
      state = STATE_PREDICE
      continue

    if c == "(" :
      ds = DiceSet()
      current_set[-1].add_dice_set( ds )
      current_set.append( ds )
      continue
    
    if c == SYMBOL_DICE :
      data["count"] = int( data.pop( "const" ) )
      state = "sides"
      continue

    if c == SYMBOL_HITS :
      state = "hit"
      continue

    if c == SYMBOL_EXPLODES :
      state = "explodes"
      continue

    if c == SYMBOL_FAILS :
      state = "fails"
      continue

  return base_set

class Dice :
  def __init__( self, count, sides, hit = 0, explodes = 0, fails = 0, sign = "+" ) :
    self.sides    = sides
    self.count    = count
    self.hit      = hit
    self.explodes = explodes
    self.fails    = fails
    self.sign     = sign
    self.reroll()

  def __str__( self ) :
    out = "{}{}{}".format( self.count, SYMBOL_DICE, self.sides )
    if self.hit :
      out += "{}{}".format( SYMBOL_HITS, self.hit )
    if self.explodes :
      out += "{}{}".format( SYMBOL_EXPLODES, self.explodes )
    if self.fails :
      out += "{}{}".format( SYMBOL_FAILS, self.fails )
    out += "({})".format( ", ".join( map( str, self.result ) ) )
    return out

  def __repr__( self ) :
    return "Dice({},{})".format( self.count, self.sides )

  def pretty( self ) :
    noun = "dice" if self.count != 1 else "die"
    out  = "{} {}-sided {}".format( self.count, self.sides, noun )
    if self.hit :
      out += " hit at {}".format( self.hit )
    if self.explodes :
      out += " explode at {}".format( self.explodes )
    if self.fails :
      out += " fail at {}".format( self.fails )
    return out

  def reroll( self ) :
    self.result = []
    self.add_dice( self.count, explode = True )

  def add_dice( self, num, explode = False ) :
    for i in range( num ) :
      roll = _roll( self.sides )
      self.result.append( roll )

      if self.explodes and roll >= self.explodes :
        self.add_dice( 1, explode = True )

  def remove_dice( self, num ) :
    if num > len( self.result ) :
      raise IndexError( "attempted to remove more dice than were in the dice pool", num, len( self.result ) )

    for i in range( num ) :
      self.result.pop()

  def total( self ) :
    return sum( self.result )

  def failures( self ) :
    return len( filter( lambda x : x <= self.fails, self.result ) )

  def hits( self ) :
    return len( filter( lambda x : x >= self.hit, self.result ) )

class DiceSet :
  def __init__( self ) :
    self.dice     = []
    self.const    = 0
    self.can_hit  = False
    self.can_fail = False

  def __str__( self ) :
    out = "({}".format( ", ".join( map( str, self.dice ) ) )
    if self.const :
      out += ", {}".format( self.const )
    return out + ")"

  def pretty( self ) :
    out = "[{}".format( " + ".join( map( lambda x : x.pretty(), self.dice ) ) )
    if self.const :
      out += " + {}".format( self.const )
    return out + "]"

  def add_const( self, const ) :
    self.const += const

  def add_dice( self, dice ) :
    self.dice.append( dice )

    if dice.hit :
      self.can_hit = True
    if dice.fails :
      self.can_fail = True

    return dice

  def add_dice_set( self, diceset ) :
    self.dice.append( diceset )

    if diceset.can_hit :
      self.can_hit = True
    if diceset.can_fail :
      self.can_fail = True

    return diceset

  def hits( self ) :
    return sum( map( lambda x: x.hits(), self.dice ) )

  def failures( self ) :
    return sum( map( lambda x: x.failures(), self.dice ) )

  def total( self ) :
    return sum( map( lambda x: x.total(), self.dice ) ) + self.const

  def hits_str( self ) :
    out = "{} hits".format( self.hits() )
    if self.can_fail :
      out += " and {} critical failures".format( self.failures() )
