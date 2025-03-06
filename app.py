import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class SecurityReviewTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Security Review Tracker")
        self.root.geometry("1000x600")
        
        # Workflow steps
        self.workflow_steps = [
            "Initial Engagement",
            "SPIA Form Sent",
            "SPIA Form Completed",
            "Standards Sent",
            "Proof Submitted",
            "Review & Approval"
        ]
        
        # Data storage
        self.projects = []
        self.data_file = "projects.json"
        self.load_data()
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Search frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.update_table())
        
        ttk.Button(search_frame, text="Add Project", command=self.add_project).pack(side="right")
        
        # Main table
        self.tree = ttk.Treeview(self.root, columns=("PPM", "Title", "Contact", "Progress"), 
                                show="headings", selectmode="browse")
        self.tree.heading("PPM", text="PPM Number")
        self.tree.heading("Title", text="Project Title")
        self.tree.heading("Contact", text="Point of Contact")
        self.tree.heading("Progress", text="Progress %")
        
        self.tree.column("PPM", width=100)
        self.tree.column("Title", width=400)
        self.tree.column("Contact", width=300)
        self.tree.column("Progress", width=100)
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self.show_project_details)
        
        self.update_table()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.projects = json.load(f)
        
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.projects, f, indent=4)
            
    def calculate_progress(self, current_step):
        if not current_step:
            return 0
        step_index = self.workflow_steps.index(current_step)
        return int(((step_index + 1) / len(self.workflow_steps)) * 100)
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = self.search_var.get().lower()
        for project in self.projects:
            if (search_term in project["ppm_number"].lower() or 
                search_term in project["title"].lower() or 
                search_term in project["contact"].lower()):
                progress = self.calculate_progress(project.get("current_step", ""))
                self.tree.insert("", "end", values=(
                    project["ppm_number"],
                    project["title"],
                    project["contact"],
                    f"{progress}%"
                ))
    
    def add_project(self):
        self.show_project_details(None, new=True)
    
    def show_project_details(self, event, new=False):
        if new:
            project = {
                "ppm_number": "",
                "title": "",
                "contact": "",
                "description": "",
                "budget_code": "",
                "links": {"spia": "", "ppm": "", "onenote": ""},
                "current_step": ""
            }
        else:
            selected = self.tree.selection()
            if not selected:
                return
            item = self.tree.item(selected[0])
            ppm = item["values"][0]
            project = next(p for p in self.projects if p["ppm_number"] == ppm)
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Project Details")
        detail_window.geometry("600x500")
        
        # Project details frame
        details_frame = ttk.LabelFrame(detail_window, text="Project Details")
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        entries = {}
        for i, (label, key) in enumerate([
            ("PPM Number:", "ppm_number"),
            ("Title:", "title"),
            ("Point of Contact:", "contact"),
            ("Description:", "description"),
            ("Budget Code:", "budget_code")
        ]):
            ttk.Label(details_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            entries[key] = ttk.Entry(details_frame, width=50)
            entries[key].grid(row=i, column=1, padx=5, pady=5)
            entries[key].insert(0, project[key])
            
        # Links frame
        links_frame = ttk.LabelFrame(detail_window, text="Links")
        links_frame.pack(fill="x", padx=5, pady=5)
        
        link_entries = {}
        for i, (label, key) in enumerate([
            ("SPIA Form:", "spia"),
            ("PPM Page:", "ppm"),
            ("OneNote:", "onenote")
        ]):
            ttk.Label(links_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            link_entries[key] = ttk.Entry(links_frame, width=50)
            link_entries[key].grid(row=i, column=1, padx=5, pady=5)
            link_entries[key].insert(0, project["links"][key])
            
        # Progress frame
        progress_frame = ttk.LabelFrame(detail_window, text="Progress")
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        current_step = tk.StringVar(value=project["current_step"])
        ttk.Label(progress_frame, text="Current Step:").pack(side="left", padx=5)
        step_menu = ttk.Combobox(progress_frame, textvariable=current_step, 
                               values=[""] + self.workflow_steps, state="readonly")
        step_menu.pack(side="left", padx=5)
        
        progress = self.calculate_progress(project["current_step"])
        progress_bar = ttk.Progressbar(progress_frame, length=200, maximum=100, value=progress)
        progress_bar.pack(side="left", padx=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(detail_window)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        def save_project():
            updated_project = {
                "ppm_number": entries["ppm_number"].get(),
                "title": entries["title"].get(),
                "contact": entries["contact"].get(),
                "description": entries["description"].get(),
                "budget_code": entries["budget_code"].get(),
                "links": {
                    "spia": link_entries["spia"].get(),
                    "ppm": link_entries["ppm"].get(),
                    "onenote": link_entries["onenote"].get()
                },
                "current_step": current_step.get()
            }
            
            if new:
                self.projects.append(updated_project)
            else:
                project.update(updated_project)
                
            self.save_data()
            self.update_table()
            detail_window.destroy()
            
        def delete_project():
            if not new and messagebox.askyesno("Confirm", "Delete this project?"):
                self.projects.remove(project)
                self.save_data()
                self.update_table()
                detail_window.destroy()
        
        ttk.Button(buttons_frame, text="Save", command=save_project).pack(side="left", padx=5)
        if not new:
            ttk.Button(buttons_frame, text="Delete", command=delete_project).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Close", command=detail_window.destroy).pack(side="left", padx=5)

def main():
    root = tk.Tk()
    app = SecurityReviewTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()