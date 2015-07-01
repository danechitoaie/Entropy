# Python Modules
import os
import tempfile
import zipfile
import xml.etree.ElementTree
import traceback

# Sublime Text 3 Modules
import sublime
import sublime_plugin

# Lib Modules
from .lib import requests
from .lib import constants
from .lib import animations
from .lib import exceptions


class EntropyCleanProjectCommand(sublime_plugin.WindowCommand):
    def run(self):
        sublime.set_timeout_async(lambda: self.clean_project_async(), 0)

    def clean_project_async(self):
        if not self.window.project_file_name():
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Current window is not associated with a project.\n\n",
                    "Please run \"Project > Save Project As...\" or \"Project > Open Project...\" ",
                    "before atempting to run clean project.",
                ]))
            return

        project_data = self.window.project_data()
        entropy_data = project_data.get(constants.PROJECT_DATA_KEY, {})

        # Check if Entropy is enabled for this window
        if entropy_data.get("enabled", "No") != "Yes":
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Entropy is not enabled for this project!",
                ]))
            return

        dw_hostname  = entropy_data.get("hostname")
        dw_username  = entropy_data.get("username")
        dw_password  = entropy_data.get("password")
        dw_directory = entropy_data.get("directory")

        entropy_settings      = sublime.load_settings("Entropy.sublime-settings")
        entropy_settings_vssl = entropy_settings.get("verify_ssl_certificates", True)
        entropy_settings_vcd  = entropy_settings.get("verify_code_directory", True)

        animation = animations.EntropyCleanProjectAnimation(self.window)
        animation.start()

        try:
            # Check if the code directory exists on the server
            req1_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)
            req1     = requests.head(req1_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

            # Authentication failed
            if req1.status_code == requests.codes.UNAUTHORIZED:
                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req1.status_code, req1.reason))

            # Code directory does not exist on the server
            if req1.status_code == requests.codes.NOT_FOUND:
                # verify_code_directory is True
                if entropy_settings_vcd:
                    raise exceptions.EntropyVerifyCodeDirectoryException()

                # verify_code_directory is False so we are ok to create the directory
                else:
                    req2_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)
                    req2     = requests.request("MKCOL", req2_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                    # Authentication failed
                    if req2.status_code == requests.codes.UNAUTHORIZED:
                        raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req2.status_code, req2.reason))

                    # Directory was not created
                    if req2.status_code != requests.codes.CREATED:
                        raise exceptions.EntropyHttpMkcolException("{0} - {1}".format(req2.status_code, req2.reason))

            # Cleaning up previous code
            req3_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}".format(dw_hostname, dw_directory)
            req3_xml = "".join([
                    "<?xml version=\"1.0\"?>\n",
                    "<a:propfind xmlns:a=\"DAV:\">\n",
                    "   <a:prop>\n",
                    "       <a:resourcetype/>\n",
                    "   </a:prop>\n",
                    "</a:propfind>\n",
                ])
            req3     = requests.request("PROPFIND", req3_url, auth=(dw_username, dw_password), data=req3_xml, headers={"Depth" : "1"}, verify=entropy_settings_vssl)

            # Authentication failed
            if req3.status_code == requests.codes.UNAUTHORIZED:
                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req3.status_code, req3.reason))

            # Unexpected response
            if req3.status_code != requests.codes.MULTI_STATUS:
                raise exceptions.EntropyHttpPropFindException("{0} - {1}".format(req3.status_code, req3.reason))

            xml_etree = xml.etree.ElementTree.fromstring(req3.text.strip())
            xml_hrefs = xml_etree.findall("./{DAV:}response/{DAV:}href")[1:]

            # Cleanup the old files in the code directory
            for xml_href in xml_hrefs:
                req4_href = xml_href.text
                req4_url  = "https://{0}{1}".format(dw_hostname, req4_href)
                req4      = requests.delete(req4_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

                # Authentication failed
                if req4.status_code == requests.codes.UNAUTHORIZED:
                    raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req4.status_code, req4.reason))

                # Unexpected response
                if req4.status_code != requests.codes.NO_CONTENT:
                    raise exceptions.EntropyHttpNoContentException("{0} - {1}".format(req4.status_code, req4.reason))

            # Create temporary directory that will get deleted automatically once it's not needed anymore
            with tempfile.TemporaryDirectory() as tmp_dir_path:
                # Create new zip file from the temporary file created above
                f_pth = os.path.join(tmp_dir_path, "entropy_project.zip")
                f_zip = zipfile.ZipFile(f_pth, mode="w")

                # Loop trought the folders that belong to this project
                for project_folder in project_data.get("folders", []):
                    absolute_folder_path = project_folder.get("path")

                    # Fix path for cases when ST3 adds it as a relative path
                    if not os.path.isabs(absolute_folder_path):
                        absolute_folder_path = os.path.join(
                                os.path.dirname(self.window.project_file_name()), absolute_folder_path
                            )

                    for dir_path, dir_names, file_names in os.walk(absolute_folder_path):
                        absolute_dir_path = dir_path
                        relative_dir_path = absolute_dir_path[len(os.path.dirname(absolute_folder_path)):]

                        # Fix for Windows - Convert \ to / in the path
                        relative_dir_path = relative_dir_path.replace("\\", "/")

                        # Remove the / character if it's present at the begining or the end of the path
                        relative_dir_path = relative_dir_path.strip("/")

                        # Add folder to ZIP
                        f_zip.write(absolute_dir_path, arcname=relative_dir_path, compress_type=zipfile.ZIP_STORED)

                        for file_name in file_names:
                            absolute_file_path = os.path.join(absolute_dir_path, file_name)
                            relative_file_path = absolute_file_path[len(os.path.dirname(absolute_folder_path)):]

                            # Fix for Windows - Convert \ to / in the path
                            relative_file_path = relative_file_path.replace("\\", "/")

                            # Remove the / character if it's present at the begining or the end of the path
                            relative_file_path = relative_file_path.strip("/")

                            # Add file to ZIP
                            f_zip.write(absolute_file_path, arcname=relative_file_path, compress_type=zipfile.ZIP_DEFLATED)

                f_zip.close()

                with open(f_pth, "rb") as f_tmp:
                    # Uploading entropy_project.zip
                    req5_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/entropy_project.zip".format(dw_hostname, dw_directory)
                    req5     = requests.put(req5_url, auth=(dw_username, dw_password), data=f_tmp, verify=entropy_settings_vssl)

                    # Authentication failed
                    if req5.status_code == requests.codes.UNAUTHORIZED:
                        raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req5.status_code, req5.reason))

                    # Unexpected response
                    if req5.status_code != requests.codes.CREATED:
                        raise exceptions.EntropyHttpPutException("{0} - {1}".format(req5.status_code, req5.reason))

            # Extracting entropy_project.zip
            req6_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/entropy_project.zip".format(dw_hostname, dw_directory)
            req6     = requests.post(req6_url, auth=(dw_username, dw_password), data={"method" : "UNZIP"}, verify=entropy_settings_vssl)

            # Authentication failed
            if req6.status_code == requests.codes.UNAUTHORIZED:
                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req6.status_code, req6.reason))

            # Unexpected response
            if req6.status_code != requests.codes.CREATED:
                raise exceptions.EntropyHttpPutException("{0} - {1}".format(req6.status_code, req6.reason))

            # Deleting entropy_project.zip
            req7_url = "https://{0}/on/demandware.servlet/webdav/Sites/Cartridges/{1}/entropy_project.zip".format(dw_hostname, dw_directory)
            req7     = requests.delete(req7_url, auth=(dw_username, dw_password), verify=entropy_settings_vssl)

            # Authentication failed
            if req7.status_code == requests.codes.UNAUTHORIZED:
                raise exceptions.EntropyHttpUnauthorizedException("{0} - {1}".format(req7.status_code, req7.reason))

            # Unexpected response
            if req7.status_code != requests.codes.NO_CONTENT:
                raise exceptions.EntropyHttpNoContentException("{0} - {1}".format(req7.status_code, req7.reason))

            sublime.message_dialog("".join([
                "Project has been succesfully cleaned!",
            ]))

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
                exceptions.EntropyHttpPropFindException,
                exceptions.EntropyHttpNoContentException,
                exceptions.EntropyHttpPutException,
                xml.etree.ElementTree.ParseError,
                requests.exceptions.RequestException,
                IOError) as e:

            traceback.print_exc()
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Error cleaning project!",
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
