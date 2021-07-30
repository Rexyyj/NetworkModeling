#!/usr/bin/python3


import random
import simpy


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay,ForwardToCould):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.waitingDelay = 0
        self.forwardToCould = ForwardToCould
        self.bufferCount =0
        self.busytimeCount =0


# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self,Type,ArrivalT):
        self.type = Type
        self.Tarr = ArrivalT


# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE = 10.0 # av service time
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1

SIM_TIME = 500000

arrivals=0
users=0
BusyServer=False # True: server is currently busy; False: server is currently idle

queueSize = 1
MM1=[]

# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue,queueSize):
    global users
    global BusyServer
    while True:
        #print("Arrival no. ",data.arr+1," at time ",environment.now," with ",users," users" )

        # cumulate statistics
        data.arr += 1
        data.ut += users*(environment.now-data.oldT)
        data.oldT = environment.now
        data.bufferCount+=len(MM1)
        # sample the time until the next event
        inter_arrival = random.expovariate(1.0/ARRIVAL)

        #update state variable and put the client in the queue
        # Implementation of controlling queueing size
        if len(queue)<queueSize:
            cl=Client(TYPE1,env.now)
            queue.append(cl)
            users += 1
        else:
            data.forwardToCould+=1
            yield environment.timeout(inter_arrival)
            continue

        if users == 1:
            BusyServer = True
            service_time = random.expovariate(1.0/SERVICE)
            env.process(departure_process(env, service_time,queue))

        # yield an event to the simulator
        yield environment.timeout(inter_arrival)

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue):
    global users
    global BusyServer

    #measure the waiting time
    data.waitingDelay += (environment.now-queue[0].Tarr)

    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

    # cumulate statistics
    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now

    #update state variable and extract the client in the queue
    users -= 1

    user=queue.pop(0)
    data.delay += (env.now-user.Tarr)

    if users==0:
        BusyServer = False
    else:
        service_time = random.expovariate(1.0/SERVICE)
        env.process(departure_process(env, service_time,queue))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"


# ******************************************************************************
def busyMonitor(environment):
    start =0
    while True:
        if BusyServer == True:
            start= environment.now
            while True:
                if BusyServer == False:
                    data.busytimeCount+=environment.now-start
                    break
                yield environment.timeout(0.1)
        yield environment.timeout(0.1)


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(42)

data = Measure(0,0,0,0,0,0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1,queueSize))
env.process(busyMonitor(env))

# simulate until SIM_TIME
env.run(until=SIM_TIME)
print("Total number of packets arrived fog controller: ",data.arr)
print("Number of pre-processed packets: ",data.dep)
print("Pre-processing probability: ",data.dep/data.arr)
print("Number of packets forwarded to could: ",data.forwardToCould)
print("Forward to could probability: ",data.forwardToCould/data.arr)
print("Average number of packets in system:", data.dep/env.now)
print("Average queueing delay: ", data.delay/data.dep)
print("Average waiting delay: ", data.waitingDelay/data.dep) # All packets
print("Average buffer occupancy: ",data.bufferCount/data.arr)
print("Busy time: ",data.busytimeCount)
print("Server busy rate: ",data.busytimeCount/SIM_TIME)
# print output data
# print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
#       data.arr,"- No. of departures =",data.dep,"- No. of forwards =",data.forwardToCould)
#
# print("Load: ",SERVICE/ARRIVAL)
# print("\nArrival rate: ",data.arr/env.now," - Departure rate: ",data.dep/env.now)
#
# print("\nAverage number of users: ",data.ut/env.now)
#
# print("Average delay: ",data.delay/data.dep)
# print("Actual queue size: ",len(MM1))
#
# if len(MM1)>0:
#     print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].Tarr)
