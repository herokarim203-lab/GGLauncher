import hashlib
import json
import os
import platform
import random
import shutil
import subprocess
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import requests
import customtkinter as ctk

try:
    import minecraft_launcher_lib
except ImportError:  # pragma: no cover - handled at runtime
    minecraft_launcher_lib = None


class GGLauncherApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("GG Launcher")
        self.geometry("1200x760")
        self.minsize(1000, 700)
        self.configure(fg_color="#0f1117")

        self.base_dir = Path.home() / ".gg_launcher"
        self.base_dir.mkdir(exist_ok=True)
        self.state_file = self.base_dir / "state.json"
        self.instances_dir = self.base_dir / "instances"
        self.instances_dir.mkdir(exist_ok=True)

        self.state: Dict[str, any] = self.load_state()
        self.current_profile: Optional[Dict[str, str]] = None
        self.selected_instance: Optional[Dict[str, str]] = None
        self.login_frame: Optional[ctk.CTkFrame] = None
        self.dashboard_frame: Optional[ctk.CTkFrame] = None
        self.status_bar: Optional[ctk.CTkLabel] = None
        self.instances_list_frame: Optional[ctk.CTkFrame] = None
        self.mods_frame: Optional[ctk.CTkScrollableFrame] = None
        self.profile_label: Optional[ctk.CTkLabel] = None

        self.build_ui()
        self.show_login_screen()

    def load_state(self) -> Dict[str, any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"profiles": [], "instances": []}
        return {"profiles": [], "instances": []}

    def save_state(self) -> None:
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(0, weight=1)

        self.dashboard_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)

        self.create_login_screen()
        self.create_dashboard()

    def create_login_screen(self) -> None:
        content = ctk.CTkFrame(self.login_frame, corner_radius=24, fg_color="#121722", border_width=1, border_color="#2d3650")
        content.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(content, text="GG Launcher", font=("Segoe UI", 35, "bold"))
        title.grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        subtitle = ctk.CTkLabel(content, text="A modern Minecraft launcher inspired by the Modrinth experience.", font=("Segoe UI", 16), text_color="#8ea3c3")
        subtitle.grid(row=1, column=0, padx=24, pady=(0, 20), sticky="w")

        cards = ctk.CTkFrame(content, fg_color="transparent")
        cards.grid(row=2, column=0, padx=24, pady=10, sticky="ew")
        cards.grid_columnconfigure(0, weight=1)
        cards.grid_columnconfigure(1, weight=1)

        offline_card = ctk.CTkFrame(cards, corner_radius=20, fg_color="#181d2d", border_width=1, border_color="#2f3752")
        offline_card.grid(row=0, column=0, padx=(0, 12), pady=8, sticky="nsew")
        offline_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(offline_card, text="Offline / Cracked", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        ctk.CTkLabel(offline_card, text="Quick login with a custom username and offline UUID.", font=("Segoe UI", 13), text_color="#7a8aa9").grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")
        ctk.CTkButton(offline_card, text="Continue Offline", command=self.handle_offline_login, height=42, corner_radius=12, fg_color="#2d6cdf", hover_color="#2359b0").grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")

        microsoft_card = ctk.CTkFrame(cards, corner_radius=20, fg_color="#181d2d", border_width=1, border_color="#2f3752")
        microsoft_card.grid(row=0, column=1, padx=(12, 0), pady=8, sticky="nsew")
        microsoft_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(microsoft_card, text="Microsoft Login", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        ctk.CTkLabel(microsoft_card, text="Simulated Microsoft sign-in for a polished demo experience.", font=("Segoe UI", 13), text_color="#7a8aa9").grid(row=1, column=0, padx=18, pady=(0, 12), sticky="w")
        ctk.CTkButton(microsoft_card, text="Sign in with Microsoft", command=self.handle_microsoft_login, height=42, corner_radius=12, fg_color="#3b9248", hover_color="#2e7538").grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")

        footer = ctk.CTkLabel(content, text="GG Launcher is a demo launcher. It installs local instances and launches Minecraft through launcher-lib.", font=("Segoe UI", 12), text_color="#61708f")
        footer.grid(row=3, column=0, padx=24, pady=(10, 24), sticky="w")

        self.login_frame.grid_columnconfigure(0, weight=1)

    def create_dashboard(self) -> None:
        self.dashboard_frame.grid_remove()
        header = ctk.CTkFrame(self.dashboard_frame, height=120, corner_radius=24, fg_color="#121722", border_width=1, border_color="#2d3650")
        header.grid(row=0, column=0, padx=24, pady=(24, 12), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(header, text="GG Launcher Dashboard", font=("Segoe UI", 26, "bold"))
        title.grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.profile_label = ctk.CTkLabel(header, text="Signed in as: Guest", font=("Segoe UI", 14), text_color="#8ea3c3")
        self.profile_label.grid(row=0, column=1, padx=20, pady=18, sticky="e")

        actions = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        actions.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(actions, text="Add Instance", command=self.open_add_instance_dialog, height=42, corner_radius=12, fg_color="#2d6cdf", hover_color="#2359b0").grid(row=0, column=0, padx=(0, 8), sticky="ew")
        ctk.CTkButton(actions, text="Browse Mods", command=self.load_mods, height=42, corner_radius=12, fg_color="#3b9248", hover_color="#2e7538").grid(row=0, column=1, padx=8, sticky="ew")
        ctk.CTkButton(actions, text="PLAY", command=self.launch_selected_instance, height=48, corner_radius=14, fg_color="#d47b1f", hover_color="#b76516", font=("Segoe UI", 16, "bold")).grid(row=0, column=2, padx=(8, 0), sticky="ew")

        body = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        body.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(body, corner_radius=24, fg_color="#121722", border_width=1, border_color="#2d3650")
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left_panel, text="Installed Instances", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")
        self.instances_list_frame = ctk.CTkScrollableFrame(left_panel, corner_radius=16, fg_color="#171c2a")
        self.instances_list_frame.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="nsew")
        self.instances_list_frame.grid_columnconfigure(0, weight=1)

        right_panel = ctk.CTkFrame(body, corner_radius=24, fg_color="#121722", border_width=1, border_color="#2d3650")
        right_panel.grid(row=0, column=0, padx=(10, 0), sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(right_panel, text="Popular Mods", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")
        self.mods_frame = ctk.CTkScrollableFrame(right_panel, corner_radius=16, fg_color="#171c2a")
        self.mods_frame.grid(row=1, column=0, padx=16, pady=(4, 16), sticky="nsew")
        self.mods_frame.grid_columnconfigure(0, weight=1)

        self.status_bar = ctk.CTkLabel(self.dashboard_frame, text="Ready", font=("Segoe UI", 12), text_color="#9eb0d2")
        self.status_bar.grid(row=3, column=0, padx=24, pady=(0, 12), sticky="w")

        self.grid_rowconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)

    def show_login_screen(self) -> None:
        self.dashboard_frame.grid_remove()
        self.login_frame.grid()

    def show_dashboard(self) -> None:
        self.login_frame.grid_remove()
        self.dashboard_frame.grid()
        self.refresh_instances()
        self.load_mods()

    def handle_offline_login(self) -> None:
        username = f"GGPlayer{random.randint(1000, 9999)}"
        uuid_value = self.make_offline_uuid(username)
        self.current_profile = {"type": "offline", "username": username, "uuid": uuid_value}
        self.state.setdefault("profiles", []).append(self.current_profile)
        self.save_state()
        self.update_profile_label()
        self.show_dashboard()
        self.set_status(f"Signed in offline as {username}")

    def handle_microsoft_login(self) -> None:
        username = "MicrosoftDemoUser"
        self.current_profile = {"type": "microsoft", "username": username, "uuid": str(uuid.uuid4())}
        self.state.setdefault("profiles", []).append(self.current_profile)
        self.save_state()
        self.update_profile_label()
        self.show_dashboard()
        self.set_status("Signed in with simulated Microsoft account")

    def make_offline_uuid(self, username: str) -> str:
        digest = hashlib.md5(f"OfflinePlayer:{username}".encode("utf-8")).hexdigest()
        return str(uuid.UUID(digest[:8] + "-" + digest[8:12] + "-" + digest[12:16] + "-" + digest[16:20] + "-" + digest[20:32]))

    def update_profile_label(self) -> None:
        if self.profile_label is None or self.current_profile is None:
            return
        label = self.current_profile["username"]
        if self.current_profile["type"] == "microsoft":
            label += " (Microsoft)"
        else:
            label += " (Offline)"
        self.profile_label.configure(text=f"Signed in as: {label}")

    def set_status(self, message: str) -> None:
        if self.status_bar is not None:
            self.status_bar.configure(text=message)

    def refresh_instances(self) -> None:
        if self.instances_list_frame is None:
            return
        for child in self.instances_list_frame.winfo_children():
            child.destroy()

        instances = self.state.get("instances", [])
        if not instances:
            label = ctk.CTkLabel(self.instances_list_frame, text="No instances yet. Add one to start playing.", text_color="#8ea3c3")
            label.grid(row=0, column=0, padx=12, pady=18, sticky="w")
            return

        for idx, instance in enumerate(instances):
            card = ctk.CTkFrame(self.instances_list_frame, corner_radius=16, fg_color="#171c2a", border_width=1, border_color="#2f3752")
            card.grid(row=idx, column=0, padx=6, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            title = ctk.CTkLabel(card, text=instance["name"], font=("Segoe UI", 16, "bold"))
            title.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")

            details = ctk.CTkLabel(card, text=f"Version {instance['version']} • {instance['directory']}", font=("Segoe UI", 11), text_color="#8ea3c3", wraplength=460)
            details.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

            button = ctk.CTkButton(card, text="Select", command=lambda current=instance: self.select_instance(current), width=80, height=32)
            button.grid(row=0, column=1, padx=12, pady=12, rowspan=2)

            if self.selected_instance and self.selected_instance.get("name") == instance.get("name"):
                card.configure(border_color="#2d6cdf")

    def select_instance(self, instance: Dict[str, str]) -> None:
        self.selected_instance = instance
        self.refresh_instances()
        self.set_status(f"Selected {instance['name']}")

    def open_add_instance_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Minecraft Instance")
        dialog.geometry("420x260")
        dialog.configure(fg_color="#121722")
        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(dialog, text="Add a new instance", font=("Segoe UI", 20, "bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        name_var = ctk.StringVar(value="My Instance")
        version_var = ctk.StringVar(value="1.20.1")

        ctk.CTkLabel(dialog, text="Instance Name").grid(row=1, column=0, padx=20, pady=(8, 2), sticky="w")
        ctk.CTkEntry(dialog, textvariable=name_var).grid(row=2, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(dialog, text="Minecraft Version").grid(row=3, column=0, padx=20, pady=(10, 2), sticky="w")
        version_menu = ctk.CTkComboBox(dialog, values=["1.20.1", "1.20.4", "1.20.6", "1.21.1", "1.21.5"], variable=version_var)
        version_menu.grid(row=4, column=0, padx=20, sticky="ew")

        def install_and_close() -> None:
            dialog.destroy()
            self.install_instance(name_var.get().strip() or "My Instance", version_var.get())

        ctk.CTkButton(dialog, text="Install", command=install_and_close, height=42, corner_radius=12, fg_color="#2d6cdf").grid(row=5, column=0, padx=20, pady=(16, 20), sticky="ew")

    def install_instance(self, name: str, version: str) -> None:
        if minecraft_launcher_lib is None:
            self.set_status("Install minecraft-launcher-lib before adding an instance.")
            return

        safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name).strip("_") or "instance"
        instance_dir = self.instances_dir / safe_name
        instance_dir.mkdir(exist_ok=True)

        self.set_status(f"Installing Minecraft {version}...")

        try:
            minecraft_launcher_lib.install.install_minecraft_version(
                versionid=version,
                minecraft_directory=str(instance_dir),
                launcher_name="GG Launcher",
                launcher_version="1.0.0",
            )
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            self.set_status(f"Install failed: {exc}")
            return

        instance_record = {
            "name": name,
            "version": version,
            "directory": str(instance_dir),
        }
        existing = [item for item in self.state.get("instances", []) if item.get("name") == name]
        if existing:
            for item in existing:
                self.state["instances"].remove(item)
        self.state.setdefault("instances", []).append(instance_record)
        self.save_state()
        self.selected_instance = instance_record
        self.refresh_instances()
        self.set_status(f"Installed {version} at {instance_dir}")

    def load_mods(self) -> None:
        if self.mods_frame is None:
            return
        for child in self.mods_frame.winfo_children():
            child.destroy()
        label = ctk.CTkLabel(self.mods_frame, text="Loading popular mods...", text_color="#8ea3c3")
        label.grid(row=0, column=0, padx=12, pady=16, sticky="w")

        def worker() -> None:
            try:
                response = requests.get(
                    "https://api.modrinth.com/v2/search?index=downloads&limit=6&facets=[\"project_type:mod\"]",
                    timeout=15,
                )
                response.raise_for_status()
                payload = response.json()
                mods = payload.get("hits", [])
                self.after(0, lambda: self.render_mods(mods))
            except Exception as exc:  # pragma: no cover - network dependent
                self.after(0, lambda: self.render_mods_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def render_mods(self, mods: List[Dict[str, any]]) -> None:
        if self.mods_frame is None:
            return
        for child in self.mods_frame.winfo_children():
            child.destroy()

        if not mods:
            label = ctk.CTkLabel(self.mods_frame, text="No mods were returned by the Modrinth API.", text_color="#8ea3c3")
            label.grid(row=0, column=0, padx=12, pady=16, sticky="w")
            return

        for idx, mod in enumerate(mods):
            card = ctk.CTkFrame(self.mods_frame, corner_radius=16, fg_color="#171c2a", border_width=1, border_color="#2f3752")
            card.grid(row=idx, column=0, padx=6, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)
            title = ctk.CTkLabel(card, text=mod.get("title", "Unknown"), font=("Segoe UI", 15, "bold"))
            title.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")
            description = ctk.CTkLabel(card, text=mod.get("description", "No description") or "No description", wraplength=500, text_color="#8ea3c3")
            description.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")
            meta = ctk.CTkLabel(card, text=f"Downloads: {mod.get('downloads', 0):,}", font=("Segoe UI", 11), text_color="#6ea4ff")
            meta.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="w")

    def render_mods_error(self, error: str) -> None:
        if self.mods_frame is None:
            return
        for child in self.mods_frame.winfo_children():
            child.destroy()
        label = ctk.CTkLabel(self.mods_frame, text=f"Unable to load mods: {error}", text_color="#ff6e6e")
        label.grid(row=0, column=0, padx=12, pady=16, sticky="w")

    def launch_selected_instance(self) -> None:
        if minecraft_launcher_lib is None:
            self.set_status("Install minecraft-launcher-lib to enable launching.")
            return
        if self.selected_instance is None:
            self.set_status("Select an instance first.")
            return
        if self.current_profile is None:
            self.set_status("Sign in before launching.")
            return

        instance_dir = Path(self.selected_instance["directory"])
        version = self.selected_instance["version"]
        java_path = shutil.which("java")
        if not java_path:
            self.set_status("Java was not found. Install OpenJDK 17+ and ensure the 'java' command is on PATH.")
            return

        options = {
            "username": self.current_profile["username"],
            "uuid": self.current_profile["uuid"],
            "token": "offline" if self.current_profile["type"] == "offline" else "microsoft",
            "launcherName": "GG Launcher",
            "launcherVersion": "1.0.0",
            "gameDirectory": str(instance_dir),
            "executablePath": java_path,
            "jvmArguments": ["-Xmx4G"],
        }

        self.set_status(f"Launching Minecraft {version}...")
        try:
            minecraft_launcher_lib.launch.launch_minecraft_version(version, str(instance_dir), options)
        except Exception as exc:  # pragma: no cover - depends on runtime environment
            self.set_status(f"Launch failed: {exc}")


if __name__ == "__main__":
    app = GGLauncherApp()
    app.mainloop()
