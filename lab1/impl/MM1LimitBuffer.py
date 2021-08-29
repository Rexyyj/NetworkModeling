#!/usr/bin/python3


import random
import simpy


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self, Narr, Ndep, NAveraegUser, OldTimeEvent, AverageDelay, waitingDelay, forwardToCould, bufferCount,
                 busytimeCount):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.waitingDelay = waitingDelay
        self.forwardToCould = forwardToCould
        self.bufferCount = bufferCount
        self.busytimeCount = busytimeCount


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self, Type, ArrivalT):
        self.type = Type
        self.Tarr = ArrivalT


class MM1_sys:
    def __init__(self, config):
        self.SERVICE = config["SERVICE"]  # av service time
        self.ARRIVAL = config["ARRIVAL"]  # av inter-arrival time
        self.TYPE1 = config["TYPE1"]
        self.queueSize = config["QUEUESIZE"]

        self.SIM_TIME = config["SIM_TIME"]

        self.arrivals = 0
        self.users = 0
        self.BusyServer = False  # True: server is currently busy; False: server is currently idle
        self.MM1 = []

        self.data = Measure(0, 0, 0, 0, 0, 0, 0, 0, 0)

        self.config = config
    # *********************************************************************
    def arrival_process(self, environment):
        queue = self.MM1
        queueSize = self.queueSize
        while True:
            # print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )

            # cumulate statistics
            self.data.arr += 1
            self.data.ut += self.users * (environment.now - self.data.oldT)
            self.data.bufferCount += len(queue)*(environment.now - self.data.oldT)
            self.data.oldT = environment.now

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

            if self.users == 1:
                self.BusyServer = True
                service_time = self.calculate_service_time(self.config)
                environment.process(self.departure_process(environment, service_time, queue))

            # yield an event to the simulator
            yield environment.timeout(inter_arrival)

    # ******************************************************************************
    def departure_process(self, environment, service_time, queue):
        # measure the waiting time
        self.data.waitingDelay += (environment.now - queue[0].Tarr)

        yield environment.timeout(service_time)
        # print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

        # cumulate statistics
        self.data.dep += 1
        self.data.ut += self.users * (environment.now - self.data.oldT)
        self.data.bufferCount += len(queue)*(environment.now - self.data.oldT)
        self.data.oldT = environment.now

        # update state variable and extract the client in the queue
        self.users -= 1

        user = queue.pop(0)
        self.data.delay += (environment.now - user.Tarr)

        if self.users == 0:
            self.BusyServer = False
        else:
            service_time = self.calculate_service_time(self.config)
            environment.process(self.departure_process(environment, service_time, queue))

    def calculate_service_time(self, conf):
        param = 1/conf["SERVICE"]
        return random.expovariate(param)

    # ******************************************************************************
    def busyMonitor(self, environment):
        start = 0
        while True:
            if self.BusyServer:
                start = environment.now
                while True:
                    if not self.BusyServer:
                        self.data.busytimeCount += environment.now - start
                        break
                    yield environment.timeout(1)
            yield environment.timeout(1)

    def calculate_measure(self, env):
        return {
            "numFogPack": self.data.arr,
            "numPrePack": self.data.dep,
            "preProb": self.data.dep / self.data.arr,
            "numForwCloud": self.data.forwardToCould,
            "forwCloudProb": self.data.forwardToCould / self.data.arr,
            "avgNumPack": self.data.ut / env.now,
            "avgQueDel": self.data.delay / self.data.dep,
            "avgWaitDel": self.data.waitingDelay / self.data.dep,
            "avgBufOccu": self.data.bufferCount /env.now,
            "busyTime": self.data.busytimeCount,
            "serBusyRate": self.data.busytimeCount / self.SIM_TIME
        }


if __name__ == "__main__":
    random.seed(42)

    mm1_config = {
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 2,
    }
    LOAD =0.85
    mm1_config["ARRIVAL"] = mm1_config["SERVICE"] / LOAD
    mm1_sys = MM1_sys(mm1_config)

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
