# Python Modules
import json
import re
import traceback

# Sublime Text 3 Modules
import sublime
import sublime_plugin

# Lib Modules
from .lib import requests
from .lib import constants
from .lib import animations


class EntropyServerConfigurationCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        self.animation      = animations.EntropyServerConfigurationAnimation(self.window)
        self.dw_hostname    = None
        self.dw_username    = None
        self.dw_password    = None
        self.dw_directory   = None
        self.dw_directories = []
        self.dw_enabled     = None

    # Prompt for hostname
    def run(self):
        if not self.window.project_file_name():
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Current window is not associated with a project.\n\n",
                    "Please run \"Project > Save Project As...\" or \"Project > Open Project...\" ",
                    "before atempting to setup your server configuration.",
                ]))
            return

        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})
        panel_label  = "Server Hostname:"
        panel_value  = entropy_data.get("hostname", "")

        self.window.show_input_panel(panel_label, panel_value, self.step1_on_done, None, self.on_cancel)

    # Save the hostname and prompt for username
    def step1_on_done(self, hostname):
        if len(hostname) < 1:
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Server hostname is required!",
                ]))
            return

        self.dw_hostname = hostname

        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})
        panel_label  = "Server Username:"
        panel_value  = entropy_data.get("username", "")

        self.window.show_input_panel(panel_label, panel_value, self.step2_on_done, None, self.on_cancel)

    # Save the username and prompt for password
    def step2_on_done(self, username):
        if len(username) < 1:
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Server username is required!",
                ]))
            return

        self.dw_username = username

        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})
        panel_label  = "Server Password:"
        panel_value  = entropy_data.get("password", "")

        self.window.show_input_panel(panel_label, panel_value, self.step3_on_done, None, self.on_cancel)

    # Save the password and prompt for code directory
    def step3_on_done(self, password):
        if len(password) < 1:
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Server password is required!",
                ]))
            return

        self.dw_password = password

        sublime.set_timeout_async(lambda self=self: self.step4_run_async(), 0)

    # Get the code directories from the server and display the one that's active
    def step4_run_async(self):
        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})
        panel_label  = "Code Directory:"
        panel_value  = entropy_data.get("directory", "")

        entropy_settings       = sublime.load_settings("Entropy.sublime-settings")
        entropy_settings_vssl  = entropy_settings.get("verify_ssl_certificates", True) is True
        entropy_cache_path     = os.path.join(sublime.cache_path(), "Entropy")
        entropy_certs_path     = os.path.join(sublime.cache_path(), "Entropy", "entropy.pem")
        entropy_CA_BUNDLE_PATH = entropy_certs_path if entropy_settings_vssl else False

        self.animation.start()

        try:
            request_url  = "https://{0}/on/demandware.servlet/studiosvc/Sites".format(self.dw_hostname)
            request_auth = (self.dw_username, self.dw_password)
            request_json = {"getAPIVersionReq" : ""}
            api_request  = requests.post(request_url, auth=request_auth, json=request_json, verify=entropy_CA_BUNDLE_PATH)

            # Authentication failed
            if api_request.status_code == requests.codes.UNAUTHORIZED:
                self.on_cancel()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Invalid username or password!",
                    ]))
                return

            if not api_request.ok:
                self.on_cancel()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Failed to retrieve the list of code directories from the server!\n\n",
                        "[{0} - {1}]".format(api_request.status_code, api_request.reason),
                    ]))
                return

            api_response     = api_request.json()
            code_directories = api_response.get("getAPIVersionResp", {}).get("versions", {}).get("aPIVersion", [])

            # In case aPIVersion is a typo and DW will fix it
            if len(code_directories) == 0:
                code_directories = api_response.get("getAPIVersionResp", {}).get("versions", {}).get("APIVersion", [])

            self.dw_directories = []

            for code_directory in code_directories:
                directory_name = code_directory.get("codeDirectory", None)
                is_active      = code_directory.get("isActive", False)

                if directory_name != None:
                    self.dw_directories.append(directory_name)

                if directory_name != None and is_active:
                    panel_label = "Code Directory ({0}):".format(directory_name)

        except (requests.exceptions.RequestException, ValueError) as e:
            self.on_cancel()
            traceback.print_exc()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Error retrieving the active code directory!",
                ]))
            return

        except:
            self.on_cancel()
            traceback.print_exc()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Unknown exception!",
                ]))
            return

        finally:
            self.animation.stop()

        self.window.show_input_panel(panel_label, panel_value, self.step4_on_done, None, self.on_cancel)

    # Save the code directory and prompt if Entropy is enabled for this project
    def step4_on_done(self, code_directory):
        if len(code_directory) < 1:
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Code directory is required!",
                ]))
            return

        self.dw_directory = code_directory

        entropy_settings     = sublime.load_settings("Entropy.sublime-settings")
        entropy_settings_vcd = entropy_settings.get("verify_code_directory", True)

        if entropy_settings_vcd and (not code_directory in self.dw_directories):
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Selected code directory does not exist on the server!",
                ]))
            return

        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})
        panel_label  = "Enabled (Yes/No):"
        panel_value  = entropy_data.get("enabled", "")

        self.window.show_input_panel(panel_label, panel_value, self.step5_on_done, None, self.on_cancel)

    # Save if Entropy is enabled for this project, update server configuration and notify the user
    def step5_on_done(self, enabled):
        if len(enabled) < 1:
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Enabled status is required!",
                ]))
            return

        if not enabled in ("Yes", "No"):
            self.on_cancel()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Invalid input! Only \"Yes\" or \"No\" values are allowed.",
                ]))
            return

        self.dw_enabled = enabled

        entropy_data = {
                "hostname"  : self.dw_hostname,
                "username"  : self.dw_username,
                "password"  : self.dw_password,
                "directory" : self.dw_directory,
                "enabled"   : self.dw_enabled,
            }

        self.dw_hostname    = None
        self.dw_username    = None
        self.dw_password    = None
        self.dw_directory   = None
        self.dw_directories = []
        self.dw_enabled     = None

        project_data = self.window.project_data()
        project_data[constants.PROJECT_DATA_KEY] = entropy_data
        self.window.set_project_data(project_data)

        sublime.message_dialog("".join([
                "Server configuration succesfully updated!",
            ]))

    # Cancel server configuration
    def on_cancel(self):
        self.dw_hostname    = None
        self.dw_username    = None
        self.dw_password    = None
        self.dw_directory   = None
        self.dw_directories = []
        self.dw_enabled     = None
