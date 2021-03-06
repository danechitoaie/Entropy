Entropy
===

Sublime Text 3 plugin for Demandware

Features
---

* Create new Demandware cartridge
* On save file upload to the sandbox
* Clean project
* Each server connection is tied to its own Sublime Text project (so you can be connected to multiple sandboxes at the same time as long as you have them in separate projects).
* Storefront Toolkit integration (i.e. when you click "edit template" in Storefront Toolkit it will automatically be opened in Sublime Text)

TODO
---

* Detect files changed outside of Sublime Text and sync them with the sandbox
* Script debugging

Installation Options
---

* [Package Control](https://packagecontrol.io/)
* [Download](https://bitbucket.org/danechitoaie/entropy/get/master.zip) this repo, rename it to "Entropy", and place it within your `Packages` folder. This can be found within Sublime Text at `Preferences > Browse Packages...`

Configuration
---

* `Preferences > Package Settings > Entropy`:
    * `verify_ssl_certificates` if you want the HTTPS certificate to be validated or not when requests are being made to your sandbox.
    * `verify_code_directory` if you want to verify if the code directory that you selected exists on the server or if you want it to be automatically created for you
    * `storefront_toolkit_integration` if you want to activate the Storefront Toolkit integration (this functionality is experimental so it's disabled by default).

Usage
---

* Open new window `File > New Window`
* Save the project `Project > Save Project As...` 
* Add cartridges to your project `Project > Add Folder to Project...`

Make sure you add the cartridges directly and not the parent folder that contains the cartridges (so basically same way you added cartridges in the UX Studio plugin for Eclipse).

![ss1.png](https://bitbucket.org/repo/54M5Ga/images/3487319365-ss1.png)

* Configure your server connection `Tools > Entropy > Server Configuration`. (For "Command Palette" command `COMMAND/CONTROL + SHIFT + P` type `Entropy: Server Configuration`)

* Cleanup the project `Tools > Entropy > Clean Project`. (For "Command Palette" command `COMMAND/CONTROL + SHIFT + P` type `Entropy: Clean Project`)

* Create new cartridge by running `Tools > Entropy > New Cartridge`. (For "Command Palette" command `COMMAND/CONTROL + SHIFT + P` type `Entropy: New Cartridge`)