import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser

class SecurityReviewTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Security Review Tracker")
        self.root.geometry("1280x720")
        self.root.configure(bg="#e0e0e0")
        
        self.workflow_steps = [
            "Initial Engagement",
            "SPIA Form Sent",
            "SPIA Form Completed",
            "Standards Sent",
            "Proof Submitted",
            "Review & Approval"
        ]
        
        self.projects = []
        self.data_file = "projects.json"
        self.load_data()
        
        self.setup_styles()
        self.create_main_window()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TFrame", background="#0288d1", relief="flat")
        style.configure("Header.TLabel", background="#0288d1", foreground="white", font=("Segoe UI", 18, "bold"))
        style.configure("Subheader.TLabel", background="#0288d1", foreground="white", font=("Segoe UI", 12))
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#b0bec5")
        style.configure("TLabelFrame", font=("Segoe UI", 11, "bold"))
        
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                self.projects = json.load(f)
            # Ensure all PPM numbers are strings for consistency
            for project in self.projects:
                project["ppm_number"] = str(project["ppm_number"]).strip()
        else:
            self.projects = []
                
    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.projects, f, indent=4)
            
    def calculate_progress(self, current_step):
        if not current_step:
            return 0
        step_index = self.workflow_steps.index(current_step)
        return int(((step_index + 1) / len(self.workflow_steps)) * 100)
    
    def create_main_window(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x", padx=15, pady=15)
        ttk.Label(header, text="Security Review Tracker", style="Header.TLabel").pack(pady=5)
        
        control_panel = ttk.Frame(self.root, relief="flat")
        control_panel.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(control_panel, text="Search Projects:", font=("Segoe UI", 10)).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_panel, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.update_table())
        
        ttk.Button(control_panel, text="Add Project", command=self.add_project).pack(side="right", padx=5)
        ttk.Button(control_panel, text="View Profile", command=self.view_project_profile).pack(side="right", padx=5)
        
        self.tree = ttk.Treeview(self.root, columns=("PPM", "Title", "Contact", "Progress"), 
                                show="headings", selectmode="browse", height=20)
        self.tree.heading("PPM", text="PPM Number")
        self.tree.heading("Title", text="Project Title")
        self.tree.heading("Contact", text="Point of Contact")
        self.tree.heading("Progress", text="Progress")
        
        self.tree.column("PPM", width=130, anchor="center")
        self.tree.column("Title", width=500)
        self.tree.column("Contact", width=350)
        self.tree.column("Progress", width=250)
        
        scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scroll.pack(side="left", fill="y", pady=15)
        
        self.update_table()
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = self.search_var.get().lower()
        for project in sorted(self.projects, key=lambda x: str(x["ppm_number"])):
            if (search_term in str(project["ppm_number"]).lower() or 
                search_term in project["title"].lower() or 
                search_term in project["contact"].lower()):
                progress = self.calculate_progress(project.get("current_step", ""))
                self.tree.insert("", "end", values=(
                    str(project["ppm_number"]),
                    project["title"],
                    project["contact"],
                    f"{progress}% - {project.get('current_step', 'Not Started')}"
                ))
    
    def add_project(self):
        self.show_project_editor(new=True)
    
    def view_project_profile(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a project to view its profile.")
            return
            
        # Get the PPM number from the selected row
        ppm = str(self.tree.item(selected[0])["values"][0]).strip()  # Ensure it's a string and trim whitespace
        # Debug output to trace the issue
        print("Selected PPM from Treeview:", ppm)
        print("Projects in database:", [(p["ppm_number"], p["title"]) for p in self.projects])
        
        # Search for the project by PPM number
        project = next((p for p in self.projects if str(p["ppm_number"]).strip() == ppm), None)
        if not project:
            messagebox.showerror("Error", f"Project with PPM {ppm} not found in database. "
                             f"Check if data was saved correctly.")
            return
        
        # Create modal profile window
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"Profile: {project['ppm_number']}")
        profile_window.geometry("600x500")
        profile_window.configure(bg="#e0e0e0")
        profile_window.transient(self.root)
        profile_window.grab_set()
        
        header = ttk.Frame(profile_window, style="Header.TFrame")
        header.pack(fill="x", padx=10, pady=10)
        ttk.Label(header, text=project["title"], style="Header.TLabel").pack(pady=2)
        ttk.Label(header, text=f"PPM: {project['ppm_number']}", style="Subheader.TLabel").pack()
        
        content = ttk.Frame(profile_window, relief="flat")
        content.pack(fill="both", expand=True, padx=10, pady=5)
        
        info_frame = ttk.LabelFrame(content, text="Details", padding=10)
        info_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        for label, value in [
            ("Contact:", project["contact"]),
            ("Budget Code:", project["budget_code"]),
            ("Description:", project["description"])
        ]:
            ttk.Label(info_frame, text=label, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5)
            ttk.Label(info_frame, text=value or "N/A", wraplength=550, font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=2)
        
        links_frame = ttk.LabelFrame(content, text="Links", padding=10)
        links_frame.pack(fill="both", expand=True, pady=5)
        
        for label, key in [
            ("SPIA Form:", "spia"),
            ("PPM Page:", "ppm"),
            ("OneNote:", "onenote")
        ]:
            ttk.Label(links_frame, text=label, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5)
            link = project["links"][key]
            if link:
                link_label = ttk.Label(links_frame, text=link, foreground="#0288d1", cursor="hand2", 
                                     font=("Segoe UI", 10, "underline"), wraplength=550)
                link_label.pack(anchor="w", padx=20, pady=2)
                link_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
            else:
                ttk.Label(links_frame, text="None provided", font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=2)
        
        progress_frame = ttk.Frame(content)
        progress_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(progress_frame, text="Progress:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        progress = self.calculate_progress(project["current_step"])
        progress_bar = ttk.Progressbar(progress_frame, length=400, value=progress, maximum=100, 
                                     mode="determinate", style="Horizontal.TProgressbar")
        progress_bar.pack(fill="x", pady=5)
        ttk.Label(progress_frame, text=f"{progress}% - {project['current_step'] or 'Not Started'}", 
                 font=("Segoe UI", 10)).pack(anchor="w")
        
        ttk.Button(profile_window, text="Close", command=profile_window.destroy).pack(pady=10)
    
    def show_project_editor(self, new=False, project=None):
        if new:
            project = {"ppm_number": "", "title": "", "contact": "", "description": "", 
                      "budget_code": "", "links": {"spia": "", "ppm": "", "onenote": ""}, "current_step": ""}
        
        editor = tk.Toplevel(self.root)
        editor.title("Edit Project" if not new else "New Project")
        editor.geometry("750x700")
        editor.configure(bg="#e0e0e0")
        
        form = ttk.Frame(editor, padding=15)
        form.pack(fill="both", expand=True)
        
        entries = {}
        for i, (label, key) in enumerate([
            ("PPM Number:", "ppm_number"),
            ("Title:", "title"),
            ("Point of Contact:", "contact"),
            ("Description:", "description"),
            ("Budget Code:", "budget_code")
        ]):
            ttk.Label(form, text=label, font=("Segoe UI", 10, "bold")).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            entries[key] = ttk.Entry(form, width=55)
            entries[key].grid(row=i, column=1, padx=5, pady=8)
            entries[key].insert(0, project[key])
        
        link_entries = {}
        ttk.Label(form, text="Links:", font=("Segoe UI", 10, "bold")).grid(row=5, column=0, pady=10, sticky="e")
        for i, (label, key) in enumerate([
            ("SPIA Form:", "spia"),
            ("PPM Page:", "ppm"),
            ("OneNote:", "onenote")
        ], start=6):
            ttk.Label(form, text=label, font=("Segoe UI", 10)).grid(row=i, column=0, padx=5, pady=8, sticky="e")
            link_entries[key] = ttk.Entry(form, width=55)
            link_entries[key].grid(row=i, column=1, padx=5, pady=8)
            link_entries[key].insert(0, project["links"][key])
        
        ttk.Label(form, text="Current Step:", font=("Segoe UI", 10, "bold")).grid(row=9, column=0, pady=8, sticky="e")
        current_step = tk.StringVar(value=project["current_step"])
        step_menu = ttk.Combobox(form, textvariable=current_step, values=[""] + self.workflow_steps, 
                               state="readonly", width=53)
        step_menu.grid(row=9, column=1, padx=5, pady=8)
        progress = self.calculate_progress(project["current_step"])
        progress_bar = ttk.Progressbar(form, length=450, value=progress, maximum=100, 
                                    mode="determinate", style="Horizontal.TProgressbar")
        progress_bar.grid(row=10, column=1, pady=8, sticky="w")
        ttk.Label(form, text=f"Progress: {progress}%", font=("Segoe UI", 10)).grid(row=11, column=1, sticky="w")
        
        buttons = ttk.Frame(editor)
        buttons.pack(fill="x", pady=15)
        
        def save():
            updated_project = {
                "ppm_number": str(entries["ppm_number"].get()).strip(),
                "title": entries["title"].get(),
                "contact": entries["contact"].get(),
                "description": entries["description"].get(),
                "budget_code": entries["budget_code"].get(),
                "links": {k: link_entries[k].get() for k in ["spia", "ppm", "onenote"]},
                "current_step": current_step.get()
            }
            if new:
                self.projects.append(updated_project)
            else:
                for i, p in enumerate(self.projects):
                    if str(p["ppm_number"]).strip() == str(project["ppm_number"]).strip():
                        self.projects[i] = updated_project
                        break
            self.save_data()
            self.update_table()
            editor.destroy()
            
        def delete():
            if not new and messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this project?"):
                self.projects = [p for p in self.projects if str(p["ppm_number"]).strip() != str(project["ppm_number"]).strip()]
                self.save_data()
                self.update_table()
                editor.destroy()
        
        ttk.Button(buttons, text="Save", command=save).pack(side="left", padx=10)
        if not new:
            ttk.Button(buttons, text="Delete", command=delete).pack(side="left", padx=10)
        ttk.Button(buttons, text="Cancel", command=editor.destroy).pack(side="left", padx=10)

def main():
    root = tk.Tk()
    app = SecurityReviewTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()