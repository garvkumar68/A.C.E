import serial
import time


def calculate_stationary_threshold(ser, duration=10, delay=0.1):
    """
    Calculate stationary threshold based on gyro readings collected over a specified duration.
    Returns the min and max gyro readings for x, y, and z axes.
    """
    start_time = time.time()
    gx_readings = []
    gy_readings = []
    gz_readings = []

    # Collect gyro readings for the specified duration
    while time.time() - start_time < duration:
        ser.write(b'r')  # Request data from ESP32
        line = ser.readline().decode().strip()  # Read data from ESP32
        data = line.split(',')

        if len(data) == 6:
            try:
                gx, gy, gz = map(int, data[3:])  # Parse gyroscope readings
                gx_readings.append(gx)
                gy_readings.append(gy)
                gz_readings.append(gz)
            except ValueError:
                print("Invalid data received:", data)  # Handle incorrect data
        else:
            print("Incomplete data received:", data)

        time.sleep(delay)  # Add delay to avoid overwhelming the serial connection

    # Calculate min and max gyro readings for x, y, and z axes
    stationary_threshold_min_x = min(gx_readings)
    stationary_threshold_max_x = max(gx_readings)
    stationary_threshold_min_y = min(gy_readings)
    stationary_threshold_max_y = max(gy_readings)
    stationary_threshold_min_z = min(gz_readings)
    stationary_threshold_max_z = max(gz_readings)

    return (stationary_threshold_min_x, stationary_threshold_max_x,
            stationary_threshold_min_y, stationary_threshold_max_y,
            stationary_threshold_min_z, stationary_threshold_max_z)


def main():
    try:
        ser = serial.Serial('COM4', 115200, timeout=1)  # Open serial port with a 1 second timeout
        time.sleep(2)  # Give ESP32 time to reset and start sending data

        # Calculate stationary threshold
        stationary_threshold = calculate_stationary_threshold(ser, duration=10)

        print("Stationary threshold calculated:")
        print(f"Min X: {stationary_threshold[0]}, Max X: {stationary_threshold[1]}")
        print(f"Min Y: {stationary_threshold[2]}, Max Y: {stationary_threshold[3]}")
        print(f"Min Z: {stationary_threshold[4]}, Max Z: {stationary_threshold[5]}")

        while True:
            ser.write(b'r')  # Request new data from ESP32
            line = ser.readline().decode().strip()  # Read new data
            data = line.split(',')

            if len(data) == 6:
                try:
                    gx, gy, gz = map(int, data[3:])  # Parse gyroscope readings
                    # Check if the vehicle is flipped
                    if (gx < stationary_threshold[0] or gx > stationary_threshold[1] or
                            gy < stationary_threshold[2] or gy > stationary_threshold[3] or
                            gz < stationary_threshold[4] or gz > stationary_threshold[5]):
                        print(f"⚠ Vehicle flipped! Gyroscope values - X: {gx}, Y: {gy}, Z: {gz}")
                        # Check for sudden brake application
                        if gz < stationary_threshold[4] - 500:  # Adjust the threshold if needed
                            print("⚠🚨 Accident occurred! Vehicle flipped and sudden brake applied! 🚨⚠")
                    else:
                        print(f"Vehicle is stable. Gyroscope values - X: {gx}, Y: {gy}, Z: {gz}")
                except ValueError:
                    print("Error parsing gyroscope data:", data)
            else:
                print("Incomplete data received:", data)

            time.sleep(0.1)  # Adjust delay for continuous monitoring

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        ser.close()  # Close serial connection on keyboard interrupt
        print("\nSerial connection closed.")


if __name__ == "__main__":
    main()
