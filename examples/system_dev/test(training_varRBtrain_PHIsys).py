"""
Testing Phi System training
author: Frank Patterson - 4Apr2015
Testing training modules
"""
import copy, random

import skfuzzy as fuzz
from training import *
from systems import *
import fuzzy_operations as fuzzyOps
from timer import Timer

import matplotlib.pyplot as plt

SYS_list = ['VL_SYS', 'FWD_SYS', 'WING_SYS', 'ENG_SYS'] #a list of systems 
ASPECT_list = ['VL_SYS_TYPE', 'VL_SYS_PROP', 'VL_SYS_DRV', 'VL_SYS_TECH', \
            'FWD_SYS_PROP', 'FWD_SYS_DRV', 'FWD_SYS_TYPE',\
            'WING_SYS_TYPE', \
            'ENG_SYS_TYPE']    #list of system functional aspects 

## I/O Ranges and Limits
input_ranges = \
{   'LD'   : [5, 25],
    'w'    : [0, 150],
    'e_d'  : [0.0, 0.3],
    'phi'  : [1, 9],
    'FM'   : [0.3, 1.0],
    'f'    : [1,9],
    'V_max': [150, 550],
    'eta_p': [0.6, 1.0],
    'sigma': [0.05,0.4],
    'TP'   : [0.0, 20.0],
    'PW'   : [0.01, 5.0],
    'eta_d'  : [0.5,1.0],
    'WS'   : [15,300],
    'SFC'  : [1,9],     
    }
output_ranges = \
{   'sys_FoM' : [0.0, 1.0],
    'sys_phi' : [1.0, 9.0],
}

inputLimits = {inp: [input_ranges[inp][0] - 0.1*(input_ranges[inp][1]-input_ranges[inp][0]),
                     input_ranges[inp][1] + 0.1*(input_ranges[inp][1]-input_ranges[inp][0])]for inp in input_ranges}
outputLimits = {otp: [output_ranges[otp][0] - 0.1*(output_ranges[otp][1]-output_ranges[otp][0]),
                      output_ranges[otp][1] + 0.1*(output_ranges[otp][1]-output_ranges[otp][0])]for otp in output_ranges}


##
def createMFs(ranges, n, m):
    """
    create evenly spaced MFs for inputs over ranges
    ranges : dict
        {input:[min,max]... } for inputs that MFs are needed for
    n = number of MFs
    m = MF type (3,4)#
    """
    dictX = {}
    for inp in ranges:
        if m == 3 or m == 4: #triangular and trapezoidal MFs
            mi, ma = ranges[inp][0], ranges[inp][1] #get min and max
            half_width = (ma-mi)/float(n-1)
            step_width = 2*half_width/(m-1)
            MFs = []
            for i in range(n):
                range_start = mi+(i-1)*half_width
                MFparams = [range_start + i*step_width for i in range(m)]
                MFs.append(MFparams)
            MFdict = {'A'+str(i): MFs[i] for i in range(len(MFs))}
            dictX[inp] = MFdict
        elif m == 2:   #gaussian functions
            mi, ma = ranges[inp][0], ranges[inp][1] #get min and max
            half_width = (ma-mi)/float(n-1)
            std = half_width/2.0
            MFs = []
            for i in range(n):
                mean = mi + i*half_width
                MFparams = [mean, std]
                MFs.append(MFparams)
            MFdict = {'A'+str(i): MFs[i] for i in range(len(MFs))}
            dictX[inp] = MFdict
    return dictX
    

# Read in Input Data for Morph
dataIn = readFuzzyInputData('data/morphInputs_13Jun15.csv')

# Get data linked to inputs
data = buildInputs(ASPECT_list, dataIn, 'data/phiData_251pts.csv', True)

# Get union of FWD and VL system empty weight ratio and average wing loading
operations1 = { ('VL_SYS_UNION', 'phi'):  ( [('VL_SYS_TYPE', 'phi'), ('VL_SYS_PROP', 'phi'), ('VL_SYS_DRV', 'phi'), ('VL_SYS_TECH', 'phi')], 'UNION' ),
                ('FWD_SYS_UNION', 'phi'): ( [('FWD_SYS_TYPE', 'phi'), ('FWD_SYS_PROP', 'phi'), ('FWD_SYS_DRV', 'phi')], 'UNION' ),
                ('VL_SYS_UNION', 'w'):  ( [('VL_SYS_TYPE', 'w'), ('VL_SYS_PROP', 'w'), ('VL_SYS_TECH', 'w')], 'AVERAGE' ),
                }
                
data = combine_inputs(data, operations1)

#get average system empty weight ratio
#operations1 = {('SYS_PHI_AVGofUNIONS', 'phi'):  ( [('VL_SYS_UNION', 'phi'), ('FWD_SYS_UNION', 'phi'), ('WING_SYS_TYPE', 'phi'), ('ENG_SYS_TYPE', 'phi')], 'AVERAGE' ),
#                }
#combinedData = combine_inputs(combinedData, operations1)

#write_expert_data(data, 'data/POC_combinedPhiData.csv')

# Create Input Triangular MFs
input_5gaussMFs = createMFs(input_ranges, 5, 2)
input_7gaussMFs = createMFs(input_ranges, 7, 2)
input_9gaussMFs = createMFs(input_ranges, 9, 2)
input_5triMFs = createMFs(input_ranges, 5, 3)
input_7triMFs = createMFs(input_ranges, 7, 3)
input_9triMFs = createMFs(input_ranges, 9, 3)

#Create Output Triangular MFs
output_7gaussMFs = createMFs(output_ranges, 7, 2)
output_9gaussMFs = createMFs(output_ranges, 9, 2)
output_7triMFs = createMFs(output_ranges, 7, 3)
output_9triMFs = createMFs(output_ranges, 9, 3)
output_7trapMFs = createMFs(output_ranges, 7, 4)
output_9trapMFs = createMFs(output_ranges, 7, 4)

#import pdb; pdb.set_trace()


    
    
##
def test1():
    test_name = 'SYS: In:7-2 Out:9-2   DATA: In:3 Out:3'
    
    print "*************************************"
    print "TESTING:  ", test_name
    inMFs = input_7gaussMFs       #system in
    outMFs = output_9gaussMFs
    defuzz = None
    
    outForm = 'tri'
    inDataForm = 'tri'
    outDataForm = 'tri'
    errType = 'fuzzy'
    
    input_arrays, output_arrays = generate_MFs(inMFs, outMFs)
    
    inputMFs = {    ('VL_SYS_UNION', 'phi'):        copy.deepcopy(input_arrays['phi']),('FWD_SYS_UNION', 'phi'):       copy.deepcopy(input_arrays['phi']), ('WING_SYS_TYPE', 'phi'):       copy.deepcopy(input_arrays['phi']),('ENG_SYS_TYPE', 'phi'):        copy.deepcopy(input_arrays['phi']),
                    ('VL_SYS_UNION', 'w'):          copy.deepcopy(input_arrays['w']),('VL_SYS_TYPE', 'TP'):          copy.deepcopy(input_arrays['TP']),('WING_SYS_TYPE', 'WS'):        copy.deepcopy(input_arrays['WS']),('VL_SYS_PROP', 'sigma'):       copy.deepcopy(input_arrays['sigma']),    
                    ('VL_SYS_TYPE', 'e_d'):         copy.deepcopy(input_arrays['e_d']),('VL_SYS_DRV', 'eta_d'):        copy.deepcopy(input_arrays['eta_d']),('FWD_SYS_DRV', 'eta_d'):       copy.deepcopy(input_arrays['eta_d']),('FWD_SYS_PROP', 'eta_p'):      copy.deepcopy(input_arrays['eta_p']),
                }
    inputPARAMs = { ('VL_SYS_UNION', 'phi'):        copy.deepcopy(inMFs['phi']), ('FWD_SYS_UNION', 'phi'):       copy.deepcopy(inMFs['phi']),('WING_SYS_TYPE', 'phi'):       copy.deepcopy(inMFs['phi']),('ENG_SYS_TYPE', 'phi'):        copy.deepcopy(inMFs['phi']),    
                    ('VL_SYS_UNION', 'w'):          copy.deepcopy(inMFs['w']), ('VL_SYS_TYPE', 'TP'):          copy.deepcopy(inMFs['TP']),('WING_SYS_TYPE', 'WS'):        copy.deepcopy(inMFs['WS']), ('VL_SYS_PROP', 'sigma'):       copy.deepcopy(inMFs['sigma']),    
                    ('VL_SYS_TYPE', 'e_d'):         copy.deepcopy(inMFs['e_d']),('VL_SYS_DRV', 'eta_d'):        copy.deepcopy(inMFs['eta_d']),('FWD_SYS_DRV', 'eta_d'):       copy.deepcopy(inMFs['eta_d']),('FWD_SYS_PROP', 'eta_p'):      copy.deepcopy(inMFs['eta_p']),
                }
    
    outputMFs = {'sys_phi' : copy.deepcopy(output_arrays['sys_phi'])}
    outputPARAMs = {'sys_phi' : copy.deepcopy(outMFs['sys_phi'])}
    
    combinedData = copy.deepcopy(data)
    print combinedData[0]
    #generate rules
    with Timer() as t:
        rule_grid = train_system(inputMFs, outputMFs, combinedData, 
                                 inDataMFs=inDataForm, outDataMFs=outDataForm,
                                 ruleMethod=3)
    
    #write out FCL
    write_fcl_file_FRBS(inputPARAMs, outputPARAMs, rule_grid, defuzz, 'test_sys_phi.fcl')
    
    #get system
    inputs, outputs, rulebase, AND_operator, OR_operator, aggregator, implication, \
        defuzz = build_fuzz_system('test_sys_phi.fcl')
    sys = Fuzzy_System(inputs, outputs, rulebase, AND_operator, OR_operator, aggregator, 
                    implication, defuzz)
    
    print '=> ', t.secs, 'secs to build', len(sys.rulebase), 'rules'
    
    #test system
    with Timer() as t:
        error = getError(combinedData, sys, inMF=inDataForm, outMF=outDataForm, sysOutType=errType)
    print '=> ', t.secs, 'secs to check error'
    print 'Total System Error:', sum([err[2] for err in error])
    print 'Mean Square System Error:', (1.0/len(error))*sum([err[2]**2 for err in error])
    print 'Root Mean Square System Error:', ( (1.0/len(error)) * sum([err[2]**2 for err in error]) )**0.5
    
    #actual vs. predicted plot
    plt.figure()
    plt.title('Actual vs. Predicted at Max Alpha Cut'+test_name)
    for err in error:
        if outDataForm == 'gauss': AC_actual = fuzzyOps.alpha_cut(0.8, [err[0][0],err[0][1]])
        else: AC_actual = fuzzyOps.alpha_at_val(err[0][0],err[0][1])
        if outForm == 'gauss': AC_pred = fuzzyOps.alpha_cut(0.8, (err[1][0],err[1][1]))
        else: AC_pred = fuzzyOps.alpha_at_val(err[1][0],err[1][1])
        
        plt.scatter(AC_actual[0], AC_pred[0], marker='o', c='r')
        plt.scatter(AC_actual[1], AC_pred[1], marker='x', c='b')
    
    plt.plot([1,9],[1,9], '--k')     
    plt.xlim([1,9])
    plt.ylim([1,9])
    plt.xlabel('Actual')
    plt.ylabel('Predicted')
    
    #visuzlize system with random data point
    #i = random.randrange(0, len(combinedData))
    #inputs = {key[0]+"_"+key[1]:combinedData[i][0][key] for key in combinedData[i][0]}
    #sys.run(inputs, TESTMODE=True)
    
    #check random data points (9)
    plt.figure()
    plt.title('Random Tests:'+test_name)
    for j in range(9):
        i = random.randrange(0, len(combinedData))
        inputs = {key[0]+"_"+key[1]:combinedData[i][0][key] for key in combinedData[i][0]}
        sysOut = sys.run(inputs)
        sysOut = sysOut[sysOut.keys()[0]]
        plt.subplot(3,3,j+1)
        plt.plot(sysOut[0], sysOut[1], '-r')
        plt.plot(combinedData[i][2][0], combinedData[i][2][1], '--k')
        plt.ylim([0,1.1])
        plt.xlim([1,9])
    
    #actual vs. error plot
    plt.figure()
    plt.title('Actual (Centroid) vs. Error'+test_name)
    cents = [fuzz.defuzz(err[0][0], err[0][1], 'centroid') for err in error]
    plt.scatter(cents, [err[2] for err in error])
    plt.xlabel('Actual (Centroid)')
    plt.ylabel('Fuzzy Error')   
    

    
        
#Testing plot:
#plot_rule_grid(rule_grid, inputMFs, outputMFs, combinedData, ('VL_SYS_UNION',   'phi'), ('FWD_SYS_UNION', 'phi'), ('WING_SYS_TYPE',   'phi'))
#plot_parallel(rule_grid, inputMFs, outputMFs, combinedData, None)
if __name__ == "__main__":
    test1()
    #test2()
    #test3()
    #test4()
    #test5()
    #test6()
    #test7()
    #test8()
    plt.show()