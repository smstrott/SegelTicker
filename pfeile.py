import numpy as np
import matplotlib.pyplot as plt

# Beispielwerte
x = np.arange(10)
y = np.zeros_like(x)

wind_deg = np.linspace(0, 360, 10)  # Windrichtungen in Grad

# Einheitlicher Vektor (Länge = 1)
u = np.sin(np.radians(wind_deg))
v = np.cos(np.radians(wind_deg))

# Pfeile sollen sich um die Mitte drehen
x_shifted = x - u / 2
y_shifted = y - v / 2

# Plot
fig, ax = plt.subplots()
ax.quiver(x_shifted, y_shifted, u, v, angles='xy', scale_units='xy', scale=1, width=0.005, color='tab:blue')
ax.set_aspect('equal')
ax.set_xlim(-1, 10)
ax.set_ylim(-1.5, 1.5)
ax.set_title("Windrichtungen – Pfeile mit fester Länge und Mitte als Anker")
plt.grid(True)
plt.show()