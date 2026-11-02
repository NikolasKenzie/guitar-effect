import sounddevice as sd
import numpy as np
import sys
import keyboard

SAMPLE_RATE = 44100
# BUFFER_SIZE = 8192
BUFFER_SIZE = 7168

DISTORTION = False
PRE_AMP = False
DELAY = False
REVERB = False
# delay state 
DELAY_TIME = 370 
DELAY_MIX = 0.25
DELAY_FEEDBACK = 0.08

# REVERB STATE
REVERB_TIME = 17

delay_samples = int(
    DELAY_TIME / 1000 * SAMPLE_RATE
)

delay_buffer = np.zeros(delay_samples)

delay_index = 0


def audio_callback(indata, outdata, frames, time, status):
    global PRE_AMP
    if status:
        print(status)

    outdata[:] = signal_processing(indata)

def signal_processing(indata):

    chain = []

    if DISTORTION:
        chain.append(distortion)

    if PRE_AMP:
        chain.append(amplifier)
    if DELAY:
        chain.append(delay)
    

    audio = indata

    for effect in chain:
        audio = effect(audio)

    return audio



def distortion(indata):
    
    gain = indata * 10

    audio_clip = np.clip(gain, -0.7, 0.7)
    level_audio = audio_clip * 0.7

    return level_audio

    

def amplifier(indata):

    global PRE_AMP

    gain = 2

    audio = indata[:, 0]

    audio *= gain

    audio = np.tanh(audio)

    audio = equalizer_amp(
        audio,
        SAMPLE_RATE,
        bass_gain=0.7,
        mid_gain=0.5,
        treble_gain=5,
        presence_gain=6
    )
    # 

    # volume
    audio *= 1

    return audio.reshape(-1, 1)



def equalizer_amp(audio,
           sample_rate,
           bass_gain=-4.0,
           mid_gain=2.0,
           treble_gain=5.0,
           presence_gain=7.0):
    

    fft = np.fft.rfft(audio)

    freqs = np.fft.rfftfreq(
        len(audio),
        d=1/sample_rate
    )

    
    fft[(freqs >= 20) & (freqs < 250)] *= bass_gain

    
    fft[(freqs >= 250) & (freqs < 2000)] *= mid_gain

    
    fft[(freqs >= 2000) & (freqs < 6000)] *= treble_gain

    
    fft[freqs >= 6000] *= presence_gain

    audio = np.fft.irfft(
        fft,
        n=len(audio)
    )

    return audio

def delay(indata):
    global delay_buffer
    global delay_index

    audio = indata[:, 0]

    output = np.zeros_like(audio)

    for i in range(len(audio)):

        sample = audio[i]

        delayed = delay_buffer[delay_index]

        # dry + wet
        output[i] = sample + delayed * DELAY_MIX

        # feedback
        delay_buffer[delay_index] = (
            sample +
            delayed * DELAY_FEEDBACK
        )

        delay_index += 1

        if delay_index >= len(delay_buffer):
            delay_index = 0

    output = np.clip(output, -1.0, 1.0)

    return output.reshape(-1, 1)

def reverb(indata):
   return


    

try:
    with sd.Stream(
        device=(2, 7),
        samplerate=SAMPLE_RATE,
        blocksize=BUFFER_SIZE,
        callback=audio_callback
    ):
        while True:
            if keyboard.is_pressed('q'):
                break
            
            if keyboard.is_pressed('x'):
                PRE_AMP = not PRE_AMP

                if PRE_AMP:
                    print("preamp is on")
                else:
                    print("preamp is off")

                sd.sleep(200)

            if keyboard.is_pressed('z'):
                DISTORTION =  not DISTORTION 
                
                if DISTORTION:
                    print("distortion is on")
                else:
                    print("distortionb is off")
                sd.sleep(200)

            if keyboard.is_pressed('c'):
                DELAY =  not DELAY 
                
                if DELAY:
                    print("delay is on")
                else:
                    print("delay is off")
                sd.sleep(200)
            if keyboard.is_pressed('v'):
                DELAY =  not DELAY 
                
                if DELAY:
                    print("reverb is on")
                else:
                    print("reverb is off")
                sd.sleep(200)

            sd.sleep(10)
except Exception as e:
    print(f"\nERROR: {e}")