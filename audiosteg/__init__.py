"""
Audio steganography top-level module
"""

import logging
from binutil import bitsForInt,intForBits,intsToBytes,bytesToInts
from math import ceil,floor,log
import io
import numpy as np
import wave
import sys
import random

<<<<<<< local
# Echo delays, in ms
ZERO_DELAY = 14
ONE_DELAY = 3
ECHO_SCALE = 0.4
=======
### Constants ###
WINDOWSIZE = 1024
FREQ0 = range(399,420)
FREQ1 = range(416,440)
TONE = complex(120000,120000)
>>>>>>> other

### Set up logging ###
__LOGGER = logging.getLogger("audiosteg")

def _include_exc_info(func):
    """Convenience decorator for logging function.
    Automatically adds exception info to the log
    """
    def new_func(*args, **kwargs):
        exc = sys.exc_info()
        if reduce(lambda x,y: y or x, exc): # check if there was an exception
            return func(exc_info=sys.exc_info(),*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return new_func
    
_logDebug = _include_exc_info(__LOGGER.debug)
_logInfo = _include_exc_info(__LOGGER.info)
_logWarning = _include_exc_info(__LOGGER.warning)
_logError = _include_exc_info(__LOGGER.error)
######

### Custom Errors ###

class InvalidSize(Exception):
    """Error raised when the size of the payload is invalid
    """
    
    def __init__(self,msg=None):
        """Instantiate a new error
        
        Parameters:
            msg - [Optional] a custom error message
        """
        self.msg = msg
    
    def __str__(self):
        return self.msg or "File size is invalid; see log for more details"

#######

### Embedding / Decoding ###

def embedSS(carrierFile,payloadFile,outFile):
    from amm import wavread,wavwrite

    # read in the carrier file
    left,right,params = wavread(carrierFile)
    sampleRate = params[2]
    sampleLength = params[3]*2
    
    # Read the payload in and store it as a list of zeros and ones
    payload = None
    payloadData = None
    try:
        payload = open(payloadFile, 'rb')
        payloadData = bytesToInts(payload.read())
    except (IOerror) as err:
        _logError("Error reading from file '%s'" % payloadFile)
        raise err
    finally:
        if payload: payload.close()
    
    payloadSize = len(payloadData)
    sizeRatio = (float(payloadSize)/sampleLength)
    _logDebug("Payload is %d bits; that is %f%% of carrier size" % (payloadSize, sizeRatio*100))
    
    # verify that the payload is not too large
    if (sizeRatio > 0.001):
        err = InvalidSize("Payload is too large")
        _logError("Can't embed the payload in the carrier")
        raise err
    
    # calculate window size
    # this is the number of samples that will encode each bit of the payload
    # it is 0.1% the number of samples, divided by 2 because left and right echo
    # must be the same
    windowSize = int(floor(sampleLength*0.001/2))
    _logDebug("Using window size of %d samples" % windowSize)
    
    payloadSizeBits = int(floor(log(sampleLength*0.001,2)) - 1)
    _logDebug("%d bits needed to encode size of payload" % payloadSizeBits)
    
    payloadData = bitsForInt(len(payloadData),size=payloadSizeBits) + payloadData
    
    from apm import FFT,iFFT
    fftl = FFT(left,windowSize)
    fftr = FFT(right,windowSize)

    
    

def embed(carrierFile,payloadFile,outFile):
    """Embed a message in the carrier audio using echo coding
    
    Writes the resulting audio data to outFile
    
    Parameters:
        carrierFile - the name of the carrier audio file
        payloadFile - the name of the payload file
        outFile - the file to which the package will be written
    """
    from amm import wavread,wavwrite
    
    # read in the carrier file
    left,right,params = wavread(carrierFile)
    sampleRate = params[2]
    sampleLength = params[3]*2
    
    # Read the payload in and store it as a list of zeros and ones
    payload = None
    payloadData = None
    try:
        payload = open(payloadFile, 'rb')
        payloadData = bytesToInts(payload.read())
    except (IOerror) as err:
        _logError("Error reading from file '%s'" % payloadFile)
        raise err
    finally:
        if payload: payload.close()
    
    payloadSize = len(payloadData)
    sizeRatio = (float(payloadSize)/sampleLength)
    _logDebug("Payload is %d bits; that is %f%% of carrier size" % (payloadSize, sizeRatio*100))
    
    # verify that the payload is not too large
    if (sizeRatio > 0.001):
        err = InvalidSize("Payload is too large")
        _logError("Can't embed the payload in the carrier")
        raise err

    from apm import FFTs,iFFTs

    timeStep = 1.0/sampleRate
    frequencies = np.fft.fftfreq(WINDOWSIZE,timeStep)
    
    leftFFTs = FFTs(left,WINDOWSIZE,timeStep)
    rightFFTs = FFTs(right,WINDOWSIZE,timeStep)
    
    for i in range(len(leftFFTs)):
        if payloadData[i % payloadSize] == 1:
            freqs = FREQ1
        else:
            freqs = FREQ0
        for f in freqs:
            leftFFTs[i][f] = TONE
    
    for i in range(len(rightFFTs)):
        if payloadData[i % payloadSize] == 1:
            freqs = FREQ1
        else:
            freqs = FREQ0
        for f in freqs:
            rightFFTs[i][f] = TONE
    
<<<<<<< local

       
    for i in xrange(0,len(left),windowSize):
        delay = zeroDelay if payloadData[i % payloadSize] == 0 else oneDelay
        stop = min(i+windowSize,min(len(left), len(right)))
        for j in xrange(i,stop):
            embedded_left[j] = (left[j] if j < delay 
                                else left[j] + ECHO_SCALE*left[j-delay])
            embedded_right[j] = (right[j] if j < delay 
                                 else right[j] + ECHO_SCALE*right[j-delay])
=======
    embedded_left = iFFTs(leftFFTs,timeStep)
    embedded_right = iFFTs(rightFFTs,timeStep)
>>>>>>> other
    
    _logInfo("Embedding complete. Writing file...")
    wavwrite(outFile,params,leftStream=embedded_left,rightStream=embedded_right)

def decode2(packageFile,outFile):
    from amm import wavread
    _logInfo("Decoding...")
    left,right,params = wavread(packageFile)
    sampleRate = params[2]
    sampleLength = params[3]*2

    windowSize = int(floor(sampleLength*0.001/2))
    _logDebug("window size is %d samples" % windowSize)
    
    payloadSizeBits = int(floor(sampleLength*0.001,2))
    _logDebug("First %d bits represent size of payload" % payloadSizeBits)

    

def decode(packageFile,outFile):
    """Decode the embedded message from the given package using echo coding

    Writes the binary decoded message to a file

    Parameters:
        packageFile - the name of the package audio file
        outFile - the name of the file to which the decoded payload will be written
    """
    from amm import wavread
    _logInfo("Decoding...")
    left,right,params = wavread(packageFile)
    sampleRate = params[2]
    sampleLength = params[3]*2
<<<<<<< local
    
    windowSize = int(floor(sampleLength*0.001/2))
    _logDebug("Window size is %d samples" % windowSize)
    
    payloadSizeBits = int(floor(log(sampleLength*0.001,2)) - 1)
    _logDebug("First %d bits represent size of payload" % payloadSizeBits)
    
    import matplotlib.pyplot as plt
    from apm import FFT,iFFT
    
    testsamples = left[windowSize*30:windowSize*31]
    autocorrelate = signal.correlate(testsamples,testsamples)
    cepstrum = pow(np.abs(FFT(np.log(pow(np.abs(FFT(autocorrelate)),2)))),2)
    autocepstrum = cepstrum[len(cepstrum)/2:]
    delayMax = int(floor(sampleRate*0.001*max(ONE_DELAY,ZERO_DELAY)))
    
    
=======
>>>>>>> other

<<<<<<< local
=======
    timeStep = 1.0/sampleRate
    frequencies = np.fft.fftfreq(WINDOWSIZE,timeStep)
>>>>>>> other

<<<<<<< local
    plt.figure(1)
    plt.subplot(211)
    plt.subplot(212)
    plt.plot(np.array(range(delayMax+200))/float(sampleRate),autocepstrum[:delayMax+200])
    plt.show()
  
    ## DECODING IS NOT COMPLETE YET
=======
    from apm import FFTs,iFFTs

    leftFFTs = FFTs(left,WINDOWSIZE,timeStep)
    rightFFTs = FFTs(right,WINDOWSIZE,timeStep)

    decoded_data = []

    for i in range(len(leftFFTs)):
        mag1 = np.mean([abs(leftFFTs[i][f]) for f in FREQ1])
        mag0 = np.mean([abs(leftFFTs[i][f]) for f in FREQ0])
        bit = 0 if mag0 > mag1 else 1
        decoded_data.append(bit)

    payload = intsToBytes(decoded_data)

    out = None
    try:
        out = io.open(outFile,'wb')
        out.write(bytearray(payload))
        out.flush()
    except IOError as err:
        _logError("Error writing out decoded data")
        raise err
    finally:
        if out: out.close()

    _logInfo("Success!")
>>>>>>> other

def embed_LSB(carrierFile,payloadFile,outFile):
    """Embed a message in the carrier audio using modified LSB coding
   
    Returns audio data with the embedded payload
        
    Parameters:
        carrierFile - the name of the carrier audio file
        payloadFile - the name of the payload file
        outFile - the name of the file to which the package will be written
    """
    from amm import wavread,wavwrite
    _logInfo("Encoding...")
    
    # read in the carrier file
    samples,params = wavread(carrierFile,bSplit=False)
    samples = samples.tolist()
    sampleLength = len(samples)

    # Read the payload in and store it as a list of integers
    payload = None
    payloadData = None
    try:
        payload = open(payloadFile, 'rb')
        payloadData = bytesToInts(payload.read())
    except (IOerror) as err:
        _logError("Error reading from file '%s'" % payloadFile)
        raise err
    finally:
        if payload: payload.close()
    
    payloadDataLength = len(payloadData)
    payloadSizeData = bitsForInt(payloadDataLength,size=32)
    payloadSizeDataLength = len(payloadSizeData)

    _logDebug("Payload is %d bits" % payloadDataLength)
    _logDebug("That is %f of # of samples" % (float(payloadDataLength)/sampleLength))
    
    # Verify that the payload is reasonably sized
    if (payloadDataLength > (sampleLength - 32)):
        err = InvalidSize("Payload is too large.")
        _logError("Can't embed the payload into the carrier")
        raise err

    # Embed payload size into first 32 bits of package
    for i in xrange(32):
        if (samples[i] % 2 != payloadSizeData[i]):
            samples[i] += 1
    
    # Embed the payload in the carrier
    for i in xrange(payloadDataLength):
        if (samples[i+32] % 2 != payloadData[i]):
            samples[i+32] += 1

    # Write the package to file
    wavwrite(outFile,params,stream=samples)
    
    _logInfo("Success!")

def decode_LSB(packageFile,outFile):
    """Decode the embedded message from the given package using modified LSB coding
        
    Returns the binary embedded message
        
    Parameters:
        packageFile - the name of the package audio file
        outFile - the name of the file to which the decoded payload will be written
    """
    from amm import wavread
    _logInfo("Decoding...")
    samples,params = wavread(packageFile,bSplit=False)
    
    # the first 32 bits encode the size of the payload
    payloadSizeChunk = samples[0:32]
    payloadSize = intForBits([i % 2 for i in payloadSizeChunk])
    _logDebug("Payload size = %d" % payloadSize)
    
    # check that the encoded payload size is not too large
    if (payloadSize > (len(samples) - 32)):
        err = InvalidSize("Specified payload size is too large")
        _logError("Invalid input for decoding")
        raise err
    
    payloadSegment = samples[32:32+payloadSize]
    
    payload = intsToBytes([i % 2 for i in payloadSegment])
    
    out = None
    try:
        out = io.open(outFile,'wb')
        out.write(bytearray(payload))
        out.flush()
    except IOError as err:
        _logError("Error writing out decoded data")
        raise err
    finally:
        if out: out.close()
    
    _logInfo("Success!")

###
