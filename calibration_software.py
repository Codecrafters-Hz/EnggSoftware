import tkinter as tk 
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import random

# Constants
MAX_FORCE = 10  # Maximum acceptable force (in Newtons)
CONNECTOR_TYPES = {
    "Type A": 4,  # 4 contact points
    "Type B": 6,  # 6 contact points
    "Type C": 8   # 8 contact points
}

# Global Variables
is_running = False
force_data = []
resistance_data = []
time_data = []
connector_status = {}
current_connector_type = "Type A"
start_time = None
force_values = []  # Real-time force values for bar graph
voltage_1 = 0
voltage_2 = 0

# Function to simulate real-time data
def simulate_force_data(num_points):
    """Simulates force values for each contact point."""
    return [random.uniform(5, 15) for _ in range(num_points)]

def simulate_resistance_data():
    """Simulates resistance values."""
    return random.uniform(10, 50)

# Update Resistance Graph
def update_resistance_graph():
    """Updates the resistance vs time graph."""
    resistance_ax.clear()
    resistance_ax.plot(time_data, resistance_data, label="Resistance (Ohms)", color="blue")
    resistance_ax.set_title("Resistance vs Time")
    resistance_ax.set_xlabel("Time (s)")
    resistance_ax.set_ylabel("Resistance (Ohms)")
    resistance_ax.legend()
    resistance_canvas.draw()

# Update Force Distribution Bar Graph
def update_force_bar_graph():
    """Updates the bar graph for force distribution."""
    force_ax.clear()
    num_points = len(force_values)
    x_labels = [f"CP{i+1}" for i in range(num_points)]
    colors = ["green" if force <= MAX_FORCE else "red" for force in force_values]

    force_ax.bar(x_labels, force_values, color=colors)
    force_ax.set_title("Contact Force Distribution")
    force_ax.set_ylabel("Force (N)")
    force_ax.set_ylim(0, MAX_FORCE + 5)
    force_canvas.draw()

# Update Force Table
def update_force_table(forces):
    """Update the connector force table."""
    for i, force in enumerate(forces):
        color = "green" if force <= MAX_FORCE else "red"
        connector_status[i].config(
            text=f"CP{i+1} – {force:.2f} N",
            background=color,
            foreground="white"
        )

# Real-Time Monitoring Thread
def real_time_monitoring():
    """Thread function to simulate force and resistance readings."""
    global is_running, start_time, force_values

    num_contact_points = CONNECTOR_TYPES[current_connector_type]
    start_time = time.time()

    while is_running:
        elapsed_time = time.time() - start_time

        # Simulate new data
        new_force_data = simulate_force_data(num_contact_points)
        new_resistance = simulate_resistance_data()

        # Update data lists
        force_values = new_force_data
        resistance_data.append(new_resistance)
        time_data.append(elapsed_time)

        # Update the force table and graphs
        update_force_table(new_force_data)
        update_resistance_graph()
        update_force_bar_graph()

        time.sleep(1.5)  # Update every 1.5 seconds

# Control Functions
def start_monitoring():
    """Start monitoring if all conditions are met."""
    if not voltage_1_entry.get() or not voltage_2_entry.get():
        status_var.set("Error: Please enter both Voltage 1 and Voltage 2 values.")
        return
    
    try:
        force_value = float(force_entry.get())
        if force_value > MAX_FORCE:
            status_var.set(f"Error: Force value exceeds {MAX_FORCE} N limit.")
            force_entry.delete(0, tk.END)  # Clear the input field
            return
    except ValueError:
        status_var.set("Error: Please enter a valid force value.")
        return
    
    global is_running
    if is_running:
        return
    is_running = True
    status_var.set("Monitoring Started")
    threading.Thread(target=real_time_monitoring, daemon=True).start()

def stop_monitoring():
    """Stop monitoring."""
    global is_running
    is_running = False
    status_var.set("Monitoring Stopped")

def reset_monitoring():
    """Reset all monitoring data."""
    global is_running, force_values, resistance_data, time_data, voltage_1_entry, voltage_2_entry
    is_running = False
    force_values.clear()
    resistance_data.clear()
    time_data.clear()
    voltage_1_entry.delete(0, tk.END)
    voltage_2_entry.delete(0, tk.END)
    avg_voltage_label.config(text="Average Voltage: 0.00 V")
    for lbl in connector_status.values():
        lbl.config(text="Not Measured", background="red")
    resistance_ax.clear()
    force_ax.clear()
    resistance_canvas.draw()
    force_canvas.draw()
    status_var.set("System Reset")

def change_connector_type(selected_type):
    """Change the connector type and reset the system."""
    global current_connector_type
    current_connector_type = selected_type
    reset_monitoring()
    status_var.set(f"Connector Type Changed to {selected_type}")
    initialize_contact_points()

# Initialize Contact Points Display
def initialize_contact_points():
    """Set up the connector table display."""
    for widget in force_frame.winfo_children():
        widget.destroy()
    connector_status.clear()

    num_points = CONNECTOR_TYPES[current_connector_type]
    for i in range(num_points):
        lbl = ttk.Label(force_frame, text=f"CP{i+1} – Not Measured", background="red", foreground="white")
        lbl.grid(row=i // 4, column=i % 4, padx=10, pady=5)
        connector_status[i] = lbl

# Calculate Average Voltage
def calculate_avg_voltage():
    """Calculate and update the average voltage."""
    try:
        voltage_1_value = float(voltage_1_entry.get())
        voltage_2_value = float(voltage_2_entry.get())
        avg_voltage = (voltage_1_value + voltage_2_value) / 2
        avg_voltage_label.config(text=f"Average Voltage: {avg_voltage:.2f} V")
    except ValueError:
        status_var.set("Error: Please enter valid voltage values.")

# Force Value Input Validation
def validate_force_input(force_value):
    """Validate the force input value."""
    try:
        force_value = float(force_value)
        if force_value > MAX_FORCE:
            status_var.set(f"Error: Force value cannot exceed {MAX_FORCE} N.")
            force_entry.delete(0, tk.END)  # Clear the input field
        else:
            force_label.config(text=f"Force Value: {force_value:.2f} N")
            force_values.append(force_value)  # Add the valid force value to the list
            update_force_table(force_values)  # Update the force table
            update_force_bar_graph()  # Update the bar graph
    except ValueError:
        status_var.set("Error: Please enter a valid force value.")

# Voltage Input Fields Change Event
def on_voltage_change(*args):
    """Automatically calculate average voltage when both voltages are entered."""
    if voltage_1_entry.get() and voltage_2_entry.get():
        calculate_avg_voltage()

# GUI Setup
root = tk.Tk()
root.title("Codecrafters Project: Real-Time Monitoring")
root.geometry("1200x800")

# Connector Type Selection
type_frame = ttk.LabelFrame(root, text="Connector Type Selection")
type_frame.pack(pady=5, padx=10, fill="x")
selected_type_var = tk.StringVar(value=current_connector_type)
ttk.Label(type_frame, text="Connector Type:").pack(side="left", padx=10)
ttk.OptionMenu(type_frame, selected_type_var, current_connector_type, *CONNECTOR_TYPES.keys(), command=change_connector_type).pack(side="left")

# Status Display
status_var = tk.StringVar(value="System Ready")
ttk.Label(root, textvariable=status_var, font=("Arial", 12, "bold")).pack(pady=5)

# Force Table
force_frame = ttk.LabelFrame(root, text="Force Table (Contact Points)")
force_frame.pack(pady=10, padx=10, fill="x")
initialize_contact_points()

# Control Buttons
control_frame = ttk.LabelFrame(root, text="Controls")
control_frame.pack(pady=10, padx=10, fill="x")
ttk.Button(control_frame, text="Start", command=start_monitoring).pack(side="left", padx=10)
ttk.Button(control_frame, text="Stop", command=stop_monitoring).pack(side="left", padx=10)
ttk.Button(control_frame, text="Reset", command=reset_monitoring).pack(side="left", padx=10)

# Voltage Input and Calculation
voltage_frame = ttk.LabelFrame(root, text="Voltage Inputs")
voltage_frame.pack(pady=10, padx=10, fill="x")
ttk.Label(voltage_frame, text="Voltage 1:").pack(side="left", padx=10)
voltage_1_entry = ttk.Entry(voltage_frame)
voltage_1_entry.pack(side="left", padx=10)

ttk.Label(voltage_frame, text="Voltage 2:").pack(side="left", padx=10)
voltage_2_entry = ttk.Entry(voltage_frame)
voltage_2_entry.pack(side="left", padx=10)

avg_voltage_label = ttk.Label(voltage_frame, text="Average Voltage: 0.00 V")
avg_voltage_label.pack(side="left", padx=10)

# Force Value Input
force_frame = ttk.LabelFrame(root, text="Force Input")
force_frame.pack(pady=10, padx=10, fill="x")
force_label = ttk.Label(force_frame, text="Force Value: Not Measured", background="red", foreground="white")
force_label.pack(side="left", padx=10)
force_entry = ttk.Entry(force_frame)
force_entry.pack(side="left", padx=10)

# Graph Display Frames
graph_frame = tk.Frame(root)
graph_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Resistance vs Time Graph
resistance_fig = Figure(figsize=(5, 4), dpi=100)
resistance_ax = resistance_fig.add_subplot(111)
resistance_ax.set_title("Resistance vs Time")
resistance_ax.set_xlabel("Time (s)")
resistance_ax.set_ylabel("Resistance (Ohms)")
resistance_canvas = FigureCanvasTkAgg(resistance_fig, master=graph_frame)
resistance_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

# Contact Force Bar Graph
force_fig = Figure(figsize=(5, 4), dpi=100)
force_ax = force_fig.add_subplot(111)
force_ax.set_title("Contact Force Distribution")
force_ax.set_ylabel("Force (N)")
force_canvas = FigureCanvasTkAgg(force_fig, master=graph_frame)
force_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

# Bind voltage input change to update average voltage
voltage_1_entry.bind("<KeyRelease>", on_voltage_change)
voltage_2_entry.bind("<KeyRelease>", on_voltage_change)

# Run the GUI
root.mainloop()
