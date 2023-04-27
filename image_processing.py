"""
manipulating greyscale images to produce different effects.
"""

import math

from PIL import Image

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


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
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
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # inverted_bluegill = inverted(bluegill)
    # save_greyscale_image(inverted_bluegill, "inverted_bluegill.png")
    pigbird1 = load_greyscale_image("test_images/pigbird.png")
    #kernel_values = [0] * 169
    #kernel_values[26] = 1
    #kernel1 = {"dimension": 13, "values": kernel_values}
    #zero_pigbird = correlate(pigbird1, kernel1, "zero")
    #round_and_clip_image(zero_pigbird)
    #save_greyscale_image(zero_pigbird, "zero_pigbird1.png")

# pigbird2 = load_greyscale_image("test_images/pigbird.png")
# extend_pigbird = correlate(pigbird2, kernel, "extend")
# save_greyscale_image(extend_pigbird, "extend_pigbird.png")

# pigbird3 = load_greyscale_image("test_images/pigbird.png")
# wrap_pigbird = correlate(pigbird3, kernel, "wrap")
# save_greyscale_image(wrap_pigbird, "wrap_pigbird.png")

# cat = load_greyscale_image("test_images/cat.png")
# blurred_cat = blurred(cat, 13)
# save_greyscale_image(blurred_cat, "wrap_blurred_cat.png")

# python = load_greyscale_image("test_images/python.png")
# sharpened_python = sharpened(python, 11)
# save_greyscale_image(sharpened_python, "sharpened_python.png")

# construct = load_greyscale_image("test_images/construct.png")
# edge_construct = edges(construct)
# save_greyscale_image(edge_construct, "edge_construct.png")
