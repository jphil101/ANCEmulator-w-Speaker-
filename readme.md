# Basic Python ANC (Active Noise Cancellation) Prototype

This is a simple, real-time Active Noise Cancellation prototype written in Python. It uses the `sounddevice`, `numpy`, and `scipy` libraries to capture audio, process it, and output an "anti-noise" signal.

This implementation uses the Block Least Mean Squares (LMS) algorithm, an efficient method for adaptive filtering.

---

## What is Active Noise Cancellation (ANC)?

Active Noise Cancellation is a method for reducing unwanted sound by using a "second sound" (anti-noise) that is specifically engineered to cancel out the first (the noise).

## How ANC Works (ELI5)
(Skip this part if you know what destructive interference is)

Imagine sound as waves in a pond. A loud, annoying noise is like a big wave, with a peak (⬆️) and a trough (⬇️).

ANC works by being very fast and very smart. Dedicated hardware and efficient algorithms are what allow your modern headphones/earphones to achieve this.
1.  A microphone acts like a lookout. It *sees* the noise wave (⬆️) coming.
2.  A tiny computer instantly *predicts* what that wave looks like.
3.  It tells a speaker to shout out the *exact opposite* wave at the *exact same time*. So, when the noise wave is at its peak (⬆️), the speaker shoots out a trough (⬇️).

When the peak and the trough meet, they flatten each other out (`+1 + (-1) = 0`). This is called destructive interference. The result is silence (or at least, much less noise).

---

## How This Script Works

This script attempts to do this using a Block Least Mean Squares (LMS) adaptive filter.

1.  Callback: The `stable_lms_callback` function is the "engine." It runs every time the sound card has a new chunk (or "block") of audio.
2.  Input: It gets the latest block of noise from the microphone (`indata`).
3.  Predict: It uses its current "filter" (`w`) to make a *best guess* of what the noise sounds like. This guess is the signal `y`.
4.  Output: It immediately sends the *opposite* of its guess (`-y`) to the speakers (`outdata`). This is the anti-noise.
5.  Learn: This is the "LMS" part. The script calculates its "error" (`e = d - y`), which is the leftover sound it *failed* to cancel. It uses this error to update its filter (`w`) so that its guess for the *next* block of sound will be better.

It is "adaptive" because it is constantly learning and changing its filter `w` to match the incoming noise.

---

## Current Status & Experimental Results

This script is a very simple prototype and has a known, fundamental limitation.

Observation:
When testing with a Scarlett 2i2 as input and a wired speaker as output, the script does not produce silence. Instead, it tends to generate a loud, unstable noise. This noise sometimes *feels* like it's canceling some frequencies, but it's mostly equivalent to adding loud white noise to the room.

Why is this happening?
The current algorithm (`e = d - y`) is *too* simple. It assumes the "error" it hears at the microphone is just `Original Noise - AntiNoise`.

In reality, the anti-noise (`-y`) leaves the speaker and *travels through the air* before it gets back to the microphone. This path (from speaker to mic) is called the "secondary path." The algorithm isn't accounting for this delay and change in the sound. It's hearing its *own* anti-noise as part of the "error," creating an unstable feedback loop.

---

## Next Steps (The Solution)

The next major step is to upgrade the algorithm from "LMS" to "FxLMS" (Filtered-X Least Mean Squares).

FxLMS is designed specifically to solve this feedback problem. The process will involve:

1.  Secondary Path Modeling: First, we must run an offline test to *measure* the secondary path (speaker-to-mic). This test involves playing a known sound (like white noise) and recording it to create a "model" (another filter) of what our speaker sounds like to our microphone.
2.  Implementing FxLMS: We will update the callback to use this new model. The FxLMS algorithm "filters" its internal signals using this path model. This allows it to "understand" what its own anti-noise will sound like when it reaches the microphone, letting it correctly separate the *real* noise from its *own* feedback.

This will lead to a much more stable and effective noise cancellation system.

---

## How to Run

⚠️ Warning: This script can produce loud, sudden, and unstable noise. Always start with your speaker volume set to minimum and increase it slowly.

1. Install the required Python libraries using the requirements.txt file:
    pip install -r requirements.txt
  
2.  Find your audio devices. You *must* tell the script which microphone and speaker to use. Run DeviceCheck.py to print out this list.
    
4.  Look for your devices in the list (e.g., your "Scarlett 2i2" and "Wired Speaker"). Note their index numbers.
    ```
    > 2 Scarlett 2i2 USB, ASIO (2 in, 2 out)
    < 1 Speakers (Realtek High Defini...), MME (0 in, 2 out)
    ```
5.  Edit the script: Change these two lines at the top of the file to match your hardware:
    ```python
    INPUT_DEVICE_INDEX = 2  # Change this to your mic's index
    OUTPUT_DEVICE_INDEX = 1 # Change this to your speaker's index
    ```
6.  Run the script:
    python ANCProto.py
    
7.  Press `Ctrl+C` in the terminal to stop the stream.
