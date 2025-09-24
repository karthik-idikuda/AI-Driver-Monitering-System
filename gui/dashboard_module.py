"""
Dashboard Module for Driver Monitoring System
Provides visualization of detection results and system performance
"""

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import logging
import json
import os

logger = logging.getLogger(__name__)

class DashboardModule:
    def __init__(self, root, monitoring_system):
        self.root = root
        self.monitoring_system = monitoring_system
        
        # Create a new window for the dashboard
        self.window = tk.Toplevel(self.root)
        self.window.title("Driver Monitoring Dashboard")
        self.window.geometry("1200x800")
        self.window.protocol("WM_DELETE_WINDOW", self.close_dashboard)
        
        # Data
        self.alert_history = {
            'drowsiness': [],
            'distraction': [],
            'no_seatbelt': [],
            'inattention': [],
            'hands_off_wheel': [],
            'unauthorized_driver': [],
            'stress_detected': []
        }
        self.fps_history = []
        self.attention_history = []
        
        # Dashboard setup
        self.setup_dashboard()
        
        # Start data collection
        self.running = True
        self.collection_thread = threading.Thread(target=self.collect_data)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        
        # Data save timer
        self.last_save_time = time.time()
        self.save_interval = 300  # Save every 5 minutes
        
    def setup_dashboard(self):
        """Setup the dashboard UI"""
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.window)
        
        # Create tabs
        self.real_time_tab = ttk.Frame(self.notebook)
        self.performance_tab = ttk.Frame(self.notebook)
        self.statistics_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.real_time_tab, text="Real-time Monitoring")
        self.notebook.add(self.performance_tab, text="Performance")
        self.notebook.add(self.statistics_tab, text="Statistics")
        self.notebook.add(self.history_tab, text="History")
        
        self.notebook.pack(expand=1, fill="both")
        
        # Setup each tab
        self.setup_realtime_tab()
        self.setup_performance_tab()
        self.setup_statistics_tab()
        self.setup_history_tab()
    
    def setup_realtime_tab(self):
        """Setup real-time monitoring tab"""
        frame = self.real_time_tab
        
        # Title
        title = tk.Label(frame, text="Real-time Driver Monitoring", font=("Arial", 16))
        title.pack(pady=10)
        
        # Alert status indicators
        alert_frame = ttk.LabelFrame(frame, text="Current Alerts")
        alert_frame.pack(fill="x", padx=20, pady=10)
        
        self.alert_indicators = {}
        alert_types = [
            ("drowsiness", "Drowsiness"),
            ("distraction", "Distraction"),
            ("no_seatbelt", "Seatbelt"),
            ("inattention", "Attention"),
            ("hands_off_wheel", "Hand Position"),
            ("unauthorized_driver", "Driver ID"),
            ("stress_detected", "Stress")
        ]
        
        for i, (alert_id, alert_name) in enumerate(alert_types):
            indicator = tk.Canvas(alert_frame, width=20, height=20)
            indicator.create_oval(2, 2, 18, 18, fill="green", tags="status")
            
            label = tk.Label(alert_frame, text=alert_name)
            
            indicator.grid(row=i//3, column=(i%3)*2, padx=5, pady=5)
            label.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5, sticky="w")
            
            self.alert_indicators[alert_id] = indicator
        
        # Current stats
        stats_frame = ttk.LabelFrame(frame, text="System Status")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # FPS Display
        fps_frame = tk.Frame(stats_frame)
        fps_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(fps_frame, text="FPS:").pack(side="left")
        self.fps_label = tk.Label(fps_frame, text="0")
        self.fps_label.pack(side="left", padx=5)
        
        # Uptime Display
        uptime_frame = tk.Frame(stats_frame)
        uptime_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(uptime_frame, text="Uptime:").pack(side="left")
        self.uptime_label = tk.Label(uptime_frame, text="00:00:00")
        self.uptime_label.pack(side="left", padx=5)
        
        # Driver Info Display
        driver_frame = ttk.LabelFrame(frame, text="Driver Information")
        driver_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(driver_frame, text="Current Driver:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.driver_label = tk.Label(driver_frame, text="Unknown")
        self.driver_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(driver_frame, text="Authorization:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.auth_label = tk.Label(driver_frame, text="Unknown")
        self.auth_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Create matplotlib figure for real-time attention plot
        self.rt_figure = Figure(figsize=(8, 3), dpi=100)
        self.rt_plot = self.rt_figure.add_subplot(111)
        self.rt_plot.set_title("Driver Attention Level")
        self.rt_plot.set_ylim(0, 1)
        self.rt_plot.set_xlabel("Time (s)")
        self.rt_plot.set_ylabel("Attention Score")
        
        self.rt_canvas = FigureCanvasTkAgg(self.rt_figure, frame)
        self.rt_canvas.draw()
        self.rt_canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
    
    def setup_performance_tab(self):
        """Setup performance tab"""
        frame = self.performance_tab
        
        # Title
        title = tk.Label(frame, text="System Performance", font=("Arial", 16))
        title.pack(pady=10)
        
        # Performance metrics frame
        metrics_frame = ttk.LabelFrame(frame, text="Performance Metrics")
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # FPS History plot
        self.perf_figure = Figure(figsize=(8, 3), dpi=100)
        self.perf_plot = self.perf_figure.add_subplot(111)
        self.perf_plot.set_title("FPS History")
        self.perf_plot.set_xlabel("Time (s)")
        self.perf_plot.set_ylabel("FPS")
        
        self.perf_canvas = FigureCanvasTkAgg(self.perf_figure, metrics_frame)
        self.perf_canvas.draw()
        self.perf_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Processing time frame
        proc_frame = ttk.LabelFrame(frame, text="Detector Processing Times (ms)")
        proc_frame.pack(fill="x", padx=20, pady=10)
        
        # Create labels for each detector's processing time
        self.proc_time_labels = {}
        detectors = [
            ("drowsiness", "Drowsiness"),
            ("distraction", "Distraction"),
            ("seatbelt", "Seatbelt"),
            ("facial_recognition", "Face Recognition"),
            ("emotion", "Emotion"),
            ("hand_position", "Hand Position"),
            ("attention", "Attention")
        ]
        
        for i, (detector_id, detector_name) in enumerate(detectors):
            tk.Label(proc_frame, text=f"{detector_name}:").grid(row=i//3, column=(i%3)*2, padx=5, pady=5, sticky="w")
            label = tk.Label(proc_frame, text="0 ms")
            label.grid(row=i//3, column=(i%3)*2+1, padx=5, pady=5, sticky="w")
            self.proc_time_labels[detector_id] = label
        
        # System resources frame
        res_frame = ttk.LabelFrame(frame, text="System Resources")
        res_frame.pack(fill="x", padx=20, pady=10)
        
        # CPU and memory usage
        tk.Label(res_frame, text="CPU Usage:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.cpu_label = tk.Label(res_frame, text="0%")
        self.cpu_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(res_frame, text="Memory Usage:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.mem_label = tk.Label(res_frame, text="0 MB")
        self.mem_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Optimization settings frame
        opt_frame = ttk.LabelFrame(frame, text="Optimization Settings")
        opt_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(opt_frame, text="Resolution Scale:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.res_scale_label = tk.Label(opt_frame, text="1.0x")
        self.res_scale_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(opt_frame, text="Frame Skip:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.frame_skip_label = tk.Label(opt_frame, text="Disabled")
        self.frame_skip_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    
    def setup_statistics_tab(self):
        """Setup statistics tab"""
        frame = self.statistics_tab
        
        # Title
        title = tk.Label(frame, text="Detection Statistics", font=("Arial", 16))
        title.pack(pady=10)
        
        # Alert statistics plot
        self.stats_figure = Figure(figsize=(8, 4), dpi=100)
        self.stats_plot = self.stats_figure.add_subplot(111)
        self.stats_plot.set_title("Alert Frequency")
        self.stats_plot.set_ylabel("Count")
        
        self.stats_canvas = FigureCanvasTkAgg(self.stats_figure, frame)
        self.stats_canvas.draw()
        self.stats_canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
        
        # Session statistics frame
        session_frame = ttk.LabelFrame(frame, text="Session Statistics")
        session_frame.pack(fill="x", padx=20, pady=10)
        
        # Create session stats labels
        stats_grid = tk.Frame(session_frame)
        stats_grid.pack(fill="x", padx=10, pady=10)
        
        tk.Label(stats_grid, text="Total Alerts:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.total_alerts_label = tk.Label(stats_grid, text="0")
        self.total_alerts_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(stats_grid, text="Alert Rate:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.alert_rate_label = tk.Label(stats_grid, text="0 per minute")
        self.alert_rate_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(stats_grid, text="Most Common Alert:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.common_alert_label = tk.Label(stats_grid, text="None")
        self.common_alert_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    
    def setup_history_tab(self):
        """Setup history tab"""
        frame = self.history_tab
        
        # Title
        title = tk.Label(frame, text="Historical Data", font=("Arial", 16))
        title.pack(pady=10)
        
        # Controls for history data
        control_frame = tk.Frame(frame)
        control_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(control_frame, text="Time Range:").pack(side="left", padx=5)
        self.time_range = tk.StringVar(value="1 Hour")
        time_combo = ttk.Combobox(control_frame, textvariable=self.time_range, 
                                 values=["15 Minutes", "1 Hour", "6 Hours", "24 Hours", "7 Days"])
        time_combo.pack(side="left", padx=5)
        time_combo.bind("<<ComboboxSelected>>", self.update_history_plots)
        
        refresh_btn = ttk.Button(control_frame, text="Refresh", command=self.update_history_plots)
        refresh_btn.pack(side="left", padx=10)
        
        export_btn = ttk.Button(control_frame, text="Export Data", command=self.export_history_data)
        export_btn.pack(side="right", padx=10)
        
        # History plots
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create figure with two subplots
        self.history_figure = Figure(figsize=(8, 6), dpi=100)
        
        # Alert history plot
        self.alert_history_plot = self.history_figure.add_subplot(211)
        self.alert_history_plot.set_title("Alert History")
        self.alert_history_plot.set_ylabel("Count")
        
        # Attention history plot
        self.attention_history_plot = self.history_figure.add_subplot(212)
        self.attention_history_plot.set_title("Attention Level History")
        self.attention_history_plot.set_xlabel("Time")
        self.attention_history_plot.set_ylabel("Attention Score")
        
        self.history_canvas = FigureCanvasTkAgg(self.history_figure, plot_frame)
        self.history_canvas.draw()
        self.history_canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def collect_data(self):
        """Collect data from monitoring system"""
        while self.running:
            if not self.monitoring_system.is_running:
                time.sleep(1)
                continue
                
            # Get current detection results
            results = self.monitoring_system.detection_results
            active_alerts = results.get('active_alerts', [])
            
            # Update alert history
            timestamp = time.time()
            for alert_type in self.alert_history:
                if alert_type in active_alerts:
                    self.alert_history[alert_type].append((timestamp, 1))
                else:
                    self.alert_history[alert_type].append((timestamp, 0))
                
                # Keep only recent history (10 minutes)
                cutoff = timestamp - 600
                self.alert_history[alert_type] = [x for x in self.alert_history[alert_type] if x[0] > cutoff]
            
            # Get attention score if available
            if 'attention' in results:
                attention_score = results['attention'].get('score', 0.5)
                self.attention_history.append((timestamp, attention_score))
                
                # Keep only recent history
                self.attention_history = [x for x in self.attention_history if x[0] > cutoff]
            
            # Get system stats
            stats = self.monitoring_system.get_system_stats()
            self.fps_history.append((timestamp, stats['fps']))
            
            # Keep only recent FPS history
            self.fps_history = [x for x in self.fps_history if x[0] > cutoff]
            
            # Update dashboard UI
            self.update_dashboard_ui(results, stats)
            
            # Periodically save data
            current_time = time.time()
            if current_time - self.last_save_time > self.save_interval:
                self.save_history_data()
                self.last_save_time = current_time
            
            time.sleep(0.5)  # Update twice per second
    
    def update_dashboard_ui(self, results, stats):
        """Update dashboard UI with current data"""
        try:
            # Update alert indicators
            active_alerts = results.get('active_alerts', [])
            for alert_id, indicator in self.alert_indicators.items():
                if alert_id in active_alerts:
                    indicator.itemconfig("status", fill="red")
                else:
                    indicator.itemconfig("status", fill="green")
            
            # Update system status
            self.fps_label.config(text=f"{stats['fps']:.1f}")
            
            # Calculate uptime
            uptime = stats['uptime']
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Update driver info if facial recognition results are available
            if 'facial_recognition' in results:
                driver_name = results['facial_recognition'].get('driver_name', "Unknown")
                is_authorized = results['facial_recognition'].get('is_authorized', False)
                
                self.driver_label.config(text=driver_name)
                self.auth_label.config(text="Authorized" if is_authorized else "Unauthorized")
                
                if is_authorized:
                    self.auth_label.config(foreground="green")
                else:
                    self.auth_label.config(foreground="red")
            
            # Update real-time attention plot
            if self.attention_history:
                times = [(t - self.attention_history[0][0]) for t, _ in self.attention_history]
                values = [v for _, v in self.attention_history]
                
                self.rt_plot.clear()
                self.rt_plot.set_title("Driver Attention Level")
                self.rt_plot.set_ylim(0, 1)
                self.rt_plot.set_xlabel("Time (s)")
                self.rt_plot.set_ylabel("Attention Score")
                self.rt_plot.plot(times, values, 'b-')
                self.rt_canvas.draw()
            
            # Update performance tab
            if 'performance' in stats:
                perf_data = stats['performance']
                
                # Update processing time labels
                if 'avg_processing_times' in perf_data:
                    proc_times = perf_data['avg_processing_times']
                    for detector, label in self.proc_time_labels.items():
                        if detector in proc_times:
                            label.config(text=f"{proc_times[detector]*1000:.1f} ms")
                
                # Update optimization settings
                if 'resolution_scale' in perf_data:
                    self.res_scale_label.config(text=f"{perf_data['resolution_scale']:.1f}x")
                
                if hasattr(self.monitoring_system.performance_optimizer, 'skip_frames'):
                    if self.monitoring_system.performance_optimizer.skip_frames:
                        skip_text = f"Enabled ({self.monitoring_system.performance_optimizer.process_every_n_frames})"
                        self.frame_skip_label.config(text=skip_text)
                    else:
                        self.frame_skip_label.config(text="Disabled")
            
            # Update performance plot
            if self.fps_history:
                times = [(t - self.fps_history[0][0]) for t, _ in self.fps_history]
                values = [v for _, v in self.fps_history]
                
                self.perf_plot.clear()
                self.perf_plot.set_title("FPS History")
                self.perf_plot.set_xlabel("Time (s)")
                self.perf_plot.set_ylabel("FPS")
                self.perf_plot.plot(times, values, 'g-')
                self.perf_canvas.draw()
            
            # Update statistics tab
            alert_counts = {}
            total_alerts = 0
            
            for alert_type, history in self.alert_history.items():
                count = sum(v for _, v in history)
                alert_counts[alert_type] = count
                total_alerts += count
            
            # Update stats labels
            self.total_alerts_label.config(text=str(total_alerts))
            
            if stats['uptime'] > 0:
                alert_rate = total_alerts / (stats['uptime'] / 60)
                self.alert_rate_label.config(text=f"{alert_rate:.1f} per minute")
            
            if alert_counts:
                most_common = max(alert_counts.items(), key=lambda x: x[1])
                if most_common[1] > 0:
                    self.common_alert_label.config(text=most_common[0])
            
            # Update statistics plot
            self.stats_plot.clear()
            self.stats_plot.set_title("Alert Frequency")
            self.stats_plot.set_ylabel("Count")
            
            alert_names = list(alert_counts.keys())
            counts = [alert_counts[name] for name in alert_names]
            
            self.stats_plot.bar(alert_names, counts)
            self.stats_plot.set_xticklabels(alert_names, rotation=45)
            self.stats_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
    
    def update_history_plots(self, event=None):
        """Update history plots based on selected time range"""
        try:
            # Get selected time range
            range_text = self.time_range.get()
            
            if range_text == "15 Minutes":
                seconds = 15 * 60
            elif range_text == "1 Hour":
                seconds = 60 * 60
            elif range_text == "6 Hours":
                seconds = 6 * 60 * 60
            elif range_text == "24 Hours":
                seconds = 24 * 60 * 60
            elif range_text == "7 Days":
                seconds = 7 * 24 * 60 * 60
            else:
                seconds = 60 * 60  # Default to 1 hour
            
            # Load historical data
            self.load_history_data(seconds)
            
            # Update alert history plot
            self.alert_history_plot.clear()
            self.alert_history_plot.set_title(f"Alert History - {range_text}")
            self.alert_history_plot.set_ylabel("Count")
            
            # Plot data
            for alert_type, history in self.alert_history.items():
                if not history:
                    continue
                    
                times = [(t - history[0][0]) / 60 for t, _ in history]  # Convert to minutes
                values = [v for _, v in history]
                
                self.alert_history_plot.plot(times, values, label=alert_type)
            
            self.alert_history_plot.legend(loc='upper right')
            
            # Update attention history plot
            self.attention_history_plot.clear()
            self.attention_history_plot.set_title("Attention Level History")
            self.attention_history_plot.set_xlabel("Time (minutes)")
            self.attention_history_plot.set_ylabel("Attention Score")
            
            if self.attention_history:
                times = [(t - self.attention_history[0][0]) / 60 for t, _ in self.attention_history]
                values = [v for _, v in self.attention_history]
                
                self.attention_history_plot.plot(times, values, 'b-')
            
            self.history_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating history plots: {str(e)}")
    
    def save_history_data(self):
        """Save historical data to file"""
        try:
            data_dir = "data/history"
            os.makedirs(data_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(data_dir, f"history_{timestamp}.json")
            
            data = {
                'timestamp': timestamp,
                'alert_history': self.alert_history,
                'attention_history': self.attention_history,
                'fps_history': self.fps_history
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f)
                
            logger.info(f"History data saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving history data: {str(e)}")
    
    def load_history_data(self, time_range_seconds):
        """Load historical data from files"""
        try:
            data_dir = "data/history"
            if not os.path.exists(data_dir):
                return
            
            # Get all history files
            files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) 
                    if f.startswith("history_") and f.endswith(".json")]
            
            # Sort by creation time (newest first)
            files.sort(key=os.path.getctime, reverse=True)
            
            # Load data
            now = time.time()
            cutoff = now - time_range_seconds
            
            combined_data = {
                'alert_history': {alert_type: [] for alert_type in self.alert_history},
                'attention_history': [],
                'fps_history': []
            }
            
            for file in files:
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    
                    # Combine alert history
                    for alert_type in self.alert_history:
                        if alert_type in data['alert_history']:
                            for entry in data['alert_history'][alert_type]:
                                if entry[0] >= cutoff:
                                    combined_data['alert_history'][alert_type].append(entry)
                    
                    # Combine attention history
                    if 'attention_history' in data:
                        for entry in data['attention_history']:
                            if entry[0] >= cutoff:
                                combined_data['attention_history'].append(entry)
                    
                    # Combine FPS history
                    if 'fps_history' in data:
                        for entry in data['fps_history']:
                            if entry[0] >= cutoff:
                                combined_data['fps_history'].append(entry)
                
                except Exception as e:
                    logger.error(f"Error loading history file {file}: {str(e)}")
            
            # Sort all data by timestamp
            for alert_type in combined_data['alert_history']:
                combined_data['alert_history'][alert_type].sort(key=lambda x: x[0])
            
            combined_data['attention_history'].sort(key=lambda x: x[0])
            combined_data['fps_history'].sort(key=lambda x: x[0])
            
            # Update instance data
            self.alert_history = combined_data['alert_history']
            self.attention_history = combined_data['attention_history']
            self.fps_history = combined_data['fps_history']
            
            logger.info(f"Loaded historical data for the past {time_range_seconds/3600:.1f} hours")
            
        except Exception as e:
            logger.error(f"Error loading history data: {str(e)}")
    
    def export_history_data(self):
        """Export historical data to CSV"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            import csv
            
            # Ask for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Historical Data"
            )
            
            if not filename:
                return
            
            # Prepare data
            export_data = []
            
            # Create header row
            header = ["Timestamp", "DateTime"]
            for alert_type in sorted(self.alert_history.keys()):
                header.append(f"Alert_{alert_type}")
            header.append("Attention_Score")
            header.append("FPS")
            
            export_data.append(header)
            
            # Get all timestamps
            all_timestamps = set()
            
            for alert_history in self.alert_history.values():
                all_timestamps.update([t for t, _ in alert_history])
            
            all_timestamps.update([t for t, _ in self.attention_history])
            all_timestamps.update([t for t, _ in self.fps_history])
            
            all_timestamps = sorted(all_timestamps)
            
            # Create data rows
            for timestamp in all_timestamps:
                row = [timestamp, datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")]
                
                # Add alert data
                for alert_type in sorted(self.alert_history.keys()):
                    alert_value = 0
                    for t, v in self.alert_history[alert_type]:
                        if abs(t - timestamp) < 0.5:  # Within 0.5 seconds
                            alert_value = v
                            break
                    row.append(alert_value)
                
                # Add attention data
                attention_value = ""
                for t, v in self.attention_history:
                    if abs(t - timestamp) < 0.5:  # Within 0.5 seconds
                        attention_value = v
                        break
                row.append(attention_value)
                
                # Add FPS data
                fps_value = ""
                for t, v in self.fps_history:
                    if abs(t - timestamp) < 0.5:  # Within 0.5 seconds
                        fps_value = v
                        break
                row.append(fps_value)
                
                export_data.append(row)
            
            # Write to CSV
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(export_data)
            
            logger.info(f"Exported {len(export_data)-1} data points to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting history data: {str(e)}")
    
    def close_dashboard(self):
        """Close the dashboard"""
        self.running = False
        if hasattr(self, 'collection_thread') and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=1.0)
        
        self.save_history_data()
        self.window.destroy()
