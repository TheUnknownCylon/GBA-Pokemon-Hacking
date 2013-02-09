# Pokescript Guide


## Introduction

Welcome to this guide. In this guide some basics of the PokeScript language is explained. First of all, note that there are different implementations are available. Each PokeScript implementation could be slightly different of the others. So, the guide that you are about to read, is only appliccable to the Python GBAPkmnRomHack tool suite.

## Basic script

A PokeScript always starts at one location. In this PokeScript implementation, this is the start point. A script contains of multiple statements that are executed in order. A script can contain multiple routines, which are instruction sets. A script finishes if it hits  an `end` statement. To make things a bit easier to understand, the following code shows an example of a simple script with one start-routine, and that ends immediately after starting:

    #org $start
      end

Another routine example, where the script does not start is given below. (Note that later in this document an explanation is given why this is useful).

    #org $my_own_routine
      end


## People and text
In the game, there are a lot of talking people. If you talk to a person, a script is activated. In most cases, people say something interesting or funny to you. What they say is just a result of the script you are running. An example of a script you can use to let a person talk:

    #org $start
      facemessage $my_text
      end

    #text $my_text
    = Hello!\n
    = I am a simple text, so...\l
    = HELLO WORLD!

As you can see, the script contains of a simple command ``facemessage`` which tells the game to let the person talking to, face you as a player, and say the text that is stored in `$my_text`.


Other forms of messages are also possible:

* If you do not want to let the person face the player, of when the person talking to the player is already facing the player, the command 
``message $my_text`` can be used.

If you do not want to talk immediately, but do some other stuff first, then it is a good idea to use a different PokeScript construction, where first the person you are talking to is locked (frozen) by calling `lock`, and faces the player by calling `faceplayer`, and once finished, a `release` call unlocks the person again:

    #org $start
      lock         'Locks the script person (e.g. it stops walking)
      faceplayer   'Let the player look to the person

      ' Do something here to your likings

      release      'Unlock the locked script person (it starts walking again)
      end          'End of the script
    
### Text format:
As you already have seen, a text is set up differently than a script. Each line of a text in PokeScript starts with `=`. In your text, you can use different constructions to define where new lines start, and how they are shown in the game. These are `\n`, `\p`, or `\l`. In the list below, each of them is explained:

* `\n` Lets the text after it follow on a new line, but all text in the box is not moved upwards.
* `\l` Moves lines in the text box one level up, and text after it follows on the last line.
* `\p` Clears the text box, and the text following after it starts on the first line.

There are also some special text substrings that show not the text, but something special. These are `[player]` `[textstring]` `[rival]` `[game]` `[team]` `[otherteam]` `[teamleader]` `[otherteamleader]` `[legend]` `[otherlegend]` `\s` `\U` `\d` `\r` `\c` `\e` `[Lv]` `[PK]` `[MN]` `[PO]` `[Ke]` `[BL]` `[OC]` `[K]` `[U]` `[D]` `[L]` `[R]` `[..]` `[-"]` `[-Q]` `[male]` `[female]` `[p]` `[x]` `[>]`, and can be used in any of your text definitions.

Two examples texts taken from the game FireRed are:

    #text $string_0
    = MOM: [player]!\n
    = You should take a quick rest.

    #text $string_2
    = MOM: [..]Right.\n
    = All boys leave home someday.\l
    = It said so on TV.\p
    = Oh, yes. PROF. OAK, next door, was\n
    = looking for you.

## Fight!
Pokemon isn't Pokemon if you can't fight to wild Pokemon, or to wild trainers (huh...). There are several commands that will do fighting stuff.

###Wild Pokemon battle
In order to start a wild pokemon battle, two commands should be executed in order. First call `wildbattle <species> <level> <item>`, and next `startwildbattle`. An example is given below, where a wild Zigzagoon level 5 battle is started:

    #org $start
      wildbattle ZIGZAGOON 5 ORANBERRY
      startwildbattle
      end

Note that there also other startwildbattle commands, that start the wild battle with a different song (`startwildbattle1`, `startwildbattle2`, and `startwildbattle3`).

###Trainer battle
The command for a trainerbattle is `trainerbattle <trainer-number> <start-message> <lost-message>`. If the trainer was already defeated, the `trainerbattle` will not be executed. The following code demonstrates how to battle a trainer:

    #org $start
      trainerbattle 0x79 $string_0 $string_1
      normalmessage $string_2
      end
    
    #text $string_0
    = What?\n
    = I'm waiting for my friends to find\l
    = me here.
    
    #text $string_1
    = I lost?

    #text $string_2
    = I came because I heard there are\n
    = some very rare fossils here.

It is also possible to have a script after the end of a battle. A common use case
for this is getting an item after a battle, or getting a badge after defeating
a gym leader. In this case, you have to extend the `trainerbattle` with a jump.
As an illustration, the previous example is extended below:

    #org $start
      trainerbattle 0x79 $string_0 $string_1 jump $aftermatch
      normalmessage $string_2
    end
    
    #org $aftermatch
      message $fun
      giveitem potion 1
      release
      end
  
    #text $string_2
    = Potions restore 20HP of your Pok\emon.\n
    = You can use them during a battle too!
    
    #text $fun
    = That was fun!\n
    = Here, take this as a token of my\l
    = gratitude.
    

_Note:_ there are some other trainer battle construction. See for a full list the commands documentation (which can be found in a separate file).

## Items

__Oneliner__:
Letting the player find an item can be done by calling `finditem <itemname> <numberofitems>`. The game will show the text "[player] found a <itemname>", plays a cool sound, and adds the item to your bag.

Example: All the Pokeballs you see everywhere in the game are handled as if it were normal scripts or players (note that the game hides the pokeball automatically if you set a unique VAR for the entity, for example in AdvanceMap):

    #org $start
      finditem POTION 0x1
      end

__Oneliner__:
Let the player obtain an item can be done by calling `giveitem <itemname> <numberofitems>`. The game will show the text "[player] obtained the <itemname>", plays a cool sound, and adds the item to your bag.

__Other item commands__:
The following commands can also be used to do some item magic:

* `additem <item name> <count>`
* `additemtopc  <item name> <count>`
* `removeitem <item name> <count>`
* `checkitemspaceinbag <item name> <count>`  (result is stored in the var `LASTRESULT`)
* `checkitem  <item name> <count>` (result is stored in the var `LASTRESULT`)
* `checkitemtype  <item name>`  (item type is stored in the var `LASTRESULT`)
* `checkitempc  <item name> <count>` (result is stored in the var `LASTRESULT`)

## Weather
The following commands can be used to control the weather:

* `setweather <weathertype>` Prepares the weather change, but does not apply it.
* `dowether` Changes the weather, after doing the setweather call.
* `resetwether`

# Money
It's all about the money, dum dum dum dum... 

Controlling the amount of money the player has:
* `givemoney <amount>`
* `takemoney <amount>`
* `checkmoney <amount>`

A moneybox can be shown or hidden by using the following commands:
* `showmoneybox` Shows moneybox at top-left of the screen.
* `hidemoneybox` Hides the moneybox
* `updatemoneybox` Updates the money in the moneybox to reflect any changes.
* `showmoneybox <x> <y> 0`
* `hidemoneybox` <x> <y>`
* `updatemoneybox` <x> <y> 0`
