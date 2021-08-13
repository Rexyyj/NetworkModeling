import random
import simpy
from impl.MMmLimitBuffer import MMm_sys


class Round_Robin(MMm_sys):

    def __init__(self, config):
        super().__init__(config)
        self.position = 0

    def assignMethod(self, queue, environment):
        print("Using round robin assign method!")
        while len(queue) > 0 and (False in self.BusyServer.values()):
            cli = queue.pop(0)
            while True:
                if self.BusyServer[self.position] == False:
                    self.BusyServer[self.position] = True
                    service_time = random.expovariate(1.0 / self.SERVICE)
                    environment.process(self.departure_process(environment, service_time, queue, cli, self.position))
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
    def __init__(self, config):
        super().__init__(config)





if __name__ == "__main__":

    random.seed(42)

    mmm_config = {
        "LOAD": 0.85,
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
        "SERNUM": 2
    }
    mmm_config["ARRIVAL"] = mmm_config["SERVICE"] / mmm_config["LOAD"]

    mmm_sys = Round_Robin(mmm_config)

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
