
import wave
import struct



def backwards(sound):
    """
    takes in dictionary of mono sound and reverses the samples
    """
    backwards_sound = sound.copy()  # creates a copy and reverses the list of the copy
    samples = sound["samples"]
    backwards_samples = samples[::-1]
    backwards_sound["samples"] = backwards_samples
    return backwards_sound


def mix(sound1, sound2, p):
    """
    takes in two sounds and mixes them based on the mixing parameter 'p'
    """
    # mix 2 good sounds
    if not sound1["rate"] == sound2["rate"]:
        print("no")
        return

    r = sound1["rate"]  # get rate

    if len(sound1) == 2:  #
        sound1 = sound1["samples"]  # sets the length of mix as the shorter sound
        sound2 = sound2["samples"]
        if len(sound1) < len(sound2):
            length = len(sound1)
        elif len(sound2) < len(sound1):
            length = len(sound2)
        elif len(sound1) == len(sound2):
            length = len(sound1)
        else:
            print("whoops")
            return

        mixed_sample = []
        x = 0
        while x <= length:
            s2, s1 = p * sound1[x], sound2[x] * (1 - p)  # mix sounds
            mixed_sample.append(s1 + s2)  # add sounds
            x += 1
            if x == length:  # end
                break

        return {"rate": r, "samples": mixed_sample}  # return new sound

    elif len(sound1) == 3:
        if len(sound1["left"]) < len(
            sound2["left"]
        ):  # sets the length of mix as the shorter sound
            length = len(sound1["left"])
        elif len(sound2["left"]) < len(sound1["left"]):
            length = len(sound2["left"])
        elif len(sound1["left"]) == len(sound2["left"]):
            length = len(sound1["left"])
        else:
            print("whoops")
            return

        mixed_right = []
        mixed_left = []
        x = 0
        while x <= length:
            sl2, sl1 = p * sound1["left"][x], sound2["left"][x] * (1 - p)
            mixed_left.append(sl1 + sl2)  # add sounds
            sr2, sr1 = p * sound1["right"][x], sound2["right"][x] * (1 - p)
            mixed_right.append(sr1 + sr2)  # add sounds
            x += 1
            if x == length:  # end
                break

        return {"rate": r, "left": mixed_left, "right": mixed_right}


def convolve(sound, kernel):
    """
    Applies a filter to a sound, resulting in a new sound that is longer than
    the original mono sound by the length of the kernel - 1.
    Does not modify inputs.

    Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        kernel: A list of numbers

    Returns:
        A new mono sound dictionary.
    """
    final_sample = [0] * (
        len(kernel) + len(sound["samples"]) - 1
    )  # sets length of final sample
    samples = []
    for shift, scale in enumerate(kernel):
        if scale != 0:  # skips if no scale
            scaled_sample = [0] * shift  # offset scaled sound by filter index
            scaled_sample += [scale * x for x in sound["samples"]]  # scales each sample
            while len(scaled_sample) < (
                len(kernel) + len(sound["samples"]) - 1
            ):  # adds tailing zeros
                scaled_sample += [0]
            samples.append(scaled_sample)
    for sample in samples:
        for val, new_number in enumerate(sample):
            final_sample[
                val
            ] += new_number  # adds each scaled sample to the final sample
    return {"rate": sound["rate"], "samples": final_sample}


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    sample_delay = round(delay * sound["rate"])  # calculate delay using rate
    echo_filter = [0] * ((sample_delay * num_echoes) + 1)  # sets length of the filter
    for i in range(1, num_echoes + 1):
        offset = int(i * sample_delay)  # sets the offset using delay
        echo_filter[offset] = (
            scale**i
        )  # sets the scale in the filter, increases exponentially each time
    convolved_sound = convolve(sound, echo_filter)
    for i in range(len(sound["samples"])):
        convolved_sound["samples"][i] += sound["samples"][
            i
        ]  # adds the echo to the original sound
    return convolved_sound


def pan(sound):
    """
    makes stereo sound fade from left to right
    """
    panned_sound = {"rate": sound["rate"], "left": [], "right": []}
    for i in range(len(sound["left"])):
        new_left_sound = (1 - (i / (len(sound["left"]) - 1))) * sound["left"][
            i
        ]  # scales left sample based on given formula
        new_right_sound = (i / (len(sound["left"]) - 1)) * sound["right"][
            i
        ]  # scales right sample based on given formula
        panned_sound["left"].append(new_left_sound)  # append to new sound
        panned_sound["right"].append(new_right_sound)
    return panned_sound


def remove_vocals(sound):
    """
    removes vocals from a stereo sample by subtracting
    the left samples by the right samples
    """
    removed_vocals = {"rate": sound["rate"], "samples": []}
    for i in range(len(sound["left"])):
        new_sound = (
            sound["left"][i] - sound["right"][i]
        )  # subtracts left sound value by right sound value
        removed_vocals["samples"].append(new_sound)  # append to new sound
    return removed_vocals


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def bass_boost_kernel(boost, scale=0):
    """
    Constructs a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.

    Args:
        boost: an int that controls the frequencies that are boosted (0 will
            boost all frequencies roughly equally, and larger values allow more
            focus on the lowest frequencies in the input sound).
        scale: a float, default value of 0 means no boosting at all, and larger
            values boost the low-frequency content more);

    Returns:
        A list of floats representing a bass boost kernel.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(boost):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)

    mystery = load_wav("sounds/mystery.wav")
    # write_wav(backwards(mystery), "mystery_reversed.wav")

    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    # write_wav(mix(synth, water, 0.2), "mixed.wav")

    # ice_and_chilli = load_wav("sounds/ice_and_chilli.wav")
    # new_bass_boost_kernel = bass_boost_kernel(1000, 1.5)
    # write_wav(convolve(ice_and_chilli, new_bass_boost_kernel), "bass_boosted.wav")

    # chord = load_wav("sounds/chord.wav")
    # write_wav(echo(chord,5,.3,.6),"echo_chord.wav")

    # car = load_wav("sounds/car.wav", stereo=True)
    # write_wav(pan(car), "panned_car.wav")

    # lookout = load_wav("sounds/lookout_mountain.wav", stereo=True)
    # write_wav(remove_vocals(lookout), "no_vocals_lookout.wav")

    # synth_stereo = load_wav("sounds/synth.wav", stereo=True)
    # water_stereo = load_wav("sounds/water.wav", stereo=True)
    # write_wav(mix(synth_stereo, water_stereo, 0.3), "mixed_stereo.wav")
