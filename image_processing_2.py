"""
6.101 Spring '23 Lab 2: Image Processing 2
"""

#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# VARIOUS FILTERS


def get_pixel(image, row, col, boundary_behavior):
    """
    returns the pixel value of a pixel at a given row and column

    types include "zero", "wrap", and "extend", which tell the function
    how to handle pixels that are out of bounds
    """
    if (
        col < 0 or row < 0 or (image["width"] - 1) < col or (image["height"] - 1) < row
    ):  # checks if out of bounds then returns pixel depending on boundary behavior
        if boundary_behavior == "zero":
            return 0
        elif boundary_behavior == "wrap":
            return get_wrapped_pixel(image, row, col)
        elif boundary_behavior == "extend":
            return get_extended_pixel(image, row, col)
    else:
        index = (
            row * image["width"]
        ) + col  # calculates the index of the pixel based off the given row and column
        return image["pixels"][index]


def get_wrapped_pixel(image, row, col):
    """
    gets out of bounds pixel using the wrap boundary behavior
    """
    new_row = row
    new_col = col
    if col < 0:  # left side
        while new_col < 0:
            new_col += image["width"]
    elif (image["width"] - 1) < col:  # right side
        while (image["width"] - 1) < new_col:
            new_col -= image["width"]
    elif row < 0:  # top side
        while new_row < 0:
            new_row += image["height"]
    elif (image["height"] - 1) < row:  # bottom side
        while (image["height"] - 1) < new_row:
            new_row -= image["height"]
    return get_pixel(image, new_row, new_col, "wrap")


def get_extended_pixel(image, row, col):
    """
    gets the out of bounds pixel using the extend boundary behavior
    """
    if col < 0:  # left side
        return get_pixel(image, row, 0, "extend")
    elif row < 0:  # top side
        return get_pixel(image, 0, col, "extend")
    elif (image["width"] - 1) < col:  # right side
        return get_pixel(image, row, image["width"] - 1, "extend")
    elif (image["height"] - 1) < row:  # bottom side
        return get_pixel(image, image["height"] - 1, col, "extend")


def apply_per_pixel(image, func):
    """
    applies a function to every pixel of an image
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    for pixel in image["pixels"]:
        result["pixels"].append(func(pixel))
    return result


def inverted(image):
    """
    inverts a grey scaled image
    """
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    the kernel is represented by a dictionary with the following keys:
    "dimension" - the dimension of the matrix as an int eg. dimension 3 is a 3x3 matrix
    "values" - list of values. length is equal to dimension ** 2
    """
    if not boundary_behavior in (
        "zero",
        "wrap",
        "extend",
    ):  # checks if given boundary behavior is valid
        return None
    result = {"height": image["height"], "width": image["width"], "pixels": []}
    for row in range(image["height"]):
        for col in range(image["width"]):  # iterate through each pixel
            new_value = 0
            for i_value, value in enumerate(
                kernel["values"]
            ):  # iterates through each kernel value and index
                shifted_row = (  # calculates the shift of the row based on the kernel
                    row
                    - int(kernel["dimension"] / 2)
                    + int(i_value / kernel["dimension"])
                )
                shifted_col = (  # calculates the shift of the col based on the kernel
                    col - int(kernel["dimension"] / 2) + (i_value % kernel["dimension"])
                )
                new_value += (
                    value
                    * get_pixel(  # applies kernel to each pixel and adds up each value
                        image, shifted_row, shifted_col, boundary_behavior
                    )
                )

            result["pixels"].append(
                new_value
            )  # appends new value created by kernel to new image
    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i_pixel, pixel in enumerate(
        image["pixels"]
    ):  # itereates through each pixel and index of image
        if pixel < 0:  # clip pixel lower than 0
            image["pixels"][i_pixel] = 0
        elif 255 < pixel:  # clip pixel higher than 255
            image["pixels"][i_pixel] = 255
        elif isinstance(pixel, float):  # makes all floats into ints
            image["pixels"][i_pixel] = round(pixel)


def create_matrix(n):
    """
    creates  blur matrix given the dimension of the matrix
    """
    return {"dimension": n, "values": [1 / (n**2)] * n**2}


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = create_matrix(kernel_size)
    # then compute the correlation of the input image with that kernel
    blurred_image = correlate(image, kernel, "extend")
    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    round_and_clip_image(blurred_image)
    return blurred_image


def sharpened(image, n):
    """
    sharpens an image based on blur kernel with dimension n
    """
    blur_kernel = create_matrix(n)
    blurred_image = correlate(
        image, blur_kernel, "extend"
    )  # blurs image using blur kernel
    sharpenend_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }
    for i, j in zip(
        image["pixels"], blurred_image["pixels"]
    ):  # performs sharpening calculation using the image and blur
        sharpenend_image["pixels"].append((2 * i) - j)
    round_and_clip_image(sharpenend_image)
    return sharpenend_image


def edges(image):
    """
    filter that detects the edges in an image and highlights them
    """
    krow = {"dimension": 3, "values": [-1, -2, -1, 0, 0, 0, 1, 2, 1]}
    kcol = {"dimension": 3, "values": [-1, 0, 1, -2, 0, 2, -1, 0, 1]}
    row_image = correlate(image, krow, "extend")
    col_image = correlate(
        image, kcol, "extend"
    )  # generates two images based on formula
    pixels = []
    for i, j in zip(
        row_image["pixels"], col_image["pixels"]
    ):  # combines values on images using formula
        pixels.append(math.sqrt((i**2) + (j**2)))
    final_image = {"height": image["height"], "width": image["width"], "pixels": pixels}
    round_and_clip_image(final_image)
    return final_image


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def color_filter(image):
        red, green, blue, new_image = (
            image.copy(),
            image.copy(),
            image.copy(),
            image.copy(),
        )
        red_pix = [x[0] for x in image["pixels"]]  # separate rgb pixels into 3 lists
        green_pix = [x[1] for x in image["pixels"]]
        blue_pix = [x[2] for x in image["pixels"]]
        red["pixels"], green["pixels"], blue["pixels"] = red_pix, green_pix, blue_pix
        new_red, new_green, new_blue = (
            filt(red),
            filt(green),
            filt(blue),
        )  # apply filter to each list of pixels
        new_image["pixels"] = list(
            zip(
                new_red["pixels"], new_green["pixels"], new_blue["pixels"]
            )  # combine filtered pixels and return
        )
        return new_image

    return color_filter


def make_blur_filter(kernel_size):
    """
    creates blur filter that is compatible color_filter_from_greyscale_filter
    """

    def blur_filter(image):
        return blurred(image, kernel_size)

    return blur_filter


def make_sharpen_filter(kernel_size):
    """
    creates sharpen filter that is compatible color_filter_from_greyscale_filter
    """

    def sharpen_filter(image):
        return sharpened(image, kernel_size)

    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def new_filter(image):
        for filt in filters:  # applies each filter
            image = filt(image)
        return image

    return new_filter


def custom_feature(image):
    """
    emboss filter. intakes image and applies emboss filter.
    returns new image
    """
    new_image = image.copy()
    kernel_1 = {
        "dimension": 3,
        "values": [0, 1, 0, 0, 0, 0, 0, -1, 0],
    }  # 4 kernels for the filter
    kernel_2 = {"dimension": 3, "values": [1, 0, 0, 0, 0, 0, 0, 0, -1]}
    kernel_3 = {"dimension": 3, "values": [0, 0, 0, 1, 0, -1, 0, 0, 0]}
    kernel_4 = {"dimension": 3, "values": [0, 0, 1, 0, 0, 0, -1, 0, 0]}
    image_1 = correlate(new_image, kernel_1, "extend")  # apply each kernel
    image_2 = correlate(image_1, kernel_2, "extend")
    image_3 = correlate(image_2, kernel_3, "extend")
    image_4 = correlate(image_3, kernel_4, "extend")
    return image_4


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    new_image = image.copy()
    for _ in range(ncols):  # apply each step ncols times
        grey_image = greyscale_image_from_color_image(new_image)
        energy = compute_energy(grey_image)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        new_image = image_without_seam(new_image, seam)
    return new_image


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    grey_image = image.copy()
    red_pix = [x[0] for x in image["pixels"]]  # separate rgb pixels
    green_pix = [x[1] for x in image["pixels"]]
    blue_pix = [x[2] for x in image["pixels"]]
    grey_image["pixels"] = [
        round((0.299 * r) + (0.587 * g) + (0.114 * b))
        for r, g, b in zip(
            red_pix, green_pix, blue_pix
        )  # combine rgb pixels using formula
    ]
    return grey_image


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def make_rows(image):
    """
    intakes an image and turns pixels into list of rows
    """
    rows = []
    new_row = []
    for i_pixel, pixel in enumerate(image["pixels"]):
        new_row.append(pixel)
        if not (i_pixel + 1) % (
            image["width"]
        ):  # starts new row when previous row finishes
            rows.append(new_row)
            new_row = []
    return rows


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    rows = make_rows(energy)  # turns pixels into list of rows
    new_pixels = []
    previous_row = []
    for i_row, row in enumerate(rows):  # iterates through each row
        for i_pixel, pixel in enumerate(row):  # iterates through each pixel
            if not i_row:  # checks if first row and appends each pixel of that row
                new_pixels.append(pixel)
            elif not i_pixel:  # checks if the first pixel of a row,
                # checks for lowest adjacent pixel accordingly
                lowest_pixel = min(previous_row[i_pixel], previous_row[i_pixel + 1])
                new_pixels.append(lowest_pixel + pixel)
            elif i_pixel == (
                energy["width"] - 1
            ):  # checks if last pixel of row, then checks adjacent pixels
                lowest_pixel = min(previous_row[i_pixel - 1], previous_row[i_pixel])
                new_pixels.append(lowest_pixel + pixel)
            else:  # checks each adjacent pixel for the lowest
                lowest_pixel = min(
                    previous_row[i_pixel - 1],
                    previous_row[i_pixel],
                    previous_row[i_pixel + 1],
                )
                new_pixels.append(lowest_pixel + pixel)
        previous_row = new_pixels[-energy["width"] :]  # resets previous row
    cumulative_map = energy.copy()
    cumulative_map["pixels"] = new_pixels
    return cumulative_map


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    rows = make_rows(cem)[::-1]  # reverses the order of the rows
    indices = []
    previous_index = 1
    for i_row, row in enumerate(rows):  # iterates through the rows
        if not i_row:  # checks if the bottom row, finds lowest index of that row
            lowest = min(row)
            index = row.index(lowest)
        elif (
            not previous_index
        ):  # checks if the index is the first of the row, adjusts accordingly
            options = [row[previous_index], row[previous_index + 1]]
            lowest = min(options)
            index = options.index(lowest) + previous_index
        elif previous_index == (
            cem["width"] - 1
        ):  # checks if the index is the last of the row, then adjusts
            options = [row[previous_index - 1], row[previous_index]]
            lowest = min(options)
            index = options.index(lowest) + previous_index - 1
        else:  # checks each of the adjacent pixels for the lowest one
            options = [
                row[previous_index - 1],
                row[previous_index],
                row[previous_index + 1],
            ]
            lowest = min(options)
            index = options.index(lowest) + previous_index - 1
        previous_index = index  # resets the previous index
        indices.append(
            index + ((cem["height"] - i_row - 1) * cem["width"])
        )  # appends new index
    return indices


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    pixels = image["pixels"][:]
    new_seam = seam[:]
    new_seam.sort()
    new_seam.reverse()  # makes sure seam is in reverse order
    for index in new_seam:
        pixels.pop(index)  # pops each index
    new_image = image.copy()
    new_image["pixels"] = pixels
    new_image["width"] = image["width"] - 1  # reduces width
    return new_image


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    cat = load_color_image("test_images/cat.png")
    # inverted_cat = color_invert(cat)
    # save_color_image(inverted_cat, "inverted_cat.png")

    # python = load_color_image("test_images/python.png")
    # color_blur = color_filter_from_greyscale_filter(make_blur_filter(9))
    # save_color_image(color_blur(python), "python_blur.png")

    # sparrow_chick = load_color_image("test_images/sparrowchick.png")
    # color_sharpen = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # save_color_image(color_sharpen(sparrow_chick), "sparrow_chick_sharpen.png")

    # frog = load_color_image("test_images/frog.png")
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # save_color_image(filt(frog), "frog_cascade.png")

    # twocats = load_color_image("test_images/twocats.png")
    # save_color_image(seam_carving(twocats, 100), "seam_carved_twocats.png")

    # golden_gate = load_color_image("test_images/golden_gate.png")
    # mboss = color_filter_from_greyscale_filter(emboss)
    # save_color_image(emboss(golden_gate), "emboss_golden_gate.png")
