import csv
import math
import matplotlib.pyplot as plt
import numpy as np
import random as rd
import scipy.signal as sg

def roundto(num, tick):
    if (num/tick - num//tick) < 0.5:
        return math.floor(num/tick) * tick
    else:
        return math.ceil(num/tick) * tick

def readcsv(filename):
    """return signal list and simulation data frequency"""

    signal = []
    today = '0223'
    with open('../../rawdata/distance_test_{}/{}.csv'.format(today, filename)) as file:
        datas = csv.reader(file)
        simFreq = 0
        for ind, data in enumerate(datas):
            if ind==0: continue
            elif ind==1:
                simFreq = 1/float(data[3])
                # simFreq = 1/(float(data[3])*3)
            # elif ind%3!=2: continue
            else:
                signal.append(float(data[1]))
    # print(len(signal))
    return signal, simFreq, today

def plotSingleFile(filename):

    y, fs, today = readcsv(filename)
    print('-----------------------------')
    print('read {} file'.format(filename))
    N = len(y)                          ## number of simulation data points
    min_freq_diff = fs/N                ## spacing between two freqencies on axis
    print('N =', N)
    print('fs =', fs)
    print('min_freq_diff =',min_freq_diff)

    t_axis = [i/fs for i in range(N)]
    f_axis = [i*min_freq_diff for i in range(N)]

    yf = abs(np.fft.fft(y))
    # yfs = np.fft.fftshift(yf)         ## shift 0 frequency to middle
                                        ## [0,1,2,3,4,-4,-3,-2,-1] -> [-4,-3,-2,-1,0,1,2,3,4]
                                        ## (-fs/2, fs/2)
                                        ## just plot the positive frequency, so dont need to shift

    yfn = [i*2/N for i in yf]           ## normalization
                                        ## let the amplitude of output signal equals to inputs

    plt.figure('Figure')
    plt.suptitle(today)
    plt.subplot(211)
    plt.plot(t_axis, y)
    plt.title('Signal of '+filename+' cm')
    plt.xlabel('time (s)')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0,0), useMathText=True)

    plt.subplot(212)

    max_freq = (len(f_axis)//2)*min_freq_diff
    # max_freq = 5e5
    max_freq_index = int(max_freq/min_freq_diff)

    plt.plot(f_axis[:max_freq_index],yfn[:max_freq_index], 'r')
    peaks, _ = sg.find_peaks(yfn[:max_freq_index], height = 0.01)

    plt.plot(peaks*min_freq_diff,[ yfn[i] for i in peaks], 'x')
    peakList = []
    for ind, i in enumerate(peaks):
        plt.annotate(s=int(peaks[ind]*min_freq_diff), xy=(peaks[ind]*min_freq_diff,yfn[i]))
        print('peaks at: {} Hz, amplitude = {}'.format(int(peaks[ind]*min_freq_diff), yfn[i]))
        peakList.append( (int(peaks[ind]*min_freq_diff), yfn[i]) )

    plt.title('FFT')
    plt.xlabel('freq (Hz)')
    plt.ticklabel_format(axis='x', style='sci', scilimits=(0,0), useMathText=True)

    plt.subplots_adjust(hspace=0.5)
    plt.show()

def plotMultipleFile(filenames):

    num = len(filenames)

    fig, ax =  plt.subplots(math.ceil(num/3), 3, sharex=False, num='Figure Name')  ## num is **kw_fig

    refyfn=[]

    for pltind, filename in enumerate(filenames):

        y, fs, today = readcsv(filename)
        print('-----------------------------')
        print('read {} file'.format(filename))
        N = len(y)                          ## number of simulation data points
        min_freq_diff = fs/N                ## spacing between two freqencies on axis
        print('N =', N)
        print('fs =', fs)
        print('min_freq_diff =',min_freq_diff)

        t_axis = [i/fs for i in range(N)]
        f_axis = [i*min_freq_diff for i in range(N)]

        yf = abs(np.fft.fft(y))
        # yfs = np.fft.fftshift(yf)         ## shift 0 frequency to middle
                                            ## [0,1,2,3,4,-4,-3,-2,-1] -> [-4,-3,-2,-1,0,1,2,3,4]
                                            ## (-fs/2, fs/2)
                                            ## just plot the positive frequency, so dont need to shift

        yfn = [i*2/N for i in yf]           ## normalization
                                            ## let the amplitude of output signal equals to inputs

        
        # plt.subplot(211)
        # plt.plot(t_axis, y)
        # plt.title('Signal of '+filename+' cm')
        # plt.xlabel('time (s)')
        # plt.ticklabel_format(axis='x', style='sci', scilimits=(0,0), useMathText=True)

        max_freq = (len(f_axis)//2)*min_freq_diff
        # max_freq = 5e5
        max_freq_index = int(max_freq/min_freq_diff)


        offsetyfn = yfn

        # remove background
        # if pltind==0:
        #     refyfn=yfn
        #     continue
        # offsetyfn = [yfn[i]-refyfn[i] for i in range(max_freq_index)]

        # print(ax[pltind])

        ax[pltind//3, pltind%3].plot(f_axis[:max_freq_index],offsetyfn[:max_freq_index], color='red')
        peaks, _ = sg.find_peaks(offsetyfn[:max_freq_index], height = 0.015)

        # ax[pltind//3, pltind%3].plot(peaks*min_freq_diff,[ offsetyfn[i] for i in peaks], marker='x')
        peakList = []
        for ind, i in enumerate(peaks):
            ax[pltind//3, pltind%3].annotate(s=int(peaks[ind]*min_freq_diff), xy=(peaks[ind]*min_freq_diff,offsetyfn[i]))
            print('peaks at: {} Hz, amplitude = {}'.format(int(peaks[ind]*min_freq_diff), offsetyfn[i]))
            peakList.append( (int(peaks[ind]*min_freq_diff), offsetyfn[i]) )

        ax[pltind//3, pltind%3].set_title(filename+' cm')
        # ax[pltind//3, pltind%3].ticklabel_format(axis='x', style='sci', scilimits=(0,0), useMathText=True)
        ax[pltind//3, pltind%3].set_ylim((0, 0.1))

    fig.suptitle(today)
    fig.subplots_adjust(hspace=0.6)
    plt.show()

def plotTheoretical(distanceList, distanceOffset, BW, tm, simTime, roundup, doPlot=True):
    """ plot threoretical frequency
       
         _ ↑
         ↑ |      /\/\        /\/\
         | |     / /\ \      / /\ \
         B |    / /  \ \    / /  \ \
         W |   / /    \ \  / /
         | |  / /      \ \/ /
         ↓ | / /        \/\/
         ¯ + -------------------------->
             |<-- tm -->|
             |<----  simTime  ---->|

    """

    fm = 1/tm
    slope = BW/tm*2
    freqRes = 1/simTime

    print('fm', fm)
    print('freqRes', freqRes)

    freqList = []

    for distance in distanceList:

        distance*=2

        timeDelay = (distance+distanceOffset)/3e8
        beatFreq = timeDelay*slope
        fbRoundUp = roundto(roundto(beatFreq, fm), freqRes)
        if not roundup:
            # print('ggg', beatFreq)
            freqList.append(beatFreq)
        else:
            # print('fff', fbRoundUp)
            freqList.append(fbRoundUp)

    if doPlot:

        plt.figure('Figure')

        plt.scatter(distanceList, freqList)
        plt.xlabel('Distance (m)')
        plt.ylabel('Frequency (Hz)')
        plt.xticks(distanceList)
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)

        plt.show()

    return freqList

def plotExpAndTheo(filenames, distanceList, distanceOffset, BW, tm, simTime, roundup):

    freqList = []

    for filename in filenames:

        y, fs, today = readcsv(filename)
        print('-----------------------------')
        print('read {} file'.format(filename))
        N = len(y)                          ## number of simulation data points
        minFreqDiff = fs/N                ## spacing between two freqencies on axis
        print('N =', N)
        print('fs =', fs)
        print('minFreqDiff =',minFreqDiff)

        t_axis = [i/fs for i in range(N)]
        f_axis = [i*minFreqDiff for i in range(N)]

        yf = abs(np.fft.fft(y))
        # yfs = np.fft.fftshift(yf)         ## shift 0 frequency to middle
                                            ## [0,1,2,3,4,-4,-3,-2,-1] -> [-4,-3,-2,-1,0,1,2,3,4]
                                            ## (-fs/2, fs/2)
                                            ## just plot the positive frequency, so dont need to shift

        yfn = [i*2/N for i in yf]           ## normalization
                                            ## let the amplitude of output signal equals to inputs

        ## remove aliasing of image frequency and DC

        for i in range(len(yfn)//4,len(yfn)):
            print(i)
            yfn[i]=0
        yfn[0]=0

        max_freq = (len(f_axis)//2)*minFreqDiff
        # max_freq = 5e5
        max_freq_index = int(max_freq/minFreqDiff)
        freqList.append(f_axis[yfn.index(max(yfn[:max_freq_index]))])

    print(freqList)

    theoFreqList = plotTheoretical(distanceList, distanceOffset, BW, tm, simTime, roundup, doPlot=False)

    plt.figure('Figure')
    plt.title(today)
    plt.plot(distanceList, freqList, label='exp')
    plt.plot(distanceList, theoFreqList, label='theo')
    # plt.scatter(distanceList, freqList, label='exp')
    # plt.scatter(distanceList, theoFreqList, label='theo')
    plt.xlabel('Distance (m)')
    plt.ylabel('Frequency (Hz)')
    plt.xticks(distanceList)
    plt.legend()
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)

    plt.show()

def plotHeatmap(filenames, distanceList, distanceOffset, BW, tm, simTime, roundup):
    freqData = []

    for filename in filenames:

        y, fs = readcsv(filename)
        print('-----------------------------')
        print('read {} file'.format(filename))
        N = len(y)                          ## number of simulation data points
        minFreqDiff = fs/N                ## spacing between two freqencies on axis
        print('N =', N)
        print('fs =', fs)
        print('minFreqDiff =',minFreqDiff)

        t_axis = [i/fs for i in range(N)]
        f_axis = [i*minFreqDiff for i in range(N)]

        yf = abs(np.fft.fft(y))
        # yfs = np.fft.fftshift(yf)         ## shift 0 frequency to middle
                                            ## [0,1,2,3,4,-4,-3,-2,-1] -> [-4,-3,-2,-1,0,1,2,3,4]
                                            ## (-fs/2, fs/2)
                                            ## just plot the positive frequency, so dont need to shift

        yfn = [i*2/N for i in yf]           ## normalization
                                            ## let the amplitude of output signal equals to inputs


        max_freq = (len(f_axis)//2)*minFreqDiff
        # max_freq = 5e5
        max_freq_index = int(max_freq/minFreqDiff)
        for i in range(25):
            freqData.append(np.zeros(max_freq_index))
        freqData.append(np.flip(yfn[:max_freq_index]))
        for i in range(25):
            freqData.append(np.zeros(max_freq_index))
        # print(yfn[:max_freq_index])
        # freqList.append(f_axis[yfn.index(max(yfn[:max_freq_index]))])

    # print(freqList)
    freqDataNp = np.array(freqData)
    print('freqDataNp', freqDataNp.shape)
    # np.transpose(freqDataNp)
    freqDataNp=freqDataNp.transpose()
    print('freqDataNp', freqDataNp.shape)

    theoFreqList = plotTheoretical(distanceList, distanceOffset, BW, tm, simTime, roundup, doPlot=False)

    plt.figure('Figure')

    plt.imshow(freqDataNp)
    plt.colorbar()

    plt.xlabel('Distance (m)')
    plt.xticks([i for i in range(51*12) if i%51==25], distanceList)

    plt.ylabel('Frequency (Hz)')
    # plt.yticks( np.arange(50))
    # plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)

    plt.show()


def main():

    ## 0220 files

    # filenames = ['0001','0251','0501','0751','1001','1251','1501','1751','2001','2251','2501','2751','3001']
    # filenames = ['0002','0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752','3002']

    ## 0221 files

    # filenames = ['0001','0251','0501','0751','1001','1251','1501','1751','2001','2251','2501','2751']
    # filenames = ['0002','0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752']
    # filenames = ['3001','3251','3501','3751','4001','4251','4501','4751','5001']
    # filenames = ['3002','3252','3502','3752','4002','4252','4502','4752','5002']
    # filenames = ['0001','0251','0501','0751','1001','1251','1501','1751','2001','2251','2501','2751','3001','3251', '3501','3751','4001','4251','4501','4751','5001']
    # filenames = ['0002','0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752','3002','3252', '3502','3752','4002','4252','4502','4752','5002']
   
    ## 0222 files

    # filenames = ['0251','0501','0751','1001','1251','1501','1751','2001','2251','2501','2751','3001']
    # filenames = ['0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752','3002']

    ## 0223 files

    # filenames = ['0251','0501','0751','1001','1251','1501','1751','2001','2251','2501','2751','3001']
    filenames = ['0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752','3002']
    # filenames = ['3251','3501','3751','4001','4251','4501','4751','5001','5251','5501','5751','6001']
    # filenames = ['3252','3502','3752','4002','4252','4502','4752','5002','5252','5502','5752','6002']
    # filenames = ['0252','0502','0752','1002','1252','1502','1752','2002','2252','2502','2752','3002','3252','3502','3752','4002','4252','4502','4752','5002','5252','5502','5752','6002']
    


    # plotSingleFile('3002')
    plotMultipleFile(filenames)
    # plotTheoretical(distanceList=np.arange(0.25, 3, 0.25), distanceOffset=10*2.24**0.5,
    #                 BW=99.9969e6, tm=2048e-6, simTime=24e-3, roundup=True)

    # plotExpAndTheo(filenames, distanceList=np.arange(0.25, 6.01, 0.25), distanceOffset=10*2.24**0.5,
    #                BW=99.9969e6, tm=2048e-6, simTime=24e-3, roundup=True)

    # plotHeatmap(filenames, distanceList=np.arange(0.25, 3.01, 0.25), distanceOffset=10*2**0.5,
    #             BW=99.9969e6, tm=2048e-6, simTime=24e-3, roundup=True)


if __name__ == '__main__':
    main()
