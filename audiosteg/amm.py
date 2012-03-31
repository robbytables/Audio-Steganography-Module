"""
Audio Manipulation Module

Reads and writes wav files in RIFF format.
"""

import wave
import sys
import numpy
from . import _logDebug,_logInfo,_logWarning,_logError

RIFF_DTYPE = '<i2'

def wavread(strFileName, bSplit = True):
    """
    Read a wav file.
    
    returns two integer arrays with samples for the left and right
    channels, respectively. Also returns the contents of 
    Wave_read.getparams().
    
    Parameters:
        strFileName - the file to be opened
        bSplit - if True, split the samples into left and right channel.
                 Otherwise, return a single array. Defaults to True.
    
    Raises:
        IOError - if an error occurs while reading from the file
        wave.Error - if an error occurs while processing the WAV
    """
    
    # read in the wav file
    wavfile = None
    try:
        wavfile = wave.open(strFileName, 'rb')
        rawframes = wavfile.readframes(wavfile.getnframes())
        params = wavfile.getparams()
    except (IOError, wave.Error) as err:
        _logError("Error reading file: %s" % strFileName)
        raise err
    finally:
        if wavfile: wavfile.close() # close the file, if it exists
    
    # read the wav bitstream into an array
    samples = numpy.frombuffer(rawframes, numpy.dtype(RIFF_DTYPE))
    
    if bSplit:
        # split array into left and right arrays
        leftchannel = samples[0::2]
        rightchannel = samples[1::2]
        
        return (leftchannel, rightchannel, params)
    else:
        return (samples, params)

def wavwrite(strFileName, wavParams, **kwargs):
    """
    Write a wav file
    
    Parameters:
        strFileName - the file to write to
        leftStream - the array of samples for the left channel
        rightStream - the array of samples for the right channel
        wavParams - the parameters of the WAV file to write out
        
    Raises:
        IOError - if an error occurs while writing the file
        wave.error - if an error occurs while writing data to the file
        KeyError - if the function wasn't given either two mono streams
        	(leftStream and rightStream) or one interleaved stream (stream)
    """
    
    stream = []
    if (kwargs.has_key('leftStream') and kwargs.has_key('rightStream')):
        # merge the left and right arrays into a single array
        for i in range(len(kwargs['leftStream'])):
            stream += [kwargs['leftStream'][i], kwargs['rightStream'][i]]
    elif kwargs.has_key('stream'):
        stream = kwargs['stream']
    else:
		err = KeyError("wavwrite() given incorrect arguments.")
		_logError("left and right or interleaved, please", err)
		raise err
    
    # get ready to rumble. (open file for writing, set params)
    outfile = None
    try:
        outfile = wave.open(strFileName, 'wb')
        outfile.setparams(wavParams)
    
        # write file by converting array to 16le bitstream
        outfile.writeframes(numpy.array(stream).astype(RIFF_DTYPE).tostring())
    except (IOError, wave.Error) as err:
        _logError("Could not open file for writing in wav module: %s"
                  % strFileName)
        raise err
    finally:
        if outfile: outfile.close()
    
    return
