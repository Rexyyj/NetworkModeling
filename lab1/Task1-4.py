import random
import simpy
from impl.MM1LimitBuffer import MM1_sys


class MG1_sys(MM1_sys):

    def __init__(self, config):
        super().__init__(config)

    def calculate_service_time(self, conf):
        return random.gammavariate(conf["alpha"], conf["beta"])


if __name__ == "__main__":
    random.seed(42)

    mm1_config = {
        "LOAD": 0.85,
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 3,
        "SERVICE_CONF": {}
    }

    mm1_config["ARRIVAL"] = mm1_config["SERVICE"] / mm1_config["LOAD"]
    mm1_config["SERVICE_CONF"] = {"alpha": 1, "beta": 2}
    mm1_sys = MG1_sys(mm1_config)

    env = simpy.Environment()

    # start the arrival processes
    env.process(mm1_sys.arrival_process(env))
    env.process(mm1_sys.busyMonitor(env))

    # simulate until SIM_TIME
    env.run(until=mm1_sys.SIM_TIME)

    measure = mm1_sys.calculate_measure(env)

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
