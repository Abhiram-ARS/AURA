"""
===========================================================
AURA - ADB Utility for Remote Administration
===========================================================

File          : aura_app.py
File Type     : Frontend
Author        : ABHIRAM S (https://github.com/Abhiram-ARS)
Project       : AURA
Language      : Python 3
Platform      : Linux
Version       : AURA_1.1
Creation Date : 09-05-2026
Last Updated  : 19-05-2026
Status        : Active Development

==========================================================
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
import subprocess
import threading
import shutil


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AdvancedGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AURA : ADB Utility for Remote Administration")
        self.geometry("850x600")

        # ======================
        # CHECK ADB
        # ======================
        self.adb_path = shutil.which("adb")

        if not self.adb_path:

            messagebox.showerror(
                "ADB Not Found",
                "ADB is not installed or not added to PATH"
            )

            self.destroy()
            return

        # ======================
        # TITLE
        # ======================
        ctk.CTkLabel(
            self,
            text="""
  _  _   _ ___    _   
/_\| | | | _ \  /_\ 
/ _ \ |_| |   / / _ \ 
/_/ \_\___/|_|_\/_/ \_\.
                 
ADB Utility for Remote Administration
                        
                """,
            font=("Courier New", 15, "bold")
        ).pack(pady=20)

        # ======================
        # BUTTON FRAME
        # ======================
        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="Connect",
            width=150,
            command=self.open_pair_popup
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            button_frame,
            text="List Devices",
            width=150,
            command=self.start_load_devices
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            button_frame,
            text="Access",
            width=150,
            command=self.access_device
        ).grid(row=0, column=2, padx=10)

        # ======================
        # TABLE FRAME
        # ======================
        table_frame = ctk.CTkFrame(
            self,
            width=700,
            height=260
        )

        table_frame.pack(pady=20)
        table_frame.pack_propagate(False)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background="#2B2B2B",
            foreground="white",
            fieldbackground="#2B2B2B",
            rowheight=30,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#1F6AA5",
            foreground="white",
            font=("Segoe UI", 11, "bold")
        )

        scrollbar = ttk.Scrollbar(table_frame)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Device", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=8
        )

        scrollbar.config(command=self.tree.yview)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Device", text="Device")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Device", width=350)
        self.tree.column("Status", width=180, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # ======================
        # EXIT BUTTON
        # ======================
        ctk.CTkButton(
            self,
            text="Exit",
            width=150,
            fg_color="#444",
            hover_color="red",
            command=self.exit_application
        ).pack(side="bottom", pady=15)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.exit_application
        )

    # ======================
    # SAFE MESSAGEBOX
    # ======================
    def safe_messagebox(self, box_type, title, text):

        self.after(
            0,
            lambda: getattr(messagebox, box_type)(title, text)
        )

    # ======================
    # PAIR POPUP
    # ======================
    def open_pair_popup(self):

        popup = ctk.CTkToplevel(self)

        popup.title("ADB Pair")
        popup.geometry("350x320")
        popup.resizable(False, False)

        ctk.CTkLabel(
            popup,
            text="ADB Pair Device",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        # IP
        entry_ip = ctk.CTkEntry(
            popup,
            placeholder_text="IP Address"
        )

        entry_ip.pack(pady=10)

        # PAIR PORT
        entry_pair_port = ctk.CTkEntry(
            popup,
            placeholder_text="Pairing Port"
        )

        entry_pair_port.pack(pady=10)

        # PAIR CODE
        entry_code = ctk.CTkEntry(
            popup,
            placeholder_text="Pairing Code"
        )

        entry_code.pack(pady=10)

        ctk.CTkButton(
            popup,
            text="Pair Device",
            command=lambda: self.start_pairing(
                entry_ip,
                entry_pair_port,
                entry_code,
                popup
            )
        ).pack(pady=20)

        popup.after(10, popup.grab_set)

    # ======================
    # START PAIRING THREAD
    # ======================
    def start_pairing(
        self,
        entry_ip,
        entry_pair_port,
        entry_code,
        popup
    ):

        ip = entry_ip.get().strip()
        pair_port = entry_pair_port.get().strip()
        pairing_code = entry_code.get().strip()

        if not ip or not pair_port or not pairing_code:

            self.safe_messagebox(
                "showerror",
                "Error",
                "All fields are required"
            )

            return

        popup.destroy()

        threading.Thread(
            target=self.adb_pair,
            args=(ip, pair_port, pairing_code),
            daemon=True
        ).start()

    # ======================
    # ADB PAIR
    # ======================
    def adb_pair(self, ip, pair_port, pairing_code):

        try:

            process = subprocess.run(
                [
                    self.adb_path,
                    "pair",
                    f"{ip}:{pair_port}"
                ],
                input=pairing_code + "\n",
                text=True,
                capture_output=True,
                timeout=15
            )

            output = process.stdout.strip()
            error = process.stderr.strip()

            print(output)

            if "Successfully paired" in output:

                self.safe_messagebox(
                    "showinfo",
                    "Pair Success",
                    output
                )

                # OPEN CONNECT POPUP
                self.after(
                    0,
                    lambda: self.open_connect_popup(ip)
                )

            else:

                self.safe_messagebox(
                    "showerror",
                    "Pair Failed",
                    output if output else error
                )

        except subprocess.TimeoutExpired:

            self.safe_messagebox(
                "showerror",
                "Timeout",
                "ADB pairing timed out"
            )

        except Exception as e:

            self.safe_messagebox(
                "showerror",
                "Error",
                str(e)
            )

    # ======================
    # CONNECT POPUP
    # ======================
    def open_connect_popup(self, ip):

        popup = ctk.CTkToplevel(self)

        popup.title("ADB Connect")
        popup.geometry("350x220")
        popup.resizable(False, False)

        ctk.CTkLabel(
            popup,
            text="ADB Connect Device",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=15)

        ctk.CTkLabel(
            popup,
            text=f"IP: {ip}",
            font=("Segoe UI", 14)
        ).pack(pady=5)

        # CONNECT PORT
        entry_connect_port = ctk.CTkEntry(
            popup,
            placeholder_text="Debugging Port"
        )

        entry_connect_port.pack(pady=15)

        ctk.CTkButton(
            popup,
            text="Connect Device",
            command=lambda: self.start_connect(
                ip,
                entry_connect_port,
                popup
            )
        ).pack(pady=15)

        popup.after(10, popup.grab_set)

    # ======================
    # START CONNECT THREAD
    # ======================
    def start_connect(
        self,
        ip,
        entry_connect_port,
        popup
    ):

        connect_port = entry_connect_port.get().strip()

        if not connect_port:

            self.safe_messagebox(
                "showerror",
                "Error",
                "Connect port is required"
            )

            return

        popup.destroy()

        threading.Thread(
            target=self.adb_connect,
            args=(ip, connect_port),
            daemon=True
        ).start()

    # ======================
    # ADB CONNECT
    # ======================
    def adb_connect(self, ip, connect_port):

        try:

            process = subprocess.run(
                [
                    self.adb_path,
                    "connect",
                    f"{ip}:{connect_port}"
                ],
                text=True,
                capture_output=True,
                timeout=15
            )

            output = process.stdout.strip()
            error = process.stderr.strip()

            print(output)

            if "connected" in output.lower():

                self.safe_messagebox(
                    "showinfo",
                    "Connected",
                    output
                )

            else:

                self.safe_messagebox(
                    "showerror",
                    "Connection Failed",
                    output if output else error
                )

        except subprocess.TimeoutExpired:

            self.safe_messagebox(
                "showerror",
                "Timeout",
                "ADB connection timed out"
            )

        except Exception as e:

            self.safe_messagebox(
                "showerror",
                "Error",
                str(e)
            )

    # ======================
    # LOAD DEVICES THREAD
    # ======================
    def start_load_devices(self):

        threading.Thread(
            target=self.load_devices,
            daemon=True
        ).start()

    # ======================
    # LOAD ADB DEVICES
    # ======================
    def load_devices(self):

        try:

            process = subprocess.run(
                [self.adb_path, "devices"],
                text=True,
                capture_output=True,
                timeout=10
            )

            output = process.stdout.strip().splitlines()

            self.after(
                0,
                lambda: self.update_table(output)
            )

        except Exception as e:

            self.safe_messagebox(
                "showerror",
                "Error",
                str(e)
            )

    # ======================
    # UPDATE TABLE
    # ======================
    def update_table(self, output):

        self.tree.delete(*self.tree.get_children())

        if len(output) <= 1:

            self.safe_messagebox(
                "showinfo",
                "Devices",
                "No devices found"
            )

            return

        count = 1

        for line in output[1:]:

            if line.strip():

                parts = line.split()

                if len(parts) >= 2:

                    device = parts[0]
                    status = parts[1]

                    tag = (
                        "evenrow"
                        if count % 2 == 0
                        else "oddrow"
                    )

                    self.tree.insert(
                        "",
                        "end",
                        values=(count, device, status),
                        tags=(tag,)
                    )

                    count += 1

        self.tree.tag_configure(
            "evenrow",
            background="#2B2B2B"
        )

        self.tree.tag_configure(
            "oddrow",
            background="#242424"
        )

    # ======================
    # ACCESS DEVICE
    # ======================
    def access_device(self):

        selected = self.tree.selection()

        if selected:

            item = self.tree.item(selected[0])

            print(item["values"])

        else:

            self.safe_messagebox(
                "showwarning",
                "No Selection",
                "Please select a device"
            )

    # ======================
    # EXIT APPLICATION
    # ======================
    def exit_application(self):

        try:

            subprocess.run(
                [self.adb_path, "kill-server"],
                timeout=5,
                capture_output=True
            )

        except:
            pass

        self.destroy()


# ======================
# MAIN
# ======================
if __name__ == "__main__":

    app = AdvancedGUI()

    app.mainloop()