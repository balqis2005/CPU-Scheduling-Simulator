import customtkinter as ctk
from tkinter import messagebox

#Algorithms

def calculate_fcfs(processes, arrival_times, burst_times):
    n = len(processes)
    completion_times, turnaround_times, waiting_times, response_times = [0]*n, [0]*n, [0]*n, [0]*n
    gantt_data, current_time = [], 0
    for i in range(n):
        if current_time < arrival_times[i]: current_time = arrival_times[i]
        start_time = current_time
        response_times[i] = current_time - arrival_times[i]
        current_time += burst_times[i]
        completion_times[i] = current_time
        turnaround_times[i] = completion_times[i] - arrival_times[i]
        waiting_times[i] = turnaround_times[i] - burst_times[i]
        gantt_data.append((processes[i], start_time, current_time))
    return processes, turnaround_times, waiting_times, response_times, gantt_data

def calculate_sjf(processes, arrival_times, burst_times):
    n = len(processes)
    completion_times, is_completed, response_times = [0]*n, [False]*n, [0]*n
    gantt_data, current_time, completed_count = [], 0, 0
    while completed_count < n:
        idx, min_burst = -1, float('inf')
        for i in range(n):
            if arrival_times[i] <= current_time and not is_completed[i]:
                if burst_times[i] < min_burst: min_burst, idx = burst_times[i], i
        if idx == -1: current_time += 1
        else:
            start_time = current_time
            response_times[idx] = current_time - arrival_times[idx]
            current_time += burst_times[idx]
            completion_times[idx] = current_time
            is_completed[idx] = True
            completed_count += 1
            gantt_data.append((processes[idx], start_time, current_time))
    tat = [completion_times[i] - arrival_times[i] for i in range(n)]
    wt = [tat[i] - burst_times[i] for i in range(n)]
    return processes, tat, wt, response_times, gantt_data

def calculate_srtf(processes, arrival_times, burst_times):
    n = len(processes)
    rem_bt, completion_times, response_times = list(burst_times), [0]*n, [-1]*n
    gantt_data, current_time, completed = [], 0, 0
    while completed < n:
        idx, min_rem = -1, float('inf')
        for i in range(n):
            if arrival_times[i] <= current_time and rem_bt[i] > 0:
                if rem_bt[i] < min_rem: min_rem, idx = rem_bt[i], i
        if idx == -1: current_time += 1
        else:
            if response_times[idx] == -1: response_times[idx] = current_time - arrival_times[idx]
            if not gantt_data or gantt_data[-1][0] != processes[idx]: 
                gantt_data.append([processes[idx], current_time, current_time + 1])
            else: gantt_data[-1][2] += 1
            rem_bt[idx] -= 1
            current_time += 1
            if rem_bt[idx] == 0: completion_times[idx] = current_time; completed += 1
    tat = [completion_times[i] - arrival_times[i] for i in range(n)]
    wt = [tat[i] - burst_times[i] for i in range(n)]
    return processes, tat, wt, response_times, gantt_data

def calculate_rr(processes, arrival_times, burst_times, q):
    n = len(processes)
    rem_bt, completion_times, response_times = list(burst_times), [0]*n, [-1]*n
    gantt_data, current_time, queue, visited = [], 0, [], [False] * n
    for i in range(n):
        if arrival_times[i] <= current_time: queue.append(i); visited[i] = True
    while queue:
        idx = queue.pop(0)
        if response_times[idx] == -1: response_times[idx] = current_time - arrival_times[idx]
        exec_time = min(rem_bt[idx], q)
        start_time = current_time
        current_time += exec_time
        rem_bt[idx] -= exec_time
        gantt_data.append((processes[idx], start_time, current_time))
        for i in range(n):
            if arrival_times[i] <= current_time and not visited[i]: queue.append(i); visited[i] = True
        if rem_bt[idx] > 0: queue.append(idx)
        else: completion_times[idx] = current_time
    tat = [completion_times[i] - arrival_times[i] for i in range(n)]
    wt = [tat[i] - burst_times[i] for i in range(n)]
    return processes, tat, wt, response_times, gantt_data

#GUI
class CpuSimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Simulator")
        self.geometry("1450x920")
        self.configure(fg_color="#0b0f19")
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        self.footer = None
        self.show_home()

    def clear_ui(self):
        for w in self.container.winfo_children(): w.destroy()
        if self.footer:
            self.footer.destroy()
            self.footer = None

    def show_home(self):
        self.clear_ui()
        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(content, text="CPU Scheduling Simulator", font=("Times New Roman", 80, "bold"), text_color="#2ecc71").pack()
        desc_text = (
            "A high-performance CPU Scheduling Simulator designed for engineers.\n\n"
            "• Visualize FCFS, SJF, SRTF, and RR algorithms.\n"
            "• Real-time Gantt Chart generation.\n"
            "• Precise performance metrics (Waiting, Turnaround, Response times)."
        )
        ctk.CTkLabel(content, text=desc_text, font=("Cairo", 18), text_color="#bdc3c7", justify="center").pack(pady=30)
        
        ctk.CTkButton(content, text="LAUNCH SIMULATOR", fg_color="#2ecc71", text_color="black", 
                     font=("Orbitron", 18, "bold"), height=60, width=320, corner_radius=30, 
                     command=self.show_menu).pack(pady=20)

    def show_menu(self):
        self.clear_ui()
        ctk.CTkLabel(self.container, text="Select Algorithm", font=("Orbitron", 45, "bold"), text_color="white").pack(pady=(60, 40))
        
        grid = ctk.CTkFrame(self.container, fg_color="transparent")
        grid.pack(expand=True, padx=20)
        
        algos = [
            ("FCFS", "➡", "First Come First Served.\nLinear and non-preemptive logic."),
            ("SJF", "📊", "Shortest Job First.\nOptimized for throughput."),
            ("SRTF", "⏱", "Shortest Remaining Time.\nPreemptive version of SJF."),
            ("RR", "🔄", "Round Robin.\nFair distribution using Time Quantum.")
        ]
        
        for i, (name, icon, desc) in enumerate(algos):
            card = ctk.CTkFrame(grid, width=320, height=450, fg_color="#161b22", corner_radius=25, border_width=1, border_color="#30363d")
            card.grid(row=0, column=i, padx=20, pady=20)
            card.grid_propagate(False)
            
            ctk.CTkLabel(card, text=icon, font=("Arial", 65)).pack(pady=(45, 15))
            ctk.CTkLabel(card, text=name, font=("Orbitron", 30, "bold"), text_color="#2ecc71").pack()
            ctk.CTkLabel(card, text=desc, font=("Cairo", 15), text_color="#8b949e", justify="center", wraplength=270).pack(pady=25, padx=20)
            
            ctk.CTkButton(card, text=f"SELECT {name}", fg_color="#2ecc71", text_color="black", 
                         font=("Orbitron", 14, "bold"), height=55, width=220, corner_radius=15,
                         command=lambda n=name: self.show_workspace(n)).pack(side="bottom", pady=35)

    def show_workspace(self, algo):
        self.clear_ui()
        side = ctk.CTkFrame(self.container, width=320, fg_color="#0d1117")
        side.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(side, text=algo, font=("Orbitron", 24, "bold"), text_color="#2ecc71").pack(pady=30)
        
        bt_in = self.create_input(side, "Burst Times (e.g. 10,5,8):", "10,5,8")
        at_in = self.create_input(side, "Arrival Times (e.g. 0,1,2):", "0,1,2")
        q_in = self.create_input(side, "Time Quantum:", "2") if algo == "RR" else None

        disp = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        disp.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.footer = ctk.CTkFrame(self, height=120, fg_color="#161b22", corner_radius=20, border_width=2, border_color="#2ecc71")
        self.footer.pack(side="bottom", fill="x", padx=40, pady=(0, 25))

        def run():
            try:
                for w in disp.winfo_children(): w.destroy()
                for w in self.footer.winfo_children(): w.destroy()
                
                b = [int(x.strip()) for x in bt_in.get().split(',')]
                a = [int(x.strip()) for x in at_in.get().split(',')]
                procs = [f"P{i+1}" for i in range(len(b))]

                if algo == "FCFS": p, tat, wt, rt, gantt = calculate_fcfs(procs, a, b)
                elif algo == "SJF": p, tat, wt, rt, gantt = calculate_sjf(procs, a, b)
                elif algo == "SRTF": p, tat, wt, rt, gantt = calculate_srtf(procs, a, b)
                elif algo == "RR":
                    q = int(q_in.get())
                    p, tat, wt, rt, gantt = calculate_rr(procs, a, b, q)

                self.draw_results(disp, p, b, wt, tat, gantt)

                for label, val in [("AVG WAITING", sum(wt)/len(wt)), ("AVG TAT", sum(tat)/len(tat)), ("AVG RESPONSE", sum(rt)/len(rt))]:
                    m_f = ctk.CTkFrame(self.footer, fg_color="transparent")
                    m_f.pack(side="left", expand=True)
                    ctk.CTkLabel(m_f, text=label, font=("Orbitron", 11), text_color="#8b949e").pack()
                    ctk.CTkLabel(m_f, text=f"{val:.2f}ms", font=("Orbitron", 22, "bold"), text_color="#2ecc71").pack()
            except Exception as e: messagebox.showerror("Execution Error", f"Invalid Data: {e}")

        ctk.CTkButton(side, text="RUN SIMULATION", fg_color="#2ecc71", text_color="black", height=55, 
                     font=("Orbitron", 14, "bold"), corner_radius=15, command=run).pack(pady=35, padx=25, fill="x")
        ctk.CTkButton(side, text="← BACK TO MENU", fg_color="transparent", font=("Orbitron", 11), 
                     command=self.show_menu).pack(side="bottom", pady=25)

    def create_input(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Cairo", 14), text_color="#8b949e").pack(anchor="w", padx=30)
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, fg_color="#0b0f19", border_color="#30363d", height=45)
        entry.pack(pady=8, padx=25, fill="x")
        return entry

    def draw_results(self, disp, p, bts, wt, tat, gantt):
        tab = ctk.CTkFrame(disp, fg_color="#161b22", border_width=1, border_color="#30363d")
        tab.pack(fill="x", padx=15, pady=15)
        for j, h in enumerate(["PROCESS", "BURST", "WAITING", "TAT"]):
            ctk.CTkLabel(tab, text=h, font=("Orbitron", 12, "bold"), text_color="#2ecc71").grid(row=0, column=j, padx=45, pady=15)
        for i in range(len(p)):
            for j, v in enumerate([p[i], bts[i], wt[i], tat[i]]):
                ctk.CTkLabel(tab, text=str(v), font=("Cairo", 15)).grid(row=i+1, column=j, pady=10)
        
        ctk.CTkLabel(disp, text="GANTT CHART", font=("Orbitron", 22, "bold"), text_color="#2ecc71").pack(pady=(35, 15))
        g_s = ctk.CTkScrollableFrame(disp, orientation="horizontal", height=120, fg_color="transparent")
        g_s.pack(fill="x", padx=15)
        g_f = ctk.CTkFrame(g_s, fg_color="transparent"); g_f.pack()
        colors = ["#2ecc71", "#3498db", "#e67e22", "#9b59b6", "#e74c3c"]
        for i, (pid, s, e) in enumerate(gantt):
            box = ctk.CTkFrame(g_f, width=max((e-s)*55, 75), height=65, fg_color=colors[i%len(colors)], corner_radius=10)
            box.pack(side="left", padx=3)
            ctk.CTkLabel(box, text=f"{pid}\n{s}-{e}", text_color="black", font=("bold", 13)).place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    app = CpuSimulatorApp(); app.mainloop()