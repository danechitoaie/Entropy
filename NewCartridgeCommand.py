# Python Modules
import os
import datetime
import re

# Sublime Text 3 Modules
import sublime
import sublime_plugin


class EntropyNewCartridgeCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        self.cartridge_name = None
        self.cartridge_path = None

    # Prompt for cartridge name
    def run(self):
        self.window.show_input_panel("Cartridge Name:", "", self.step1_on_done, None, self.on_cancel)

    # Save the cartridge name and prompt for cartridge path
    def step1_on_done(self, name):
        re_pattern = re.compile("^[a-zA-Z0-9_]+$")
        re_match   = re_pattern.match(name)

        if not re_match:
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Invalid cartridge name \"{0}\"!\n".format(name),
                    "Only ^[a-zA-Z0-9_]+$ values are allowed."
                ]))
            self.on_cancel()
            return

        self.cartridge_name = name
        self.window.show_input_panel("Cartridge Path:", "", self.step2_on_done, None, self.on_cancel)

    # Save the cartridge path and run the cartridge creation worker
    def step2_on_done(self, path):
        cartridge_name = self.cartridge_name
        cartridge_path = os.path.expanduser(path)

        if len(cartridge_path) < 1:
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "Cartridge path is required!\n",
                ]))
            self.on_cancel()
            return

        if not os.path.exists(cartridge_path):
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "\"{0}\" does not exist!".format(cartridge_path),
                ]))
            self.on_cancel()
            return

        if not os.path.isdir(cartridge_path):
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "\"{0}\" is not a directory!".format(cartridge_path),
                ]))
            self.on_cancel()
            return

        if os.path.exists(os.path.join(cartridge_path, cartridge_name)):
            sublime.error_message("".join([
                    "ERROR!\n\n",
                    "\"{0}\" already exists in \"{1}\"!".format(cartridge_name, cartridge_path),
                ]))
            self.on_cancel()
            return

        self.cartridge_name = None
        self.cartridge_path = None

        sublime.set_timeout_async(lambda: self.make_cartridge_async(cartridge_name, cartridge_path), 0)

    # Create the cartridge async in a worker process
    def make_cartridge_async(self, cartridge_name, cartridge_path):
        dirs_to_make = [
                os.path.join(cartridge_path, cartridge_name),
                os.path.join(cartridge_path, cartridge_name, "cartridge"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "forms"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "forms", "default"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "pipelines"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "scripts"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "static"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "static", "default"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "templates"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "templates", "default"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "templates", "resources"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "webreferences"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "webreferences2"),
            ]

        for dir_to_make in dirs_to_make:
            os.makedirs(dir_to_make)

        cartridge_project_file_name = ".project"
        cartridge_project_file_path = os.path.join(cartridge_path, cartridge_name, cartridge_project_file_name)

        with open(cartridge_project_file_path, "w") as f:
            f.write("".join([
                    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n",
                    "<projectDescription>\n",
                    "    <name>{0}</name>\n".format(cartridge_name),
                    "    <comment></comment>\n",
                    "    <projects></projects>\n",
                    "    <buildSpec>\n",
                    "        <buildCommand>\n",
                    "            <name>com.demandware.studio.core.beehiveElementBuilder</name>\n",
                    "            <arguments></arguments>\n",
                    "        </buildCommand>\n",
                    "    </buildSpec>\n",
                    "    <natures>\n",
                    "        <nature>com.demandware.studio.core.beehiveNature</nature>\n",
                    "    </natures>\n",
                    "</projectDescription>\n",
                ]))

        cartridge_properties_file_date = datetime.datetime.now(datetime.timezone.utc)
        cartridge_properties_file_name = "{0}.properties".format(cartridge_name)
        cartridge_properties_file_path = os.path.join(cartridge_path, cartridge_name, "cartridge", cartridge_properties_file_name)

        d_of_the_week = {
                "d0" : "Sun",
                "d1" : "Mon",
                "d2" : "Tue",
                "d3" : "Wed",
                "d4" : "Thu",
                "d5" : "Fri",
                "d6" : "Sat",
            }

        m_of_the_year = {
                "m01" : "Jan",
                "m02" : "Feb",
                "m03" : "Mar",
                "m04" : "Apr",
                "m05" : "May",
                "m06" : "Jun",
                "m07" : "Jul",
                "m08" : "Aug",
                "m09" : "Sep",
                "m10" : "Oct",
                "m11" : "Nov",
                "m12" : "Dec",
            }

        with open(cartridge_properties_file_path, "w") as f:
            f.write("".join([
                    "## cartridge.properties for cartridge {0}\n".format(cartridge_name),
                    "#{0} {1} {2} {3} UTC {4}\n".format(
                            d_of_the_week.get("d{0}".format(cartridge_properties_file_date.strftime("%w")), "???"),
                            m_of_the_year.get("m{0}".format(cartridge_properties_file_date.strftime("%m")), "???"),
                            cartridge_properties_file_date.strftime("%d"),
                            cartridge_properties_file_date.strftime("%H:%M:%S"),
                            cartridge_properties_file_date.strftime("%Y"),
                        ),
                    "demandware.cartridges.{0}.id={0}\n".format(cartridge_name),
                    "demandware.cartridges.{0}.multipleLanguageStorefront=true\n".format(cartridge_name),
                ]))

        files_to_make = [
                os.path.join(cartridge_path, cartridge_name, "cartridge", "forms", "default", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "pipelines", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "scripts", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "static", "default", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "templates", "default", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "templates", "resources", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "webreferences", ".gitkeep"),
                os.path.join(cartridge_path, cartridge_name, "cartridge", "webreferences2", ".gitkeep"),
            ]

        for file_to_make in files_to_make:
            with open(file_to_make, "w") as f:
                pass

        sublime.message_dialog("".join([
                "{0} has been created!".format(cartridge_name),
            ]))

    # Cancel cartridge creation
    def on_cancel(self):
        self.cartridge_name = None
        self.cartridge_path = None
