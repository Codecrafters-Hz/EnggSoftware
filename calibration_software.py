import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import random

# Global variables
is_running = False
resistance_data = []
time_data = []
connectors_status = [False] * 8  # Simulate 8 connectors

# Force range for validation
force_ranges = [10, 20, 30, 40, 50, 60, 70, 80]  # Example acceptable force values

def calculate_average(v1, v2):
    """Calculate the average of two voltages."""
    try:
        return (float(v1) + float(v2)) / 2
    except ValueError:
        return "Invalid Input"

def start_calibration():
    """Start the calibration process."""
    global is_running
    is_running = True
    status_var.set("Started")
    threading.Thread(target=update_graph, daemon=True).start()

def stop_calibration():
    """Stop the calibration process."""
    global is_running
    is_running = False
    status_var.set("Finished")

def reset_calibration():
    """Reset all values and clear the graph."""
    global resistance_data, time_data
    is_running = False
    resistance_data.clear()
    time_data.clear()
    status_var.set("Reset")
    avg_voltage_var.set("")
    v1_var.set("")
    v2_var.set("")
    force_var.set("")
    for i in range(8):
        connectors_status[i] = False
        connector_labels[i].config(text=f"Connector {i+1}: Not Placed", background="red")
    ax.clear()
    ax.set_title("Resistance vs Time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Resistance (Ohms)")
    canvas.draw()

def update_graph():
    """Simulate resistance changes and update the graph dynamically."""
    global is_running
    start_time = time.time()
    while is_running:
        elapsed_time = time.time() - start_time
        resistance = random.uniform(10, 50)  # Simulated resistance value
        resistance_data.append(resistance)
        time_data.append(elapsed_time)
        ax.clear()
        ax.plot(time_data, resistance_data, label="Resistance (Ohms)", color="blue")
        ax.set_title("Resistance vs Time")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Resistance (Ohms)")
        ax.legend()
        canvas.draw()
        update_connectors()
        time.sleep(0.5)

def update_connectors():
    """Simulate connector placement and force validation."""
    for i in range(8):
        simulated_force = random.uniform(5, 85)  # Simulate force for each connector
        force_diff = abs(simulated_force - force_ranges[i])
        if force_diff <= 10:
            connectors_status[i] = True
            connector_labels[i].config(text=f"Connector {i+1}: OK ({simulated_force:.2f} N)", background="green")
        else:
            connectors_status[i] = False
            connector_labels[i].config(text=f"Connector {i+1}: Not OK ({simulated_force:.2f} N)", background="red")

# GUI setup
root = tk.Tk()
root.title("Calibration Software")
root.geometry("1000x700")

# Input frame
input_frame = ttk.LabelFrame(root, text="Input Parameters")
input_frame.pack(pady=10, padx=10, fill="x")

ttk.Label(input_frame, text="Voltage 1 (V):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
v1_var = tk.StringVar()
ttk.Entry(input_frame, textvariable=v1_var).grid(row=0, column=1, padx=10, pady=5)

ttk.Label(input_frame, text="Voltage 2 (V):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
v2_var = tk.StringVar()
ttk.Entry(input_frame, textvariable=v2_var).grid(row=1, column=1, padx=10, pady=5)

ttk.Label(input_frame, text="Force (N):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
force_var = tk.StringVar()
ttk.Entry(input_frame, textvariable=force_var).grid(row=2, column=1, padx=10, pady=5)

# Average voltage calculation
avg_voltage_var = tk.StringVar()
ttk.Label(input_frame, text="Average Voltage (V):").grid(row=3, column=0, padx=10, pady=5, sticky="w")
ttk.Entry(input_frame, textvariable=avg_voltage_var, state="readonly").grid(row=3, column=1, padx=10, pady=5)

def calculate_and_display_avg():
    avg_voltage = calculate_average(v1_var.get(), v2_var.get())
    avg_voltage_var.set(avg_voltage)

ttk.Button(input_frame, text="Calculate Average", command=calculate_and_display_avg).grid(row=4, column=0, columnspan=2, pady=10)

# Status bar
status_var = tk.StringVar(value="Ready")
ttk.Label(root, text="Status:", font=("Arial", 12, "bold")).pack(pady=5)
status_label = ttk.Label(root, textvariable=status_var, font=("Arial", 10))
status_label.pack()

# Calibration control bar
control_frame = ttk.LabelFrame(root, text="Calibration Controls")
control_frame.pack(pady=10, padx=10, fill="x")

ttk.Button(control_frame, text="Start", command=start_calibration).pack(side="left", padx=10, pady=10)
ttk.Button(control_frame, text="Stop", command=stop_calibration).pack(side="left", padx=10, pady=10)
ttk.Button(control_frame, text="Reset", command=reset_calibration).pack(side="left", padx=10, pady=10)

# Connector status frame
connector_frame = ttk.LabelFrame(root, text="Connectors Status")
connector_frame.pack(pady=10, padx=10, fill="x")

connector_labels = []
for i in range(8):
    label = tk.Label(connector_frame, text=f"Connector {i+1}: Not Placed", background="red", fg="white", padx=10, pady=5)
    label.grid(row=i // 4, column=i % 4, padx=10, pady=5)
    connector_labels.append(label)

# Graph area
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Resistance vs Time")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Resistance (Ohms)")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(pady=20)

# Run the GUI
root.mainloop()
