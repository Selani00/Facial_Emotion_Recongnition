from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents import (
    average_emotion_agent,
    task_detection_agent,
    recommendation_agent,
    task_execution_agent,
    task_exit_agent
)

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("calculate_emotion", average_emotion_agent)
    workflow.add_node("detect_task", task_detection_agent)
    workflow.add_node("generate_recommendation", recommendation_agent)
    workflow.add_node("execute_action", task_execution_agent)
    workflow.add_node("exit_action", task_exit_agent)
    workflow.set_entry_point("calculate_emotion")
    workflow.add_edge("calculate_emotion", "detect_task")
    workflow.add_edge("detect_task", "generate_recommendation")
    # workflow.add_edge("calculate_emotion", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "execute_action")
    workflow.add_edge("execute_action", "exit_action")
    workflow.add_edge("exit_action", END)
    return workflow.compile()

agent_workflow = create_workflow()

def process_agent_system(emotions):
    from .state import AgentState
    initial_state = AgentState(
        emotions=emotions,
        average_emotion=None,
        detected_task=None,
        recommendation=None,
        recommendation_options=[],
        executed=False,
        action_executed = None,
        action_time_start = 0
    )
    return agent_workflow.invoke(initial_state)


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
# from win32com.shell import shellcon
# import customtkinter as ctk
# import psutil
# import win32process
# from database.db import get_app_data,get_connection

# def get_newest_parent_pid_by_app_name(app_name):
#     """Return the newest parent PID that matches app_name."""
#     app_name = app_name.lower()
#     candidates = []

#     for proc in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
#         try:
#             name = (proc.info['name'] or "").lower()
#             exe = (proc.info['exe'] or "").lower()

#             if app_name in name.lower() or app_name in exe.lower():
#                 parent = proc.parent()
#                 # Only include if no parent or parent's name/exe doesn't match
#                 if not parent or (
#                     app_name not in (parent.name() or "").lower()
#                     and app_name not in (parent.exe() or "").lower()
#                 ):
#                     candidates.append(proc)
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             continue

#     if not candidates:
#         return None

#     # Pick the newest by create_time
#     newest_proc = max(candidates, key=lambda p: p.info['create_time'])
#     return newest_proc.info['pid']

# try:
#     # Selenium setup for web apps—allows controlled close
#     from selenium import webdriver
#     from selenium.webdriver.chrome.service import Service
#     from selenium.webdriver.chrome.options import Options
#     _SELENIUM_AVAILABLE = True
# except ImportError:
#     _SELENIUM_AVAILABLE = False


  
# def open_recommendations(chosen_recommendation: dict) -> tuple:
#     """
#     Launches a local app or opens a web app with auto-close after 20 seconds
#     Includes notification before closing
#     """
#     # get app_type from database    
    
#     app_name = chosen_recommendation.get("app_name", "Unknown App")
#     app_url = chosen_recommendation.get("app_url", "")
#     search_query = chosen_recommendation.get("search_query", "")
#     is_local = chosen_recommendation.get("is_local", False)
#     conn = get_connection()

#     print("Chosen Recommendation:", chosen_recommendation)
#     app_info = get_app_data(conn, app_name.lower())
#     print("[App Data]:", app_info)

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
#             toast.set_audio(audio.Mail, loop=True)
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
    
#     def unified_app_launcher(app_info):
#         try:
#             if app_info["app_type"] == "uwp":
#                 app_id = app_info["app_id"]
#                 subprocess.Popen(f'explorer shell:AppsFolder\\{app_id}', shell=True)
#                 print(f"[Launch] UWP app: {app_info['name']}")
#                 return True

#             elif app_info["app_type"] == "classic":
#                 exe_path = app_info["path"]
#                 if not exe_path or not os.path.isfile(exe_path):
#                     print(f"[Error] Executable not found: {exe_path}")
#                     return False
                
#                 shell.ShellExecuteEx(
#                         lpVerb='runas',
#                         lpFile=exe_path,
#                         lpParameters='',
#                         nShow=win32con.SW_SHOWNORMAL
#                 )
#                 print(f"[Launch] Classic app as Admin: {exe_path}")
#                 return True

#         except Exception as e:
#             print(f"[Launch Error] {e}")
#             return False


#     # 1) Local app path
#     if is_local:
#         try:
#             unified_app_launcher(app_info)
#             print(f"[Admin Launch] Launched")
#             print(f"[Local App] Launched {app_name}")
#             found_pid = get_newest_parent_pid_by_app_name(app_name)
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

#         # check if app name is WhatsApp
#         if app_name.lower() == "whatsapp":
#             show_whatsapp_popup()
#             # wait for 15 seconds to allow user to send message
#             time.sleep(15)

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
#                 toast.set_audio(audio.Mail, loop=True)
#                 toast.show()
#             except Exception:
#                 pass
            
#             return True, None, 'web'
#         except Exception as ex:
#             print(f"Webbrowser error: {ex}")
#             return False, None, None
            
#     return False, None, None