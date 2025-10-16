def get_cpu_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp_milli = int(f.read().strip())
            return temp_milli / 1000.0
    except Exception as e:
        print(f"Error reading CPU temperature: {e}")
        return None

if __name__ == "__main__":
    cpu_temp = get_cpu_temp()
    print(f"CPU Temperature: {cpu_temp:.1f}C")
