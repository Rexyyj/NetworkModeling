import random
import simpy
from impl.MMmLimitBuffer import MMm_sys
import matplotlib.pyplot as plt

mmm_config = {
        "LOAD": 0.85,
        "SERVICE": 10.0,
        "ARRIVAL": 0.0,  # need to be set!!
        "TYPE1": 1,
        "SIM_TIME": 500000,
        "QUEUESIZE": 0,
        "SERNUM":2
    }
mmm_config["ARRIVAL"] = mmm_config["SERVICE"] / mmm_config["LOAD"]

# Compare with infinite buffer size
measures = []
buffer_size = []
for i in range(5):
    mmm_config["QUEUESIZE"]=1+i
    buffer_size.append(1+i)
    random.seed(42)

    mmm_sys = MMm_sys(mmm_config)
    env = simpy.Environment()
    # start the arrival processes
    env.process(mmm_sys.arrival_process(env))
    for server in mmm_sys.BusyServer.keys():
        env.process(mmm_sys.busyMonitor(env, server))

    # simulate until SIM_TIME
    env.run(until=mmm_sys.SIM_TIME)
    measure = mmm_sys.calculate_measure(env)
    measures.append(measure)
    print("Finished 1 iteration")

preProProb = []
forCloProb = []
buffOccu = []
busyRate0 = []
busyRate1 = []

queueDelay = []
waitDelay = []
for mea in measures:
    preProProb.append(mea["preProb"])
    forCloProb.append(mea["forwCloudProb"])
    buffOccu.append(mea["avgBufOccu"]) # have some problem in counting !!!!!
    busyRate0.append(mea["serBusyRate"][0])
    busyRate1.append(mea["serBusyRate"][1])
    queueDelay.append(mea["avgQueDel"])
    waitDelay.append(mea["avgWaitDel"])

plt.plot(buffer_size, preProProb, "b", label="Pre-process Prob")
plt.plot(buffer_size, forCloProb, "g", label="Forward Prob")
plt.plot(buffer_size, buffOccu, "r", label="Avg Buffer Occupancy")
plt.plot(buffer_size, busyRate0, "y", label="Busy rate of server0")
plt.plot(buffer_size, busyRate1, "y", label="Busy rate of server1")
plt.legend()
plt.show()


plt.plot(buffer_size, queueDelay, "b", label="Avg Queue delay")
plt.plot(buffer_size, waitDelay, "g", label="Avg wait delay")
plt.legend()
plt.show()
