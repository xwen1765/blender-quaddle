from PIL import Image
import os

def change_alpha(image_path, alpha_value, save_path):
    # Load the image
    image = Image.open(image_path).convert("RGBA")
    pixels = image.load()

    # Change the alpha value of non-transparent pixels
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b, a = pixels[i, j]
            if a > 0:
                pixels[i, j] = (r, g, b, int(alpha_value * 255))

    # Save the new image
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    new_file_name = f"{file_name}_{int(alpha_value*100)}.png"
    new_file_path = os.path.join(save_path, new_file_name)
    image.save(new_file_path)


if __name__ == "__main__":
    # Set the input image path and save path
    input_path = "/Users/wenxuan/Documents/Blender/Assets/morphing_fractals/F (28).png"
    save_path = "/Users/wenxuan/Documents/Blender/Assets/morphing_fractals/"

    # Create the save path if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Loop over the desired alpha values
    for alpha_value in [0, 0.2, 0.4, 0.6, 0.8, 1]:
        # Change the alpha value and save the new image
        change_alpha(input_path, alpha_value, save_path)