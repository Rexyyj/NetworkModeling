import random
import simpy
from impl.MMmLimitBuffer import MMm_sys
import matplotlib.pyplot as plt
import numpy as np
import math


class Least_Cost(MMm_sys):
    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost = 0

    # Override assign method to least cost
    def assignMethod(self, queue, environment):
        # print("Using least cost assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            free_sers = []
            for ser in self.BusyServer.keys():
                if self.BusyServer[ser] == False:
                    free_sers.append(ser)
            cost = 999
            least_cost_ser = None
            for ser in free_sers:
                if self.cost[ser] < cost:
                    least_cost_ser = ser
                    cost = self.cost[ser]

            if least_cost_ser != None:
                self.totalCost += cost
                self.BusyServer[least_cost_ser] = True
                service_rate = self.SERVICE[least_cost_ser]
                service_time = random.expovariate(1.0 / service_rate)
                environment.process(
                    self.departure_process(environment, service_time, queue, cli, least_cost_ser, service_rate))


class Round_Robin_Cost(MMm_sys):

    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.position = 0
        self.totalCost = 0

    # Override assign method to round robin
    def assignMethod(self, queue, environment):
        # print("Using round robin assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            while True:
                if self.BusyServer[self.position] == False:
                    self.totalCost += self.cost[self.position]
                    self.BusyServer[self.position] = True
                    service_rate = self.SERVICE[self.position]
                    service_time = random.expovariate(1.0 / service_rate)
                    environment.process(
                        self.departure_process(environment, service_time, queue, cli, self.position, service_rate))
                    if self.position == self.serverNum - 1:
                        self.position = 0
                    else:
                        self.position += 1
                    break
                else:
                    if self.position == self.serverNum - 1:
                        self.position = 0
                    else:
                        self.position += 1


class Random_Assign(MMm_sys):
    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost = 0

    # Override assign method to least cost
    def assignMethod(self, queue, environment):
        # print("Using random assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            for ser in self.BusyServer.keys():
                if self.BusyServer[ser] == False:
                    self.totalCost += self.cost[ser]
                    self.BusyServer[ser] = True
                    service_rate = self.SERVICE[ser]
                    service_time = random.expovariate(1.0 / service_rate)
                    environment.process(
                        self.departure_process(environment, service_time, queue, cli, ser, service_rate))
                    break


if __name__ == "__main__":

    random.seed(42)

    mmm_config = {
        "SERVICE": {},
        "ARRIVAL": 10 / 0.85,
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
        "SERNUM": 5
    }

    cost_map = {}
    for i in range(mmm_config["SERNUM"]):
        cost = mmm_config["SERNUM"] - i
        cost_map[i] = cost
        mmm_config["SERVICE"][i] = 15 - cost * 2

    measures = []

    print("Processing random assign...")
    mmm_sys_random = Random_Assign(mmm_config, cost_map)
    env_random = simpy.Environment()
    env_random.process(mmm_sys_random.arrival_process(env_random))
    for server in mmm_sys_random.BusyServer.keys():
        env_random.process(mmm_sys_random.busyMonitor(env_random, server))
    env_random.run(until=mmm_sys_random.SIM_TIME)
    measure_random = mmm_sys_random.calculate_measure(env_random)
    total_random = mmm_sys_random.totalCost
    measures.append(measure_random)

    print("Processing round robin assign...")
    mmm_sys_round = Round_Robin_Cost(mmm_config, cost_map)
    env_round = simpy.Environment()
    env_round.process(mmm_sys_round.arrival_process(env_round))
    for server in mmm_sys_round.BusyServer.keys():
        env_round.process(mmm_sys_round.busyMonitor(env_round, server))
    env_round.run(until=mmm_sys_round.SIM_TIME)
    measure_round = mmm_sys_round.calculate_measure(env_round)
    total_round = mmm_sys_round.totalCost
    measures.append(measure_round)

    print("Processing least cost assign...")
    mmm_sys = Least_Cost(mmm_config, cost_map)
    env = simpy.Environment()
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))
    env.run(until=mmm_sys.SIM_TIME)
    measure_Lest = mmm_sys.calculate_measure(env)
    total_lest = mmm_sys.totalCost
    measures.append(measure_Lest)

    plt.figure()
    x_label = []
    x_num = np.arange(mmm_config["SERNUM"])
    for i in range(mmm_config["SERNUM"]):
        x_label.append("ser" + str(i))

    wid = 0.17
    plt.bar(x_num - wid, measure_random["serBusyRate"].values(), width=wid, label="Random")
    plt.bar(x_num, measure_round["serBusyRate"].values(), width=wid, label="Round")
    plt.bar(x_num + wid, measure_Lest["serBusyRate"].values(), width=wid, label="Least")
    plt.xticks(range(mmm_config["SERNUM"]), x_label)
    plt.xlabel("server")
    plt.ylabel("load on server")
    plt.grid(True)
    plt.legend()
    plt.show()

    local_prob = []
    could_prob = []
    avg_queue = []
    avg_wait = []
    buff_occu = []
    for measure in measures:
        local_prob.append(measure["preProb"])
        could_prob.append(measure["forwCloudProb"])
        avg_queue.append(measure["avgQueDel"])
        avg_wait.append(measure["avgWaitDel"])
        buff_occu.append(measure["avgBufOccu"])

    # x_num = np.arange(3)
    # x_label = ["Random Assign", "Round Robin", "Least Cost"]
    # fig, ax1 = plt.subplots()
    # p1, =ax1.plot(x_num, local_prob, "g-", label="local process prob")
    # p2, =ax1.plot(x_num, buff_occu, "g--", label="avg buffer occu")
    # ax2 = ax1.twinx()
    # p3, = ax2.plot(x_num, avg_queue, "b-", label="avg queue delay")
    # p4, = ax2.plot(x_num, avg_wait, "b--", label="avg wait delay")
    # ax1.yaxis.label.set_color(p1.get_color())
    # ax2.yaxis.label.set_color(p3.get_color())
    # tkw = dict(size=4, width=1.5)
    # ax1.tick_params(axis='y', colors=p1.get_color(), **tkw)
    # ax2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    # plt.xticks(range(3), x_label)
    # ax1.set_xlabel("Assign methods")
    # ax1.set_ylabel("Probability")
    # ax2.set_ylabel("Delays [s]")
    # plt.grid(True)
    # plt.legend(handles=[p1, p2, p3,p4])
    # plt.show()


    labels = ["Random Assign", "Round Robin", "Least Cost"]
    print("\t\t",labels)
    print("LocalProb:",local_prob)
    print("Queue Occu:",buff_occu)
    print("Queue Delay:",avg_queue)
    print("Wait Delay:",avg_wait)
    print("Cost: \t",[total_random,total_round,total_lest])

