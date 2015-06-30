# Sublime Text 3 Modules
import sublime

# Lib Modules
from .constants import PROJECT_DATA_KEY


class EntropyServerConfigurationAnimation():
    def __init__(self, window):
        self.SET_STATUS_KEY = "{0}__{1}".format(PROJECT_DATA_KEY, self.__class__.__name__)
        self.window         = window
        self.view           = window.active_view()
        self.run_animation  = False
        self.current_frame  = 0
        self.frame_text     = "Retrieving the list of code directories"
        self.frames         = [
                "[ =          ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[          = ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
            ]

    def start(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = True
        self.current_frame = 0
        self.next_frame()

    def next_frame(self):
        self.view.set_status(self.SET_STATUS_KEY, self.frames[self.current_frame])
        self.current_frame += 1

        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        if self.run_animation:
            sublime.set_timeout(lambda: self.next_frame(), 500)

        else:
            self.view.erase_status(self.SET_STATUS_KEY)

    def stop(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = False
        self.current_frame = 0


class EntropyOnPostSaveAnimation():
    def __init__(self, view, file_path):
        self.SET_STATUS_KEY = "{0}__{1}".format(PROJECT_DATA_KEY, self.__class__.__name__)
        self.window         = view.window()
        self.view           = view
        self.run_animation  = False
        self.current_frame  = 0
        self.frame_text     = "Uploading {0}".format(file_path if len(file_path) <= 64 else "...{0}".format(file_path[-61:]))
        self.frames         = [
                "[ =          ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[          = ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
            ]

    def start(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = True
        self.current_frame = 0
        self.next_frame()

    def next_frame(self):
        self.view.set_status(self.SET_STATUS_KEY, self.frames[self.current_frame])
        self.current_frame += 1

        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        if self.run_animation:
            sublime.set_timeout(lambda: self.next_frame(), 500)

        else:
            self.view.erase_status(self.SET_STATUS_KEY)

    def stop(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = False
        self.current_frame = 0


class EntropyCleanProjectAnimation():
    def __init__(self, window):
        self.SET_STATUS_KEY = "{0}__{1}".format(PROJECT_DATA_KEY, self.__class__.__name__)
        self.window         = window
        self.view           = window.active_view()
        self.run_animation  = False
        self.current_frame  = 0
        self.frame_text     = "Cleaning up the project"
        self.frames         = [
                "[ =          ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[          = ] {0}".format(self.frame_text),
                "[         =  ] {0}".format(self.frame_text),
                "[        =   ] {0}".format(self.frame_text),
                "[       =    ] {0}".format(self.frame_text),
                "[      =     ] {0}".format(self.frame_text),
                "[     =      ] {0}".format(self.frame_text),
                "[    =       ] {0}".format(self.frame_text),
                "[   =        ] {0}".format(self.frame_text),
                "[  =         ] {0}".format(self.frame_text),
            ]

    def start(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = True
        self.current_frame = 0
        self.next_frame()

    def next_frame(self):
        self.view.set_status(self.SET_STATUS_KEY, self.frames[self.current_frame])
        self.current_frame += 1

        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        if self.run_animation:
            sublime.set_timeout(lambda: self.next_frame(), 500)

        else:
            self.view.erase_status(self.SET_STATUS_KEY)

    def stop(self):
        self.view.erase_status(self.SET_STATUS_KEY)
        self.run_animation = False
        self.current_frame = 0
