from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass
from http.cookiejar import CookieJar
from typing import Any


@dataclass(frozen=True)
class CompanionState:
    connection: str
    status: dict[str, Any]
    signals: list[dict[str, Any]]
    portfolio: list[dict[str, Any]]


class TradingHelperApiClient:
    def __init__(self, server_url: str, timeout: float = 5.0) -> None:
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    def request(self, path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(
            f"{self.server_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with self.opener.open(request, timeout=self.timeout) as response:
            return json.loads(response.read())

    def login(self, username: str, password: str) -> bool:
        try:
            self.request("/auth/login", "POST", {"username": username, "password": password})
        except (urllib.error.URLError, urllib.error.HTTPError):
            return False
        return True

    def snapshot(self) -> CompanionState:
        try:
            status = self.request("/status")
            signals = self.request("/signals?min_score=60&limit=5")
            portfolio = self.request("/portfolio")
        except urllib.error.HTTPError as exc:
            state = "AUTH_ERROR" if exc.code == 401 else "SERVER_ERROR"
            return CompanionState(state, {}, [], [])
        except urllib.error.URLError:
            return CompanionState("OFFLINE", {}, [], [])
        return CompanionState("ONLINE", status, signals, portfolio)


def run_companion() -> None:  # pragma: no cover - native UI is verified manually
    import tkinter as tk
    from tkinter import ttk

    server_url = os.getenv("TRADING_HELPER_SERVER_URL", "http://127.0.0.1:8787")
    client = TradingHelperApiClient(server_url)
    root = tk.Tk()
    root.title("TradingHelper Companion")
    root.geometry("340x460")
    root.minsize(280, 80)
    status_var = tk.StringVar(value="● CONNECTING")
    top_var = tk.BooleanVar(value=True)
    login_window: tk.Toplevel | None = None
    root.attributes("-topmost", True)
    ttk.Label(root, textvariable=status_var, font=("sans", 11, "bold")).pack(pady=10)
    content = ttk.Frame(root, padding=10)
    content.pack(fill="both", expand=True)

    def toggle_top() -> None:
        root.attributes("-topmost", top_var.get())

    def toggle_mini() -> None:
        if root.geometry().split("+")[0].startswith("340x"):
            root.geometry("300x90")
            content.pack_forget()
        else:
            root.geometry("340x460")
            content.pack(fill="both", expand=True)

    controls = ttk.Frame(root)
    controls.pack(fill="x", padx=10, pady=6)
    ttk.Checkbutton(controls, text="Always On Top", variable=top_var, command=toggle_top).pack(
        side="left"
    )
    ttk.Button(controls, text="Mini", command=toggle_mini).pack(side="right")
    ttk.Button(controls, text="Dashboard", command=lambda: webbrowser.open(server_url)).pack(
        side="right", padx=5
    )

    def show_login() -> None:
        nonlocal login_window
        if login_window is not None and login_window.winfo_exists():
            login_window.lift()
            return
        login_window = tk.Toplevel(root)
        login_window.title("TradingHelper — logowanie")
        login_window.geometry("320x230")
        login_window.resizable(False, False)
        login_window.transient(root)
        login_window.grab_set()
        form = ttk.Frame(login_window, padding=18)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Nazwa użytkownika").pack(anchor="w")
        username = ttk.Entry(form)
        username.insert(0, os.getenv("TRADING_HELPER_USERNAME", "trader"))
        username.pack(fill="x", pady=(3, 12))
        ttk.Label(form, text="Hasło").pack(anchor="w")
        password = ttk.Entry(form, show="•")
        password.pack(fill="x", pady=(3, 12))
        error_var = tk.StringVar()
        ttk.Label(form, textvariable=error_var, foreground="#a83232").pack(anchor="w")
        submit = ttk.Button(form, text="Zaloguj")
        submit.pack(anchor="e", pady=(8, 0))

        def finish_login(success: bool) -> None:
            submit.state(["!disabled"])
            if success:
                login_window.destroy()
                start_poll()
            else:
                error_var.set("Nieprawidłowe dane lub brak połączenia z serwerem.")
                password.delete(0, "end")
                password.focus_set()

        def perform_login() -> None:
            success = client.login(username.get().strip(), password.get())
            root.after(0, finish_login, success)

        def submit_login(_event: object | None = None) -> None:
            if not username.get().strip() or not password.get():
                error_var.set("Podaj nazwę użytkownika i hasło.")
                return
            error_var.set("")
            submit.state(["disabled"])
            threading.Thread(target=perform_login, daemon=True).start()

        submit.configure(command=submit_login)
        password.bind("<Return>", submit_login)
        username.focus_set()

    def render(state: CompanionState) -> None:
        status_var.set(f"● {state.connection} · {state.status.get('provider', '—').upper()}")
        for widget in content.winfo_children():
            widget.destroy()
        ttk.Label(content, text="TOP SETUPS", font=("sans", 10, "bold")).pack(anchor="w")
        for item in state.signals:
            button = ttk.Button(
                content,
                text=f"{item['symbol']}    {item['score']}    {item['label']}",
                command=lambda symbol=item["symbol"]: webbrowser.open(
                    f"{server_url}/#signal-{symbol}"
                ),
            )
            button.pack(fill="x", pady=2)
        ttk.Separator(content).pack(fill="x", pady=10)
        ttk.Label(content, text="PORTFOLIO", font=("sans", 10, "bold")).pack(anchor="w")
        for item in state.portfolio[:5]:
            ttk.Label(
                content, text=f"{item['symbol']}  {item['quantity']} @ {item['entry_price']}"
            ).pack(anchor="w", pady=2)
        if state.connection == "AUTH_ERROR":
            ttk.Label(content, text="Zaloguj się do centralnego serwera.").pack(pady=12)
            ttk.Button(content, text="Zaloguj", command=show_login).pack()

    def poll() -> None:
        state = client.snapshot()
        root.after(0, render, state)
        delay = 30_000 if state.connection == "ONLINE" else 10_000
        root.after(delay, start_poll)

    def start_poll() -> None:
        threading.Thread(target=poll, daemon=True).start()

    start_poll()
    root.mainloop()


if __name__ == "__main__":
    run_companion()
