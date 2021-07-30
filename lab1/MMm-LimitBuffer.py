#!/usr/bin/python3


import random
import simpy


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay):
        self.arr = Narr
        self.dep = Ndep
        self.ut = NAveraegUser
        self.oldT = OldTimeEvent
        self.delay = AverageDelay
        self.waitingDelay = 0
        self.forwardToCould = 0
        self.bufferCount =0
        self.busytimeCount = {}


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
queueSize = 1
serverNum = 2
SIM_TIME = 500000

arrivals=0
users =0
MM1=[]

BusyServer={} # True: server is currently busy; False: server is currently idle
for i in range(serverNum):
    BusyServer[i]=False

for elem in BusyServer:
    print (elem)


# ******************************************************************************
# generator yield events to the simulator
# ******************************************************************************

# arrivals *********************************************************************
def arrival_process(environment,queue,queueSize,serverNum):
    global BusyServer
    global users
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
            users+=1
        else:
            data.forwardToCould+=1
            yield environment.timeout(inter_arrival)
            continue

        while len(queue)>0 and (False in BusyServer.values()):
            cli = queue.pop(0)
            for server in BusyServer.keys():
                if BusyServer[server] == False:
                    BusyServer[server] = True
                    service_time = random.expovariate(1.0/SERVICE)
                    env.process(departure_process(env, service_time,queue,cli,server))
                    print("Assigned to Server: ",server)
                    break


        # yield an event to the simulator
        yield environment.timeout(inter_arrival)

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"

# ******************************************************************************

# departures *******************************************************************
def departure_process(environment, service_time, queue,user,server):
    global BusyServer
    global users
    data.waitingDelay += (environment.now-user.Tarr)

    yield environment.timeout(service_time)
    #print("Departure no. ",data.dep+1," at time ",environment.now," with ",users," users" )

    # cumulate statistics

    data.dep += 1
    data.ut += users*(environment.now-data.oldT)
    data.oldT = environment.now
    users -= 1
    #update state variable and extract the client in the queue
    data.delay += (env.now-user.Tarr)

    if len(queue)==0:
        BusyServer[server] = False
    else:
        cli = queue.pop(0)
        service_time = random.expovariate(1.0/SERVICE)
        env.process(departure_process(env, service_time,queue,cli,server))

        # the execution flow will resume here
        # when the "timeout" event is executed by the "environment"


# ******************************************************************************
def busyMonitor(environment,server):
    data.busytimeCount[server]=0
    while True:
        if BusyServer[server] == True:
            start= environment.now
            while True:
                if BusyServer[server] == False:
                    data.busytimeCount[server]+=environment.now-start
                    break
                yield environment.timeout(1)
        yield environment.timeout(1)


# ******************************************************************************
# the main body of the simulation
# ******************************************************************************


# create the environment

random.seed(42)

data = Measure(0,0,0,0,0)

env = simpy.Environment()

# start the arrival processes
env.process(arrival_process(env, MM1,queueSize,serverNum))
for server in BusyServer.keys():
    env.process(busyMonitor(env,server))

# simulate until SIM_TIME
env.run(until=SIM_TIME)


print("Total number of packets arrived fog controller: ",data.arr)
print("Number of pre-processed packets: ",data.dep)
print("Pre-processing probability: ",data.dep/data.arr)
print("Number of packets forwarded to could: ",data.forwardToCould)
print("Forward to could probability: ",data.forwardToCould/data.arr)
print("Average number of packets in system:", data.ut/env.now)
print("Average queueing delay: ", data.delay/data.dep)
print("Average waiting delay: ", data.waitingDelay/data.dep) # All packets
print("Average buffer occupancy: ",data.bufferCount/data.arr)
print("Busy time: ",data.busytimeCount)
busyRate = {}
for server in data.busytimeCount.keys():
    busyRate[server] = data.busytimeCount[server]/SIM_TIME
print("Server busy rate: ",busyRate)
