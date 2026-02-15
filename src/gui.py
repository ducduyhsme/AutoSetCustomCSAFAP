"""Tkinter-based GUI for the CS2 Lineup Config Generator."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.constants import (
    GRENADES,
    MAPS,
    RADIO_TAB_MAX,
    RADIO_TAB_MIN,
    RADIO_TEXT_MAX,
    RADIO_TEXT_MIN,
    SIDES,
)
from src.core import (
    build_message_name,
    calculate_value,
    extract_yaw_pitch,
    format_lineup_name,
    generate_unique_id,
    parse_getpos,
)
from src.config_generator import (
    append_command,
    append_label,
    append_main_cfg,
    append_platform_english,
    find_first_empty_slot,
    get_occupied_slots,
    remove_from_main_cfg,
    remove_from_platform_english,
    remove_slot_from_commands,
    remove_slot_from_labels,
)
from src.storage import (
    add_lineup,
    find_lineup,
    get_existing_ids,
    load_data,
    remove_lineup,
    save_data,
)


class Application(tk.Tk):
    """Main application window."""

    def __init__(self, storage_dir: str | None = None):
        super().__init__()
        self.title("CS2 Lineup Config Generator (CSAFAP)")
        self.geometry("900x650")
        self.resizable(True, True)

        # Storage
        self.storage_dir = storage_dir or os.path.join(
            os.path.expanduser("~"), ".csafap"
        )
        self.data = load_data(self.storage_dir)

        # Auto slot mode
        self.auto_slot = tk.BooleanVar(value=True)

        self._build_ui()
        self._refresh_lineup_list()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.add_frame = ttk.Frame(notebook)
        self.list_frame = ttk.Frame(notebook)
        self.settings_frame = ttk.Frame(notebook)

        notebook.add(self.add_frame, text="Add New Lineup")
        notebook.add(self.list_frame, text="Saved Lineups")
        notebook.add(self.settings_frame, text="Settings")

        self._build_add_form()
        self._build_lineup_list()
        self._build_settings()

    # --- Add New Lineup form ---

    def _build_add_form(self):
        f = self.add_frame

        # Side
        ttk.Label(f, text="Side:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.side_var = tk.StringVar(value=SIDES[0])
        ttk.Combobox(
            f, textvariable=self.side_var, values=SIDES, state="readonly", width=10
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Map
        ttk.Label(f, text="Map:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.map_var = tk.StringVar(value=MAPS[0])
        ttk.Combobox(
            f, textvariable=self.map_var, values=MAPS, state="readonly", width=15
        ).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Grenade
        ttk.Label(f, text="Grenade:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.grenade_var = tk.StringVar(value=GRENADES[0])
        ttk.Combobox(
            f,
            textvariable=self.grenade_var,
            values=GRENADES,
            state="readonly",
            width=15,
        ).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Lineup name
        ttk.Label(f, text="Lineup Name:").grid(
            row=3, column=0, sticky="w", padx=5, pady=2
        )
        self.name_entry = ttk.Entry(f, width=40)
        self.name_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        # getpos output
        ttk.Label(f, text="getpos Output:").grid(
            row=4, column=0, sticky="nw", padx=5, pady=2
        )
        self.getpos_text = tk.Text(f, height=3, width=50)
        self.getpos_text.grid(row=4, column=1, sticky="w", padx=5, pady=2)

        # Auto/manual slot selection
        ttk.Checkbutton(
            f, text="Auto-select empty slot", variable=self.auto_slot
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        # Manual slot selection
        slot_frame = ttk.Frame(f)
        slot_frame.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        ttk.Label(slot_frame, text="Tab (0-2):").pack(side=tk.LEFT, padx=2)
        self.tab_var = tk.IntVar(value=0)
        ttk.Spinbox(
            slot_frame,
            from_=RADIO_TAB_MIN,
            to=RADIO_TAB_MAX,
            textvariable=self.tab_var,
            width=5,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Label(slot_frame, text="Text (1-8):").pack(side=tk.LEFT, padx=2)
        self.text_var = tk.IntVar(value=1)
        ttk.Spinbox(
            slot_frame,
            from_=RADIO_TEXT_MIN,
            to=RADIO_TEXT_MAX,
            textvariable=self.text_var,
            width=5,
        ).pack(side=tk.LEFT, padx=2)

        # Occupied slots display
        ttk.Button(f, text="Show Occupied Slots", command=self._show_occupied).grid(
            row=7, column=0, columnspan=2, sticky="w", padx=5, pady=2
        )
        self.occupied_label = ttk.Label(f, text="")
        self.occupied_label.grid(
            row=8, column=0, columnspan=2, sticky="w", padx=5, pady=2
        )

        # Save button
        ttk.Button(f, text="Save Lineup", command=self._save_lineup).grid(
            row=9, column=0, columnspan=2, pady=10, padx=5
        )

    # --- Saved Lineups list ---

    def _build_lineup_list(self):
        f = self.list_frame
        cols = ("ID", "Map", "Side", "Grenade", "Name", "Slot")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(f)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Generate Configs", command=self._generate_configs).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Delete Selected", command=self._delete_lineup).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_lineup_list).pack(
            side=tk.LEFT, padx=5
        )

    # --- Settings ---

    def _build_settings(self):
        f = self.settings_frame
        ttk.Label(f, text="CS2 Installation Path:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        self.cs2_path_var = tk.StringVar(
            value=self.data.get("settings", {}).get("cs2_path", "")
        )
        ttk.Entry(f, textvariable=self.cs2_path_var, width=50).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )
        ttk.Button(f, text="Browse…", command=self._browse_cs2_path).grid(
            row=0, column=2, padx=5, pady=5
        )

        ttk.Label(f, text="Sensitivity:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        self.sensitivity_var = tk.DoubleVar(
            value=self.data.get("settings", {}).get("sensitivity", 1.0)
        )
        ttk.Entry(f, textvariable=self.sensitivity_var, width=10).grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )

        ttk.Button(f, text="Save Settings", command=self._save_settings).grid(
            row=2, column=0, columnspan=3, pady=10
        )

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _cs2_cfg_dir(self) -> str:
        """Return the CSAFAP cfg directory inside the CS2 installation."""
        return os.path.join(self.cs2_path_var.get(), "csgo", "cfg", "CSAFAP")

    def _cs2_resource_dir(self) -> str:
        """Return the resource directory inside the CS2 installation."""
        return os.path.join(self.cs2_path_var.get(), "csgo", "resource")

    def _browse_cs2_path(self):
        path = filedialog.askdirectory(title="Select CS2 Installation Folder")
        if path:
            self.cs2_path_var.set(path)

    def _save_settings(self):
        self.data.setdefault("settings", {})["cs2_path"] = self.cs2_path_var.get()
        self.data["settings"]["sensitivity"] = self.sensitivity_var.get()
        save_data(self.storage_dir, self.data)
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def _show_occupied(self):
        cfg_dir = self._cs2_cfg_dir()
        map_name = self.map_var.get()
        side = self.side_var.get()
        occupied = get_occupied_slots(cfg_dir, map_name, side)
        if occupied:
            text = ", ".join(f"tab={t} text={x}" for t, x in sorted(occupied))
        else:
            text = "No occupied slots."
        self.occupied_label.config(text=text)

    def _save_lineup(self):
        # Validate CS2 path
        cs2_path = self.cs2_path_var.get()
        if not cs2_path:
            messagebox.showerror("Error", "Please set the CS2 installation path in Settings.")
            return

        # Parse getpos
        raw_getpos = self.getpos_text.get("1.0", tk.END).strip()
        if not raw_getpos:
            messagebox.showerror("Error", "Please paste the getpos output.")
            return
        try:
            parsed = parse_getpos(raw_getpos)
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        lineup_name = self.name_entry.get().strip()
        if not lineup_name:
            messagebox.showerror("Error", "Please enter a lineup name.")
            return

        side = self.side_var.get()
        map_name = self.map_var.get()
        grenade = self.grenade_var.get()

        cfg_dir = self._cs2_cfg_dir()

        # Determine slot
        if self.auto_slot.get():
            slot = find_first_empty_slot(cfg_dir, map_name, side)
            if slot is None:
                messagebox.showerror("Error", "All slots are occupied for this map/side.")
                return
            tab, text = slot
        else:
            tab = self.tab_var.get()
            text = self.text_var.get()
            occupied = get_occupied_slots(cfg_dir, map_name, side)
            if (tab, text) in occupied:
                overwrite = messagebox.askyesno(
                    "Slot Occupied",
                    f"Slot tab={tab} text={text} is already occupied. Overwrite?",
                )
                if not overwrite:
                    return

        # Calculate values
        yaw_angle, pitch_angle = extract_yaw_pitch(parsed["setang"])
        yaw_value = calculate_value(yaw_angle)
        pitch_value = calculate_value(pitch_angle)

        # Generate unique ID
        existing_ids = get_existing_ids(self.data)
        unique_id = generate_unique_id(existing_ids)

        # Build names
        message_name = build_message_name(map_name, grenade, unique_id)
        formatted_name = format_lineup_name(lineup_name)

        # Write config files
        resource_dir = self._cs2_resource_dir()
        try:
            append_main_cfg(cfg_dir, grenade, unique_id, yaw_value, pitch_value)
            append_platform_english(resource_dir, message_name, formatted_name)
            append_label(cfg_dir, map_name, side, tab, text, message_name)
            append_command(cfg_dir, map_name, side, tab, text, grenade, unique_id)
        except OSError as exc:
            messagebox.showerror("File Error", str(exc))
            return

        # Save to storage
        lineup_entry = {
            "unique_id": unique_id,
            "side": side,
            "map": map_name,
            "grenade": grenade,
            "name": lineup_name,
            "raw_getpos": raw_getpos,
            "yaw_value": yaw_value,
            "pitch_value": pitch_value,
            "message_name": message_name,
            "tab": tab,
            "text": text,
        }
        self.data = add_lineup(self.data, lineup_entry)
        save_data(self.storage_dir, self.data)

        messagebox.showinfo(
            "Success",
            f"Lineup saved!\nID: {unique_id}\nSlot: tab={tab} text={text}",
        )
        self._clear_add_form()
        self._refresh_lineup_list()

    def _generate_configs(self):
        """Regenerate all config files from stored lineup data."""
        cs2_path = self.cs2_path_var.get()
        if not cs2_path:
            messagebox.showerror("Error", "Please set the CS2 installation path in Settings.")
            return

        cfg_dir = self._cs2_cfg_dir()
        resource_dir = self._cs2_resource_dir()

        try:
            for lu in self.data.get("lineups", []):
                append_main_cfg(
                    cfg_dir, lu["grenade"], lu["unique_id"],
                    lu["yaw_value"], lu["pitch_value"],
                )
                append_platform_english(
                    resource_dir, lu["message_name"],
                    format_lineup_name(lu["name"]),
                )
                append_label(
                    cfg_dir, lu["map"], lu["side"],
                    lu["tab"], lu["text"], lu["message_name"],
                )
                append_command(
                    cfg_dir, lu["map"], lu["side"],
                    lu["tab"], lu["text"], lu["grenade"], lu["unique_id"],
                )
        except OSError as exc:
            messagebox.showerror("File Error", str(exc))
            return

        messagebox.showinfo("Success", "Config files generated successfully!")

    def _delete_lineup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a lineup to delete.")
            return
        item = self.tree.item(selected[0])
        unique_id = item["values"][0]
        lineup = find_lineup(self.data, unique_id)
        if lineup is None:
            messagebox.showerror("Error", "Lineup not found.")
            return

        if not messagebox.askyesno("Confirm", f"Delete lineup {unique_id}?"):
            return

        cfg_dir = self._cs2_cfg_dir()
        resource_dir = self._cs2_resource_dir()

        # Remove from config files
        remove_from_main_cfg(cfg_dir, unique_id)
        remove_from_platform_english(resource_dir, lineup["message_name"])
        remove_slot_from_labels(
            cfg_dir, lineup["map"], lineup["side"], lineup["tab"], lineup["text"]
        )
        remove_slot_from_commands(
            cfg_dir, lineup["map"], lineup["side"], lineup["tab"], lineup["text"]
        )

        self.data = remove_lineup(self.data, unique_id)
        save_data(self.storage_dir, self.data)
        self._refresh_lineup_list()
        messagebox.showinfo("Deleted", f"Lineup {unique_id} deleted.")

    def _clear_add_form(self):
        self.name_entry.delete(0, tk.END)
        self.getpos_text.delete("1.0", tk.END)

    def _refresh_lineup_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for lu in self.data.get("lineups", []):
            self.tree.insert(
                "",
                tk.END,
                values=(
                    lu["unique_id"],
                    lu["map"],
                    lu["side"],
                    lu["grenade"],
                    lu["name"],
                    f"tab={lu['tab']} text={lu['text']}",
                ),
            )
