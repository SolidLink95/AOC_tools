import cv2
import numpy as np
import sys

def colorize_image_preserve_alpha(input_image_path, output_image_path, color):
    """
    Colorize a black and white image using the specified color, preserving the alpha channel.

    Args:
    - input_image_path: str, the path to the input black and white image (with alpha channel).
    - output_image_path: str, the path to save the colorized image.
    - color: list or tuple, the BGR color to apply (e.g., [0, 165, 255] for orange).
    """
    # Load the image with alpha channel (transparency)
    image = cv2.imread(input_image_path, cv2.IMREAD_UNCHANGED)

    # Check if the image has an alpha channel
    if image.shape[2] == 4:
        # Split the image into color and alpha channels
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        
        # Convert the color part (grayscale) to color
        grayscale = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        colored_image = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2BGR)

        # Apply the specified color tint while keeping the grayscale intensity
        colored_image = np.array([[(int(pixel[0] * color[0] / 255), 
                                    int(pixel[0] * color[1] / 255), 
                                    int(pixel[0] * color[2] / 255)) for pixel in row] 
                                  for row in colored_image])

        # Merge the colorized image with the original alpha channel
        final_image = np.dstack((colored_image, alpha))
    else:
        # If no alpha channel, proceed with colorization
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        colored_image = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2BGR)

        # Apply the specified color tint
        colored_image = np.array([[(int(pixel[0] * color[0] / 255), 
                                    int(pixel[0] * color[1] / 255), 
                                    int(pixel[0] * color[2] / 255)) for pixel in row] 
                                  for row in colored_image])
        final_image = colored_image

    # Save the colored image with transparency preserved (if available)
    cv2.imwrite(output_image_path, final_image)

    # Optionally display the result (remove or comment out for non-GUI environments)
    # cv2.imshow('Colorized Image', final_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

# Example usage with orange color:
orange_color = [9, 123, 253]  # BGR value for orange
colorize_image_preserve_alpha(sys.argv[1], 'orange_colored_image.png', orange_color)
