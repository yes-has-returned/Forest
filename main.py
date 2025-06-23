import os
import math
from random import choice, randint


# class for each region or biome of a map, encompassing its information
class region:
    def __init__(self, loot_table, description, name, entity_encounters, background_message, radiation):
        # region values
        self.loot_table = loot_table
        self.description = description
        self.name = name
        self.entity_encounters = entity_encounters
        self.background_message = background_message
        self.radiation = radiation

    def tick_region(self):
        # generates a regional encounter, returns None if nothing is encountered, otherwise returns a string representing an enemy
        possibilities = []
        for i in self.entity_encounters.keys():
            for j in range(self.entity_encounters[i]):
                possibilities.append(i)
        for i in range(100 - len(possibilities)):
            possibilities.append(None)
        if randint(1, 3) == 1:

            return choice(possibilities)
        else:
            return None

    def search_region(self):
        # returns a series of possible found items
        possibilities = []
        for i in self.loot_table.keys():
            for j in range(self.loot_table[i]):
                possibilities.append(i)
        for i in range(100 - len(possibilities)):
            possibilities.append(None)
        returned = []
        for i in range(randint(1, 5)):
            returned.append(choice(possibilities))
        return returned


# class representing the campfire
class campfire:
    def __init__(self, cookable):
        # campfire values
        self.dead = True
        self.firestatus = -1
        self.cooking = []

        # campfire description at each stage
        self.firestatusmessages = {
            5: "The fire is roaring.",
            4: "The fire crackles merrily.",
            3: "The fire wavers.",
            2: "The fire is flickering.",
            1: "The embers smoulder.",
            0: "The coals are cold.",
            -1: "The fire is dead.",
        }
        self.cookable = cookable

    def light_fire(self):
        # lights fire at the start of the game
        if self.dead:
            self.firestatus = 2
            self.dead = False

    def stoke_fire(self):
        # adds 1 to firestatus if it is less than 5
        if not self.dead and self.firestatus < 5:
            self.firestatus += 1

    def tick_fire(self):
        # returns any cooked food
        food = None
        if self.cooking != []:
            self.cooking[0][1] = self.cooking[0][1] - self.firestatus
            if self.cooking[0][1] <= 0:
                food = self.cooking.pop(0)
                if food[0] in self.cookable:
                    food = "cooked " + food[0]
                else:
                    food = "burnt mess"
        firestatusstr = "The coals are cold."
        died = False
        # returns the fire description based on the fire level
        if int(self.firestatus) in self.firestatusmessages.keys():
            firestatusstr = self.firestatusmessages[int(self.firestatus)]
        if self.firestatus > 0:
            self.firestatus -= 0.25
            if self.firestatus <= 0:
                self.firestatus = -1
                self.dead = True
                died = True
        return food, firestatusstr, died

    def add_cooking(self, food, cookingdict):
        # adds a piece of food to the fire
        if food in cookingdict.keys():
            self.cooking.append([food, cookingdict[food]])
        else:
            self.cooking.append([food, 5])


# class representing the player
class player:
    def __init__(self):
        # player values
        self.inventory = {"sharpened stick": 1, "geiger counter": 1}
        self.temperature = 0
        self.hp = 100  # health
        self.atkmult = 1  # attack multiplier
        self.hunger = 100
        self.shield = 0
        self.hungerbar = ""
        self.effects = {}
        self.radiation = 0
        self.radiationbar = "\U00002622"
        for i in range(math.ceil(self.radiation / 100)):
            self.radiationbar += ">"
        
        for i in range(11-len(list(self.radiationbar))):
            self.radiationbar += "-"

        self.radiationbar += "\U0001F480"

        # generates the hunger bar
        for i in range(math.ceil(self.hunger / 10)):
            self.hungerbar += "\U0001f356"
           

        # generates a message based on player temperature
        self.temperaturemessage = {
            5: "You feel hot.",
            4: "You feel warm.",
            3: "It is slightly chilly.",
            2: "The cold is starting to seep in.",
            1: "Your teeth are chattering.",
            0: "The cold pierces you to the bone.",
        }

    def gain_object(self, object):
        # adds an object to a player's inventory
        if object not in self.inventory.keys():
            self.inventory[object] = 1
        else:
            self.inventory[object] += 1

    def tick_player(self, outside_temp_level, radiation_level):
        # updates the player's health according to the temperature
        if outside_temp_level > self.temperature:
            self.temperature += 1
            if self.temperature > 5:
                self.temperature = 5
        elif outside_temp_level < self.temperature:
            self.temperature -= 1
            if self.temperature < 0:
                self.temperature = 0
        if self.temperature == 0:
            self.hp -= 2
            
        # regenerates player health
        self.hp += 1
        
        # updates player health based on hunger
        if self.hp > 100:
            self.hp = 100
        self.hunger -= 1
        self.radiation += radiation_level
        if self.radiation >= 1000:
            self.radiation = 1000
            radiationsicknessmessage = "You taste blood and your head begins to swim."
            self.hp -= 10
        else:
            radiationsicknessmessage = ""


        # returns message based on hunger
        if self.hunger <= 0:
            self.hunger = 0
            hungermessage = "Starvation sets in."
            self.hp -= 5
        else:
            hungermessage = ""
            
        # updates hunger bar
        self.hungerbar = ""
        for i in range(math.ceil(self.hunger / 10)):
            self.hungerbar += "\U0001f356"
        for i in range(10 - math.ceil(self.hunger / 10)):
            self.hungerbar += "\U0000274c"

        self.radiationbar = "\U00002622"
        for i in range(math.ceil(self.radiation / 100)):
            self.radiationbar += ">"
        
        for i in range(11-len(list(self.radiationbar))):
            self.radiationbar += "-"

        self.radiationbar += "\U0001F480"
            
        # returns all values
        return self.temperaturemessage[self.temperature], hungermessage, radiationsicknessmessage

    def eat_food(self, food_name, food_val):
        # eat inputed food name
        self.hunger += food_val
        if self.hunger > 100:
            self.hunger = 100
        self.inventory[food_name] -= 1
        if self.inventory[food_name] == 0:
            self.inventory.pop(food_name)

    def use_item(self, item_name):
        # use an item
        self.inventory[item_name] -= 1
        if self.inventory[item_name] == 0:
            self.inventory.pop(item_name)

    def opp_turn(self, opp_dmg, opp_effects):
        # takes away shield based on opponent damage
        self.shield -= opp_dmg
        if self.shield < 0:
            self.hp += self.shield
            self.shield = 0
            
        # adds effects inflicted to the player's effects
        if opp_effects != {}:
            for i in opp_effects.keys():
                if opp_effects[i] != None:
                    self.effects[i] = opp_effects[i]
                else:
                    for n in range(int(i.split()[1])):
                        self.hp, self.shield, self.atkmult, dmg = effects[i.split()[0]].tick(
                            self.hp, self.shield, self.atkmult, 0, opp_dmg
                        )

    def tick(self):
        
        # ticks all effects on the player, reducing the duration of all of them by 1, any effects with a duration of 0 are added to the remove list
        remove_list = []
        for i in self.effects.keys():
            for n in range(int(i.split()[1])):
                self.hp, self.shield, self.atkmult, dmg = effects[i.split()[0]].tick(
                    self.hp, self.shield, self.atkmult, 0, 0
                )
            self.effects[i] -= 1
            if self.effects[i] <= 0:
                remove_list.append(i)
                    
        # removes all effects on the remove list from the player's effects
        if remove_list != []:
            for i in remove_list:
                self.effects.pop(i)
                
        # transitions any damage not taken by shield to the player's health
        if self.shield < 0:
            self.hp -= self.shield
            self.shield = 0
        self.shield = int(self.shield / 2)
        self.hp = int(self.hp)

    def self_turn(self, shield, health, selfeffects):
        
        # updates player's values
        self.hp += health
        if self.hp > 100:
            self.hp = 100
        self.shield += shield
        for i in selfeffects.keys():
            self.effects[i] = selfeffects[i]


# class representing the map
class map:
    def __init__(self, biomelist):
        
        # inputs possible biomes, accepts a list of region() classes as an input
        self.biomelist = biomelist

        # sets starting biome to a forest
        self.map = {(0, 0): biomelist["Forest"]}

        # sets the starting player location
        self.playerlocation = (0, 0)

    def generatebiome(self, coordinate):
        # generates a biome based on an inputted coordinate
        if coordinate not in self.map.keys():
            biomechoices = []
            for i in [coordinate[0] + 1, coordinate[0] - 1, coordinate[0]]:
                for j in [coordinate[1] + 1, coordinate[1] - 1, coordinate[1]]:
                    if (i, j) in list(self.map.keys()):
                        for k in range(30):
                            biomechoices.append(self.map[(i, j)])
            for i in self.biomelist.keys():
                biomechoices.append(self.biomelist[i])
            self.map[coordinate] = choice(biomechoices)
        return self.map[coordinate]

    def moveplayer(self, direction):
        # takes in an inputted direction and updates the player coordinate based on the direction
        direction = direction.lower()
        previouscoords = self.playerlocation
        if (
            direction == "up"
            or direction == "north"
            or direction == "u"
            or direction == "n"
        ):
            self.playerlocation = (self.playerlocation[0], self.playerlocation[1] - 1)
        elif (
            direction == "down"
            or direction == "south"
            or direction == "d"
            or direction == "s"
        ):
            self.playerlocation = (self.playerlocation[0], self.playerlocation[1] + 1)
        elif (
            direction == "left"
            or direction == "west"
            or direction == "l"
            or direction == "w"
        ):
            self.playerlocation = (self.playerlocation[0] - 1, self.playerlocation[1])
        elif (
            direction == "right"
            or direction == "east"
            or direction == "r"
            or direction == "e"
        ):
            self.playerlocation = (self.playerlocation[0] + 1, self.playerlocation[1])
            
        # generates the biome the player is on
        self.generatebiome(self.playerlocation)
        
        # returns False if the player coordinates have not changed, returns True if the player coordinates have changed
        if previouscoords == self.playerlocation:
            return False
        else:
            return True


# class representing an item
class item:
    def __init__(self, name, weight, crafting_methods):
        self.name = name
        self.weight = weight
        self.crafting_methods = crafting_methods


# class representing a tool (currently unused)
class tool(item):
    def __init__(self, name, weight, crafting_methods, durability, use):
        # sets tool values
        super().__init__(name, weight, crafting_methods)
        self.durability = durability
        self.use = use

    def use_tool(self):
        # changes durability by use
        self.durability -= 1
        if self.durability <= 0:
            return False
        else:
            return True


# class representing a weapon
class weapon(tool):
    def __init__(
        self, name, weight, crafting_methods, durability, attachedmoves, damagemult
    ):
        # sets the values of the weapon
        super().__init__(name, weight, crafting_methods, durability, "weapon")
        self.moves = attachedmoves
        self.damagemult = damagemult

    def use_weapon(self, move):
        # returns a move() class based on the move used
        dura = self.use_tool()
        return dura, self.damagemult, self.moves[move]


# class representing a move
class move:
    def __init__(
        self, name, dmg, effect, shield, heal, type, selfeffect, attachedweapon
    ):
        # sets move values
        self.name = name
        self.dmg = dmg  # damage
        self.effects = effect  # effects inflicted on opponent
        self.shield = shield
        self.type = type
        self.hpgain = heal  # health gain from move
        self.selfeffects = selfeffect  # effects put on user
        self.weapon = attachedweapon  # weapon the move is attached to


# class representing the enemy
class enemy:
    def __init__(self, hp, moves, move_pattern, drops, drop_number):
        self.hp = hp  # health
        self.moves = moves
        self.effects = {}
        self.shield = 0
        self.atkmult = 1  # attack multiplier
        self.move_pattern = move_pattern  # the move pattern the enemy follows
        self.drop_number = drop_number  # how many drops the enemy yields when defeated
        self.pattern_position = 0  # position in move pattern
        self.move_types = (
            {  # possible moves sorted into a dictionary based on the move type
                "attacking": [],
                "defending": [],
                "healing": [],
                "special": [],
            }
        )
        for i in moves:
            self.move_types[i.type].append(i)  # sorts moves into move_types
        self.drops = drops  # sets the possible drops the enemy may give when defeated
        self.orighp = hp  # sets the health the enemy spawns with

    def opp_turn(self, opp_atk, opp_effect):
        # updates shield based on opponet attack
        self.shield -= opp_atk

        # reduces health by any residual attack not absorbed by the shield
        if self.shield < 0:
            self.hp += self.shield
            self.shield = 0
            
        # updates effects based on the effects inflicted by the mov
        if opp_effect != {}:
            for i in opp_effect.keys():
                if opp_effect[i] != None:
                    self.effects[i] = opp_effect[i]
                else:
                    for n in range(int(i.split()[1])):
                        effects[i.split()[0]].tick(
                            self.hp, self.shield, self.atkmult, 0, opp_atk
                        )

    def self_turn(self, opponent_fleeing):
        # determines the move based on the move pattern
        moveselect = choice(
            self.move_types[
                self.move_pattern[self.pattern_position % (len(self.move_pattern))]
            ]
        )
        if opponent_fleeing == True and "attacking" in self.move_types.keys():
            moveselect = choice(self.move_types["attacking"])

        # updates health and shield based on the move
        self.hp += moveselect.hpgain
        self.shield += moveselect.shield

        # updates effects based on the move
        for i in moveselect.selfeffects.keys():
            self.effects[i] = moveselect.selfeffects[i]

        self.pattern_position += 1
        
        # returns all values of the move
        return (
            moveselect.dmg,
            moveselect.effects,
            moveselect.hpgain,
            moveselect.shield,
            moveselect.selfeffects,
            moveselect.name,
        )

    def tick(self):
        remove_list = []

        # updates all effects and adds all effects with duration 0 to remove_list
        for i in self.effects.keys():
            for n in range(int(i.split()[-1])):
                self.hp, self.shield, self.atkmult, dmg = effects[" ".join(i.split()[:-1])].tick(
                    self.hp, self.shield, self.atkmult, 0, 0
                )
            self.effects[i] -= 1
            if self.effects[i] <= 0:
                remove_list.append(i)
        
        # removes all effect values in remove_list
        if remove_list != []:
            for i in remove_list:
                self.effects.pop(i)
        
        # transfers any extra damage not absorbed by shield to health
        if self.shield <= 0:
            self.hp += self.shield
            self.shield = 0

    def reset(self):
        # resets the value of the class so it can be reused in future encounters
        self.hp = self.orighp
        self.atkmult = 1
        self.effects = {}
        self.pattern_position = 0
        self.shield = 0


# class representing effects
class effect:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class rage(effect):
    def __init__(self):
        super().__init__(
            "rage",
            "A pure rage flows through your veins. Increases your attack multiplier.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # adds .3 to the entity's attack multiplier
        entityatkmult += 0.3
        return entityhp, entityshield, entityatkmult, dmg


class raise_guard(effect):
    def __init__(self):
        super().__init__(
            "raise guard",
            "You raise your guard and immediately feel more wary. Gain shield.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # adds 10 shield to entity
        entityshield += 10
        return entityhp, entityshield, entityatkmult, dmg


class poison(effect):
    def __init__(self):
        super().__init__(
            "poison",
            "A toxic smell emits from the chemical. Poisons the enemy, making them take damage every turn.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # entity loses 5 health a turn
        entityhp -= 5
        return entityhp, entityshield, entityatkmult, dmg


class bludgeoning(effect):
    def __init__(self):
        super().__init__(
            "bludgeouning",
            "A hefty blow from this seems powerful. Reduces enemy shield by half.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # halves entity shield
        entityshield = int(entityshield / 2)
        return entityhp, entityshield, entityatkmult, dmg


class piercing(effect):
    def __init__(self):
        super().__init__("piercing", "Seems sharp. Ignores enemy armour.")

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # attack goes through entity shield
        entityshield += dmgincoming
        entityhp -= dmgincoming
        return entityhp, entityshield, entityatkmult, dmg


class weakening_toxin(effect):
    def __init__(self):
        super().__init__(
            "weakening toxin",
            "Contains a potent toxin. Reduces enemy shield and atk multiplier by 25%.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # multiplies shield and attack multiplier by 75%
        entityshield = int(entityshield * 3 / 4)
        entityatkmult = entityatkmult * 3 / 4
        return entityhp, entityshield, entityatkmult, dmg


class healing(effect):
    def __init__(self):
        super().__init__(
            "healing", "Seems rejuvenating. Restores a certain amount of health."
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # adds 10 to entity health
        entityhp += 10
        return entityhp, entityshield, entityatkmult, dmg


class off_balance(effect):
    def __init__(self):
        super().__init__(
            "offbalance",
            "This move seems like it will take the enemy off balance. Removes shield per turn.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # reduces entity shield by 10
        entityshield -= 10
        return entityhp, entityshield, entityatkmult, dmg


class irradiated(effect):
    def __init__(self):
        super().__init__(
            "irradiated",
            "Infects the opponent with radiation, reducing their stats all around.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # halves both entity health and entity shield, and lowering entity attack multiplier by 0.1
        entityhp = int(entityhp * 0.95)
        entityshield = int(entityshield * 0.95)
        entityatkmult -= 0.1
        return entityhp, entityshield, entityatkmult, dmg


class irradiated_frenzy(effect):
    def __init__(self):
        super().__init__(
            "irradiated frenzy",
            "Drives the user into a radiation induced rage, giving extra attack but also harming the user.",
        )

    def tick(self, entityhp, entityshield, entityatkmult, dmg, dmgincoming):
        # raises entity stats all around
        entityhp = int(entityhp * 0.95)
        entityshield = int(entityshield * 0.95)
        entityatkmult += 0.5
        return entityhp, entityshield, entityatkmult, dmg


# class representing a move
class move:
    def __init__(
        self, name, dmg, effect, shield, heal, type, selfeffect, attachedweapon
    ):
        self.name = name
        self.dmg = dmg
        self.effects = effect
        self.shield = shield
        self.type = type
        self.hpgain = heal
        self.selfeffects = selfeffect
        self.weapon = attachedweapon

    def tick(self):
        return self.dmg, self.shield, self.hpgain, self.selfeffects, self.effects
    
class floor:
    def __init__(
        self, enemies, clear_rewards, clear_rewards_amount, description
    ):
        self.enemies = enemies
        self.clear_rewards = clear_rewards
        self.clear_rewards_amount = clear_rewards_amount
        self.description = description

class structure:
    def __init__(
        self, floors, clear_rewards, clear_rewards_amount
    ):
        self.floors = floors
        self.current_player_floor = 0
        self.clear_rewards = clear_rewards
        self.clear_rewards_amount = clear_rewards_amount

# dictionary of effects in the format "name":effect()
effects = {
    "healing": healing(),
    "weakening toxin": weakening_toxin(),
    "piercing": piercing(),
    "bludgeoning": bludgeoning(),
    "poison": poison(),
    "raise guard": raise_guard(),
    "rage": rage(),
    "irradiated": irradiated(),
    "offbalance": off_balance(),
    "irradiated frenzy":irradiated_frenzy()
}

# dictionary of moves in the format "name":move(name, attack, effects inflicted on opponent, shield, health healed, type, effects applied to self, weapons the move is attached to)
moves = {
    "delete":move("delete", 100000, {}, 0, 0, "developer", {}, []),
    "punch": move("punch", 5, {}, 0, 0, "attacking", {}, []),
    "defensive_stance": move("defensive stance", 0, {}, 25, 0, "defending", {}, []),
    "heavy_swing": move(
        "heavy swing",
        10,
        {"bludgeoning 1": None},
        0,
        0,
        "attacking",
        {"raise guard 2": 2},
        [],
    ),
    "light_swing": move(
        "light swing",
        5,
        {"bludgeoning 1": None},
        0,
        0,
        "attacking",
        {"raise guard 1": 2},
        [],
    ),
    "stab": move(
        "stab", 5, {"piercing 1": None}, 0, 0, "attacking", {}, ["sharpened stick"]
    ),
    "bash": move(
        "bash", 2, {"piercing 1": None}, 0, 0, "attacking", {}, ["sharpened stone"]
    ),
    "side_slash": move(
        "slide slash",
        5,
        {"offbalance 1": 3, "bludgeoning 1": None},
        0,
        0,
        "attacking",
        {},
        ["crude stone axe"],
    ),
    "overhead_slash": move(
        "overhead slash",
        10,
        {"bludgeoning 1": None},
        0,
        0,
        "attacking",
        {"raise guard 2": 2},
        ["crude stone axe"],
    ),
    "scavenged_goods": move(
        "scavenged goods", 0, {}, 10, 5, "healing", {"healing 1": 3}, []
    ),
    "poisoned_slash": move(
        "poisoned slash", 5, {"poison 2": 2}, 0, 0, "attacking", {}, []
    ),
    "aggressive_hiss": move(
        "aggressive hiss", 0, {}, 0, 0, "special", {"rage 2": 2}, []
    ),
    "struggle": move("struggle", 0, {}, 0, 0, "special", {}, []),
    "added_padding": move("added padding", 0, {}, 50, 0, "defending", {}, []),
    "bite": move("bite", 10, {"bludgeoning 1": None}, 0, 0, "attacking", {}, []),
    "radioactive_bite": move(
        "radioactive bite",
        10,
        {"bludgeoning 1": None, "irradiated 2": 2},
        0,
        0,
        "attacking",
        {"irradiated frenzy 1": 3},
        [],
    ),
    "irradiated_reinforcement": move(
        "irradiated reinforcement",
        0,
        {},
        30,
        0,
        "defending",
        {"irradiated frenzy 2": None},
        [],
    ),
    "howl": move("howl", 0, {}, 0, 0, "special", {"rage 2": 2}, []),
    "piercing_round": move(
        "piercing round",
        30,
        {"piercing 1": None},
        0,
        0,
        "attacking",
        {"rage 2": 2},
        ["gold plated glock"],
    ),
    "miniaturised_shotgun_round": move(
        "miniaturised shotgun round",
        50,
        {"bludgeoning 1": None},
        0,
        0,
        "attacking",
        {"rage 2": 2},
        ["gold plated glock"],
    ),
    "gun_slinger's_stance": move(
        "gun slinger's stance",
        0,
        {},
        30,
        0,
        "defending",
        {"raise guard 3": 2},
        ["gold plated glock"],
    ),
    "heavy_radiation": move(
        "heavy radiation",
        0,
        {"irradiated 3": 3},
        0,
        0,
        "special",
        {"irradiated frenzy 3": 2},
        ["gamma gun"],
    ),
    "gamma_burst": move(
        "gamma burst",
        5,
        {"irradiated 2": 2},
        0,
        0,
        "attacking",
        {"irradiated frenzy 3": 2},
        ["gamma gun"],
    ),
    "bloodlust": move(
        "bloodlust", 0, {}, 0, 0, "special", {"rage 3": 2}, ["alpha's blade"]
    ),
    "alpha_leadership": move(
        "alpha leadership", 0, {}, 20, 50, "healing", {}, ["alpha's blade"]
    ),
    "full_moon's_call": move(
        "full moon's call", 0, {}, 50, 0, "defending", {"rage 2": 2}, ["alpha's blade"]
    ),
}

# dictionary of items in the format "name":item(name, weight (unused), crafting recipes)
items = {
    "long grass": item("long grass", 2, []),
    "stick": item("stick", 2, []),
    "rotting meat": item("rotting meat", 4, []),
    "wolf meat": item("wolf meat", 5, []),
    "cooked wolf meat": item("cooked wolf meat", 5, []),
    "fur": item("fur", 3, []),
    "lizard skin": item("lizard skin", 2, []),
    "lizard tongue": item("lizard tongue", 4, []),
    "lizard poison": item("lizard poison", 2, []),
    "poisoned lizard tongue": item(
        "poisoned lizard tongue", 5, [{"lizard tongue": 1, "lizard poison": 1}]
    ),
    "wood": item("wood", 5, [{"stick": 8}]),
    "deer meat": item("deer meat", 7, []),
    "cooked deer meat": item("cooked deer meat", 7, []),
    "leaves": item("leaves", 1, []),
    "fruit": item("fruit", 3, []),
    "berries": item("berries", 2, []),
    "elk meat": item("elk meat", 10, []),
    "burned mess": item("burned mess", 1, []),
    "cooked elk meat": item("cooked elk meat", 10, []),
    "irradiated meat": item("irradiated meat", 4, []),
    "radioactive gunk": item(
        "radioactive gunk", 3, [{"irradiated meat": 2, "burned mess": 1}]
    ),
    "vines": item("vines", 2, [{"long grass": 10}]),
    "branch": item("branch", 5, []),
    "sand": item("sand", 2, []),
    "cactus": item("cactus", 4, []),
    "stones": item("stones", 2, []),
    "gold coin": item("gold coin", 1, []),
    "alpha canine": item("alpha canine", 1, []),
    "advanced weaponry fragment": item("advanced weaponry fragment", 1, []),
    "gamma gun core": item("gamma gun core", 1, []),
    "alpha's blade": weapon(
        "alpha's blade",
        3,
        [{"alpha canine": 2, "fur": 7, "sharpened stone": 1, "stick": 2}],
        250,
        [moves["full_moon's_call"], moves["bloodlust"], moves["alpha_leadership"]],
        2,
    ),
    "gamma gun": weapon(
        "gamma gun",
        5,
        [{"gamma gun core": 1, "advanced weaponry fragment": 9}],
        500,
        [moves["gamma_burst"], moves["heavy_radiation"]],
        10,
    ),
    "sharpened stone": weapon(
        "sharpened stone", 2, [{"stones": 3}], 5, [moves["bash"]], 1
    ),
    "sharpened stick": weapon(
        "sharpened stick",
        4,
        [{"branch": 1, "sharpened stone": 1}],
        10,
        [moves["stab"]],
        1,
    ),
    "crude stone axe": weapon(
        "crude stone axe",
        8,
        [{"stones": 5, "branch": 1, "vines": 2}],
        20,
        [moves["side_slash"], moves["overhead_slash"]],
        1.3,
    ),
    "gold plated glock": weapon(
        "gold plated glock",
        3,
        [],
        200,
        [
            moves["piercing_round"],
            moves["miniaturised_shotgun_round"],
            moves["gun_slinger's_stance"],
        ],
        1,
    ),
}

# dictionary of weapons in the format of "name":weapon(name, weight, crafting, durability, moves, weapon attack multiplier)
weaponlist = {
    "alpha's blade": weapon(
        "alpha's blade",
        3,
        [{"alpha canine": 2, "fur": 7, "sharpened stone": 1, "stick": 2}],
        250,
        [moves["full_moon's_call"], moves["bloodlust"], moves["alpha_leadership"]],
        2,
    ),
    "gamma gun": weapon(
        "gamma gun",
        5,
        [{"gamma gun core": 1, "advanced weaponry fragment": 9}],
        500,
        [moves["gamma_burst"], moves["heavy_radiation"]],
        10,
    ),
    "sharpened stone": weapon(
        "sharpened stone", 2, [{"stones": 3}], 5, [moves["bash"]], 1
    ),
    "sharpened stick": weapon(
        "sharpened stick",
        4,
        [{"branch": 1, "sharpened stone": 1}],
        10,
        [moves["stab"]],
        1,
    ),
    "crude stone axe": weapon(
        "crude stone axe",
        8,
        [{"stones": 5, "branch": 1, "vines": 2}],
        20,
        [moves["side_slash"], moves["overhead_slash"]],
        1.3,
    ),
    "gold plated glock": weapon(
        "gold plated glock",
        3,
        [],
        200,
        [
            moves["piercing_round"],
            moves["miniaturised_shotgun_round"],
            moves["gun_slinger's_stance"],
        ],
        1,
    ),
}

# dictionary of biomes in the format of "name":region(possible search items, description, possible encounters)
BiomeList = {
    "Grassland": region(
        {"long grass": 30, "stick": 10, "rotting meat": 5, "wolf meat": 3, "stones": 7},
        "Long grass stretches for miles, many grasses growing up to your knees. Who knows what it could conceal...",
        "Grassland",
        {"scavenger": 10, "poisonous lizard": 20, "rich man": 1},
        "The breeze rustles the tall grass.\n",
        3,
    ),
    "Forest": region(
        {
            "wolf meat": 20,
            "fur": 10,
            "wood": 30,
            "deer meat": 5,
            "leaves": 20,
            "fruit": 10,
            "stones": 8,
        },
        "The leafy green forest seems almost vibrant against the eternally grey clouds. It seems alluring, too alluring...",
        "Forest",
        {"scavenger": 10, "wolf": 15, "rich man": 1},
        "A lone howl pierces the night.\n",
        2,
    ),
    "Tundra": region(
        {"berries": 10, "elk meat": 5, "stones": 3},
        "The tundra white seems to almost blend in with the grey sky. Faded green bushes poke out here and there.",
        "Tundra",
        {"scavenger": 10, "gaunt man": 20},
        "The wind howls across the barren landscape.\n",
        4,
    ),
    "Nuclear Wasteland": region(
        {"irradiated meat": 10},
        "It feels unsettling, the radiation there but unfelt. The barren grey earth indicates no vegetation or signs of life.\n\nYour geiger counter's clicks rapidly blend into a shrill hum.",
        "Nuclear Wasteland",
        {"mutated wolf": 20, "scavenger": 10, "gaunt man": 5, "mutated monstrosity": 1},
        "The night is eerily quiet.\n",
        10,
    ),
    "Jungle": region(
        {
            "fruit": 30,
            "deer meat": 10,
            "wolf meat": 20,
            "vines": 5,
            "branch": 10,
            "stick": 15,
        },
        "The jungle is thick, bird calls and animal howls echoing underneath the canopy. The lush vegetation obscures sight.",
        "Jungle",
        {"scavenger": 10, "wolf": 30, "wolf pack": 10, "baboon": 5, "monkey": 15},
        "A lone howl pierces the night.\n",
        2,
    ),
    "Desert": region(
        {"sand": 30, "cactus": 10},
        "The desert stretches for miles, the once burning sands partially turned to glass from nuclear blasts.",
        "Desert",
        {"scavenger": 10, "gaunt man": 20, "shrivelled husk": 10},
        "The wind howls across the barren landscape.\n",
        6,
    ),
}

# list of enemies in the format of "name":enemy(health, moves, move pattern, drops, drop amount)
EnemyList = {
    "scavenger": enemy(
        50,
        [moves["stab"], moves["scavenged_goods"]],
        ["attacking", "attacking", "healing"],
        ["rotting meat", "elk meat", "branch", "berries", "fruit"],
        2,
    ),
    "poisonous lizard": enemy(
        20,
        [moves["poisoned_slash"], moves["aggressive_hiss"]],
        ["attacking", "attacking", "special"],
        ["poison tipped lizard tongue", "lizard tongue", "lizard skin"],
        1,
    ),
    "rich man": enemy(
        500,
        [moves["struggle"], moves["added_padding"]],
        ["defending", "special", "special", "special", "special"],
        [
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold coin",
            "gold plated glock",
        ],
        23,
    ),
    "wolf": enemy(
        25,
        [moves["side_slash"], moves["howl"], moves["bite"]],
        ["attacking", "special"],
        ["fur", "wolf meat"],
        3,
    ),
    "gaunt man": enemy(
        30,
        [moves["bite"], moves["stab"], moves["overhead_slash"]],
        ["attacking"],
        ["rotting meat", "irradiated meat"],
        4,
    ),
    "mutated wolf": enemy(
        40,
        [moves["radioactive_bite"], moves["irradiated_reinforcement"]],
        ["defending", "attacking", "attacking"],
        ["irradiated meat", "fur", "wolf meat"],
        4,
    ),
    "mutated monstrosity": enemy(
        100,
        [
            moves["radioactive_bite"],
            moves["irradiated_reinforcement"],
            moves["heavy_radiation"],
            moves["gamma_burst"],
        ],
        ["special", "attacking", "attacking", "attacking"],
        [
            "radioactive gunk",
            "radioactive gunk",
            "radioactive gunk",
            "advanced weapon fragment",
            "gamma gun core",
        ],
        2,
    ),
    "wolf pack": enemy(
        150,
        [
            moves["alpha_leadership"],
            moves["full_moon's_call"],
            moves["bloodlust"],
            moves["bite"],
        ],
        ["special", "attacking", "attacking", "defending", "healing"],
        [
            "wolf meat",
            "wolf meat",
            "wolf meat",
            "wolf meat",
            "fur",
            "fur",
            "fur",
            "fur",
            "alpha canine",
        ],
        2,
    ),
    "baboon": enemy(
        75,
        [moves["bash"], moves["bite"]],
        ["attacking"],
        ["vines", "branch", "leaves", "fruit"],
        2,
    ),
    "monkey": enemy(
        30,
        [moves["bite"], moves["bash"]],
        ["attacking"],
        ["vines", "branch", "leaves", "fruit"],
        1,
    ),
    "shrivelled husk": enemy(
        20,
        [moves["bash"], moves["stab"], moves["aggressive_hiss"]],
        ["special", "attacking"],
        ["rotting meat", "sand"],
        3,
    ),
}

# dictionary of edible foods and their hunger values
food_values = {
    "wolf meat": 10,
    "deer meat": 20,
    "fruit": 10,
    "cooked wolf meat": 30,
    "cooked deer meat": 50,
    "rotting meat": 5,
    "cooked rotting meat": 10,
    "elk meat": 30,
    "cooked elk meat": 60,
    "berries":5
}

# dictionary of cookable foods and their cooking times
# if a food is not in the dictionary, it will return "charred mess" with a cooking time of 5
cook_values = {"wolf meat": 20, "deer meat": 30, "rotting meat": 10, "elk meat": 40}

os.system("cls" if os.name == "nt" else "clear")

# initalisation of classes
Fire = campfire(list(cook_values.keys()))
Player = player()
Map = map(BiomeList)

# boolean determining if it is the first turn
first_turn = True

encounter_value_override = None

deletemode = False

invincibility = False

entity_override = False

# main game loop
while Player.hp > 0:
    # updates region
    encounter_value = Map.map[Map.playerlocation].tick_region()

    #overrides encounter with summon command
    if encounter_value_override != None and encounter_value_override in EnemyList.keys():
        print(f"{encounter_value_override} successfully summoned.\n")
        encounter_value = encounter_value_override
    encounter_value_override = None

    # blocks encounter if it is the first turn
    if encounter_value != None and first_turn == False and entity_override == False:

        # entity attacking player message
        if Map.map[Map.playerlocation].name == "Grassland":
            if encounter_value == "scavenger":
                print(f"A {encounter_value} lunges from behind the tall grass, blades flashing.\n")
            elif encounter_value == "poisonous lizard":
                print(f"A hissing {encounter_value} crawls into the open.\n")
            elif encounter_value == "rich man":
                print(f"A {encounter_value} charges towards you, ready to fight.\n")
        elif Map.map[Map.playerlocation].name == "Forest":
            if encounter_value == "scavenger":
                print(f"You hear a screech as a {encounter_value} leaps out from behind a tree.\n")
            elif encounter_value == "wolf":
                print(f"A snarling {encounter_value} springs at you from the underbrush.\n")
            elif encounter_value == "rich man":
                print(f"A {encounter_value} suddenly appears and attacks you.\n")
        elif Map.map[Map.playerlocation].name == "Tundra":
            if encounter_value == "scavenger":
                print(f"A {encounter_value}, wrapped in furs, runs at you with its sword drawn.\n")
            elif encounter_value == "gaunt man":
                print(f"A {encounter_value} attacks with a crazed look in his eyes.\n")
        elif Map.map[Map.playerlocation].name == "Nuclear Wasteland":
            if encounter_value == "mutated wolf":
                print(f"A {encounter_value} lunges at you, eyes glowing with hunger.\n")
            elif encounter_value == "scavenger":
                print(f"A lone {encounter_value}, dressed in rags, hurls a piece of debris at you.\n")
            elif encounter_value == "gaunt man":
                print(f"A {encounter_value} runs at you, hands outstretched.\n")
            elif encounter_value == "mutated monstrosity":
                print(f"A {encounter_value} charges at you, its many eyes glowing with rage.\n")
        elif Map.map[Map.playerlocation].name == "Jungle":
            if encounter_value == "scavenger":
                print(f"A {encounter_value} slashes at you with a rusted dagger.\n")
            elif encounter_value == "wolf":
                print(f"A {encounter_value} lunges at you, fangs bared.\n")
            elif encounter_value == "wolf pack":
                print(f"Howls surround you as a hungry {encounter_value} stalks out from the undergrowth.\n")
            elif encounter_value == "baboon":
                print(f"A {encounter_value} charges at you, head-on.\n")
            elif encounter_value == "monkey":
                print(f"A {encounter_value} swings down from the trees and screeches at you.\n")
        elif Map.map[Map.playerlocation].name == "Desert":
            if encounter_value == "scavenger":
                print(f"A parched {encounter_value} raises his blade, ready to fight.\n")
            elif encounter_value == "gaunt man":
                print(f"A {encounter_value} staggers towards you, a crazed look in his eyes.\n")
            elif encounter_value == "shrivelled husk":
                print(f"A {encounter_value} rises from the sand and shuffles towards you.\n")
        enemy_facing = EnemyList[encounter_value]
        encounter_done = False
        turns = 0
        fleeing = False
        input("Fight >> ")

        # main fight game loop
        while encounter_done == False:
            turns += 1

            # top status bar
            print(f"--Turn {turns}--")
            print(
                f"|{encounter_value}|\U00002764: {enemy_facing.hp}|Next move: {enemy_facing.move_pattern[enemy_facing.pattern_position%(len(enemy_facing.move_pattern))]}|"
            )
            print("-------------")

            # generates list of possible player moves
            possible_moves = []
            move_select_ui = {}
            for i in Player.inventory.keys():
                if i in weaponlist.keys():
                    for f in weaponlist[i].moves:
                        possible_moves.append(f)
            possible_moves.append(moves["punch"])
            possible_moves.append(moves["defensive_stance"])
            if deletemode == True:
                possible_moves.append(moves["delete"])
            for i in range(len(possible_moves)):
                move_select_ui[str(i)] = possible_moves[i - 1]
            
            # generates move selection UI
            for i in move_select_ui.keys():
                print(
                    f"{i}: {move_select_ui[i].name}"
                )  # name of move and key to press to select move
                d, s, h, se, e = move_select_ui[i].tick()  # pulls the move's values
                print(
                    f"|   \U00002694 {d} | \U0001f6e1 {s} | \U00002764 {h}"
                )  # displays the move's damage, shield, and health gain

                # displays self applied effects by the move
                if se != {}:
                    print("|  --SELF--")
                    for i in se:
                        print(f"|  {i}: {se[i]} turns")
                        print(f"|  ({effects[i.split()[0]].description})")
                
                # display effects applied to opponents by the move
                if e != {}:
                    print("|  --ENEMY--")
                    for i in e:
                        if e[i] == None:
                            print(f"|  {i}: instant")
                        else:
                            print(f"|  {i}: {e[i]} turns")
                        print(f"|  ({effects[i.split()[0]].description})")
                print("L---->")
                
            print(f"flee: escape from the battle")
            # lower status bar
            print(f"|\U00002764: {Player.hp}|\U0001f6e1  {Player.shield} |")
            for i in Player.effects.keys():
                print(f"{i} - {effects[i.split()[0]].description}")
            
            # player move selection input
            move_input = input("Move number >> ")
            while move_input not in move_select_ui.keys() and move_input != "flee":
                # asks for input again when input is invalid
                move_input = input("Move number >> ")
            
            if move_input == "flee":
                fleeing = True
            if not fleeing:
                # pulls the details of selected move
                d, s, h, se, e = move_select_ui[move_input].tick()

                # applies shield, health gain, and self applied effects to the player
                Player.self_turn(s, h, se)
                os.system("cls" if os.name == "nt" else "clear")

                # displays the effects of the move
                print(f"You used {move_select_ui[move_input].name}")
                print(f"You deal {d} damage")
                print(f"You gain {s} shield")
                print(f"You heal for {h} health")

                # displays effects gained by player
                if se != {}:
                    for i in se.keys():
                        print(f"You gain {i} for {se[i]} turns")
                
                # displays effects inflicted on opponent
                if e != {}:
                    for i in e.keys():
                        if e[i] == None:
                            print(f"You inflict {i} on enemy {encounter_value}")
                        else:
                            print(
                                f"You inflict {i} on enemy {encounter_value} for {e[i]} turns"
                            )
                input("Press anything to continue >> ")
                os.system("cls" if os.name == "nt" else "clear")

                # inflicts damage and effects on opponent
                enemy_facing.opp_turn(d, e)

            # pulls details of enemy move
            d, e, h, s, se, movechosen = enemy_facing.self_turn(fleeing)
            d = int(d * enemy_facing.atkmult)
            dorig = d
            eorig = e

            if invincibility == True:
                d = 0
                e = {}

            # inflicts damage and effects on player
            Player.opp_turn(d, e)

            if fleeing:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"You turn your back and flee, letting the {encounter_value} get one last move at your turned back.\n")
                input("Press anything to continue >> ")
                os.system("cls" if os.name == "nt" else "clear")

            # displays the effects of opponent's turn
            print(f"{encounter_value} used {movechosen}")
            print(f"{encounter_value} deals {dorig} damage to you")
            print(f"{encounter_value} gains {s} shield")
            print(f"{encounter_value} heals for {h} health")
            if se != {}:
                for i in se.keys():
                    print(f"{encounter_value} gains {i} for {se[i]} turns")
            if eorig != {}:
                for i in eorig.keys():
                    if eorig[i] == None:
                        print(f"{encounter_value} inflicts {i} on you")
                    else:
                        print(f"{encounter_value} inflict {i} on you for {eorig[i]} turns")
            if invincibility == True:
                print("All damage was blocked by your invincibility. ")
            input("Press anything to continue >> ")
            os.system("cls" if os.name == "nt" else "clear")

            # ticks enemy and player effects
            enemy_facing.tick()
            Player.tick()

            # processes loot drops and adds it to player inventory
            if Player.hp <= 0 or enemy_facing.hp <= 0:
                if enemy_facing.hp <= 0:
                    print(f"You successfully defeated {encounter_value}.")
                    loot = []
                    for i in range(enemy_facing.drop_number):
                        loot.append(choice(enemy_facing.drops))
                    print(f"You obtained {', '.join(loot)}")
                    for i in loot:
                        Player.gain_object(i)
                    enemy_facing.reset()
                    input("Press anything to continue >> ")
                    os.system("cls" if os.name == "nt" else "clear")
                encounter_done = True

            if fleeing:
                print("You successfully flee from the battle. ")
                encounter_done = True
                input("Press anything to continue >>")
                os.system("cls" if os.name == "nt" else "clear")
                enemy_facing.reset()
    
    # ends main game loop early if the player is dead from the encounter
    if Player.hp <= 0:
        break
    if first_turn == True:
        print()
        print("Type 'help' for list of commands and tutorial.\n")
    
    # updates the food statuses that are cooking in the fire, updates fire message
    cooked_food, firemessage, firedied = Fire.tick_fire()
    if firedied == True:
        print(f"The fire sputters and dies. Darkness descends upon the {Map.map[Map.playerlocation].name.lower()}.\n")
    elif Fire.dead == True:
        pass

    # returns any finished cooking foods
    if cooked_food != None:
        print(f"You retrieve {cooked_food} from the fire.\n")
        Player.gain_object(cooked_food)
    
    # updates player hp according to the temperature
    hungermessage, temperaturemessage, radiationmessage = Player.tick_player(Fire.firestatus, Map.map[Map.playerlocation].radiation)

    #random messages
    if not first_turn:
        if randint(1,10) == 1:
            print(Map.map[Map.playerlocation].background_message)
        if randint(1, 10) == 1:
            print("Your geiger counter clicks.\n")
    
    # top status bar
    print(
        f"|\U00002764: {Player.hp}|{Player.hungerbar}|{Player.radiationbar}|{Map.map[Map.playerlocation].name}|\n"
    )
    print(firemessage)
    print(temperaturemessage)
    print(radiationmessage)

    # displays starving message
    if hungermessage != "":
        print(hungermessage)
    act = input("\n>> ")
    os.system("cls" if os.name == "nt" else "clear")

    # player command processing
    
    # lights the fire
    if act.lower() == "light fire":
        if Fire.dead:
            Fire.light_fire()
            print(
                "The light from the fire spills through the forest, out into the dark.\n"
            )
        else:
            continue
    
    # stokes the fire
    elif act.lower() == "stoke fire":
        if not Fire.dead:
            Fire.stoke_fire()
            print("You stoke the coals and the fire blazes.\n")
        else:
            continue
    
    # returns random amount of items from biome loot pool
    elif act.lower() == "search":
        found_item = Map.map[Map.playerlocation].search_region()
        found_item = [i for i in found_item if i != None]
        if found_item == []:
            print("You can't seem to find anything.\n")
        else:
            for i in found_item:
                Player.gain_object(i)
            print(f"You look around and find {', '.join(found_item)}.\n")
    
    # displays player inventory
    elif act.lower() == "view inventory":
        print("Inventory:")
        for i in Player.inventory.keys():
            print(f"{Player.inventory[i]} x {i}")
        print()
    
    # displays most recent cooking item
    elif act.lower() == "view cooking":
        if Fire.cooking == []:
            print("Nothing is cooking.")
        else:
            print(
                f"{Fire.cooking[0][0]} will be ready in {Fire.cooking[0][1]} turns.\n"
            )
    
    # displays all unlocked crafting recipes
    elif act.lower() == "view crafting recipes":
        if Player.inventory == {}:
            print("There doesn't seem to be any crafting recipes evident.\n")
        else:
            craftable_recipes = {}

            for j in list(items.keys()):
                for k in items[j].crafting_methods:
                    for l in list(k.keys()):
                        if l in Player.inventory:
                            craftable_recipes[j] = items[j].crafting_methods
            for i in list(craftable_recipes.keys()):
                materials_str = ""
                for j in craftable_recipes[i][0].keys():
                    materials_str += f"{craftable_recipes[i][0][j]} x {j}, "
                print(f"{i}: {materials_str}")
            print()
    
    # help and tutorial system
    elif act.lower() == "help":
        helping = True
        mechanical_helping = False
        os.system("cls" if os.name == "nt" else "clear")
        while helping:
            os.system("cls" if os.name == "nt" else "clear")
            if not mechanical_helping:
                print("INTRODUCTION\n")
                print(
                    "Forest takes place in a post-apocalyptic wasteland, where the weather is forever a frosty -20°C.\nIn order to survive this harsh landscape, you must trek through endless terrain, fight mutated monsters, and above all, survive.\n"
                )
                print("[1]: Game mechanics")
                print("[2]: Available commands")
                print("[3]: Technical information")
                print("[Any other button]: Exit help")
                help_mode = input("\n>> ")
                os.system("cls" if os.name == "nt" else "clear")
            if help_mode == "1":
                mechanical_helping = True
                print("GAME MECHANICS\n")
                print("[1]: The status bar")
                print("[2]: Materials and crafting system")
                print("[3]: Weapons, combat, moves, and effects")
                print("[4]: Temperature, campfire, and cooking food")
                print("[5]: Biomes, loot tables, and encounter values")
                print("[Any other button]: Back")
                mechanic_help_mode = input("\n>> ")
                while mechanical_helping:
                    os.system("cls" if os.name == "nt" else "clear")
                    if mechanic_help_mode == "1":
                        print("STATUS BAR\n")
                        print(
                            "The status bar at the top of your screen gives you vital information to stay alive. It is split into a couple main components:\n"
                        )
                        print(
                            "1. Your health is at the very top right. It displays as a heart symbol and then a number out of 100. When you reach 0 health, the game ends.\n"
                        )
                        print(
                            "2. The hunger bar is second from the left. It displays how much hunger you have left. Eat food to replenish your hunger.\nGet too low, and you will start to starve, taking damage.\n"
                        )
                        print(
                            "3. The radiation bar is third from the left. It displays the dose of radiation you have recieved so far. When it reaches dangerously high levels, you will begin to take damage.\n"
                        )
                        print(
                            "4. The biome you're currently in is at the top right of the status bar. The biome determines what drops and encounters you will find.\nTo learn more, visit [5]: Biomes, loot tables, and encounter values."
                        )
                        if "" in input("\n[Any key to go back]"):
                            help_mode = "1"
                            break
                    elif mechanic_help_mode == "2":
                        print("MATERIALS AND CRAFTING SYSTEM\n")
                        print(
                            "This game also has a crafting system. In order to craft weapons and tools, you will first need to find materials.\n"
                        )
                        print(
                            "Materials are gained randomly when searching, with different materials for different biomes.\n"
                        )
                        print(
                            "In order to know which materials correspond to which biomes, visit [5]: Biomes, loot tables, and encounter values.\n"
                        )
                        print(
                            "You can view the different crafting recipes available, and once you have enough materials, you can begin crafting."
                        )
                        if "" in input("\n[Any key to go back]"):
                            help_mode = "1"
                            break
                    elif mechanic_help_mode == "3":
                        print("WEAPONS, COMBAT, MOVES, AND EFFECTS\n")
                        print(
                            "Along your travels, you may encounter different enemies, ranging from scavengers to mutated monstrosities.\n"
                        )
                        print(
                            "These will randomly appear every turn, and will enter into a turn based combat system.\n"
                        )
                        print(
                            "For each turn, you will perform an available move, and then the enemy will. Unlock more moves by crafting new weapons.\n"
                        )
                        print(
                            "Each move will deal a certain amount of damage, heal for a certain amount, and grant shield.\n"
                        )
                        print(
                            "Enemies will also drop loot once defeated. Some drop common loot you can find by searching, but others drop items necessary to craft powerful weapons."
                        )
                        if "" in input("\n[Any key to go back]"):
                            help_mode = "1"
                            break
                    elif mechanic_help_mode == "4":
                        print("TEMPERATURE, CAMPFIRE, AND COOKING FOOD\n")
                        print(
                            "In this desolate wasteland, it is necessary to keep a fire burning at all times to keep the cold away.\n"
                        )
                        print(
                            "A fire can help keep you warm, but you must stoke it to keep it burning. Fortunately, this does not require resources.\n"
                        )
                        print(
                            "If you don't stoke the fire enough, it will burn out, causing you to start freezing. Freeze for a long enough time and you will start taking damage.\n"
                        )
                        print(
                            "A fire can also help cook food, some meats are cookable and will replenish more hunger when cooked.\n"
                        )
                        print(
                            "But beware, cooking an uncookable object gives you a charred mess, which will be inedible and unusable."
                        )
                        if "" in input("\n[Any key to go back]"):
                            help_mode = "1"
                            break
                    elif mechanic_help_mode == "5":
                        print("BIOMES, LOOT TABLES, AND ENCOUNTER VALUES\n")
                        print(
                            "There are many different biomes in this game, each one yielding different resources when searching: "
                        )
                        for i in BiomeList:
                            print(
                                f"{i}: {', '.join(list(BiomeList[i].loot_table.keys()))}"
                            )
                        print()
                        print("Different entities will also spawn in each biome: ")
                        for i in BiomeList:
                            print(
                                f"{i}: {', '.join(list(BiomeList[i].entity_encounters.keys()))}"
                            )
                        if "" in input("\n[Any key to go back]"):
                            help_mode = "1"
                            break
                    else:
                        mechanical_helping = False
            elif help_mode == "2":
                print("AVAILABLE COMMANDS\n")
                print("{ light fire } - starts the fire\n")
                print("{ stoke fire } - stokes the fire\n")
                print("{ search } - searches the biome for items\n")
                print("{ view inventory } - view player inventory\n")
                print("{ view cooking } - view most recent cooking item\n")
                print("{ view crafting recipes } - views unlocked crafting recipes\n")
                print(
                    "{ eat [item] } - eats the specified item (only edible items will be successfully eaten.)\n"
                )
                print(
                    "{ cook [item] } - cooks the specified item (only cookable items will be succesfully cooked.)\n"
                )
                print(
                    "{ move [direction] } - moves in specified direction (accepts 'up', 'down', 'left', 'right', 'north', 'south', 'east', 'west'.)\n"
                )
                print(
                    "{ craft [item] } - crafts the specified item (will only craft if there are enough materials in player inventory.)"
                )
                if "" in input("\n[Any key to go back]"):
                    pass
            elif help_mode == "3":
                print("CHANGELOG")
                print("Version 1.0.0 - launched game (16/6/25)\n")
                print("Version 1.0.1 - miscellaneous bug fixes and format updates (18/6/25)\n")
                print("TECHNICAL INFORMATION\n")
                print("Version: 1.0.1\n")
                print("Error reporting: ian.tang3@education.nsw.gov.au")
                if "" in input("\n[Any key to go back]"):
                    pass
            else:
                helping = False

    elif act.lower() == "devtools":
        com = input(">> ").lower()

        if com == "diagnose entities":
            for i in EnemyList.keys():
                print(f"{i}: hp{EnemyList[i].hp}|shield{EnemyList[i].shield}|atkmult{EnemyList[i].atkmult}|effects{EnemyList[i].effects}")

        elif com == "toggle deletion":
            if deletemode == True:
                deletemode = False

            else:
                deletemode = True

            print(f"entity deletion toggled to {deletemode}")

        elif com == "max health":
            Player.hp = 100

        elif com == "toggle entity suppression":
            if entity_override == True:
                entity_override = False
            else:
                entity_override = True
            print(f"Entity suppression toggled to {entity_override}.\n")

        elif com == "toggle invincibility":
            if invincibility == True:
                invincibility = False
            else:
                invincibility = True
            print(f"Invincibility toggled to  {invincibility}. \n")



        elif "summon" in com.lower().split(" ")[0]:
            encounter_value_override = " ".join(com.lower().split(" ")[1:])

        elif "forcereset" in com.lower().split(" ")[0]:
            if " ".join(com.lower().split(" ")[1:]) in EnemyList.keys():
                EnemyList[" ".join(com.lower().split(" ")[1:])].reset()

        elif "give" in com.lower().split(" ")[0]:
            if " ".join(com.lower().split(" ")[1:]) in items.keys():
                comamount = input(">> ")
                try:
                    for i in range(int(comamount)):
                        Player.gain_object(" ".join(com.lower().split(" ")[1:]))
                    print(f"{comamount} x {' '.join(com.lower().split(' ')[1:])} given successfully.\n")
                except:
                    os.system("cls" if os.name == "nt" else "clear")

    
    # eats selected food if in food_values dict, otherwise, displays inedible message
    elif "eat" in act.lower().split(" ")[0]:
        act = act.replace("eat ", "")
        if act in Player.inventory.keys() and act in food_values.keys():
            Player.eat_food(act, food_values[act])
            print(f"You swallow the {act} and feel less hungry.\n")
        elif act in Player.inventory.keys():
            print("This does not seem edible.\n")
        else:
            print("You can't seem to find that item.\n")
    
    # cooks selected item, returning cooked (insert item name here) if in cook_values dict, otherwise, returns a charred mess
    elif "cook" in act.lower().split(" ")[0]:
        act = act.lower().replace("cook ", "")
        if act in Player.inventory.keys():
            Fire.add_cooking(act, cook_values)
            Player.use_item(act)
            print(f"You add {act} to the fire.\n")
        else:
            print("You can't seem to find that item.\n")
            
    # moves player around the map, generating a biome if they haven't been there before
    elif "move" in act.lower().split(" ")[0]:
        act = act.lower().replace("move ", "")
        moved = Map.moveplayer(act)
        if moved == False:
            print("You cannot move in that direction.\n")
        else:
            print(Map.map[Map.playerlocation].description)
            print()
            
    # crafts an item if all materials present, otherwise, returns error statement
    elif "craft" in act.lower().split(" ")[0]:
        act = act.lower().replace("craft ", "")
        if act in items.keys():
            desired = items[act]
            craftable = True
            for i in list(desired.crafting_methods[0].keys()):
                if i in Player.inventory.keys():
                    if desired.crafting_methods[0][i] <= Player.inventory[i]:
                        pass
                    else:
                        craftable = False
                else:
                    craftable = False
            if craftable == True:
                Player.gain_object(act)
                for i in items[act].crafting_methods[0].keys():
                    for n in range(items[act].crafting_methods[0][i]):
                        Player.use_item(i)
                if act[0] not in ["a", "e", "i", "o", "u"]:
                    print(f"You successfully craft a {act}.\n")
                else:
                    print(f"You successfully craft an {act}.\n")
            else:
                print("You don't seem to have enough materials...\n")
        else:
            print("That item does not exist.\n")
    else:
        continue
    
    # ends first turn
    first_turn = False

# death screen
os.system("cls" if os.name == "nt" else "clear")
print("The world fades.")
