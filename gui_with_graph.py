import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Global Appearance Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- Algorithms (Logic preserved and extended for trace) ---------------- #
def get_fifo_trace(pages, capacity):
    memory, faults, trace = [], 0, []
    for page in pages:
        is_hit = True
        if page not in memory:
            is_hit = False
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
        trace.append((list(memory), is_hit))
    return faults, trace

def get_lru_trace(pages, capacity):
    memory, faults, trace = [], 0, []
    for page in pages:
        is_hit = True
        if page not in memory:
            is_hit = False
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
        else:
            memory.remove(page)
            memory.append(page)
        trace.append((list(memory), is_hit))
    return faults, trace

def get_lfu_trace(pages, capacity):
    memory, freq, faults, trace = [], {}, 0, []
    for page in pages:
        is_hit = True
        if page not in memory:
            is_hit = False
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                lfu_page = min(memory, key=lambda x: freq.get(x, 0))
                memory.remove(lfu_page)
                memory.append(page)
        else:
            is_hit = True
        freq[page] = freq.get(page, 0) + 1
        trace.append((list(memory), is_hit))
    return faults, trace

def get_optimal_trace(pages, capacity):
    memory, faults, trace = [], 0, []
    for i in range(len(pages)):
        page = pages[i]
        is_hit = True
        if page not in memory:
            is_hit = False
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                future = pages[i+1:]
                index = []
                for m in memory:
                    index.append(future.index(m) if m in future else float('inf'))
                memory[index.index(max(index))] = page
        trace.append((list(memory), is_hit))
    return faults, trace

# ---------------- UI Classes ---------------- #
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced Page Replacement Simulator")
        self.geometry("1280x800")

        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------- Sidebar (Controls) -------- #
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="OS SIMULATOR", 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text="Replacement Algorithms", 
                     font=ctk.CTkFont(size=12)).pack(pady=(0, 30))

        # Inputs
        self.input_group = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.input_group.pack(fill="x", padx=20)

        ctk.CTkLabel(self.input_group, text="Reference String:", anchor="w").pack(fill="x")
        self.entry_pages = ctk.CTkEntry(self.input_group, placeholder_text="e.g. 7 0 1 2 0 3")
        self.entry_pages.insert(0, "7 0 1 2 0 3 0 4 2 3 0 3 2")
        self.entry_pages.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(self.input_group, text="Frame Capacity:", anchor="w").pack(fill="x")
        self.entry_frames = ctk.CTkEntry(self.input_group, placeholder_text="e.g. 3")
        self.entry_frames.insert(0, "3")
        self.entry_frames.pack(fill="x", pady=(5, 20))

        # Action Buttons
        self.btn_calc = ctk.CTkButton(self.sidebar, text="⚡ Run Simulation", 
                                      command=self.calculate, height=45, 
                                      font=ctk.CTkFont(weight="bold"))
        self.btn_calc.pack(padx=20, pady=10, fill="x")

        self.btn_reset = ctk.CTkButton(self.sidebar, text="🔄 Reset All", 
                                       command=self.reset, fg_color="transparent", 
                                       border_width=1)
        self.btn_reset.pack(padx=20, pady=5, fill="x")

        self.theme_switch = ctk.CTkSwitch(self.sidebar, text="Dark Mode", command=self.toggle_theme)
        self.theme_switch.select()
        self.theme_switch.pack(side="bottom", pady=30)

        # -------- Main Content -------- #
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Top Header / Summary Cards
        self.summary_frame = ctk.CTkFrame(self.main_container, height=100)
        self.summary_frame.pack(fill="x", pady=(0, 20))
        
        self.summary_label = ctk.CTkLabel(self.summary_frame, text="Run simulation to see overall efficiency", 
                                          font=ctk.CTkFont(size=16))
        self.summary_label.pack(expand=True)

        # Tabbed View
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(expand=True, fill="both")

        self.tab_chart = self.tabview.add("📊 Analytics Chart")
        self.tab_comparison = self.tabview.add("📋 Comparative Table")
        self.tab_trace = self.tabview.add("🔍 Live Execution Trace")

        # --- Table UI ---
        self.table_box = ctk.CTkTextbox(self.tab_comparison, font=("Consolas", 15))
        self.table_box.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Trace UI ---
        self.trace_container = ctk.CTkScrollableFrame(self.tab_trace)
        self.trace_container.pack(expand=True, fill="both", padx=10, pady=10)

        self.canvas = None

    def calculate(self):
        try:
            pages = list(map(int, self.entry_pages.get().split()))
            capacity = int(self.entry_frames.get())
            if capacity <= 0: raise ValueError
            
            total = len(pages)

            # Get data and traces
            fifo_f, fifo_t = get_fifo_trace(pages, capacity)
            lru_f, lru_t = get_lru_trace(pages, capacity)
            lfu_f, lfu_t = get_lfu_trace(pages, capacity)
            opt_f, opt_t = get_optimal_trace(pages, capacity)

            results = {
                "FIFO": fifo_f,
                "LRU": lru_f,
                "LFU": lfu_f,
                "Optimal": opt_f
            }

            traces = {
                "FIFO": fifo_t,
                "LRU": lru_t,
                "LFU": lfu_t,
                "Optimal": opt_t
            }

            best_algo = min(results, key=results.get)
            self.summary_label.configure(text=f"Simulation Complete! Most Efficient Algorithm: {best_algo} ({results[best_algo]} Faults)")

            self.update_table(results, total, best_algo)
            self.update_graph(results)
            self.update_trace(pages, traces)

        except:
            messagebox.showerror("Input Error", "Please provide a valid numeric string and frame capacity.")

    def update_table(self, results, total, best):
        self.table_box.delete("1.0", "end")
        header = f"{'ALGORITHM':<15} {'FAULTS':<10} {'HITS':<10} {'HIT RATIO':<10}\n"
        sep = "-" * 50 + "\n"
        self.table_box.insert("end", header + sep)

        for name, faults in results.items():
            hits = total - faults
            ratio = (hits / total) * 100
            winner_tag = " [WINNER]" if name == best else ""
            line = f"{name:<15} {faults:<10} {hits:<10} {ratio:>8.1f}% {winner_tag}\n"
            self.table_box.insert("end", line)

    def update_graph(self, results):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(7, 5))
        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = '#2b2b2b' if is_dark else '#dbdbdb'
        text_color = 'white' if is_dark else 'black'

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

        algos = list(results.keys())
        faults = list(results.values())
        
        bars = ax.bar(algos, faults, color=['#3b82f6', '#8b5cf6', '#ec4899', '#10b981'], 
                      edgecolor=text_color, linewidth=1, width=0.6)

        ax.set_title("Comparative Performance (Page Faults)", color=text_color, pad=20, fontsize=14, weight='bold')
        ax.set_ylabel("Total Faults", color=text_color)
        ax.tick_params(colors=text_color)
        
        # Grid
        ax.yaxis.grid(True, linestyle='--', alpha=0.3, color=text_color)
        ax.set_axisbelow(True)

        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', color=text_color, weight='bold')

        self.canvas = FigureCanvasTkAgg(fig, master=self.tab_chart)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill="both")
        plt.close(fig)

    def update_trace(self, pages, all_traces):
        # Clear trace frame
        for widget in self.trace_container.winfo_children():
            widget.destroy()

        # Build execution trace for each algorithm
        for algo_name, trace_data in all_traces.items():
            algo_lbl = ctk.CTkLabel(self.trace_container, text=f"Algorithm: {algo_name}", 
                                    font=ctk.CTkFont(size=16, weight="bold"), text_color="#3b82f6")
            algo_lbl.pack(pady=(15, 5), anchor="w")

            scroll_x = ctk.CTkScrollableFrame(self.trace_container, orientation="horizontal", height=120)
            scroll_x.pack(fill="x", pady=5)

            # Display each step
            for i, (mem_state, is_hit) in enumerate(trace_data):
                step_frame = ctk.CTkFrame(scroll_x, width=60, 
                                          fg_color="#065f46" if is_hit else "#991b1b")
                step_frame.pack(side="left", padx=2, pady=5)
                
                ctk.CTkLabel(step_frame, text=f"P: {pages[i]}", font=ctk.CTkFont(weight="bold")).pack()
                
                # Show memory slots
                mem_str = "\n".join([str(x) for x in mem_state])
                ctk.CTkLabel(step_frame, text=mem_str, font=("Consolas", 11)).pack(pady=2)
                
                status_txt = "HIT" if is_hit else "MISS"
                ctk.CTkLabel(step_frame, text=status_txt, font=ctk.CTkFont(size=9)).pack()

    def reset(self):
        self.entry_pages.delete(0, 'end')
        self.entry_frames.delete(0, 'end')
        self.table_box.delete("1.0", "end")
        self.summary_label.configure(text="Run simulation to see overall efficiency")
        for widget in self.trace_container.winfo_children():
            widget.destroy()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        # Refresh graph colors if results exist
        try:
            pages = list(map(int, self.entry_pages.get().split()))
            self.calculate()
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()