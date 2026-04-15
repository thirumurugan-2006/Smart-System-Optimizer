import psutil
import pandas as pd
import time
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

print("📊 Collecting system data...\n")

data = []

# -------------------------------
# STEP 1: DATA COLLECTION (SAFE)
# -------------------------------
try:
    for i in range(60):   # change to 10 for quick testing
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        processes = len(psutil.pids())

        print(f"[{i+1}] CPU: {cpu}% | RAM: {ram}% | Disk: {disk}% | Processes: {processes}")

        data.append([cpu, ram, disk, processes])
        time.sleep(1)

except KeyboardInterrupt:
    print("\n⚠️ Data collection stopped by user")

# Create DataFrame
df = pd.DataFrame(data, columns=["cpu", "ram", "disk", "processes"])

if df.empty:
    print("❌ No data collected. Exiting...")
    exit()

# -------------------------------
# STEP 2: LABELING
# -------------------------------
def label(row):
    if row["cpu"] > 85 or row["ram"] > 85:
        return "Critical"
    elif row["cpu"] > 60 or row["processes"] > 150:
        return "Slow"
    else:
        return "Normal"

df["status"] = df.apply(label, axis=1)

df.to_csv("system_data.csv", index=False)
print("\n✅ Data saved\n")

# -------------------------------
# STEP 3: VISUALIZATION
# -------------------------------
df["time"] = range(len(df))

plt.figure()
plt.plot(df["time"], df["cpu"])
plt.title("CPU Usage Over Time")
plt.xlabel("Time")
plt.ylabel("CPU %")
plt.show()

plt.figure()
plt.plot(df["time"], df["ram"])
plt.title("RAM Usage Over Time")
plt.xlabel("Time")
plt.ylabel("RAM %")
plt.show()

# -------------------------------
# STEP 4: MACHINE LEARNING
# -------------------------------
X = df[["cpu", "ram", "disk", "processes"]]
y = df["status"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2)

model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"\n🤖 Model Accuracy: {accuracy:.2f}")

# -------------------------------
# STEP 5: FEATURE IMPORTANCE
# -------------------------------
print("\n📊 Feature Importance:")
features = ["cpu", "ram", "disk", "processes"]
for f, imp in zip(features, model.feature_importances_):
    print(f"{f}: {imp:.2f}")

# -------------------------------
# STEP 6: USER INPUT
# -------------------------------
print("\n🔍 Enter system values:")

cpu_input = float(input("CPU (%): "))
ram_input = float(input("RAM (%): "))
disk_input = float(input("Disk (%): "))
proc_input = float(input("Processes: "))

sample = [[cpu_input, ram_input, disk_input, proc_input]]

prediction = model.predict(sample)
status = le.inverse_transform(prediction)[0]

print(f"\n🧠 Predicted Status: {status}")

# -------------------------------
# STEP 7: SMART SUGGESTIONS
# -------------------------------
print("\n💡 Suggestions:")

if status == "Critical":
    print("🔥 System overload detected!")
    print("👉 Close heavy apps immediately")
elif status == "Slow":
    print("⚠️ System slowing down")
    print("👉 Reduce background apps")
else:
    print("✅ System running smoothly")

if cpu_input > 85:
    print("🔥 High CPU usage")
if ram_input > 80:
    print("⚠️ High RAM usage")
if proc_input > 150:
    print("⚠️ Too many processes")
if disk_input > 80:
    print("💾 Disk almost full")

# -------------------------------
# STEP 8: PROCESS TABLE
# -------------------------------
print("\n📊 Fetching processes...\n")

process_list = []

for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
    try:
        process_list.append(proc.info)
    except:
        pass

process_df = pd.DataFrame(process_list)

# Sort by CPU
process_df = process_df.sort_values(by="cpu_percent", ascending=False)

print("🔥 Top Processes:\n")
print(process_df.head(10))

# -------------------------------
# STEP 9: HEAVY PROCESS FILTER
# -------------------------------
heavy_df = process_df[process_df["cpu_percent"] > 5]

print("\n⚠️ Heavy Processes:\n")
print(heavy_df.head(10))

# -------------------------------
# STEP 10: SAFE PROCESS KILL
# -------------------------------
choice = input("\nKill any process? (yes/no): ")

if choice.lower() == "yes":
    try:
        pid = int(input("Enter PID: "))
        process = psutil.Process(pid)

        safe_list = ["System", "Idle", "System Idle Process", "explorer.exe"]

        if process.name() in safe_list:
            print("⚠️ Cannot terminate system process!")
        else:
            process.terminate()
            print("✅ Process terminated")

    except Exception as e:
        print("❌ Error:", e)

print("\n✅ Program Completed Successfully!")