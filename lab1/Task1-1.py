import random
import simpy
from impl.MM1LimitBuffer import MM1_sys
import matplotlib.pyplot as plt

mm1_config = {
    "SERVICE": 0.0,
    "ARRIVAL": 30,
    "TYPE1": 1,
    "SIM_TIME": 500000,
    "QUEUESIZE": 0
}
service_time_range = [1,60]
step = 1
service = service_time_range[0]
measures = []
avg_service_time = []
it = 0
theo_drop = []
while service <= service_time_range[1]:
    it = it+1
    random.seed(42)
    mm1_config["SERVICE"] = service
    avg_service_time.append(service)
    # mm1_config["ARRIVAL"] = mm1_config["SERVICE"] / mm1_config["LOAD"]

    mm1_sys = MM1_sys(mm1_config)
    env = simpy.Environment()
    # start the arrival processes
    env.process(mm1_sys.arrival_process(env))
    env.process(mm1_sys.busyMonitor(env))

    # simulate until SIM_TIME
    env.run(until=mm1_sys.SIM_TIME)
    measure = mm1_sys.calculate_measure(env)
    measures.append(measure)
    print("Finished iteration {}".format(it))
    ro = mm1_config["SERVICE"]/mm1_config["ARRIVAL"]
    drop =ro/(1+ro)
    theo_drop.append(drop)


    service += step

preProProb = []
forCloProb = []

busyRate = []

queueDelay = []
waitDelay = []
for mea in measures:
    preProProb.append(mea["preProb"])
    forCloProb.append(mea["forwCloudProb"])
    busyRate.append(mea["serBusyRate"])
    queueDelay.append(mea["avgQueDel"])
    waitDelay.append(mea["avgWaitDel"])


plt.plot(avg_service_time, preProProb, "b", label="pre-process prob")
plt.plot(avg_service_time, busyRate, "r", label="server busy rate")
plt.plot(avg_service_time, forCloProb, "g", label="forward prob")
plt.xlabel('service time [s]')
plt.ylabel('normalized value')
plt.grid(True)
plt.legend()
plt.show()


plt.plot(avg_service_time, queueDelay, "b", label="avg queue delay")
plt.plot(avg_service_time, waitDelay, "g", label="avg wait delay")
plt.xlabel('service time [s]')
plt.ylabel('delay time [s]')
plt.legend()
plt.grid(True)
plt.show()


plt.plot(avg_service_time, forCloProb, "g", label="Measure")
plt.plot(avg_service_time,theo_drop, "r", label="Theory")
plt.xlabel('service time [s]')
plt.ylabel('forward probability')
plt.grid(True)
plt.legend()
plt.show()
