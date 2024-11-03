import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Generate some example data
num_points = 50
x = np.random.rand(num_points)
y = np.random.rand(num_points)

# Set up the figure and axis
fig, ax = plt.subplots()
sc = ax.scatter([], [])

# Set limits for the axes
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Update function to add points
def update(frame):
    sc.set_offsets(np.c_[x[:frame], y[:frame]])
    return sc,

# Create the animation
ani = FuncAnimation(fig, update, frames=num_points + 1, blit=True, repeat=False)

# Show the animation
plt.show()
