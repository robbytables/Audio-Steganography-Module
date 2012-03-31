"""
Audio Processing Module

Provides routines such as FFT and inverse FFT w/ scaling and windowing.
"""

import numpy as np

def A_weighting(freq):
    """Scaling function for low-frequency noise reduction.
    http://en.wikipedia.org/wiki/A-weighting#Function_realisation_of_some_common_weightings
    
    Parameters:
        freq - the input frequency
    
    Returns a scalar which represents the scaling for that frequency
    """
    t1 = (freq * freq) + math.pow(20.6,2)
    t2 = (freq * freq) + math.pow(12200.0,2)
    t3 = math.sqrt((freq * freq) + math.pow(107.7,2))
    t4 = math.sqrt((freq * freq) + math.pow(737.9,2))
    return math.pow(12200.0,2) * math.pow(freq, 4) / (t1 * t2 * t3 * t4)

def FFT(samples,window=None):
    """Compute the one-dimensional discrete Fourier Transform of the input data
    
    Parameters:
        samples - the sample values (a Numpy array of integers)
        window - an optional window to be applied to the results of the FFT
    
    Returns an array of complex values representing the output of the FFT
    """
    if window:
        samples = samples * window
    return np.fft.fft(samples)

def iFFT(fftData, window=None):
    """Compute the inverse of the one-dimensional discrete Fourier Transform
    
    Parameters:
        fftData - the data representing the output of the FFT
        window - the original windowing applied to the input to the FFT
    
    Returns an array of complex values representing the original input.
    If the symmetry of the Fourier Transform was preserved,
    then the imaginary components of the values should be very close to zero
    """
    originalData = np.fft.ifft(fftData)
    if window:
        originalData = originalData / window
    return originalData

def FFTs(data,windowSize,timeStep,scaling=None,windowing=None):
    """Compute a series of FFTs over the given data
    using the specified window size and, optionally, scaling and windowing
    
    Parameters:
        data - a Numpy array of integers represent the data to process
        windowSize - the maximum number of samples to process at a time.
                     this affects the range and resolution of the frequencies
                     that can be detected by the FFT.
        timeStep - the time-separation of any two consecutive samples.
                    i.e. 1 / sample-rate
        scaling - the scaling function to use on resulting frequency values
        windowing - the windowing function to use on input values
                    e.g. numpy.hamming
    """
    frequencies = np.fft.fftfreq(windowSize,timeStep)
    
    SCALE = None
    if scaling:
        SCALE = np.array(map(scaling,frequencies))
        
    WINDOW = None
    if windowing:
        WINDOW = windowing(windowSize)
        
    stop = len(data)
    results = []
    for i in xrange(0,stop,windowSize):
        window = WINDOW
        scale = SCALE
        next = min(i+windowSize,stop)
        chunk = data[i:next]
        if (next - i) < windowSize:
            if windowing:
                window = windowing(next-i)
            if scaling:
                scale = np.array(map(scaling,np.fft.fftfreq(next-i,timeStep)))
        
        fft = FFT(chunk,window)
        
        results.append(scale * fft if scale else fft)
    
    return results

def iFFTs(fftData,timeStep,scaling=None,windowing=None):
    """Reconstruct audio data from an array of FFT outputs.
    
    Parameters:
        fftData - the output of a series of FFTs applied to the original data
        timeStep - the time-separation of any two consecutive samples.
                   i.e. 1 / sample-rate
        scaling - the scaling function used on original frequency values
        windowing - the windowing function uses on original values
                    e.g. numpy.hamming
    """
    windowSize = len(fftData[0])
    frequencies = np.fft.fftfreq(windowSize,timeStep)
    
    WINDOW = None
    if windowing:
        WINDOW = windowing(windowSize)

    SCALE = None
    if scaling:
        SCALE = np.array(map(scaling,frequencies))
        
    data = []
    for fft in fftData:
        window = WINDOW
        scale = SCALE
        fftSize = len(fft)
        
        if fftSize < windowSize:
            if windowing:
                window = windowing(fftSize)
            if scaling:
                scale = np.array(map(scaling,np.fft.fftfreq(fftSize,timeStep)))
        
        if scaling:
            fft = fft / scale
            
        data += iFFT(fft,window).real.tolist()
    return data

def constantEcho(samples,delay,scale=1.0):
    """Add echo with constant delay and scale to a set of samples
    
    Parameters:
        samples - the original audio samples
        delay - the number of samples by which to delay the echo.
                This is NOT a time value; for a 1s echo delay, the value
                of `delay' should be equal to the sample rate
        scale - the amount by which to scale the amplitude of the echo.
                Defaults to 1.0 -- the full volume of the echoed sample
    """
    return [samples[i] if i < delay
            else samples[i] + scale*samples[i-delay]
            for i in xrange(len(samples))]
    