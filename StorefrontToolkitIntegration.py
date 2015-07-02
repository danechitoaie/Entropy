# Python Modules
import os
import http.server
import re
import traceback

# Sublime Text 3 Modules
import sublime

# Lib Modules
from .lib import constants


class EntropyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        re_pattern = re.compile("^\/target=\/c\/(.+)\/t\/(.+)&count=(.+)$")
        re_match   = re_pattern.match(self.path)

        if re_match:
            req_cartridge_name = re_match.group(1)
            req_template_path  = re_match.group(2)
            req_requests_count = re_match.group(3)

            # Fix for Windows - Convert / to \ in the path
            req_template_path  = os.path.sep.join(req_template_path.split("/"))

            for window in sublime.windows():
                project_data = window.project_data()
                entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})

                # Check if Entropy is enabled for this window
                if entropy_data.get("enabled", "No") != "Yes":
                    continue

                # Loop trought the folders that belong to this project
                for project_folder in project_data.get("folders", []):
                    absolute_folder_path = project_folder.get("path")

                    # Fix path for cases when ST3 adds it as a relative path
                    if not os.path.isabs(absolute_folder_path):
                        absolute_folder_path = os.path.join(
                                os.path.dirname(window.project_file_name()), absolute_folder_path
                            )

                    cartridge_name = os.path.basename(absolute_folder_path)
                    template_path  = os.path.join(absolute_folder_path, "cartridge", "templates", req_template_path)

                    # Cartridge name matches and the template exists
                    if cartridge_name == req_cartridge_name and os.path.isfile(template_path):
                        window.focus_view(window.open_file(template_path))


        # Output a 1x1 transparent pixel so that everyone's happy
        content_length = 42
        content_type   = "image/gif"
        content_body   = b"".join([
                b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00",
                b"\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C",
                b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3B",
            ])

        self.send_response_only(200)
        self.send_header("Content-Length", content_length)
        self.send_header("Content-Type", content_type)
        self.send_header("Date", self.date_time_string())
        self.end_headers()
        self.wfile.write(content_body)


def run_storefront_toolkit_httpd():
    try:
        # Create new HTTPServer instance and start the server
        httpd = http.server.HTTPServer(("127.0.0.1", 60606), EntropyHTTPRequestHandler)
        httpd.serve_forever()

    except:
        traceback.print_exc()
        sublime.error_message("".join([
                "ERROR!\n\n",
                "Error starting the Storefront Toolkit Service!\n\n",
                "This may be due to the fact that Eclipse (with UX Studio plugin) ",
                "is running at the same time or you've closed and reopened Sublime Text 3 ",
                "too fast and the service didn't had enough time to proprely close before ",
                "being opened again."
            ]))


def plugin_loaded():
    entropy_settings      = sublime.load_settings("Entropy.sublime-settings")
    entropy_settings_sftk = entropy_settings.get("storefront_toolkit_integration", False) is True

    if entropy_settings_sftk:
            # Start the HTTP server async so that we don't block the UI thread
            sublime.set_timeout_async(lambda: run_storefront_toolkit_httpd(), 0)
