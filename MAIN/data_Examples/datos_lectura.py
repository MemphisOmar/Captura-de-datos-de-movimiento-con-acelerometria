import matplotlib.pyplot as plt
import csv

def plot_acceleration_from_csv(filename="sensor_data_wifi.csv"):
    """
    Reads acceleration data from a CSV file and plots it.
    """
    time = []
    acc_x = []
    acc_y = []
    acc_z = []

    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Skip the header row
        for row in reader:
            try:
                t, x, y, z, _, _, _ = row  # Unpack the row, ignore angles
                time.append(float(t))
                acc_x.append(float(x))
                acc_y.append(float(y))
                acc_z.append(float(z))
            except ValueError as e:
                print(f"Error processing row: {row} - {e}")
                continue

    # Create the plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].plot(time, acc_x, label='Acc X')
    axes[0].set_xlabel('Tiempo (s)')
    axes[0].set_ylabel('Aceleración (m/s^2)')
    axes[0].set_title('Aceleración en X')
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(time, acc_y, label='Acc Y', color='orange')
    axes[1].set_xlabel('Tiempo (s)')
    axes[1].set_ylabel('Aceleración (m/s^2)')
    axes[1].set_title('Aceleración en Y')
    axes[1].legend()
    axes[1].grid(True)

    axes[2].plot(time, acc_z, label='Acc Z', color='green')
    axes[2].set_xlabel('Tiempo (s)')
    axes[2].set_ylabel('Aceleración (m/s^2)')
    axes[2].set_title('Aceleración en Z')
    axes[2].legend()
    axes[2].grid(True)

    plt.tight_layout()  # Adjust layout to prevent overlapping plots
    plt.show()

if __name__ == "__main__":
    plot_acceleration_from_csv()
