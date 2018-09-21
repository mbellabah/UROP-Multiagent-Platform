from typing import NamedTuple
import agent

'''
Agents will assign qualifiers after receiving several locutions
Fuzzy logic will be applied: Friendly, Neutral, Rival, Enemy

In our case, all threats, promises and etc. will be achieved 
throught the offer object -- that's to say, in a threat, agent-b
will threaten opt out of the negotiation (closed = True) and set 
all issues (quantities like price, volume, duration, etc.) to 0
    -> Create the mechanisms to handle this on the side of the 
        EV 

Look at tester style of programming. Whenever an agent receives
some locution from another agent, it will simulate the locution
and depending on whether the value is positive or negative, will 
proceed to next state of locution. Testing Testing . . .
'''

# MARK: Locutions; typically looks like <object, object, function>
Assist = NamedTuple('Assist', [('from', object), ('who', object), ('action', lambda: None)])
Threaten = NamedTuple('Threaten', [('from', object), ('who', object), ('action', lambda: None), ('t_action', lambda:None)])
Promise = NamedTuple('Promise', [('from', object), ('who', object), ('action', lambda: None)])


# MARK: The classes that describe BID
class belief:
    def __init__(self):
        pass

    def __call__(self):
        pass


class desire:
    def __init__(self):
        pass

    def __call__(self):
        pass


class interest:
    def __init__(self):
        pass

    def __call__(self):
        pass


if __name__ == '__main__':
    def say_hi() -> str:
        return "Hi!"

    def say_bye() -> str:
        return "Bye!"

    my_threat = Threaten('Me', say_hi, say_bye)
    # Agent will simulate the scenario to see what would happen, it then assigns a qualifier
    # to the locution


