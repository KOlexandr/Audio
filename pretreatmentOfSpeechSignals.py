from beans.WavFile import WavFile
from handlers.Plotter import Plotter

__author__ = 'Olexandr'


signal = WavFile('example.wav').samples
plotter = Plotter()
plotter.add_sub_plot_data("original", signal)

# signal: fdyscr=16 KHz, 16 bit
# acoustic preprocessing of signal

d=len(signal)
tim=1 i=1
while i<d-408 y=signal(i:i+408) # block processing result - acoustic vector

x(1)=0.0
for j=2:409 x(j)=y(j)-y(j-1) end #premphasis

# pi=3.14
for j=1:409 z(j)=(0.54-0.46*cos(2*pi*(j-1)/408))*x(j) end  #Hamming window  
C=fft(z,512)  C=abs(C)   # FFT
S=C(1:256) # amplitudes

# binning of 255 spectral values amplitudes, j=2,3,...,256
f=[0 74.24 156.4 247.2 347.6 458.7 581.6 717.5 867.9 1034 1218 1422 1647 1895 2171 2475 2812 3184 3596 4052 4556 5113 5730 6412 7166 8000]

krok=16000/512           # krok=31,25
a(1:26)=0 j=2 k=1 n(1:26)=0
h=krok*(j-1) 

while k<26 
while and(f(k)<h,h<f(k+1)) alfa=(h-f(k))/(f(k+1)-f(k))  # interval [f(k),f(k+1)]
a(k+1)=a(k+1)+S(j)*alfa n(k+1)=n(k+1)+1
a(k)=a(k)+S(j)*(1-alfa) n(k)=n(k)+1
j=j+1 h=krok*(j-1)
end  
a(k)=a(k)/n(k)  k=k+1
end 

O(tim,1:24)=a(2:25)
#O(tim,25)=sum(y.^2)
norma(tim)=norm(O(tim,1:24))
i=i+160 tim=tim+1 # next block 
end # end of block proccesing
time=tim-1

normamax=max(norma(1:time))
O(1:time,1:24)= O(1:time,1:24)/normamax # normalization
# end of signal acoustic preprocessing


subplot(3,3,2) plot(y)title('                409 values ')
subplot(3,3,3) plot(x)title('              premphasis ')
subplot(3,3,4) plot(z)title('        Hemming')
subplot(3,3,5) plot(C)title('     512 fft ')
subplot(3,3,6) plot(S)title('      256 elements ')
subplot(3,3,7)  plot(O(time,1:24))title('                  24-element vector')