import requests
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Endpoint to your Flask server
URL = "http://127.0.0.1:5001/process_image"
# File path to your image
IMAGE_PATH = '/Users/karim/Downloads/pix.jpg'

def plot_histogram(data):
    colors = ['blue', 'green', 'red']
    
    for color in colors:
        plt.plot(data[color], color=color)
    
    plt.title("Color Histogram")
    plt.xlabel("Pixel Value")
    plt.ylabel("Frequency")
    plt.show()

def display_colors_as_rectangles(colors):
    fig, ax = plt.subplots(1, 1, figsize=(8, 2))
    
    # Plot rectangles of each color
    for i, color in enumerate(colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=color))
    
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.show()

def plot_color_moments(color_moments):
    # Set up the figure and axes
    fig, ax = plt.subplots(3, 1, figsize=(8, 6))

    channels = ['L', 'a', 'b']
    moments = ['mean', 'std_dev', 'skewness']

    # For each moment (mean, std_dev, skewness), plot a bar for each channel (L, a, b)
    for i, moment in enumerate(moments):
        values = [color_moments[channel][moment] for channel in channels]
        ax[i].bar(channels, values, color=['black', 'green', 'blue'])
        ax[i].set_ylabel(moment)
        ax[i].set_ylim(0, max(values) + 20)

    plt.tight_layout()
    plt.show()

def main():
    # Sending image to server
    with open(IMAGE_PATH, 'rb') as image:
        response = requests.post(URL, files={"image": image})
    
    # If successful, parse the JSON and plot
    if response.status_code == 200:
        data = response.json()
        
        plot_histogram(data['histogram'])
        
        hex_dominant_colors = [f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}" for color in data['dominant_colors']]
        display_colors_as_rectangles(hex_dominant_colors)

        # Print or plot color moments here
        plot_color_moments(data['color_moments'])
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()
