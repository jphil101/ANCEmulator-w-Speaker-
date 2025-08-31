import sounddevice as sd
import numpy as np
from scipy.signal import lfilter
import time

# --- Configuration ---
# Set these to match your hardware setup
INPUT_DEVICE_INDEX = 2  # <-- Use your Scarlett 2i2
OUTPUT_DEVICE_INDEX = 1 # <-- Use your Built-in Output

# --- CRITICAL SETTING ---
# This MUST match the sample rate set in your Focusrite Control software.
# 44100 is the standard and most compatible rate.
SAMPLE_RATE = 44100

# --- Performance & Stability Parameters ---
BLOCK_SIZE = 2048       # A balanced block size for good performance
LATENCY = 'low'         # Your Scarlett can likely handle low latency

# --- Adaptive Filter Parameters (Tunable) ---
FILTER_LENGTH = 512
# A conservative step size is best to start with.
STEP_SIZE = 0.2

# --- Global State ---
w = np.zeros(FILTER_LENGTH)
zi = np.zeros(FILTER_LENGTH - 1)
overlap = np.zeros(FILTER_LENGTH - 1)

def stable_lms_callback(indata, outdata, frames, time, status):
    """
    This callback uses the efficient Block LMS algorithm for stable performance.
    """
    global w, zi, overlap

    if status:
        print(status)

    d_block = indata.flatten()
    d = np.concatenate((overlap, d_block))
    overlap = d[- (FILTER_LENGTH - 1):]

    # 1. Generate the anti-noise signal
    y, zf = lfilter(w, 1.0, d, zi=zi)
    zi = zf

    # 2. Simulate the error signal
    e = d - y
    
    # 3. Update the filter weights using the Block LMS algorithm
    num_frames = len(d_block)
    strides = (d.strides[0], d.strides[0])
    shape = (num_frames, FILTER_LENGTH)
    x_frames = np.lib.stride_tricks.as_strided(d, shape=shape, strides=strides)

    gradient = np.dot(x_frames.T, e[FILTER_LENGTH - 1:])
    w += (STEP_SIZE / num_frames) * gradient
    np.clip(w, -2.0, 2.0, out=w)

    # Send the anti-noise to the output
    outdata[:] = -y[FILTER_LENGTH - 1:].reshape(-1, 1)


def main():
    """
    Sets up and starts the stable single-microphone audio stream.
    """
    print("--- Starting Stable ANC Prototype ---")
    print("Using efficient Block LMS algorithm.")
    
    try:
        print(f"Input Device: {sd.query_devices(INPUT_DEVICE_INDEX)['name']}")
        print(f"Output Device: {sd.query_devices(OUTPUT_DEVICE_INDEX)['name']}")
        print(f"Sample Rate: {SAMPLE_RATE} Hz")
        print("Press Ctrl+C to stop.")

        with sd.Stream(
            device=(INPUT_DEVICE_INDEX, OUTPUT_DEVICE_INDEX),
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            latency=LATENCY,
            channels=1,
            dtype=np.float32,
            callback=stable_lms_callback
        ):
            while True:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStream stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
