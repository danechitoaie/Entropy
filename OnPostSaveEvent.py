# Python Modules
import os
import urllib
import traceback

# Sublime Text 3 Modules
import sublime
import sublime_plugin

# Lib Modules
from .lib import requests
from .lib import constants
from .lib import animations
from .lib import exceptions


class EntropyOnPostSaveEvent(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        window = view.window()

        # Check if current window is associated with a project
        if not window.project_file_name():
            return

        # Check if the view has been saved to a file on the disk
        if not view.file_name():
            return

        project_data = window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})

        # Check if Entropy is enabled for this window
        if entropy_data.get("enabled", "No") != "Yes":
            return

        dw_hostname  = entropy_data.get("hostname")
        dw_username  = entropy_data.get("username")
        dw_password  = entropy_data.get("password")
        dw_directory = entropy_data.get("directory")

        entropy_settings      = sublime.load_settings("Entropy.sublime-settings")
        entropy_settings_vssl = entropy_settings.get("verify_ssl_certificates", True)
        entropy_settings_vcd  = entropy_settings.get("verify_code_directory", True)

        # Loop trought the folders that belong to this project
        for project_folder in project_data.get("folders", []):
            absolute_file_path = view.file_name()
            absolute_fldr_path = project_folder.get("path")

            # Fix path for cases when ST3 adds it as a relative path
            if not os.path.isabs(absolute_fldr_path):
                absolute_fldr_path = os.path.join(os.path.dirname(window.project_file_name()), absolute_fldr_path)

            # Check if the file that's being saved belongs to this folder and if not skip to the next one
            if not absolute_file_path.startswith(absolute_fldr_path):
                continue

            l_file_path = absolute_file_path
            r_file_path = absolute_file_path[len(os.path.dirname(absolute_fldr_path)):]

            # Fix for Windows - Convert \ to / in the path
            r_file_path = r_file_path.replace("\\", "/")

            # Remove the / character if it's present at the begining or the end of the path
            r_file_path = r_file_path.strip("/")

            # Encode URL components
            r_file_path = urllib.parse.quote(r_file_path)

            animation = animations.EntropyOnPostSaveAnimation(view, l_file_path)
            animation.start()

            try:
                # Check if parent directory of the file exists on the server
                r_file_d = os.path.dirname(r_file_path).strip("/")
                req1_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/{2}".format(dw_hostname, dw_directory, r_file_d)
                req1     = requests.head(req1_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                # Authentication failed
                if req1.status_code == requests.codes.UNAUTHORIZED:
                    raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req1.status_code, req1.reason))

                # Parent directory of the file does not exist on the server
                if req1.status_code == requests.codes.NOT_FOUND:
                    # Check if the code directory exists on the server
                    req2_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)
                    req2     = requests.head(req2_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                    # Authentication failed
                    if req2.status_code == requests.codes.UNAUTHORIZED:
                        raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req2.status_code, req2.reason))

                    # Code directory does not exist on the server
                    if req2.status_code == requests.codes.NOT_FOUND:
                        # verify_code_directory is True
                        if entropy_settings_vcd:
                            raise exceptions.EntropyVerifyCodeDirectoryException()

                        # verify_code_directory is False so we are ok to create the directory
                        else:
                            req3_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)
                            req3     = requests.request("MKCOL", req3_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                            # Authentication failed
                            if req3.status_code == requests.codes.UNAUTHORIZED:
                                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req3.status_code, req3.reason))

                            # Directory was not created
                            if req3.status_code != requests.codes.CREATED:
                                raise exceptions.EntropyHttpMkcolException("{0} - {1}".format(req3.status_code, req3.reason))

                    req4_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)

                    # Loop trough directories in the path and check if they exists or if they need to be created
                    for req4_url_path in r_file_d.split("/"):
                        req4_url = "{0}/{1}".format(req4_url, req4_url_path)
                        req4     = requests.head(req4_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                        # Authentication failed
                        if req4.status_code == requests.codes.UNAUTHORIZED:
                            raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req4.status_code, req4.reason))

                        # Directory does not exist
                        if req4.status_code == requests.codes.NOT_FOUND:
                            req5_url = req4_url
                            req5     = requests.request("MKCOL", req5_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                            # Authentication failed
                            if req5.status_code == requests.codes.UNAUTHORIZED:
                                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req5.status_code, req5.reason))

                            # Directory was not created
                            if req5.status_code != requests.codes.CREATED:
                                raise exceptions.EntropyHttpMkcolException("{0} - {1}".format(req5.status_code, req5.reason))

                # Upload the file
                with open(l_file_path, "rb") as f:
                    req6_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/{2}".format(dw_hostname, dw_directory, r_file_path)
                    req6     = requests.put(req6_url, auth=(dw_username, dw_password), data=f, verify=entropy_settings_vssl)

                    # Authentication failed
                    if req6.status_code == requests.codes.UNAUTHORIZED:
                        raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req6.status_code, req6.reason))

                    # File was not uploaded
                    if not req6.status_code in (requests.codes.CREATED, requests.codes.NO_CONTENT):
                        raise exceptions.EntropyHttpPutException("{0} - {1}".format(req6.status_code, req6.reason))

            except exceptions.EntropyHttpUnauthorizedException as e:
                traceback.print_exc()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Invalid username or password!",
                    ]))
                return

            except exceptions.EntropyVerifyCodeDirectoryException as e:
                traceback.print_exc()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Code directory does not exist on the server!",
                    ]))
                return

            except (exceptions.EntropyHttpMkcolException,
                    exceptions.EntropyHttpPutException,
                    requests.exceptions.RequestException,
                    IOError) as e:

                traceback.print_exc()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Error uploading {0}!".format(
                            l_file_path if len(l_file_path) <= 64 else "...{0}".format(l_file_path[-61:])
                        ),
                    ]))
                return

            except:
                traceback.print_exc()
                sublime.error_message("".join([
                        "ERROR!\n\n",
                        "Unknown exception!",
                    ]))
                return

            finally:
                animation.stop()

            return
