import cv2
import numpy as np
from scipy.stats import skew
from sklearn.cluster import KMeans

def get_color_histogram(image):
    hists = {}
    for i, color in enumerate(['blue', 'green', 'red']):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        hists[color] = hist.flatten().tolist()
    return hists

def get_dominant_colors(image, n=5):
    resized_image = cv2.resize(image, (50, 50))  
    hsv_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)  
    pixels = hsv_image.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n)
    kmeans.fit(pixels)

    # Extracting dominant colors and their frequencies
    unique, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_indices = np.argsort(counts)[::-1]

    dominant_colors = kmeans.cluster_centers_[sorted_indices].astype(int)
    dominant_colors_rgb = cv2.cvtColor(np.uint8([dominant_colors]), cv2.COLOR_HSV2BGR)[0]

    return [tuple(map(int, color)) for color in dominant_colors_rgb]


def get_color_moments(image):
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2Lab)
    moments = {}
    for i, color in enumerate(['L', 'a', 'b']):
        channel = lab_image[:, :, i]
        mean = np.mean(channel)
        std_dev = np.std(channel)
        skewness = skew(channel.reshape(-1))
        moments[color] = {"mean": mean, "std_dev": std_dev, "skewness": skewness}

    return moments
