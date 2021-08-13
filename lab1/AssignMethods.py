import random
import simpy
from impl.MMmLimitBuffer import MMm_sys


class Round_Robin(MMm_sys):

    def __init__(self, config):
        super().__init__(config)
        self.position = 0

    # Override assign method to round robin
    def assignMethod(self, queue, environment):
        print("Using round robin assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            while True:
                if self.BusyServer[self.position] == False:
                    self.BusyServer[self.position] = True
                    service_time = random.expovariate(1.0 / self.SERVICE)
                    environment.process(self.departure_process(environment, service_time, queue, cli, self.position,self.SERVICE))
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
                self.BusyServer[least_cost_ser] = True
                service_time = random.expovariate(1.0 / self.SERVICE)
                environment.process(self.departure_process(environment, service_time, queue, cli, least_cost_ser,self.SERVICE))


if __name__ == "__main__":

    random.seed(42)

    mmm_config = {
        "LOAD": 0.85,
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
        "SERNUM": 3
    }
    mmm_config["ARRIVAL"] = mmm_config["SERVICE"] / mmm_config["LOAD"]
    cost_map = {}
    for i in range(mmm_config["SERNUM"]):
        cost_map[i] = random.randint(1, 10)

    mmm_sys = Lest_Cost(mmm_config, cost_map)
    # mmm_sys = Round_Robin(mmm_config)
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
