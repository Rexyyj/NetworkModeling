#!/usr/bin/python3


import random
import simpy


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.waitingDelay = 0
        self.forwardToCould = 0
        self.bufferCount = 0
        self.busytimeCount = {}


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, Type, ArrivalT):
        self.type = Type
        self.Tarr = ArrivalT


class MMm_sys:
    def __init__(self, config):
        self.LOAD = config["LOAD"]
        self.SERVICE = config["SERVICE"]  # av service time
        self.ARRIVAL = config["ARRIVAL"]  # av inter-arrival time
        self.TYPE1 = config["TYPE1"]
        self.SIM_TIME = config["SIM_TIME"]

        self.queueSize = config["QUEUESIZE"]
        self.serverNum = config["SERNUM"]


        self.arrivals = 0
        self.users = 0
        self.MMm = []
        self.data = Measure(0, 0, 0, 0, 0)

        self.BusyServer = {}  # True: server is currently busy; False: server is currently idle
        for i in range(self.serverNum):
            self.BusyServer[i] = False

    # arrivals *********************************************************************
    def arrival_process(self, environment):
        queue = self.MMm
        queueSize = self.queueSize

        while True:
            # cumulate statistics
            self.data.arr += 1
            self.data.ut += self.users * (environment.now - self.data.oldT)
            self.data.oldT = environment.now
            self.data.bufferCount += len(self.MMm)
            # sample the time until the next event
            inter_arrival = random.expovariate(1.0 / self.ARRIVAL)

            # update state variable and put the client in the queue
            # Implementation of controlling queueing size
            if len(queue) < (queueSize + 1):
                cl = Client(self.TYPE1, environment.now)
                queue.append(cl)
                self.users += 1
            else:
                self.data.forwardToCould += 1
                yield environment.timeout(inter_arrival)
                continue

            while len(queue) > 0 and (False in self.BusyServer.values()):
                cli = queue.pop(0)
                for ser in self.BusyServer.keys():
                    if self.BusyServer[ser] == False:
                        self.BusyServer[ser] = True
                        service_time = random.expovariate(1.0 / self.SERVICE)
                        environment.process(self.departure_process(environment, service_time, queue, cli, ser))
                        break

            # yield an event to the simulator
            yield environment.timeout(inter_arrival)

            # the execution flow will resume here
            # when the "timeout" event is executed by the "environment"

    # departures *******************************************************************
    def departure_process(self, environment, service_time, queue, user, server):

        self.data.waitingDelay += (environment.now - user.Tarr)

        yield environment.timeout(service_time)
        # print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

        # cumulate statistics

        self.data.dep += 1
        self.data.ut += self.users * (environment.now - self.data.oldT)
        self.data.oldT = environment.now
        self.users -= 1
        # update state variable and extract the client in the queue
        self.data.delay += (environment.now - user.Tarr)

        if len(queue) == 0:
            self.BusyServer[server] = False
        else:
            cli = queue.pop(0)
            service_time = random.expovariate(1.0 / self.SERVICE)
            environment.process(self.departure_process(environment, service_time, queue, cli, server))

            # the execution flow will resume here
            # when the "timeout" event is executed by the "environment"

# ******************************************************************************
    def busyMonitor(self, environment, server):
        self.data.busytimeCount[server] = 0
        while True:
            if self.BusyServer[server] == True:
                start = environment.now
                while True:
                    if self.BusyServer[server] == False:
                        self.data.busytimeCount[server] += environment.now - start
                        break
                    yield environment.timeout(1)
            yield environment.timeout(1)

    def calculate_measure(self,env):
        busyRate = {}
        for server in self.data.busytimeCount.keys():
            busyRate[server] = self.data.busytimeCount[server] / self.SIM_TIME
        return {
            "numFogPack": self.data.arr,
            "numPrePack": self.data.dep,
            "preProb": self.data.dep / self.data.arr,
            "numForwCloud": self.data.forwardToCould,
            "forwCloudProb": self.data.forwardToCould / self.data.arr,
            "avgNumPack": self.data.ut / env.now,
            "avgQueDel": self.data.delay / self.data.dep,
            "avgWaitDel": self.data.waitingDelay / self.data.dep,
            "avgBufOccu": self.data.bufferCount / self.data.arr,
            "busyTime": self.data.busytimeCount,
            "serBusyRate": busyRate
        }

# ******************************************************************************
# the main body of the simulation
# ******************************************************************************

if __name__=="__main__":

    random.seed(42)

    mmm_config = {
        "LOAD": 0.85,
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 0,
        "SERNUM":1
    }
    mmm_config["ARRIVAL"] = mmm_config["SERVICE"] / mmm_config["LOAD"]

    mmm_sys = MMm_sys(mmm_config)

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
