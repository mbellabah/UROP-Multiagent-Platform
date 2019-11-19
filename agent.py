import time, random, math, datetime, copy
from osbrain import run_agent, run_nameserver, Agent
from collections import defaultdict
import agent_gui as ag

# TODO: Get multiple agents onto the system and have them learn negotiation tactics via insights
# TODO: Use the offer object rather than sharing dictionaries

# -> Information marketplace?
GUI = False

# MARK: Signals
MAIN_CHANNEL = 'main'   # Main channel by which all agents communicate


# MARK: Functions
def renewable_generation_func(t, a=300, k=0.06666, b=13) -> float:
    return float((a*math.exp(-k*(t-b)**2))/10)


def base_load_curve(t, a=116.06, b=-50.67, c=21.861, d=-2.554, e=0.1189, f=-0.001962) -> float:
    return float((a + b * t + c * (t ** 2) + d * (t ** 3) + e * (t ** 4) + f * (t ** 5))/100)


def current_time() -> float:
    now = datetime.datetime.now()
    return float(str(now.hour) + '.' + str(now.minute))


# MARK: Offer Classes
class Offer(object):    # TODO: Have it encapsulate everything
    def __init__(self, closed=False, proposal=None, notes=None, round=0 ):
        self._time_created = datetime.datetime.now()
        self.time_created = f'{self._time_created:%Y-%m-%d %H:%M:%S}'

        self.closed = closed
        self.notes = notes
        self.round = round

        if proposal is not None:
            self.proposal = proposal
        else:
            self.proposal = self.build_proposal()

    def build_proposal(self) -> dict:
        offer_dictionary = {
            'Price': self.price,
            'Volume': self.volume,
            'Duration': self.duration
        }
        return offer_dictionary

    def __str__(self) -> str:
        return str(self.proposal)

    def __repr__(self):
        return str(self.proposal)


# MARK: Agent Classes
class ChargingStation(Agent):
    def on_init(self):

        # Attributes
        self.ev_current_offer = None
        self.my_current_offer = None
        self.price_range = [10, 20]
        self.volume_range = [1, 5]
        self.duration_range = [3, 7]
        self.weightings = [0.5, 0.3, 0.2]

        self.type = 'Charging Station'
        self.amount_charging_devices = random.randint(6, 12)
        self.connected_EVs = []
        self.max_load = None
        self.base_price = 5
        self.avg_load = 12
        self.n_connected_EVs = None
        self.max_k = 8
        self.current_k = 0
        self.transaction_log = defaultdict(list)    # Looks like date: list(n_connected_EVs)

        # MARK: GUI
        if GUI:
            self.gui = ag.GUI(name=self.name, agent_object=self)
            self.gui.run()

        # MARK: Communication
        self.bind('PUB', alias=MAIN_CHANNEL)

    def receive_charge_request(self, offer: Offer) -> None:

        if self.current_k > self.max_k:
            self.log_info(f'{self.name} chooses to opt out')
        else:
            self.ev_current_offer = offer

            cs_expected_value = self.generate_expected_offer_value()
            value_of_ev_offer = self.evaluate_offer(self.ev_current_offer)
            counter_proposal = Offer(proposal=self.ev_current_offer, round=self.current_k)

            self.log_info(f"Received opponent offer: {self.ev_current_offer}")

            if value_of_ev_offer > cs_expected_value:    # Negotiation closed
                self.log_info(f"Acceptable opponent offer: {value_of_ev_offer} > {cs_expected_value}")
                counter_proposal.closed = True
                setattr(counter_proposal.proposal, 'Sender', self.name)

                # Log transaction into self.transactions_log and attach EV
                self.transaction_log[self.today_date].append(counter_proposal)
                # self.attach_ev(ev=None) --> Add the EV

            else:   # Negotiations proceed
                self.log_info(f"Unacceptable opponent offer: {value_of_ev_offer} < {cs_expected_value}")
                _notes = 'Suggest you increase price to increase offer value'    # Improve suggestions
                # Counter proposal created informed by the _notes above
                self.my_current_offer = self.deliberate_current_offer(self.ev_current_offer)

                self.my_current_offer.proposal['Sender'] = self.name
                counter_proposal.proposal = self.my_current_offer
                counter_proposal.notes = _notes
                counter_proposal.round += 1
                self.current_k += 1

            # Send counter proposal, can be accept or deny
            self.continue_negotiation(counter_proposal, self.ev_current_offer.proposal['Sender'])

    # MARK: Utility functions
    @property
    def n_connect_EVs(self) -> int:
        return len(self.connected_EVs)

    @property
    def today_date(self) -> str:
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')

    @property
    def avg_connected_EVs(self) -> int:
        if len(self.transaction_log) > 0:
            return sum([len(connected_list) for _, connected_list in self.transaction_log.items()])/len(self.transaction_log)
        return 1

    def discount_factor_appropriate(self) -> float:
        # Check to see if the negotiating opponent is making their offer gradually better
        # For now return 0.97
        return 0.94

    # MARK: Transaction functions
    def deliberate_current_offer(self, offer) -> Offer:
        ''' deliberates on current offer and submits some counter offer '''
        omega = 0.5
        _avg_price = 17     # TODO: Fix this up

        counter_offer = copy.deepcopy(offer)

        def _price(offer_price, avg_price):
            evs_connected_atm = self.n_connect_EVs if self.n_connect_EVs > 0 else 1
            return offer_price*(1-omega*(self.avg_connected_EVs/evs_connected_atm)*((offer_price-avg_price)/offer_price))

        def _volume():
            pass

        def _duration():
            pass

        counter_offer.proposal['Price'] = _price(offer.proposal['Price'], _avg_price)   # TODO: Create property to find average price
        counter_offer.proposal['Avg_Price'] = _avg_price
        counter_offer.proposal['Sender'] = self.name
        return counter_offer

    def generate_expected_offer_value(self) -> float:   # Generates its expected offer value
        '''
        Generates the expected offer value based on its current state and reservations
        :return: Float, offer value
        '''

        # We implement discounting in the generate expected value - we assume that
            # that the the negotiating opponent is updating their values in a manner
            # consistent with the discounting on the part of the CS agent

        A = 0.95    # Threshold charge value
        duty_cycle = 0.75

        discount_factor = self.discount_factor_appropriate()

        idling_charging_devices = self.amount_charging_devices - self.n_connect_EVs
        IR = duty_cycle/idling_charging_devices
        load_ev = sum([((A - ev.SOC)*ev.battery_capacity)/((A - ev.SOC)/0.25) for ev in self.connected_EVs])
        load_net = load_ev - renewable_generation_func(current_time())

        # Some parameters that can be later adjusted based on agent's performance
        alpha_1 = 1
        alpha_2 = random.randrange(1, 10)/100   # Sweet spot seems to be 0.01
        delta = 0.02

        return (discount_factor**self.current_k)*self.base_price*(1+delta)*(alpha_1*IR + alpha_2*(load_net/self.avg_load)**2)

    def evaluate_offer(self, offer: Offer) -> float:    # Takes in a offer and makes it a dict, and gives a numerical value
        offer = offer.proposal
        assert sum(self.weightings) == 1, "Ensure weightings sum to 1"

        def value_increasing_linear(x, range_list) -> float:
            return (x-range_list[0])/(range_list[1]-range_list[0])

        def value_decreasing_linear(x, range_list) -> float:
            return 1-((x-range_list[0])/(range_list[1]-range_list[0]))

        issue_value_list = [
            value_increasing_linear(offer['Price'], self.price_range),
            value_decreasing_linear(offer['Volume'], self.volume_range),
            value_decreasing_linear(offer['Duration'], self.duration_range)
        ]

        return sum(i[0] * i[1] for i in zip(issue_value_list, self.weightings))

    def attach_ev(self, ev) -> None:
        assert self.n_connected_EVs < self.amount_charging_devices, 'All charging ports in use'
        self.connected_EVs.append(ev)
        self.amount_charging_devices -= 1

    def detach_ev(self, ev) -> None:
        assert ev in self.connected_EVs, 'EV to remove not attached prior'
        self.connected_EVs.remove(ev)
        self.amount_charging_devices += 1

    # MARK: Communication functions
    def continue_negotiation(self, counter_proposal, send_to: str) -> None:    # TODO: Complete the negotiation function
        self.send(
            MAIN_CHANNEL,
            message=counter_proposal,
            topic=send_to,
            wait=5
        )

    def negotiation_receive_ev_response(self, counter_proposal) -> None:
        self.receive_charge_request(counter_proposal)


class ElectricVehicle(Agent):
    def on_init(self):

        # Attributes
        self.my_current_offer = None
        self.cs_current_offer = None

        self.caring_of_issues = [0.3, 0.2, 0.5]     # Issues the EV agent cares most about
        self.k_max = random.randint(3, 12)
        self.current_k = 1
        self.chain = []
        self.transaction_log = defaultdict(list)

        # MARK: GUI
        if GUI:
            self.gui = ag.GUI(name=self.name, agent_object=self)
            self.gui.run()

        # MARK: Communication
        self.bind('PUB', MAIN_CHANNEL)

    # MARK: Useful functions
    @property
    def today_date(self) -> str:
        now = datetime.datetime.now()
        return now.strftime('%Y-%m-%d')

    # MARK: Transaction functions
    @property
    def cs_offer_momentum(self) -> bool:    # Opponent value has been increasing (T), or decreasing (F)
        assert len(self.chain) >= 2, 'Chain is not long enough to capture momentum'
        issues = ['Price', 'Volume', 'Duration']

        def evaluate_offer(opp_offer) -> float:
            opp_offer_proposal = opp_offer.proposal

            def deviation_fn(agent_val, opp) -> float:
                return (agent_val - opp)/agent_val

            agent_list = [self.my_current_offer.proposal[issue] for issue in issues]
            opp_list = [opp_offer_proposal[issue] for issue in issues]
            deviation_value_list = [deviation_fn(agent, opp) for agent, opp in zip(agent_list, opp_list)]

            return sum([weight*dev_value for weight, dev_value in zip(self.caring_of_issues, deviation_value_list)])

        return evaluate_offer(self.chain[-1]) >= evaluate_offer(self.chain[-2])

    def deliberate_current_offer(self, offer: Offer) -> Offer:
        ''' deliberates on current offer and submits some counter offer dict '''
        omega = self.omega()

        assert isinstance(offer, Offer), 'Ensure that offer is an Offer object'
        self.chain.append(offer)    # We attach previous offer to the chain
        counter_offer = copy.deepcopy(offer)    # Offer is an Offer object - note how we have to select .proposal dict

        def _price(offer_price, avg_price):
            x = 0.05 if offer_price < avg_price else 0.03
            return offer_price*omega*(1 + min([x, (avg_price-offer_price)/offer_price]))

        def _volume():  # TODO: Implement something for volume
            pass

        def _duration():
            pass

        # Alter the various values of each issue - for now only Price
        counter_offer.proposal['Price'] = _price(offer.proposal['Price'], offer.proposal['Avg_Price'])   # TODO: Create property to find average price
        counter_offer.proposal['Sender'] = self.name
        return counter_offer

    def omega(self) -> float:    # Tactic function

        def round_dependent(current_k=self.current_k, k_max=self.k_max, behavior='boulware', offset=0.3) -> float:
            c = 0.5
            beta = 6 if behavior == 'appeaser' else 0.7
            return offset + math.exp(math.log(c)*(1 - (min([current_k, k_max])/k_max))**beta)

        def absolute_tit_for_tat(steps = 2, issue='Price', M=3) -> float:
            assert len(self.chain) >= 2, 'Chain is not long enough for abs tit-for-tat'
            opp_var = self.cs_current_offer.proposal[issue]
            opp_var_steps = self.chain[-steps].proposal[issue]
            my_var = self.my_current_offer.proposal[issue]

            s = 0 if self.cs_offer_momentum else 1 # 0 if agent's value has been increasing, else 1
            R = random.randrange(0, M)  # Maximum amount by which agent will deviate from pure imitation

            return 1 - (((opp_var - opp_var_steps) + ((-1)**s)*R)/my_var)

        behavior_weights = {
            1: round_dependent,
            2: absolute_tit_for_tat
        }

        if len(self.chain) >= 2:
            random_value = random.randint(1, 2)
            beh = behavior_weights[random_value]()   # Select a behavior randomly
            print(f'Using {random_value} with {beh}')
        else:
            beh = behavior_weights[1]()
        return beh

    # MARK: Communication functions
    def send_charge_request(self, offer, send_to) -> None:
        self.my_current_offer = offer
        self.send(
            send_to,
            self.my_current_offer,
            wait=5
        )

    def negotiation_receive_cs_response(self, counter_proposal: Offer) -> None:
        self.cs_current_offer = counter_proposal.proposal

        if self.current_k > self.k_max:
            self.log_info(f'{self.name} chooses to opt out')
        else:
            if counter_proposal.closed:  # Offer accepted
                self.log_info(f'{self.name} previous offer {self.my_current_offer} was ACCEPTED!')
                self.log_info(f'Received opponent offer: {self.cs_current_offer}')
                self.chain.append(self.my_current_offer)
                self.transaction_log[self.today_date].append(self.my_current_offer)

            else:   # Continue negotiations
                self.log_info(f'{self.name} previous offer {self.my_current_offer} was REJECTED!')
                self.log_info(f'Received opponent offer: {self.cs_current_offer}')
                self.my_current_offer = self.deliberate_current_offer(self.cs_current_offer)
                self.continue_negotiation(self.my_current_offer, self.cs_current_offer.proposal['Sender'])    # For now, we go ahead with the CS offer

    def continue_negotiation(self, counter_proposal: Offer, send_to) -> None:    # TODO: Complete the negotiation function
        self.my_current_offer = counter_proposal
        self.current_k += 1
        self.send(
            MAIN_CHANNEL,
            counter_proposal,
            topic = send_to,
            wait=5
        )


class Main:
    def __init__(self, n_cs: int, n_ev: int) -> None:

        self.cs_dict = {}
        self.ev_dict = {}

        # System deployment
        self.ns = run_nameserver()
        for i in range(n_cs):
            self.cs_dict[f'CS{i}'] = run_agent(f'CS{i}', base=ChargingStation)      # <alias, base_class>
        for y in range(n_ev):
            self.ev_dict[f'EV{y}'] = run_agent(f'EV{y}', base=ElectricVehicle)

    def run(self) -> None:

        # System configuration
        for cs_name, cs_agent in self.cs_dict.items():
            for ev_name, ev_agent in self.ev_dict.items():

                cs_agent.connect(ev_agent.addr(MAIN_CHANNEL), handler={cs_name:'negotiation_receive_ev_response', 'ev_charge_request': 'receive_charge_request'})
                ev_agent.connect(cs_agent.addr(MAIN_CHANNEL), handler={ev_name:'negotiation_receive_cs_response'})

    @property
    def agent_dict(self) -> dict:
        # We merge the two dicts
        return {**self.cs_dict, **self.ev_dict}

    def submit_charge_request(self, ev, sample_offer) -> None:
        assert self.ev_dict[ev], f'{ev} does not exist'
        self.ev_dict[ev].send(MAIN_CHANNEL, sample_offer, topic='ev_charge_request')



