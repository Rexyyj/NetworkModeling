import random
import simpy
from impl.MMmLimitBuffer import MMm_sys
import matplotlib.pyplot as plt
import numpy as np
import math
class First_Assign(MMm_sys):
    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost = 0
        self.loadDist = []
        for j in range(self.serverNum):
            self.loadDist.append(0)


    def assignMethod(self, queue, environment):
        # print("Using random assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            for ser in self.BusyServer.keys():
                if self.BusyServer[ser] == False:
                    self.BusyServer[ser] = True
                    self.totalCost+=self.cost[ser]
                    self.loadDist[ser]+=1
                    service_time = random.expovariate(1.0 / self.SERVICE)
                    environment.process(
                        self.departure_process(environment, service_time, queue, cli, ser, self.SERVICE))
                    break

class Round_Robin(MMm_sys):

    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost =0
        self.position = 0
        self.loadDist = []
        for j in range(self.serverNum):
            self.loadDist.append(0)

    # Override assign method to round robin
    def assignMethod(self, queue, environment):
        # print("Using round robin assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            while True:
                if self.BusyServer[self.position] == False:
                    self.BusyServer[self.position] = True
                    self.totalCost+=self.cost[self.position]
                    self.loadDist[self.position]+=1
                    service_time = random.expovariate(1.0 / self.SERVICE)
                    environment.process(
                        self.departure_process(environment, service_time, queue, cli, self.position, self.SERVICE))
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


class Lest_Cost(MMm_sys):
    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost=0
        self.loadDist = []
        for j in range(self.serverNum):
            self.loadDist.append(0)
    # Override assign method to least cost
    def assignMethod(self, queue, environment):
        # print("Using least cost assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            free_sers = []
            for ser in self.BusyServer.keys():
                if self.BusyServer[ser] == False:
                    free_sers.append(ser)
            cost = math.inf
            least_cost_ser = None
            for ser in free_sers:
                if self.cost[ser] < cost:
                    least_cost_ser = ser
                    cost = self.cost[ser]

            if least_cost_ser != None:
                self.BusyServer[least_cost_ser] = True
                self.totalCost+=self.cost[least_cost_ser]
                self.loadDist[least_cost_ser]+=1
                service_time = random.expovariate(1.0 / self.SERVICE)
                environment.process(
                    self.departure_process(environment, service_time, queue, cli, least_cost_ser, self.SERVICE))


if __name__ == "__main__":

    random.seed(42)

    mmm_config = {
        "SERVICE": 10.0,
        "ARRIVAL": (10 / 0.85),
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
        "SERNUM": 5
    }
    cost_map = {}
    for i in range(mmm_config["SERNUM"]):
        cost_map[i] = mmm_config["SERNUM"]-i

    print("Processing first free assign...")
    mmm_sys_first = First_Assign(mmm_config, cost_map)
    env_first = simpy.Environment()
    env_first.process(mmm_sys_first.arrival_process(env_first))
    for server in mmm_sys_first.BusyServer.keys():
        env_first.process(mmm_sys_first.busyMonitor(env_first, server))
    env_first.run(until=mmm_sys_first.SIM_TIME)
    measure_first = mmm_sys_first.calculate_measure(env_first)
    total_first = mmm_sys_first.totalCost
    load_first = mmm_sys_first.loadDist

    print("Processing round robin assign...")
    mmm_sys_round = Round_Robin(mmm_config,cost_map)
    env_round = simpy.Environment()
    env_round.process(mmm_sys_round.arrival_process(env_round))
    for server in mmm_sys_round.BusyServer.keys():
        env_round.process(mmm_sys_round.busyMonitor(env_round, server))
    env_round.run(until=mmm_sys_round.SIM_TIME)
    measure_round = mmm_sys_round.calculate_measure(env_round)
    total_round = mmm_sys_round.totalCost
    load_round = mmm_sys_round.loadDist

    print("Processing least cost assign...")
    mmm_sys = Lest_Cost(mmm_config, cost_map)
    env = simpy.Environment()
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))
    env.run(until=mmm_sys.SIM_TIME)
    measure_Lest = mmm_sys.calculate_measure(env)
    total_lest = mmm_sys.totalCost
    load_lest = mmm_sys.loadDist

    plt.figure()
    x_label = []
    x_num = np.arange(mmm_config["SERNUM"])
    for i in range(mmm_config["SERNUM"]):
        x_label.append("ser" + str(i))

    wid = 0.17
    plt.grid(True)
    plt.bar(x_num - wid, load_first, width=wid, label="First")
    plt.bar(x_num, load_round,width=wid, label="Round" )
    plt.bar(x_num + wid, load_lest,width=wid, label="Least" )
    plt.xticks(range(mmm_config["SERNUM"]),x_label)
    plt.xlabel("server")
    plt.ylabel("load [packets]")
    plt.legend()
    plt.show()

    plt.grid(True)
    plt.bar(x_num - wid, measure_first["serBusyRate"].values(), width=wid, label="First")
    plt.bar(x_num, measure_round["serBusyRate"].values(),width=wid, label="Round" )
    plt.bar(x_num + wid, measure_Lest["serBusyRate"].values(),width=wid, label="Least" )
    plt.xticks(range(mmm_config["SERNUM"]),x_label)
    plt.xlabel("server")
    plt.ylabel("busy probability")
    plt.legend()
    plt.show()

    print("The total cost of each assign method:")
    print("First assign: ", total_first)
    print("Round robin assign: ",total_round)
    print("Lest cost assign: ",total_lest)
    print("The average waiting delay of each assign method:")
    print("First assign: ", measure_first["avgWaitDel"])
    print("Round robin assign: ",measure_round["avgWaitDel"])
    print("Lest cost assign: ",measure_Lest["avgWaitDel"])
    print("The queuing delay of each assign method:")
    print("First assign: ", measure_first["avgQueDel"])
    print("Round robin assign: ",measure_round["avgQueDel"])
    print("Lest cost assign: ",measure_Lest["avgQueDel"])
    print("The pre-processed prob of each assign method:")
    print("First assign: ", measure_first["preProb"])
    print("Round robin assign: ",measure_round["preProb"])
    print("Lest cost assign: ",measure_Lest["preProb"])

