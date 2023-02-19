#Paco Navarro
#2/17/2023
#EXTREMEwater.py for MCM

import random 
import numpy as np
import matplotlib.pyplot as plt
import math

#In this function Determine the WFPS of water after a certain number of time steps and an annual starting time

def water(intialWater, startT, time, Area, xH, xW ):
    """Simulates water as a function of time in a random environment
        Intial water helps set the area in which this is happening, assuming our soil is saturated
        time is time in hours
        xHeat (prob of extreme temp change, Intensity, duration)
        xWater (prob of extreme rain fall, Intensity, duration)"""
    if Area==0:
        Area = intialWater/500 #If we don't know the water amount we will assume the plot of soil we are selecting will be saturated
    timestep = 8 #time is in hours
    numsteps = time/timestep #length of time step 
    numstep = int(numsteps) #calaculates the number of steps that will be taken in this simulation
    tempList = Temp(time, startT)
    fTemp = tempList[0] #define a starting step
    pressure = 1 #initial pressure in atmospheres
    ratio0 = intialWater/Area
    waterlist = [ratio0/975]
    xlist= [0]
    tL = [263]
    dcount= 0 #if the system has died
    X1= 0 #Current length left of extreme temp
    X2= 0 #Current length left of extreme rain
    X3 =0 #are we leaving a drought
    xW[0]= .75+ (xW[0])*.25 #normalizes the rain function

    for step in range(0,numstep): #for each time step

        #Determines how much water is evaporated
        airDensity= pressure/ fTemp / .286 #determines air density using pvnrt
        iTemp= fTemp   #update i temp
        #if drought vast change in temp else do a small random walk
        if xH[2]*random.randint(0,1000)/1000 < xH[0] and X2 == 0:
            xtreme = Xheat(tempList[int(step/3)], xH[1], pressure)
            fTemp =  xtreme[0]
            pressure = xtreme[1]
            deltaT = abs(fTemp -iTemp)
            X1 += xH[2]-1
        elif X1 != 0:
            fTemp += random.randint(-4,4)
            pressure=  pressure 
            deltaT = abs(fTemp -iTemp)#how much the temp changes
            X1 += -1
            if X1 == 0:
                X3 = 1
        else:
            fTemp = tempList[int(step/3)] + random.randint(-2,2) #shifts temp by random walk 
            deltaT = fTemp -iTemp
            if deltaT < 0 and X3==1 :
                X3= 0
                deltaT = -deltaT
        tL.append(fTemp) 
        specificHeat= .2 #define specfic heat of soil
        thermalRes= 1.222* 10 #thermal resistance of soil: calculated based on the integral of the amount of air that circulates over a unit area per timestep
        heatCap= 4.186    #Heat capacity of water
        dis = evaporation(airDensity, deltaT, specificHeat, thermalRes, Area, heatCap, timestep, pressure) 
        pressure = dis[1]


        #Simulates rain
        adjust = 2*pressure
        rainchance= random.randint(0,1000) + adjust
        if rainchance > 950:
            if random.randint(0,1000)/1000 < xW[0] and X1 == 0:
                fall = Xrain(xW[2],xW[0], pressure, timestep)
                X2 += xW[2]-1
            elif X2 != 0:
                fall =Xrain(xW[2],xW[0], pressure, timestep)
                X2 += -1
            else:
                intensity = Area*random.randint(1,6)
                alpha = 1 #shape parameter for gamma function
                beta = intensity  #scale parameter for gamma function
                fall= rain(alpha, beta, timestep, pressure)
            rained = fall[0]
            pressure = fall[1]
            
        else:
            rained =0 

        #updates the amount of water in the system
        if step % 3 == 0:
            plant= Area *2.5
        else:
            plant =0
        if dcount != 0:
            intialWater= 0
        elif intialWater > Area*1000:
            intialWater= intialWater- dis[0] -plant
        else:
            intialWater= intialWater- dis[0] +rained -plant #water changes based on water in the system minus the evap plus rain fall and minus the amount absobed by pkants
        ratio1= intialWater/Area
        waterlist.append(ratio1/1000)
        xlist.append(8*step)
        #if there is no water in the system we are basically fucked
        if intialWater < Area*50:
            dcount= 1
    plt.title("Temp")
    plt.xlabel("Time (H)")
    plt.ylabel("Temperature (K)")
    plt.plot(xlist, tL)
    
    plt.show()
    plt.title("WFPS")
    plt.xlabel("Time (H)")
    plt.ylabel("WFPS (%)")
    plt.plot(xlist, waterlist)
    plt.show()
    #after simulating the timestep we will return the final amount of water in the system.
    ratio = intialWater/Area
    norm = ratio/1000

    return pressure

#Helper Functions

def evaporation(airDensity, deltaT, specificHeat, thermalRes, Area, heatCap, time, pressure):
    """Calcultes the heat disappation per unit area using the formula from paper 19.
    Then mulitplies it by area and the heat capacity of water in order to get the 
    amount of water evaporated.""" 
    
    numer =airDensity*specificHeat * deltaT
    latentHeatLost = Area * numer /thermalRes  #calcs the latent heat lost
    Waterloss = latentHeatLost *time*60*heatCap #caculates the water loss
    pressure= pressure 
    return (Waterloss,pressure)

def rain(alpha,beta, time, pressure):
    "Takes rain in possion parameter for rainfall and simulates potential rainfall for a unit of area"
    fall= time*int(np.random.gamma(alpha, beta, 1))
    pressure = pressure
    return (fall,pressure)

def Temp(hours, startingday):
    """Generates a temp from from the northern hemisphere"""
# Define the parameters for the sine function
    amplitude = 25.0   # the amplitude of the temperature variation
    mean_temp = 280.15   # the mean temperature for the year
    period = 365.0     # the period of the temperature variation (in days)
    phase = 230 +startingday         # the phase shift of the temperature variation (in days)

    # Generate a list of daily temperatures for the year
    num_days = int(hours/24) +1
    temperatures = [mean_temp + amplitude * math.sin(2*math.pi*(day+phase)/period) for day in range(num_days)]
    return temperatures
    
#Extreme Functions

def Xheat(temp, Intensity, pressure):
    newtemp= int(temp + (Intensity*random.randint(4,7)) )
    pressure = pressure
    return (newtemp, pressure)

def Xrain(alpha, beta , pressure, time):
    fall = rain(alpha,beta, time, pressure)
    fall = [beta*beta*fall[0], fall[1] ]
    return fall

#Testing function (not important to try and run)

def averageW(intial, time, trials):
    total= 0
    totalw=0 
    dTot= 0
    for i in range(trials):
        total = water(intial, 0, time, 0, [.005,1.2,3], [.75, 9,10] ) 
        if total == "DEATH":
            dTot += 1
        else:
            totalw += total

    return (totalw/trials, dTot)