import matplotlib.pyplot as plt
import seaborn as sns
from qiskit.visualization import plot_histogram

def plot_heatmap(grid, angles_a, angles_b):
    """Heatmap of CHSH expectation values.
    grid: 2‑D numpy array shape (len(angles_a), len(angles_b))
    angles_a/b: sequences of angles (radians)
    """
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(grid, xticklabels=[f"{b:.2f}" for b in angles_b], yticklabels=[f"{a:.2f}" for a in angles_a], cmap="viridis", annot=True, fmt=".3f")
    ax.set_xlabel("Bob angle (rad)")
    ax.set_ylabel("Alice angle (rad)")
    ax.set_title("CHSH expectation heatmap")
    plt.show()

def plot_counts(counts, backend_name: str):
    plt.figure(figsize=(7, 4))
    plot_histogram(counts, title=f"Results on {backend_name}")
    plt.show()
