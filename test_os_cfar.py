# from cfar_lib import os_cfar
from operator import length_hint
from os_cfar_v2 import os_cfar
import numpy as np
from scipy.fft import fft

print("testing OS cfar")
with open("IQ_tri_20kmh.txt", "r") as raw_IQ:
		# split into sweeps
		sweeps = raw_IQ.read().split("\n")

sweeps = np.array(sweeps)
print(np.size(sweeps))
# Extract samples from 1 sweep
samples = np.array(sweeps[1499].split(" "))
i_data = samples[  0:400-1]
q_data = samples[400:800-1]

# 32 bit for embedded systems e.g. raspberry pi
i_data = i_data.astype(np.int32)
q_data = q_data.astype(np.int32)
# test = np.power([1,2,3,4],2)
# print(test)
# print(i_data)
iq_u = np.power(i_data[  0:200-1],2) + np.power(q_data[  0:200-1],2)
iq_d = np.power(i_data[200:400-1],2) + np.power(q_data[200:400-1],2)

n_fft = 512 
IQ_UP = fft(iq_u,n_fft)
IQ_DN = fft(iq_d,n_fft)

# IQ_UP = np.fft.fft(iq_u,n_fft)
# IQ_DN = np.fft.fft(iq_d,n_fft)
# Halve FFTs
IQ_UP = IQ_UP[1:round(n_fft/2)]
IQ_DN = IQ_DN[round(n_fft/2)+1:]

# Null feedthrough
nul_width_factor = 0.04
num_nul = round((n_fft/2)*nul_width_factor)
IQ_UP[1:num_nul] = 0
IQ_DN[len(IQ_DN)-num_nul+1:] = 0

# CFAR
n_samples = len(iq_u)
half_guard = n_fft/n_samples
half_guard = int(np.floor(half_guard/2)*2) # make even

half_train = round(20*n_fft/n_samples)
half_train = int(np.floor(half_train/2))
rank = 2*half_train -2*half_guard
# rank = half_train*2
Pfa_expected = 15e-3
SOS = 1
# note the abs

Pfa, cfar_res_up, th = os_cfar(half_train, half_guard, rank, SOS, abs(IQ_UP))
print("Expected Pfa = ", Pfa_expected)
print("SOS = ", SOS)
print("Actual Pfa for SOS = ", Pfa)

fthname = "threshold.txt"
np.savetxt(fthname, th, delimiter=' ', newline='\n')

fftupname = "pyFFTup.txt"
np.savetxt(fftupname,  abs(IQ_UP), delimiter=' ', newline='\n')
# print(th)
# with open(fthname, 'w') as fth:
	# fth.write(th)
# print(cfar_res_up)

for sweep in range(sweeps):
	Pfa, cfar_res_up, th = os_cfar(half_train, half_guard, rank, SOS, abs(IQ_UP()))