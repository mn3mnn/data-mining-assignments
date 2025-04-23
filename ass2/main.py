import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import random

class ClusteringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Clustering App")
        self.root.geometry("600x400")

        self.file_path = tk.StringVar()
        self.percentage = tk.IntVar(value=100)
        self.k_value = tk.IntVar(value=3)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text="Select Data File:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.file_path, width=50).pack(pady=5)
        ttk.Button(self.root, text="Browse", command=self.browse_file).pack(pady=5)

        ttk.Label(self.root, text="Select % of Data to Read:").pack(pady=5)
        ttk.Scale(self.root, from_=10, to=100, orient='horizontal', variable=self.percentage).pack(pady=5)
        ttk.Label(self.root, textvariable=self.percentage).pack()

        ttk.Label(self.root, text="Number of Clusters (K):").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.k_value).pack(pady=5)

        ttk.Button(self.root, text="Run Clustering", command=self.run_clustering).pack(pady=20)

        self.output_text = tk.Text(self.root, height=10, wrap='word')
        self.output_text.pack(padx=10, pady=10, fill='both', expand=True)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        self.file_path.set(path)

    def euclidean_distance(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def initialize_centroids(self, data, k):
        indices = random.sample(range(len(data)), k)
        return [data[i] for i in indices]

    def assign_clusters(self, data, centroids):
        clusters = [[] for _ in centroids]
        for point in data:
            distances = [self.euclidean_distance(point, centroid) for centroid in centroids]
            cluster_index = distances.index(min(distances))
            clusters[cluster_index].append(point)
        return clusters

    def update_centroids(self, clusters):
        new_centroids = []
        for cluster in clusters:
            if cluster:
                new_centroid = np.mean(cluster, axis=0).tolist()
            else:
                new_centroid = [0] * len(clusters[0][0])  # Avoid empty cluster errors
            new_centroids.append(new_centroid)
        return new_centroids

    def has_converged(self, old_centroids, new_centroids, tolerance=1e-4):
        return all(self.euclidean_distance(a, b) < tolerance for a, b in zip(old_centroids, new_centroids))

    def detect_outliers(self, data, centroids, labels):
        distances = [self.euclidean_distance(point, centroids[label]) for point, label in zip(data, labels)]
        threshold = np.mean(distances) + 2 * np.std(distances)
        outliers = [i for i, d in enumerate(distances) if d > threshold]
        return outliers

    def run_kmeans(self, data, k, max_iters=100):
        centroids = self.initialize_centroids(data, k)

        for _ in range(max_iters):
            clusters = self.assign_clusters(data, centroids)
            new_centroids = self.update_centroids(clusters)
            if self.has_converged(centroids, new_centroids):
                break
            centroids = new_centroids

        labels = []
        for point in data:
            distances = [self.euclidean_distance(point, centroid) for centroid in centroids]
            label = distances.index(min(distances))
            labels.append(label)

        return labels, centroids

    def run_clustering(self):
        path = self.file_path.get()
        percentage = self.percentage.get()
        k = self.k_value.get()

        try:
            df = pd.read_csv(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

        try:
            df_numeric = df[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].copy().dropna()
        except Exception as e:
            messagebox.showerror("Error", f"Missing or incorrect columns:\n{e}")
            return

        sample_size = int(len(df_numeric) * (percentage / 100))
        df_sampled = df_numeric.sample(n=sample_size, random_state=42).reset_index(drop=True)

        data_points = df_sampled.values.tolist()
        labels, centroids = self.run_kmeans(data_points, k)
        outlier_indices = self.detect_outliers(data_points, centroids, labels)

        # Add results to DataFrame
        df_sampled['Cluster'] = labels
        df_sampled['Outlier'] = df_sampled.index.isin(outlier_indices)

        # Display results
        self.output_text.delete(1.0, tk.END)
        for i in range(k):
            cluster_data = df_sampled[(df_sampled['Cluster'] == i) & (~df_sampled['Outlier'])]
            self.output_text.insert(tk.END, f"Cluster {i + 1}:\n")
            self.output_text.insert(tk.END, cluster_data[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].to_string(index=False))
            self.output_text.insert(tk.END, "\n\n")

        outliers = df_sampled[df_sampled['Outlier']]
        if not outliers.empty:
            self.output_text.insert(tk.END, "Outliers Detected:\n")
            self.output_text.insert(tk.END, outliers[['Age', 'Annual Income (k$)', 'Spending Score (1-100)']].to_string(index=False))
        else:
            self.output_text.insert(tk.END, "No Outliers Detected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClusteringApp(root)
    root.mainloop()
