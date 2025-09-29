from utils.tools import open_recommendations
from database.db import get_connection, get_app_data

recommendation = {

    "app_name": "SpotifyMusic",
    "app_url": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify SpotifyWidgetProvider Widget",
    "search_query": "Calming music",
    "isLocal": True
}

if __name__ == "__main__":
    open_recommendations(recommendation)



#MSTeams_8wekyb3d8bbwe!MSTeamsRemoteModuleContainer MSTeams MSTeams.Update msteamsautostarter
#SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify SpotifyWidgetProvider Widget








# import os
# import subprocess
# import time
# import threading
# import webbrowser
# from winotify import Notification
# import urllib
# import win32com.shell.shell as shell
# import win32con
# import psutil
# from typing import Union

# try:
#     from selenium import webdriver
#     from selenium.webdriver.chrome.options import Options
#     _SELENIUM_AVAILABLE = True
# except ImportError:
#     _SELENIUM_AVAILABLE = False


# def send_reminder_notification(app_name: str):
#     try:
#         icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "res", "Icon.ico")
#         icon_path = os.path.abspath(icon_path) if os.path.exists(icon_path) else None
        
#         toast = Notification(
#             app_id="EMOFI",
#             title="Time's Up!",
#             msg=f"Closing {app_name} to help you focus",
#             duration="long",
#             icon=icon_path
#         )
#         toast.add_actions(label="Got it")
#         toast.show()
#         print("[Notification] Sent reminder")
#     except Exception as e:
#         print(f"[Notification Error] {e}")


# def taskkill_process(app_process_name: str):
#     """
#     Use Windows taskkill command to forcefully terminate process(es) by executable name.
#     """
#     try:
#         print(f"[TaskKill] Terminating all '{app_process_name}' processes...")
#         subprocess.run(['taskkill', '/F', '/IM', app_process_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print(f"[TaskKill] Successfully terminated '{app_process_name}'")
#     except subprocess.CalledProcessError as e:
#         print(f"[TaskKill] Failed to terminate '{app_process_name}': {e}")


# def partial_token_match(name1: str, name2: str) -> bool:
#     tokens1 = name1.lower().split()
#     tokens2 = name2.lower().split()
#     for t1 in tokens1:
#         for t2 in tokens2:
#             if t1 in t2 or t2 in t1:
#                 return True
#     return False

# def get_processes_started_after(timestamp: float, app_name: str):
#     matched = []
#     for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline']):
#         try:
#             proc_name = proc.info['name']
#             if proc.info['create_time'] > timestamp and proc_name:
#                 if partial_token_match(proc_name, app_name):
#                     matched.append(proc)
#                     print(f"[Debug] matched proc: {proc_name} PID: {proc.info['pid']}")
#                 else:
#                     # Check if any partial token match against full joined cmdline string
#                     if proc.info['cmdline']:
#                         cmdline_str = ' '.join(proc.info['cmdline'])
#                         if partial_token_match(cmdline_str, app_name):
#                             matched.append(proc)
#                             print(f"[Debug] matched proc by cmdline: {proc_name} PID: {proc.info['pid']}")
#         except (psutil.NoSuchProcess, KeyError):
#             continue
#     return matched



# def close_process_tree(proc: psutil.Process):
#     try:
#         children = proc.children(recursive=True)
#         for child in children:
#             try:
#                 print(f"[Debug] Terminating child process {child.pid} ({child.name()})")
#                 child.terminate()
#             except psutil.NoSuchProcess:
#                 pass
#         print(f"[Debug] Terminating parent process {proc.pid} ({proc.name()})")
#         proc.terminate()
#         gone, alive = psutil.wait_procs([proc] + children, timeout=5)
#         for p in alive:
#             try:
#                 print(f"[Debug] Killing unresponsive process {p.pid} ({p.name()})")
#                 p.kill()
#             except psutil.NoSuchProcess:
#                 pass
#         print(f"[Auto-Close] Terminated process {proc.name()} (PID: {proc.pid}) and its children")
#     except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
#         print(f"[Auto-Close] Could not terminate PID {proc.pid}: {e}")


# def close_local_app(app_name: str, launch_time: float):
#     """
#     Enhanced close local app function:
#     Redirects to taskkill for Spotify and Teams for more reliable closure,
#     otherwise uses psutil method.
#     """
#     send_reminder_notification(app_name)
#     time.sleep(2)  # pause to display notification

#     # Use taskkill for Spotify and Teams
#     if app_name.lower():
#         taskkill_process("Spotify.exe")
#         return

#     # Fallback: use psutil termination for other apps
#     procs = get_processes_started_after(launch_time, app_name)
#     if not procs:
#         print(f"[Auto-Close] No running processes found matching '{app_name}'.")
#         return

#     for proc in procs:
#         close_process_tree(proc)


# def build_url(app_url: str, search_query: str) -> str:
#     if "<search_query>" in app_url:
#         if search_query:
#             encoded_query = urllib.parse.quote(search_query.strip())
#             return app_url.replace("<search_query>", encoded_query)
#         return app_url.replace("<search_query>", "")
#     elif search_query:
#         delimiter = "&" if "?" in app_url else "?"
#         return f"{app_url}{delimiter}search_query={urllib.parse.quote(search_query.strip())}"
#     return app_url


# def open_recommendations(chosen_recommendation: dict) -> tuple:
#     app_name = chosen_recommendation.get("app_name", "Unknown App")
#     app_url = chosen_recommendation.get("app_url", "")
#     search_query = chosen_recommendation.get("search_query", "")
#     is_local = chosen_recommendation.get("isLocal", False)

#     launch_time = time.time()

#     if is_local and "!" in app_url:  # UWP app AUMID
#         print(f"[Launch] {app_name} using AUMID: {app_url}")
#         try:
#             cmd = f'start shell:AppsFolder\\{app_url}'
#             subprocess.run(cmd, shell=True, check=True)
#             print(f"[Local App] Launched {app_name}")
#             threading.Timer(20.0, close_local_app, args=(app_name, launch_time)).start()
#             return True, None, 'local'
#         except Exception as ex:
#             print(f"Error launching local app via AUMID: {ex}")
#             return False, None, None

#     elif is_local:
#         if not app_url or not os.path.isfile(app_url):
#             print(f"Error: Invalid path for local app '{app_name}': {app_url}")
#             return False, None, None
#         try:
#             print(f"[Launch] {app_name} from {app_url}")
#             shell.ShellExecuteEx(
#                 lpVerb='runas',
#                 lpFile=app_url,
#                 lpParameters='',
#                 nShow=win32con.SW_SHOWNORMAL
#             )
#             print(f"[Local App] Launched {app_name}")
#             threading.Timer(20.0, close_local_app, args=(app_name, launch_time)).start()
#             return True, None, 'local'
#         except Exception as ex:
#             print(f"Error launching local app: {ex}")
#             return False, None, None

#     else:
#         if not app_url.startswith(("http://", "https://")):
#             print(f"Error: Invalid URL for web app '{app_name}': {app_url}")
#             return False, None, None

#         url = build_url(app_url, search_query)

#         if _SELENIUM_AVAILABLE:
#             try:
#                 options = Options()
#                 options.add_argument("--start-maximized")
#                 driver = webdriver.Chrome(options=options)
#                 driver.get(url)
#                 print(f"[Selenium] Opened {app_name} at {url}")
#                 threading.Timer(20.0, lambda: close_web_driver(driver)).start()
#                 return True, driver, 'web'
#             except Exception as ex:
#                 print(f"Selenium error: {ex}")

#         try:
#             webbrowser.open(url)
#             print(f"[Webbrowser] Opened {app_name} at {url}")
#             try:
#                 toast = Notification(
#                     app_id="EMOFI",
#                     title="No Auto-Close",
#                     msg="Opened in default browser. Close manually when done.",
#                     duration="long"
#                 )
#                 toast.show()
#             except Exception:
#                 pass
#             return True, None, 'web'
#         except Exception as ex:
#             print(f"Webbrowser error: {ex}")
#             return False, None, None


# def close_web_driver(driver):
#     try:
#         send_reminder_notification("web browser")
#         time.sleep(2)
#         driver.quit()
#         print("[Auto-Close] Closed web browser")
#     except Exception as e:
#         print(f"[Auto-Close] Error closing browser: {e}")
