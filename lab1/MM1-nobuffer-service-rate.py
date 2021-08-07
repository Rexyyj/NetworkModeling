import random
import simpy
from MM1LimitBuffer import MM1_sys
import matplotlib.pyplot as plt

mm1_config = {
    "LOAD": 0.85,
    "SERVICE": 10.0,
    "ARRIVAL": 0,  # need to be set!!
    "TYPE1": 1,
    "SIM_TIME": 500000,
    "QUEUESIZE": 0
}

measures = []
avg_service_time = []
for i in range(10):
    random.seed(42)
    # mm1_config["SERVICE"] = i+1
    mm1_config["LOAD"]=0.1+i*0.2
    avg_service_time.append(0.1+i*0.2)
    mm1_config["ARRIVAL"] = mm1_config["SERVICE"] / mm1_config["LOAD"]
    mm1_sys = MM1_sys(mm1_config)
    env = simpy.Environment()
    # start the arrival processes
    env.process(mm1_sys.arrival_process(env))
    env.process(mm1_sys.busyMonitor(env))

    # simulate until SIM_TIME
    env.run(until=mm1_sys.SIM_TIME)
    measure = mm1_sys.calculate_measure(env)
    measures.append(measure)
    print("Finished 1 iteration")

preProProb = []
forCloProb = []
buffOccu = []
busyRate = []
for mea in measures:
    preProProb.append(mea["preProb"])
    forCloProb.append(mea["forwCloudProb"])
    buffOccu.append(mea["avgBufOccu"])
    busyRate.append(mea["serBusyRate"])

# plt.plot(avg_service_time,preProProb,"b")
plt.plot(avg_service_time,forCloProb,"g")
# plt.plot(avg_service_time,buffOccu,"r")
# plt.plot(avg_service_time,busyRate,"y")
plt.show()
