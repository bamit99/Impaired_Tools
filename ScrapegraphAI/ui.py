import json
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from typing import List, Dict
from datetime import datetime
import tempfile
import os
import threading
from scraper import scrape_company_info

class ScraperUI:
    def __init__(self, master):
        self.master = master
        master.title("Web Scraper UI")
        
        self.dark_mode = tk.BooleanVar(value=False)
        self.create_widgets()
        self.apply_theme()

        # Configure the main window to be resizable
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)

        # Set minimum window size
        master.minsize(1200, 700)

    def create_widgets(self):
        # Create main horizontal paned window
        main_paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        main_paned.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Left pane
        left_pane = ttk.Frame(main_paned)
        main_paned.add(left_pane, weight=1)

        # Right pane
        right_pane = ttk.Frame(main_paned)
        main_paned.add(right_pane, weight=1)

        # Left pane widgets
        self.create_title(left_pane, "URL Input", "TitleLabel.TLabel")
        url_input_paned = ttk.PanedWindow(left_pane, orient=tk.HORIZONTAL)
        url_input_paned.pack(fill=tk.BOTH, expand=True)

        self.url_input = scrolledtext.ScrolledText(url_input_paned, width=50, height=10)
        self.url_status = scrolledtext.ScrolledText(url_input_paned, width=20, height=10, state='disabled')
        url_input_paned.add(self.url_input, weight=3)
        url_input_paned.add(self.url_status, weight=1)

        self.create_title(left_pane, "LLM Prompt", "TitleLabel.TLabel")
        self.prompt_input = scrolledtext.ScrolledText(left_pane, height=5, width=50)
        self.prompt_input.pack(fill=tk.BOTH, expand=True)
        self.prompt_input.insert(tk.END, "extract Project Name and Purpose")

        button_frame = ttk.Frame(left_pane)
        button_frame.pack(pady=10)
        self.scrape_button = ttk.Button(button_frame, text="Scrape", command=self.start_scraping)
        self.scrape_button.pack(side=tk.LEFT, padx=5)
        self.dark_mode_button = ttk.Button(button_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.dark_mode_button.pack(side=tk.LEFT, padx=5)

        self.create_title(left_pane, "Scraping Progress", "TitleLabel.TLabel")
        self.progress_bar = ttk.Progressbar(left_pane, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Right pane widgets
        self.create_title(right_pane, "Console Output", "TitleLabel.TLabel")
        self.console_output = scrolledtext.ScrolledText(right_pane, state='disabled', height=10, width=50)
        self.console_output.pack(fill=tk.BOTH, expand=True)

        self.create_title(right_pane, "Export Options", "TitleLabel.TLabel")
        self.export_format = tk.StringVar(value="both")
        export_options = ttk.Frame(right_pane)
        export_options.pack(pady=(0, 10))
        ttk.Radiobutton(export_options, text="JSON", variable=self.export_format, value="json").pack(side=tk.LEFT)
        ttk.Radiobutton(export_options, text="CSV", variable=self.export_format, value="csv").pack(side=tk.LEFT)
        ttk.Radiobutton(export_options, text="Both", variable=self.export_format, value="both").pack(side=tk.LEFT)

        self.export_button = ttk.Button(right_pane, text="Export Results", command=self.export_results)
        self.export_button.pack()
        self.export_button.config(state='disabled')

        self.create_title(right_pane, "Scraping Results", "TitleLabel.TLabel")
        self.results_display = scrolledtext.ScrolledText(right_pane, height=20, width=50)
        self.results_display.pack(fill=tk.BOTH, expand=True)

        self.results: Dict[str, dict] = {}
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json', encoding='utf-8')

    def create_title(self, parent, text, style):
        title = ttk.Label(parent, text=text, style=style)
        title.pack(pady=(10, 5))

    def apply_theme(self):
        bg_color = "#2b2b2b" if self.dark_mode.get() else "white"
        fg_color = "white" if self.dark_mode.get() else "black"
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=bg_color, foreground=fg_color)
        style.configure("TButton", background=bg_color, foreground=fg_color)
        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TFrame", background=bg_color)
        style.configure("TitleLabel.TLabel", font=('Helvetica', 12, 'bold'), background=bg_color, foreground=fg_color)
        
        self.master.configure(bg=bg_color)
        for widget in [self.url_input, self.url_status, self.prompt_input, self.console_output, self.results_display]:
            widget.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)

    def toggle_dark_mode(self):
        self.dark_mode.set(not self.dark_mode.get())
        self.apply_theme()

    def start_scraping(self):
        self.scrape_button.config(state='disabled')
        self.export_button.config(state='disabled')
        self.results = {}
        self.progress_bar['value'] = 0
        self.console_output.config(state='normal')
        self.console_output.delete('1.0', tk.END)
        self.console_output.config(state='disabled')
        self.update_url_status()
        
        urls = self.url_input.get("1.0", tk.END).strip().split("\n")
        prompt = self.prompt_input.get("1.0", tk.END).strip()
        if not prompt:
            prompt = "extract Project Name and Purpose"
        
        threading.Thread(target=self.scrape, args=(urls, prompt), daemon=True).start()

    def update_url_status(self):
        self.url_status.config(state='normal')
        self.url_status.delete('1.0', tk.END)
        urls = self.url_input.get("1.0", tk.END).strip().split("\n")
        for i, url in enumerate(urls, start=1):
            status = "✓" if url in self.results else " "
            self.url_status.insert(tk.END, f"{i}. [{status}]\n")
        self.url_status.config(state='disabled')

    def scrape(self, urls: List[str], prompt: str):
        total_urls = len(urls)
        for i, url in enumerate(urls, start=1):
            if url:
                self.log_to_console(f"Scraping URL {i}/{total_urls}: {url}")
                result = scrape_company_info(url, prompt)
                self.results[url] = result
                self.save_to_temp_file(url, result)
                self.update_url_status()
                self.progress_bar['value'] = (i / total_urls) * 100
                self.master.update_idletasks()
        
        self.display_results()
        self.scrape_button.config(state='normal')
        self.export_button.config(state='normal')
        self.log_to_console("Scraping completed.")

    def log_to_console(self, message: str):
        self.console_output.config(state='normal')
        self.console_output.insert(tk.END, message + "\n")
        self.console_output.see(tk.END)
        self.console_output.config(state='disabled')

    def save_to_temp_file(self, url: str, result: dict):
        self.temp_file.write(json.dumps({url: result}) + '\n')
        self.temp_file.flush()

    def display_results(self):
        self.results_display.delete("1.0", tk.END)
        formatted_results = json.dumps(self.results, indent=4)
        self.results_display.insert(tk.END, formatted_results)

    def export_results(self):
        if not self.results:
            messagebox.showinfo("No Results", "No results to export. Please scrape some URLs first.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_format = self.export_format.get()

        if export_format in ['json', 'both']:
            self.export_json(timestamp)

        if export_format in ['csv', 'both']:
            self.export_csv(timestamp)

    def export_json(self, timestamp: str):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"scraping_results_{timestamp}.json"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Export Successful", f"JSON results exported to {file_path}")

    def export_csv(self, timestamp: str):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"scraping_results_{timestamp}.csv"
        )
        if file_path:
            # Collect all unique keys from all results
            all_keys = set()
            for result in self.results.values():
                all_keys.update(self.flatten_dict(result).keys())

            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write header
                header = ['URL'] + list(all_keys)
                writer.writerow(header)

                # Write data
                for url, data in self.results.items():
                    flat_data = self.flatten_dict(data)
                    row = [url] + [flat_data.get(key, 'N/A') for key in all_keys]
                    writer.writerow(row)

            messagebox.showinfo("Export Successful", f"CSV results exported to {file_path}")

    def flatten_dict(self, d: dict, parent_key: str = '', sep: str = '_') -> dict:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def __del__(self):
        self.temp_file.close()
        os.unlink(self.temp_file.name)
