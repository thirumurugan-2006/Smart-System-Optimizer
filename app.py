import streamlit as st
import psutil
import pandas as pd
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="AI System Optimizer", layout="wide")

st.title("💻 AI Smart System Optimizer")

# -------------------------------
# AUTO REFRESH
# -------------------------------
time.sleep(2)
st.rerun()

# -------------------------------
# SYSTEM METRICS
# -------------------------------
cpu = psutil.cpu_percent()
ram = psutil.virtual_memory().percent
disk = psutil.disk_usage('/').percent
processes = len(psutil.pids())

col1, col2, col3, col4 = st.columns(4)

col1.metric("CPU %", cpu)
col2.metric("RAM %", ram)
col3.metric("Disk %", disk)
col4.metric("Processes", processes)

# -------------------------------
# LOG DATA (SAVE HISTORY)
# -------------------------------
log_df = pd.DataFrame([[cpu, ram, disk, processes]],
                      columns=["cpu", "ram", "disk", "processes"])

log_df.to_csv("system_log.csv", mode='a', header=False, index=False)

# -------------------------------
# LIVE GRAPH
# -------------------------------
st.subheader("📊 Live Performance Graph")

try:
    history = pd.read_csv("system_log.csv",
                          names=["cpu", "ram", "disk", "processes"])
    st.line_chart(history.tail(50))
except:
    st.write("No history yet")

# -------------------------------
# ML MODEL
# -------------------------------
data = history.tail(50) if 'history' in locals() else log_df

def label(row):
    if row["cpu"] > 85 or row["ram"] > 85:
        return "Critical"
    elif row["cpu"] > 60 or row["processes"] > 150:
        return "Slow"
    else:
        return "Normal"

data["status"] = data.apply(label, axis=1)

X = data[["cpu", "ram", "disk", "processes"]]
y = data["status"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y_encoded)

# -------------------------------
# PREDICTION
# -------------------------------
sample = [[cpu, ram, disk, processes]]
prediction = model.predict(sample)
status = le.inverse_transform(prediction)[0]

st.subheader("🧠 System Status")

if status == "Critical":
    st.error("🔥 Critical State")
elif status == "Slow":
    st.warning("⚠️ Slow Performance")
else:
    st.success("✅ Normal")

# -------------------------------
# ALERT SYSTEM
# -------------------------------
st.subheader("🚨 Alerts")

if cpu > 85:
    st.error("🔥 High CPU usage!")
if ram > 80:
    st.warning("⚠️ High RAM usage!")
if processes > 200:
    st.warning("⚠️ Too many processes!")
if disk > 80:
    st.warning("💾 Disk almost full!")

# -------------------------------
# SMART SUGGESTIONS
# -------------------------------
st.subheader("💡 Suggestions")

if status == "Critical":
    st.error("Close heavy apps immediately")
elif status == "Slow":
    st.warning("Reduce background apps")
else:
    st.success("System is stable")

# -------------------------------
# PROCESS TABLE
# -------------------------------
st.subheader("📊 Running Processes")

process_list = []

for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    try:
        process_list.append(proc.info)
    except:
        pass

process_df = pd.DataFrame(process_list)
process_df = process_df.sort_values(by="cpu_percent", ascending=False)

st.dataframe(process_df.head(15))

# -------------------------------
# KILL PROCESS
# -------------------------------
st.subheader("💀 Kill Process")

pid = st.number_input("Enter PID", step=1)

if st.button("Kill Process"):
    try:
        process = psutil.Process(int(pid))

        safe = ["System", "Idle", "explorer.exe"]

        if process.name() in safe:
            st.warning("Cannot kill system process!")
        else:
            process.terminate()
            st.success("Process terminated")

    except Exception as e:
        st.error(f"Error: {e}")

# -------------------------------
# FOOTER
# -------------------------------
st.write("🚀 AI Powered System Monitoring Dashboard")