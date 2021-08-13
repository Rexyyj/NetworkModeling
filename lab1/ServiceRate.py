import random
import simpy
from impl.MMmLimitBuffer import MMm_sys


class Service_Rate(MMm_sys):
    def __init__(self, config, cost):
        super().__init__(config)
        self.cost = cost
        self.totalCost = 0

    # Override assign method to least cost
    def assignMethod(self, queue, environment):
        print("Using least cost assign method!")
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

    def __init__(self, config,cost):
        super().__init__(config)
        self.cost=cost
        self.position = 0
        self.totalCost = 0

    # Override assign method to round robin
    def assignMethod(self, queue, environment):
        print("Using round robin assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            while True:
                if self.BusyServer[self.position] == False:
                    self.totalCost += self.cost[self.position]
                    self.BusyServer[self.position] = True
                    service_rate = self.SERVICE[self.position]
                    service_time = random.expovariate(1.0 / service_rate)
                    environment.process(self.departure_process(environment, service_time, queue, cli, self.position,service_rate))
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
        print("Using random assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            for ser in self.BusyServer.keys():
                if self.BusyServer[ser] == False:
                    self.totalCost+=self.cost[ser]
                    self.BusyServer[ser] = True
                    service_rate = self.SERVICE[ser]
                    service_time = random.expovariate(1.0 / service_rate)
                    environment.process(
                        self.departure_process(environment, service_time, queue, cli, ser, service_rate))
                    break


if __name__ == "__main__":

    random.seed(42)

    mmm_config = {
        "LOAD": 0.85,
        "SERVICE": {},
        "ARRIVAL": 10 / 0.85,
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
        "SERNUM": 3
    }
    cost_list = [10, 5, 1]
    cost_map = {}
    for i in range(mmm_config["SERNUM"]):
        cost = cost_list[i]
        cost_map[i] = cost
        mmm_config["SERVICE"][i] = 15 - cost

    mmm_sys = Random_Assign(mmm_config, cost_map)

    env = simpy.Environment()

    # start the arrival processes
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))

    # simulate until SIM_TIME
    env.run(until=mmm_sys.SIM_TIME)

    measure = mmm_sys.calculate_measure(env)

    print("Total number of packets arrived fog controller: ", measure["numFogPack"])
    print("Number of pre-processed packets: ", measure["numPrePack"])
    print("Pre-processing probability: ", measure["preProb"])
    print("Number of packets forwarded to could: ", measure["numForwCloud"])
    print("Forward to could probability: ", measure["forwCloudProb"])
    print("Average number of packets in system:", measure["avgNumPack"])
    print("Average queueing delay: ", measure["avgQueDel"])
    print("Average waiting delay: ", measure["avgWaitDel"])  # All packets
    print("Average buffer occupancy: ", measure["avgBufOccu"])
    print("Busy time: ", measure["busyTime"])
    print("Server busy rate: ", measure["serBusyRate"])
    print("Cost of each server: ", cost_map)
    print("Rate of each server: ", mmm_config["SERVICE"])
    print("Total cost: ",mmm_sys.totalCost)
