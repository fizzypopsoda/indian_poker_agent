import random

actions = 6

class InfoSet:

    def __init__(self):
        self.key = ""
        self.regret_sum = []
        self.strategy_sum = []
        self.strategy = []
        self.reach_pr = 0
        self.reach_pr_sum = 0

    def init(self, param):
        self.key = param
        self.regret_sum = [0] * actions
        self.strategy_sum = [0] * actions
        self.strategy = [0] * actions
        for i in range(actions):
            self.strategy[i] = 1.0 / actions

    def next_strategy(self):
        for i in range(actions):
            self.strategy_sum[i] += self.reach_pr * self.strategy[i]
        self.calculate_strategy()
        self.reach_pr_sum += self.reach_pr
        self.reach_pr = 0

    def calculate_strategy(self):
        total = 0
        for i in range(actions):
            self.strategy[i] = max(self.regret_sum[i], 0)
            total += self.strategy[i]
        if total > 0:
            for i in range(actions):
                self.strategy[i] /= total
        else:
            for i in range(actions):
                self.strategy[i] = 1.0 / actions

    def get_average_strategy(self):
        s = [0] * actions
        total = self.reach_pr_sum

        if total == 0:
            # Return a uniform strategy when reach_pr_sum is zero
            for i in range(actions):
                s[i] = 1.0 / actions
        else:
            # Calculate the average strategy
            for i in range(actions):
                s[i] = self.strategy_sum[i] / total
                if s[i] < 0.001:
                    s[i] = 0

            # Normalize the strategy
            total = sum(s)
            if total > 0:
                for i in range(actions):
                    s[i] /= total

        return s

    def get_next_move(self):
        strat = self.get_average_strategy()
        num = random.uniform(0, 1)
        for i in range(6):
            num -= strat[i]
            if num <= 0:
                return i
        return 5

    def get_next_move_limited(self):
        strat = self.get_average_strategy()
        sum = 0
        strat[3] = strat[4] = 0
        strat[5] = (strat[0] + strat[1] + strat[2]) / 10.0
        for i in range(6):
            sum += strat[i]
        for i in range(6):
            strat[i] /= sum
        num = random.uniform(0, 1)
        for i in range(6):
            num -= strat[i]
            if num <= 0:
                return i
        return 5

    def get_random_move(self):
        return random.randint(0, 5)


# dictionary
m = {}


def cfr(history="", c1=-1, c2=-1, p1=1, p2=1, pc=1, turn=False, bet1=0.5, bet2=1):
    global regrets

    # Base cases:

    # Start of game
    if history == "":
        ev = 0
        for i in range(13):
            for j in range(13):
                ev += cfr("rr", i, j, 1, 1, (12 if i == j else 16) / 2652.0)
        return ev / 169

    end = history[-1]
    # End of game
    if end == 'c' or end == 'f':
        card_player = int(c1) if not turn else int(c2)
        card_opponent = int(c2) if not turn else int(c1)
        if end == 'c':
            if card_player == card_opponent:
                return 0
            elif card_player < card_opponent:
                return bet1
            else:
                return -bet1
        else:
            if not turn:
                return bet2 + ((100 - bet2) / 2.0) if c1 == 12 else bet2
            else:
                return bet1 + ((100 - bet1) / 2.0) if c2 == 12 else bet1

    key = str(int(c1) if not turn else int(c2)) + " " + history
    if key not in m:
        info_set = InfoSet()
        info_set.init(key)
        m[key] = info_set

    s = m[key].strategy
    if not turn:
        m[key].reach_pr += p1
    else:
        m[key].reach_pr += p2

    action_utils = [0] * actions
    invalid = set()

    if not turn:
        action_utils[0] = -1 * cfr(history + "f", c1, c2, p1 * s[0], p2, pc, not turn, bet1, bet2)
    else:
        action_utils[0] = -1 * cfr(history + "f", c1, c2, p1, p2 * s[0], pc, not turn, bet1, bet2)

    if len(history) > 2:
        if not turn:
            action_utils[1] = -1 * cfr(history + 'c', c1, c2, p1 * s[1], p2, pc, not turn, bet2, bet2)
        else:
            action_utils[1] = -1 * cfr(history + "c", c1, c2, p1, p2 * s[1], pc, not turn, bet1, bet1)
    else:
        invalid.add(1)

    if bet1 < 100 and bet2 < 100:

        if not turn:
            if 3 * bet2 < 100:
                action_utils[2] = -1 * cfr(history + "r3", c1, c2, p1 * s[2], p2, pc, not turn, 3 * bet2, bet2)
            else:
                invalid.add(2)
        else:
            if 3 * bet1 < 100:
                action_utils[2] = -1 * cfr(history + "r3", c1, c2, p1, p2 * s[2], pc, not turn, bet1, 3 * bet1)
            else:
                invalid.add(2)

        if not turn:
            if 5 * bet2 < 100:
                action_utils[3] = -1 * cfr(history + "r5", c1, c2, p1 * s[3], p2, pc, not turn, 5 * bet2, bet2)
            else:
                invalid.add(3)
        else:
            if 5 * bet1 < 100:
                action_utils[3] = -1 * cfr(history + "r5", c1, c2, p1, p2 * s[3], pc, not turn, bet1, 5 * bet1)
            else:
                invalid.add(3)

        if not turn:
            if 10 * bet2 < 100:
                action_utils[4] = -1 * cfr(history + "r10", c1, c2, p1 * s[4], p2, pc, not turn, 10 * bet2, bet2)
            else:
                invalid.add(4)
        else:
            if 10 * bet1 < 100:
                action_utils[4] = -1 * cfr(history + "r10", c1, c2, p1, p2 * s[4], pc, not turn, bet1, 10 * bet1)
            else:
                invalid.add(4)

        if not turn:
            action_utils[5] = -1 * cfr(history + "s", c1, c2, p1 * s[5], p2, pc, not turn, 100, bet2)
        else:
            action_utils[5] = -1 * cfr(history + "s", c1, c2, p1, p2 * s[5], pc, not turn, bet1, 100)

    else:
        invalid.add(2)
        invalid.add(3)
        invalid.add(4)
        invalid.add(5)

    util = 0
    for i in range(actions):
        if i not in invalid:
            util += action_utils[i] * s[i]

    regrets = [0] * actions
    for i in range(actions):
        if i not in invalid:
            regrets[i] = action_utils[i] - util

    if not turn:
        for i in range(actions):
            m[key].regret_sum[i] += p2 * pc * regrets[i]
    else:
        for i in range(actions):
            m[key].regret_sum[i] += p1 * pc * regrets[i]
    return util


def legal(move, turn, bet1, bet2) -> bool:
    if move <= 1:
        return True
    elif move == 5:
        return bet1 < 100 and bet2 < 100
    elif move == 2:
        if not turn:
            return 3 * bet2 < 100
        else:
            return 3 * bet1 < 100
    elif move == 3:
        if not turn:
            return 5 * bet2 < 100
        else:
            return 5 * bet1 < 100
    else:
        if not turn:
            return 10 * bet2 < 100
        else:
            return 10 * bet1 < 100


def sim(rounds):
    v = ["f", "c", "r3", "r5", "r10", "s"]
    chips = 0
    hands = 0
    for tt in range(rounds):
        for i in range(52):
            for j in range(52):
                if i != j:
                    c1 = i // 4
                    c2 = j // 4
                    history = "rr"
                    turn = False
                    bet1 = 0.5
                    bet2 = 1
                    while True:
                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set
                        move = m[key].get_next_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet1 = bet2
                        elif move == 2:
                            bet1 = 3 * bet2
                        elif move == 3:
                            bet1 = 5 * bet2
                        elif move == 4:
                            bet1 = 10 * bet2
                        else:
                            bet1 = 100

                        turn = not turn
                        end = history[-1]
                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips += bet1
                                else:
                                    chips -= bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips += bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips += bet2
                                else:
                                    if c2 == 12:
                                        chips -= bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips -= bet1
                            hands += 1
                            break

                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set
                        move = m[key].get_next_move_limited()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move_limited()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet2 = bet1
                        elif move == 2:
                            bet2 = 3 * bet1
                        elif move == 3:
                            bet2 = 5 * bet1
                        elif move == 4:
                            bet2 = 10 * bet1
                        else:
                            bet2 = 100
                        turn = not turn
                        end = history[-1]
                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips += bet1
                                else:
                                    chips -= bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips += bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips += bet2
                                else:
                                    if c2 == 12:
                                        chips -= bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips -= bet1
                            hands += 1
                            break
        for i in range(52):
            for j in range(52):
                if i != j:
                    c1 = i // 4
                    c2 = j // 4
                    history = "rr"
                    turn = False
                    bet1 = 0.5
                    bet2 = 1
                    while True:
                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set

                        move = m[key].get_next_move_limited()

                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move_limited()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet1 = bet2
                        elif move == 2:
                            bet1 = 3 * bet2
                        elif move == 3:
                            bet1 = 5 * bet2
                        elif move == 4:
                            bet1 = 10 * bet2
                        else:
                            bet1 = 100
                        turn = not turn

                        end = history[-1]
                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips -= bet1
                                else:
                                    chips += bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips -= bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips -= bet2
                                else:
                                    if c2 == 12:
                                        chips += bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips += bet1
                            hands += 1
                            break

                        key = str(c1 if not turn else c2) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set
                        move = m[key].get_next_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet2 = bet1
                        elif move == 2:
                            bet2 = 3 * bet1
                        elif move == 3:
                            bet2 = 5 * bet1
                        elif move == 4:
                            bet2 = 10 * bet1
                        else:
                            bet2 = 100
                        turn = not turn

                        end = history[-1]
                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips -= bet1
                                else:
                                    chips += bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips -= bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips -= bet2
                                else:
                                    if c2 == 12:
                                        chips += bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips += bet1
                            hands += 1
                            break
    print("Limited CFR agent simulation")
    print(f"Net chips gained: {chips:.2f}")
    print(f"Hands played: {hands}")
    print(f"Average chips/hand gain when facing limited CFR agent: {chips / hands:.3f}")


def sim_random(rounds):
    v = ["f", "c", "r3", "r5", "r10", "s"]
    chips = 0
    hands = 0
    for tt in range(rounds):
        for i in range(52):
            for j in range(52):
                if i != j:
                    c1 = i // 4
                    c2 = j // 4
                    history = "rr"
                    turn = False
                    bet1 = 0.5
                    bet2 = 1
                    while True:
                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set

                        move = m[key].get_next_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet1 = bet2
                        elif move == 2:
                            bet1 = 3 * bet2
                        elif move == 3:
                            bet1 = 5 * bet2
                        elif move == 4:
                            bet1 = 10 * bet2
                        else:
                            bet1 = 100

                        turn = not turn
                        end = history[-1]

                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips += bet1
                                else:
                                    chips -= bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips += bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips += bet2
                                else:
                                    if c2 == 12:
                                        chips -= bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips -= bet1
                            hands += 1
                            break
                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set

                        move = m[key].get_random_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_random_move()
                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet2 = bet1
                        elif move == 2:
                            bet2 = 3 * bet1
                        elif move == 3:
                            bet2 = 5 * bet1
                        elif move == 4:
                            bet2 = 10 * bet1
                        else:
                            bet2 = 100
                        turn = not turn
                        end = history[-1]

                        if end == 'c' or end == 'f':
                            if end == 'c':
                                if c1 == c2:
                                    pass  # tie
                                elif c1 < c2:
                                    chips += bet1
                                else:
                                    chips -= bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips += bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips += bet2
                                else:
                                    if c2 == 12:
                                        chips -= bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips -= bet1
                            hands += 1
                            break
        for i in range(52):
            for j in range(52):
                if (i != j):
                    c1 = i // 4
                    c2 = j // 4
                    history = "rr"
                    turn = False
                    bet1 = 0.5
                    bet2 = 1

                    while (True):
                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set

                        move = m[key].get_random_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_random_move()

                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet1 = bet2
                        elif move == 2:
                            bet1 = 3 * bet2
                        elif move == 3:
                            bet1 = 5 * bet2
                        elif move == 4:
                            bet1 = 10 * bet2
                        else:
                            bet1 = 100

                        turn = not turn
                        end = history[-1]

                        if end == 'c' or end == 'f':
                            if end == 'c':
                                # tie
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips -= bet1
                                else:
                                    chips += bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips -= bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips -= bet2
                                else:
                                    if c2 == 12:
                                        chips += bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips += bet1
                            hands += 1
                            break

                        key = str(int(c1) if not turn else int(c2)) + " " + history
                        if key not in m:
                            info_set = InfoSet()
                            info_set.init(key)
                            m[key] = info_set

                        move = m[key].get_next_move()
                        while not legal(move, turn, bet1, bet2):
                            move = m[key].get_next_move()

                        history += v[move]
                        if move == 0:
                            pass
                        elif move == 1:
                            bet2 = bet1
                        elif move == 2:
                            bet2 = 3 * bet1
                        elif move == 3:
                            bet2 = 5 * bet1
                        elif move == 4:
                            bet2 = 10 * bet1
                        else:
                            bet2 = 100

                        turn = not turn
                        end = history[-1]

                        if end == 'c' or end == 'f':
                            if end == 'c':
                                # tie
                                if c1 == c2:
                                    pass
                                elif c1 < c2:
                                    chips -= bet1
                                else:
                                    chips += bet1
                            else:
                                if not turn:
                                    if c1 == 12:
                                        chips -= bet2 + ((100 - bet2) / 2)
                                    else:
                                        chips -= bet2
                                else:
                                    if c2 == 12:
                                        chips += bet1 + ((100 - bet1) / 2)
                                    else:
                                        chips += bet1
                            hands += 1
                            break

    print("Random agent simulation")
    print(f"Net chips gained: {chips:.2f}")
    print(f"Hands played: {hands}")
    print(f"Average chips/hand gain when facing random agent: {chips / hands:.3f}")


def solve(a, b):
    tt = a
    ev = 0
    print("Training CFR agent for", tt, "iterations")
    for _ in range(tt):
        ev += cfr()
        for j in m.values():
            j.next_strategy()
    ev /= tt
    print(ev)
    # for i in m:
    #     print(i)
    #     if i in m:
    #         print(m[i].get_average_strategy())

    sim(b)
    sim_random(b)


def main():
    tc = 1
    train = 500
    sim = 1000
    while tc > 0:
        solve(train, sim)
        tc -= 1


if __name__ == "__main__":
    main()
