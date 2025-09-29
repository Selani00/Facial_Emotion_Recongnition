# import os
# import subprocess
# import time
# import threading
# import webbrowser
# from winotify import Notification, audio
# import urllib
# import win32api
# import win32gui
# import win32com.shell.shell as shell
# import threading
# import time
# import ctypes
# import win32con
# from typing import Union
# from win32com.shell import shellcon
# from rapidfuzz import fuzz, process as rf_process
# import psutil
# import re
# from typing import List, Optional

# try:
#     # Selenium setup for web apps—allows controlled close
#     from selenium import webdriver
#     from selenium.webdriver.chrome.service import Service
#     from selenium.webdriver.chrome.options import Options
#     _SELENIUM_AVAILABLE = True
# except ImportError:
#     _SELENIUM_AVAILABLE = False

# SEARCH_PATTERNS = {
#     "youtube": "https://www.youtube.com/results?search_query={query}",
#     "spotify": "https://open.spotify.com/search/{query}",
#     "google": "https://www.google.com/search?q={query}"
# }

# def open_recommendations(chosen_recommendation: dict) -> tuple:
#     """
#     Launches a local app or opens a web app with auto-close after 20 seconds
#     Includes notification before closing
#     """
#     app_name = chosen_recommendation.get("app_name", "Unknown App")
#     app_url = chosen_recommendation.get("app_url", "")
#     search_query = chosen_recommendation.get("search_query", "")
#     is_local = chosen_recommendation.get("isLocal", False)

#     # Initialize pid as None to prevent "referenced before assignment" errors
#     pid = None

#     def get_uwp_process_name_from_aumid(app_name: str) -> Union[str, None]:
#         """
#         Finds the first process whose executable name and the passed app_name have a mutual substring relationship:
#         - either the app_name is in the process name, OR
#         - the process name is in the app_name (case insensitive).
        
#         Returns the PID of the first matching process or None if not found.
#         """
#         app_name_lower = app_name.lower()
#         pids = []

#         try:
#             for proc in psutil.process_iter(['name', 'pid']):
#                 print("procs:", proc)
#                 proc_name = proc.info['name']
#                 if not proc_name:
#                     continue
#                 print("proc name:", proc_name)
#                 proc_name_lower = proc_name.lower()
                
#                 # Normalize both strings by removing extensions like '.exe', '.bat', etc.
#                 proc_name_base = proc_name_lower.rsplit('.', 1)[0]  # e.g. "solitaire.exe" -> "solitaire"
#                 app_name_base = app_name_lower.rsplit('.', 1)[0]    # in case app_name has extension
                
#                 # Condition:
#                 if (app_name_base in proc_name_base) or (proc_name_base in app_name_base):
#                     print("proc pid of selected app",proc.info['pid'])
#                     pids.append(proc.info['pid'])
#                 print("could not go inside condition pid find",proc.info['pid'])
#             return pids
                
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#         except Exception as e:
#             print(f"Error while searching for process: {e}")
        
#         return None

#     def send_reminder_notification():
#         """Send reminder notification before closing"""
#         try:
#             icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "res", "Icon.ico")
#             icon_path = os.path.abspath(icon_path) if os.path.exists(icon_path) else None
            
#             toast = Notification(
#                 app_id="EMOFI",
#                 title="Time's Up!",
#                 msg=f"Closing {app_name} to help you focus",
#                 duration="long",
#                 icon=icon_path
#             )
#             toast.add_actions(label="Got it")
#             toast.show()
#             print("[Notification] Sent reminder")
#         except Exception as e:
#             print(f"[Notification Error] {e}")

#     def close_local_app(identifier: Union[str, int]):
#         """Helper to close local app and its children"""
#         try:
#             # Send reminder notification
#             send_reminder_notification()
            
#             # Give user a moment to see notification
#             time.sleep(2)
            
#             if isinstance(identifier, str):
#                 # Check if identifier is a process name (for UWP apps)
#                 pids = get_uwp_process_name_from_aumid(identifier)
#                 #pids = find_best_matching_process(identifier)
#                 print("pid found in close app aumid:", pids)
#                 if not pids:
#                     print(f"[Auto-Close] No running process found matching '{identifier}'")
#                     return
#                 for pid in pids:
#                     try:
#                         proc = psutil.Process(pid)
#                         # Kill children recursively
#                         for child in proc.children(recursive=True):
#                             try:
#                                 child.kill()
#                             except psutil.NoSuchProcess:
#                                 pass
#                         proc.kill()
#                         print(f"[Auto-Close] Closed process '{proc.name()}' (PID: {pid}) and its children")
#                     except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
#                         print(f"[Auto-Close] Could not close PID {pid}: {e}")
                
#             # elif isinstance(identifier, int):
#             #     try:
#             #         proc = psutil.Process(identifier)
#             #         for child in proc.children(recursive=True):
#             #             try:
#             #                 child.kill()
#             #             except psutil.NoSuchProcess:
#             #                 pass
#             #         proc.kill()
#             #         print(f"[Auto-Close] Closed process PID: {identifier} and its children")
#             #     except psutil.NoSuchProcess:
#             #         print(f"[Auto-Close] Process PID {identifier} does not exist")
#             #     except psutil.AccessDenied as e:
#             #         print(f"[Auto-Close] Access denied closing PID {identifier}: {e}")

#             else:
#                 print("[Auto-Close] Invalid identifier type: must be str or int")
#         except Exception as e:
#             print(f"[Auto-Close] Error closing app: {e}")

#     def close_web_driver(driver):
#         """Helper to close web driver"""
#         try:
#             # Send reminder notification
#             send_reminder_notification()
            
#             # Give user a moment to see notification
#             time.sleep(2)
            
#             # Close browser
#             driver.quit()
#             print("[Auto-Close] Closed web browser")
#         except Exception as e:
#             print(f"[Auto-Close] Error closing browser: {e}")

#     def build_url(app_url: str, search_query: str) -> str:
#         """Build full URL with search query"""
#         if "<search_query>" in app_url:
#             if search_query:
#                 encoded_query = urllib.parse.quote(search_query.strip())
#                 return app_url.replace("<search_query>", encoded_query)
#             return app_url.replace("<search_query>", "")
#         elif search_query:
#             delimiter = "&" if "?" in app_url else "?"
#             return f"{app_url}{delimiter}search_query={urllib.parse.quote(search_query.strip())}"
#         return app_url
    
#         # 1) Local app (AUMID)
#     if is_local and "!" in app_url:
#         print(f"[Launch] {app_name} using AUMID: {app_url}")
#         try:
            
#             # Use the 'start shell:' command to open the UWP app via its AUMID
#             cmd = f"start shell:AppsFolder\\{app_url}"
#             proc = subprocess.run(cmd, shell=True, check=True)
            
#             print(f"[Local App] Launched {app_name} with PID: {pid}")

#             # Start auto-close timer
#             threading.Timer(20.0, close_local_app, args=(app_name,)).start()

#             return True, pid, 'local'
            
#         except Exception as ex:
#             print(f"Error launching local app via AUMID: {ex}")
#             return False, None, None

#     # 1) Local app path
#     elif is_local:
#         if not app_url or not os.path.isfile(app_url):
#             print(f"Error: Invalid path for local app '{app_name}': {app_url}")
#             return False, None, None

#         try:
#             print(f"[Launch] {app_name} from {app_url}")
#             # proc = subprocess.Popen([app_url])
#             shell.ShellExecuteEx(
#                 lpVerb='runas',
#                 lpFile=app_url,
#                 lpParameters='',
#                 nShow=win32con.SW_SHOWNORMAL
#             )
#             print(f"[Local App] Launched {app_name} with PID: {pid}")
            
            
#             # Start auto-close timer
#             threading.Timer(20.0, close_local_app, args=(app_name,)).start()
            
#             return True, pid, 'local'
#         except Exception as ex:
#             print(f"Error launching local app: {ex}")
#             return False, None, None

#     # 2) Web app
#     else:
#         if not app_url.startswith(("http://", "https://")):
#             print(f"Error: Invalid URL for web app '{app_name}': {app_url}")
#             return False, None, None

#         url = build_url(app_url, search_query)

#         # Use Selenium for web apps to enable auto-close
#         if _SELENIUM_AVAILABLE:
#             try:
#                 options = Options()
#                 options.add_argument("--start-maximized")
#                 driver = webdriver.Chrome(options=options)
#                 driver.get(url)
#                 print(f"[Selenium] Opened {app_name} at {url}")
                
#                 # Start auto-close timer
#                 threading.Timer(20.0, close_web_driver, args=(driver,)).start()
                
#                 return True, driver, 'web'
#             except Exception as ex:
#                 print(f"Selenium error: {ex}")
#                 # Fall through to webbrowser method

#         # Fallback to default browser (no auto-close)
#         try:
#             webbrowser.open(url)
#             print(f"[Webbrowser] Opened {app_name} at {url}")
            
#             # Send notification that we can't auto-close
#             try:
#                 toast = Notification(
#                     app_id="EMOFI",
#                     title="No Auto-Close",
#                     msg=f"Opened in default browser. Close manually when done.",
#                     duration="long"
#                 )
#                 toast.show()
#             except Exception:
#                 pass
            
#             return True, None, 'web'
#         except Exception as ex:
#             print(f"Webbrowser error: {ex}")
#             return False, None, None
            
#     return False, None, None


# ///////////////////////////////////////////////////////////////////partially correct
import os
import subprocess
import time
import threading
import webbrowser
from winotify import Notification
import urllib
import win32com.shell.shell as shell
import win32con
import psutil
import re
from typing import Union

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    _SELENIUM_AVAILABLE = True
except ImportError:
    _SELENIUM_AVAILABLE = False

def send_reminder_notification(app_name: str):
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "res", "Icon.ico")
        icon_path = os.path.abspath(icon_path) if os.path.exists(icon_path) else None
        
        toast = Notification(
            app_id="EMOFI",
            title="Time's Up!",
            msg=f"Closing {app_name} to help you focus",
            duration="long",
            icon=icon_path
        )
        toast.add_actions(label="Got it")
        toast.show()
        print("[Notification] Sent reminder")
    except Exception as e:
        print(f"[Notification Error] {e}")

  
def smart_tokenize(name: str):
    """
    Tokenizes a string into meaningful parts for flexible matching:
    - Splits on any non-alphanumeric characters (hyphens, dots, spaces, underscores).
    - Splits camelCase boundaries.
    - Filters out common ignore tokens like 'exe'.
    """
    name = name.lower()
    # Split on non-alphanumeric chars first
    parts = re.split(r'[^a-z0-9]+', name)
    filtered = [p for p in parts if p and p != 'exe']
    tokens = []
    # Further split camelCase parts
    for part in filtered:
        camel_parts = re.findall(r'[a-z]+|[0-9]+|[A-Z][a-z]*', part) or [part]
        tokens.extend(camel_parts)
    return tokens


def partial_token_match(name1: str, name2: str) -> bool:
    tokens1 = smart_tokenize(name1)
    tokens2 = smart_tokenize(name2)
    print("appname1", tokens1)
    print("appname2", tokens2)
    for t1 in tokens1:
        for t2 in tokens2:
            if t1 in t2 or t2 in t1:
                return True
    return False


def get_processes_started_after(timestamp: float, name_substr: str):
    matched = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
        try:
            proc_name = proc.info['name']
            if proc.info['create_time'] > timestamp:
                if partial_token_match(proc_name, name_substr):
                    matched.append(proc)
                    print(f"[Debug] matched proc: {proc.info['name']} PID: {proc.info['pid']}")
                else:
                    # Check if any partial token match against full joined cmdline string
                    if proc.info['cmdline']:
                        cmdline_str = ' '.join(proc.info['cmdline'])
                        if partial_token_match(cmdline_str, name_substr):
                            matched.append(proc)
                            print(f"[Debug] matched proc by cmdline: {proc_name} PID: {proc.info['pid']}")
        except (psutil.NoSuchProcess, KeyError):
            continue
    return matched

def close_process_tree(proc: psutil.Process):
    try:
        children = proc.children(recursive=True)
        for child in children:
            try:
                print(f"[Debug] Terminating child process {child.pid} ({child.name()})")
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        print(f"[Debug] Terminating parent process {proc.pid} ({proc.name()})")
        proc.terminate()
        gone, alive = psutil.wait_procs([proc] + children, timeout=5)
        for p in alive:
            try:
                print(f"[Debug] Killing unresponsive process {p.pid} ({p.name()})")
                p.kill()
            except psutil.NoSuchProcess:
                pass
        print(f"[Auto-Close] Terminated process {proc.name()} (PID: {proc.pid}) and its children")
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"[Auto-Close] Could not terminate PID {proc.pid}: {e}")

def close_local_app(app_name: str, launch_time: float):
    send_reminder_notification(app_name)
    time.sleep(2)  # pause to display notification
    
    procs = get_processes_started_after(launch_time, app_name)
    print("[pids taken]: ", procs)
    if not procs:
        print(f"[Auto-Close] No running processes found matching '{app_name}'.")
        return
    
    for proc in procs:
        close_process_tree(proc)

def build_url(app_url: str, search_query: str) -> str:
    if "<search_query>" in app_url:
        if search_query:
            encoded_query = urllib.parse.quote(search_query.strip())
            return app_url.replace("<search_query>", encoded_query)
        return app_url.replace("<search_query>", "")
    elif search_query:
        delimiter = "&" if "?" in app_url else "?"
        return f"{app_url}{delimiter}search_query={urllib.parse.quote(search_query.strip())}"
    return app_url

def open_recommendations(chosen_recommendation: dict) -> tuple:
    app_name = chosen_recommendation.get("app_name", "Unknown App")
    app_url = chosen_recommendation.get("app_url", "")
    search_query = chosen_recommendation.get("search_query", "")
    is_local = chosen_recommendation.get("isLocal", False)

    launch_time = time.time()

    if is_local and "!" in app_url:  # UWP app AUMID
        print(f"[Launch] {app_name} using AUMID: {app_url}")
        try:
            cmd = f'start shell:AppsFolder\\{app_url}'
            subprocess.run(cmd, shell=True, check=True)
            print(f"[Local App] Launched {app_name}")
            threading.Timer(20.0, close_local_app, args=(app_name, launch_time)).start()
            return True, None, 'local'
        except Exception as ex:
            print(f"Error launching local app via AUMID: {ex}")
            return False, None, None

    elif is_local:
        if not app_url or not os.path.isfile(app_url):
            print(f"Error: Invalid path for local app '{app_name}': {app_url}")
            return False, None, None
        try:
            print(f"[Launch] {app_name} from {app_url}")
            shell.ShellExecuteEx(
                lpVerb='runas',
                lpFile=app_url,
                lpParameters='',
                nShow=win32con.SW_SHOWNORMAL
            )
            print(f"[Local App] Launched {app_name}")
            threading.Timer(20.0, close_local_app, args=(app_name, launch_time)).start()
            return True, None, 'local'
        except Exception as ex:
            print(f"Error launching local app: {ex}")
            return False, None, None

    else:
        if not app_url.startswith(("http://", "https://")):
            print(f"Error: Invalid URL for web app '{app_name}': {app_url}")
            return False, None, None

        url = build_url(app_url, search_query)

        if _SELENIUM_AVAILABLE:
            try:
                options = Options()
                options.add_argument("--start-maximized")
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                print(f"[Selenium] Opened {app_name} at {url}")
                threading.Timer(20.0, lambda: close_web_driver(driver)).start()
                return True, driver, 'web'
            except Exception as ex:
                print(f"Selenium error: {ex}")

        try:
            webbrowser.open(url)
            print(f"[Webbrowser] Opened {app_name} at {url}")
            try:
                toast = Notification(
                    app_id="EMOFI",
                    title="No Auto-Close",
                    msg=f"Opened in default browser. Close manually when done.",
                    duration="long"
                )
                toast.show()
            except Exception:
                pass
            return True, None, 'web'
        except Exception as ex:
            print(f"Webbrowser error: {ex}")
            return False, None, None

    return False, None, None

def close_web_driver(driver):
    try:
        send_reminder_notification("web browser")
        time.sleep(2)
        driver.quit()
        print("[Auto-Close] Closed web browser")
    except Exception as e:
        print(f"[Auto-Close] Error closing browser: {e}")

#############################################################

# import os
# import subprocess
# import time
# import threading
# import webbrowser
# from winotify import Notification, audio
# import urllib
# import win32api
# import win32gui
# import win32com.shell.shell as shell
# import threading
# import time
# import ctypes
# import win32con
# from typing import Union
# from win32com.shell import shellcon
# from rapidfuzz import fuzz, process as rf_process
# import psutil
# import re
# from typing import List, Optional
# from database.db import get_app_data,get_connection

# def get_uwp_process_name_from_aumid(app_name: str) -> Union[str, None]:
#     """
#     Finds the first process whose executable name and the passed app_name have a mutual substring relationship:
#     - either the app_name is in the process name, OR
#     - the process name is in the app_name (case insensitive).
    
#     Returns the PID of the first matching process or None if not found.
#     """
#     app_name_lower = app_name.lower()
#     pids = []

#     try:
#         for proc in psutil.process_iter(['name', 'pid', 'exe', 'create_time']):
#             print("procs:", proc)
#             proc_name = (proc.info['name'] or "").lower()
#             exe = (proc.info['exe'] or "").lower()
#             if not proc_name:
#                 continue
#             print("proc name:", proc_name)
            
#             # Normalize both strings by removing extensions like '.exe', '.bat', etc.
#             proc_name_base = proc_name.rsplit('.', 1)[0]  # e.g. "solitaire.exe" -> "solitaire"
#             app_name_base = app_name_lower.rsplit('.', 1)[0]    # in case app_name has extension
            
#             # Condition:
#             if (app_name_base in proc_name_base) or (proc_name_base in app_name_base) or (app_name_base in  exe):
#                 print("proc pid of selected app",proc.info['pid'])
#                 parent = proc.parent()
#                 if not parent or (
#                     app_name_base not in (parent.name() or "").lower()
#                     and app_name_base not in (parent.exe() or "").lower()
#                 ):
#                     pids.append(proc)
#             print("could not go inside condition pid find",proc.info['pid'])
#         if not pids:
#             return None
#         # Pick the newest by create_time
#         newest_proc = max(pids, key=lambda p: p.info['create_time'])
#         return newest_proc.info['pid']
            
#     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#         pass
#     except Exception as e:
#         print(f"Error while searching for process: {e}")
    
#     return None

# try:
#     # Selenium setup for web apps—allows controlled close
#     from selenium import webdriver
#     from selenium.webdriver.chrome.service import Service
#     from selenium.webdriver.chrome.options import Options
#     _SELENIUM_AVAILABLE = True
# except ImportError:
#     _SELENIUM_AVAILABLE = False

# SEARCH_PATTERNS = {
#     "youtube": "https://www.youtube.com/results?search_query={query}",
#     "spotify": "https://open.spotify.com/search/{query}",
#     "google": "https://www.google.com/search?q={query}"
# }

# def open_recommendations(chosen_recommendation: dict) -> tuple:
#     """
#     Launches a local app or opens a web app with auto-close after 20 seconds
#     Includes notification before closing
#     """
#     app_name = chosen_recommendation.get("app_name", "Unknown App")
#     app_url = chosen_recommendation.get("app_url", "")
#     search_query = chosen_recommendation.get("search_query", "")
#     is_local = chosen_recommendation.get("isLocal", False)
#     conn = get_connection()

#     print("Chosen Recommendation:", chosen_recommendation)
#     app_info = get_app_data(conn, app_name=app_name.lower())
#     print("[App Data]:", app_info)

#     # Initialize pid as None to prevent "referenced before assignment" errors
#     pid = None

#     def get_uwp_process_name_from_aumid(app_name: str) -> Union[str, None]:
#         """
#         Finds the first process whose executable name and the passed app_name have a mutual substring relationship:
#         - either the app_name is in the process name, OR
#         - the process name is in the app_name (case insensitive).
        
#         Returns the PID of the first matching process or None if not found.
#         """
#         app_name_lower = app_name.lower()
#         pids = []

#         try:
#             for proc in psutil.process_iter(['name', 'pid']):
#                 print("procs:", proc)
#                 proc_name = proc.info['name']
#                 if not proc_name:
#                     continue
#                 print("proc name:", proc_name)
#                 proc_name_lower = proc_name.lower()
                
#                 # Normalize both strings by removing extensions like '.exe', '.bat', etc.
#                 proc_name_base = proc_name_lower.rsplit('.', 1)[0]  # e.g. "solitaire.exe" -> "solitaire"
#                 app_name_base = app_name_lower.rsplit('.', 1)[0]    # in case app_name has extension
                
#                 # Condition:
#                 if (app_name_base in proc_name_base) or (proc_name_base in app_name_base):
#                     print("proc pid of selected app",proc.info['pid'])
#                     pids.append(proc.info['pid'])
#                 print("could not go inside condition pid find",proc.info['pid'])
#             return pids
                
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#         except Exception as e:
#             print(f"Error while searching for process: {e}")
        
#         return None

#     def send_reminder_notification():
#         """Send reminder notification before closing"""
#         try:
#             icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "res", "Icon.ico")
#             icon_path = os.path.abspath(icon_path) if os.path.exists(icon_path) else None
            
#             toast = Notification(
#                 app_id="EMOFI",
#                 title="Time's Up!",
#                 msg=f"Closing {app_name} to help you focus",
#                 duration="long",
#                 icon=icon_path
#             )
#             toast.add_actions(label="Got it")
#             toast.show()
#             print("[Notification] Sent reminder")
#         except Exception as e:
#             print(f"[Notification Error] {e}")

#     def close_app_by_pid(pid):
#         try:
#             proc = psutil.Process(pid)

#             # Get all child processes (recursively)
#             children = proc.children(recursive=True)

#             # Terminate children first
#             for child in children:
#                 try:
#                     child.terminate()
#                 except psutil.NoSuchProcess:
#                     pass

#             # Wait for children to terminate
#             psutil.wait_procs(children, timeout=5)

#             # Now terminate the main process
#             proc.terminate()
#             proc.wait(timeout=5)
#             print(f"Process {pid} and its children terminated.")

#         except psutil.NoSuchProcess:
#             print(f"No process found with PID {pid}.")

#         except psutil.TimeoutExpired:
#             print(f"Process {pid} did not terminate in time, killing it and its children.")
#             # Kill remaining children
#             for child in children:
#                 try:
#                     child.kill()
#                 except psutil.NoSuchProcess:
#                     pass
#             proc.kill()

#         except Exception as e:
#             print(f"Error terminating process {pid}: {e}")

#     def close_local_app(identifier: Union[str, int]):
#         """Helper to close local app and its children"""
#         try:
#             # Send reminder notification
#             send_reminder_notification()
            
#             # Give user a moment to see notification
#             time.sleep(2)
            
#             if isinstance(identifier, str):
#                 # Check if identifier is a process name (for UWP apps)
#                 pids = get_uwp_process_name_from_aumid(identifier)
#                 #pids = find_best_matching_process(identifier)
#                 print("pid found in close app aumid:", pids)
#                 if not pids:
#                     print(f"[Auto-Close] No running process found matching '{identifier}'")
#                     return
#                 for pid in pids:
#                     try:
#                         proc = psutil.Process(pid)
#                         # Kill children recursively
#                         for child in proc.children(recursive=True):
#                             try:
#                                 child.kill()
#                             except psutil.NoSuchProcess:
#                                 pass
#                         proc.kill()
#                         print(f"[Auto-Close] Closed process '{proc.name()}' (PID: {pid}) and its children")
#                     except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
#                         print(f"[Auto-Close] Could not close PID {pid}: {e}")
                
#             elif isinstance(identifier, int):
#                 try:
#                     proc = psutil.Process(identifier)
#                     for child in proc.children(recursive=True):
#                         try:
#                             child.kill()
#                         except psutil.NoSuchProcess:
#                             pass
#                     proc.kill()
#                     print(f"[Auto-Close] Closed process PID: {identifier} and its children")
#                 except psutil.NoSuchProcess:
#                     print(f"[Auto-Close] Process PID {identifier} does not exist")
#                 except psutil.AccessDenied as e:
#                     print(f"[Auto-Close] Access denied closing PID {identifier}: {e}")

#             else:
#                 print("[Auto-Close] Invalid identifier type: must be str or int")
#         except Exception as e:
#             print(f"[Auto-Close] Error closing app: {e}")

#     def close_web_driver(driver):
#         """Helper to close web driver"""
#         try:
#             # Send reminder notification
#             send_reminder_notification()
            
#             # Give user a moment to see notification
#             time.sleep(2)
            
#             # Close browser
#             driver.quit()
#             print("[Auto-Close] Closed web browser")
#         except Exception as e:
#             print(f"[Auto-Close] Error closing browser: {e}")

#     def build_url(app_url: str, search_query: str) -> str:
#         """Build full URL with search query"""
#         if "<search_query>" in app_url:
#             if search_query:
#                 encoded_query = urllib.parse.quote(search_query.strip())
#                 return app_url.replace("<search_query>", encoded_query)
#             return app_url.replace("<search_query>", "")
#         elif search_query:
#             delimiter = "&" if "?" in app_url else "?"
#             return f"{app_url}{delimiter}search_query={urllib.parse.quote(search_query.strip())}"
#         return app_url
    
#     # 1) Local app (AUMID)
#     if is_local and "!" in app_url:
#         print(f"[Launch] {app_name} using AUMID: {app_url}")
#         try:
#             subprocess.Popen(f'explorer shell:AppsFolder\\{app_url}', shell=True)
#             print(f"[Launch] UWP app: {app_name}")
#             found_pid = get_uwp_process_name_from_aumid(app_name)
#             print(f"[Local App] Found PID: {found_pid} for app '{app_name}'")

#             if not found_pid:
#                 print(f"[Local App] No matching PID found for {app_name}")
#                 return False, None, None
#             # Start auto-close timer
#             threading.Timer(20.0, close_app_by_pid, args=(found_pid,)).start()

#             return True, found_pid, 'local'
            
#         except Exception as ex:
#             print(f"Error launching local app via AUMID: {ex}")
#             return False, None, None

#     # 1) Local app path
#     elif is_local:
#         if not app_url or not os.path.isfile(app_url):
#             print(f"[Error] Executable not found: {app_url}")
#             return False

#         try:
#             shell.ShellExecuteEx(
#                 lpVerb='runas',
#                 lpFile=app_url,
#                 lpParameters='',
#                 nShow=win32con.SW_SHOWNORMAL
#             )
#             print(f"[Launch] Classic app as Admin: {app_url}")

#             found_pid = get_uwp_process_name_from_aumid(app_name)
#             print(f"[Local App] Found PID: {found_pid} for app '{app_name}'")
#             if not found_pid:
#                 print(f"[Local App] No matching PID found for {app_name}")
#                 return False, None, None
#             # Start auto-close timer
#             threading.Timer(20.0, close_app_by_pid, args=(found_pid,)).start()
            
#             return True, found_pid, 'local'
#         except Exception as ex:
#             print(f"Error launching local app: {ex}")
#             return False, None, None

#     # 2) Web app
#     else:
#         if not app_url.startswith(("http://", "https://")):
#             print(f"Error: Invalid URL for web app '{app_name}': {app_url}")
#             return False, None, None

#         url = build_url(app_url, search_query)

#         # Use Selenium for web apps to enable auto-close
#         if _SELENIUM_AVAILABLE:
#             try:
#                 options = Options()
#                 options.add_argument("--start-maximized")
#                 driver = webdriver.Chrome(options=options)
#                 driver.get(url)
#                 print(f"[Selenium] Opened {app_name} at {url}")
                
#                 # Start auto-close timer
#                 threading.Timer(20.0, close_web_driver, args=(driver,)).start()
                
#                 return True, driver, 'web'
#             except Exception as ex:
#                 print(f"Selenium error: {ex}")
#                 # Fall through to webbrowser method

#         # Fallback to default browser (no auto-close)
#         try:
#             webbrowser.open(url)
#             print(f"[Webbrowser] Opened {app_name} at {url}")
            
#             # Send notification that we can't auto-close
#             try:
#                 toast = Notification(
#                     app_id="EMOFI",
#                     title="No Auto-Close",
#                     msg=f"Opened in default browser. Close manually when done.",
#                     duration="long"
#                 )
#                 toast.show()
#             except Exception:
#                 pass
            
#             return True, None, 'web'
#         except Exception as ex:
#             print(f"Webbrowser error: {ex}")
#             return False, None, None
            
#     return False, None, None