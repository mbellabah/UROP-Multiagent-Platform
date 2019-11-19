import agent
import environment_details as ed

# TODO: Fix threading issues, in environment and agent_gui
# TODO: Make discounting more sophisticated
# TODO: Implement logical programming via Kanren (logpy)
# TODO: Make agents more descriptive
# TODO: Have agents negotiate on all issues
# TODO: Have agents learn from previous negotiations
# TODO: Implement physical behavior, i.e. attached to charging station
# TODO: Write out the Readme
# TODO: Make agent_gui more descriptive
# TODO: Simplify/Streamline agent_gui.py code


# MARK: Useful functions
def count_occurrences(my_dict: dict) -> tuple:
    n_cs = len([0 for key, _ in my_dict.items() if key.startswith('CS', 0, 2)])
    return n_cs, len(my_dict) - n_cs


# MARK: Attributes
initial_offer_0 = {
    'Price': 10,
    'Volume': 4,
    'Duration': 3,
    'Sender': 'EV0'
}

initial_offer_1 = {
    'Price': 15,
    'Volume': 5,
    'Duration': 7,
    'Sender': 'EV1'
}

_initial_offer_0 = agent.Offer(proposal=initial_offer_0)
_initial_offer_1 = agent.Offer(proposal=initial_offer_1)

node_pos_ = {
    'EV0': (400, 275),
    'CS0': (600, 275)
}

edges_list_ = "EV0:CS0"

if __name__ == '__main__':

    # System deployment
    agent_main = agent.Main(*count_occurrences(node_pos_))
    environment = ed.EnvironmentMap(node_pos_, edges_list_, agent_dict=agent_main.agent_dict)

    # agent_main.run()
    # --> environment.render_network()     # iffy: main program runs while pygame is open in separate (non-responsive) thread

    # Send the charge request, initialize the negotiation thread
    # agent_main.submit_charge_request('EV0', _initial_offer_0)
    #
    # # Shutdown all communications
    # agent_main.ns.shutdown()

