"""Windows desktop interface for Saadhya's recommendation-only workflow."""

from __future__ import annotations

import json
import queue
import threading
import traceback
from io import StringIO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.cli.market_scan import format_market_scan, run
from app.core.saadhya_app import SaadhyaApp
from app.reports.recommendation_report import RecommendationReport


class SaadhyaDesktopApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=16)
        self.master = master
        self._queue = queue.Queue()
        self.report = None
        self.opportunities = []
        self.mode = tk.StringVar(value="mock")
        self.symbols = tk.StringVar(value="HAL.NS")
        self.status = tk.StringVar(value="Ready. Recommendations only; no orders are placed.")
        self._build()
        self.pack(fill="both", expand=True)
        self.after(100, self._poll)

    def _build(self):
        self.master.title("Saadhya Market Recommendations")
        self.master.minsize(900, 620)

        controls = ttk.LabelFrame(self, text="Market scan", padding=12)
        controls.pack(fill="x")
        ttk.Label(controls, text="Symbols (comma-separated):").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.symbols, width=55).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Label(controls, text="Data:").grid(row=0, column=2, sticky="w")
        ttk.Combobox(controls, textvariable=self.mode, values=("mock", "live"), state="readonly", width=9).grid(row=0, column=3, padx=8)
        self.scan_button = ttk.Button(controls, text="Scan market", command=self.scan)
        self.scan_button.grid(row=0, column=4)
        controls.columnconfigure(1, weight=1)

        ttk.Label(self, textvariable=self.status, wraplength=820).pack(fill="x", pady=(10, 6))

        columns = ("rank", "type", "symbol", "recommendation", "score", "risk")
        self.table = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for name, label, width in (
            ("rank", "Rank", 60), ("type", "Type", 90), ("symbol", "Symbol", 130),
            ("recommendation", "Recommendation", 250), ("score", "Score", 70), ("risk", "Risk", 90),
        ):
            self.table.heading(name, text=label)
            self.table.column(name, width=width, anchor="center")
        self.table.pack(fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self._show_selected)

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=10)
        self.export_button = ttk.Button(actions, text="Export JSON", command=self.export_json, state="disabled")
        self.export_button.pack(side="right")
        ttk.Label(actions, text="Results are research only and are not trade instructions.").pack(side="left")

        details = ttk.LabelFrame(self, text="Details and source warnings", padding=8)
        details.pack(fill="both", expand=False)
        self.details = tk.Text(details, height=9, wrap="word", state="disabled")
        self.details.pack(fill="both", expand=True)

    def scan(self):
        symbols = tuple(item.strip().upper() for item in self.symbols.get().split(",") if item.strip())
        if not symbols:
            messagebox.showerror("Saadhya", "Enter at least one symbol, for example HAL.NS.")
            return
        self.scan_button.configure(state="disabled")
        self.export_button.configure(state="disabled")
        self.status.set("Scanning market data. This may take a moment in live mode.")
        threading.Thread(target=self._scan_worker, args=(symbols, self.mode.get()), daemon=True).start()

    def _scan_worker(self, symbols, data_mode):
        try:
            from app.cli.market_scan import build_market_scanner

            scanner = build_market_scanner(data_mode=data_mode, symbols=symbols)
            app = SaadhyaApp(report_engine=RecommendationReport(limit=10))
            output = StringIO()
            report = run(scanner, app, output, data_mode=data_mode)
            self._queue.put(
                ("success", report, scanner.last_opportunities, output.getvalue())
            )
        except Exception:
            self._queue.put(("error", traceback.format_exc()))

    def _poll(self):
        try:
            message = self._queue.get_nowait()
        except queue.Empty:
            self.after(100, self._poll)
            return

        if message[0] == "error":
            self.status.set("Scan failed. See details for the technical reason.")
            self._set_details(message[1])
        else:
            _, self.report, self.opportunities, rendered = message
            self._render_report(rendered)
            self.status.set(
                f"Scan complete: {self.report['total_opportunities']} opportunities. "
                "No orders were placed."
            )
            self.export_button.configure(state="normal")
        self.scan_button.configure(state="normal")
        self.after(100, self._poll)

    def _render_report(self, rendered):
        self.table.delete(*self.table.get_children())
        for item in self.report["top_opportunities"]:
            self.table.insert("", "end", values=(
                item["rank"], item["type"], item["symbol"], item["recommendation"],
                item["score"], item["risk"],
            ))
        self._set_details(rendered)

    def _show_selected(self, _event):
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0], "values")
        symbol = values[2]
        matches = [item for item in self.opportunities if item["symbol"] == symbol]
        warnings = []
        for item in matches:
            warnings.extend(item.get("details", {}).get("warnings", []))
        content = f"{values[2]}\n{values[3]}\nScore: {values[4]} | Risk: {values[5]}"
        if warnings:
            content += "\n\nWarnings:\n- " + "\n- ".join(warnings)
        self._set_details(content)

    def _set_details(self, content):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", content)
        self.details.configure(state="disabled")

    def export_json(self):
        if self.report is None:
            return
        destination = filedialog.asksaveasfilename(
            title="Save Saadhya report", defaultextension=".json",
            filetypes=(("JSON report", "*.json"),), initialfile="saadhya-report.json",
        )
        if not destination:
            return
        Path(destination).write_text(json.dumps(self.report, indent=2), encoding="utf-8")
        self.status.set(f"Report saved to {destination}")


def main():
    root = tk.Tk()
    SaadhyaDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
