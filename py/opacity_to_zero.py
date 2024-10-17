import cv2, sys
import numpy as np

def set_nontransparent_alpha_to_full(input_image_path, output_image_path):
    """
    Set the alpha channel to 255 for all non-transparent pixels (alpha > 0) in a PNG image.

    Args:
    - input_image_path: str, the path to the input PNG image.
    - output_image_path: str, the path to save the modified image with full opacity for non-transparent pixels.
    """
    # Load the image with alpha channel (transparency)
    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)

    # Check if the image has an alpha channel (i.e., it is a transparent PNG)
    if image.shape[2] != 4:
        raise ValueError("The input image does not have an alpha channel.")

    # Set alpha to 255 where alpha > 0 (making all non-transparent pixels fully opaque)
    image[:, :, 3] = np.where(image[:, :, 3] > 0, 255, image[:, :, 3])

    # Save the modified image
    cv2.imwrite(output_image_path, image)

# Example usage:
set_nontransparent_alpha_to_full(sys.argv[1], 'output_image.png')
