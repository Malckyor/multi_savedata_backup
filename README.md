# Multi Savedata Backup

The tool is intended to make and restore backup easily and automatically within a few clicks, totally friendly user and with few restrictions for lesser chances of the user doing something wrong.
It might not be perfect and it is not that fancy, but it will work as I planned it to. Give it a try, reach me out for feedback if you want, just use it wiselly and respectifully.

<img width="895" height="729" alt="image" src="https://github.com/user-attachments/assets/97245d89-ae5a-4220-ae82-5f715f09af8e" />

## ================= FOR USERS =================
Requirements:

1- Winrar or 7zip installed. Google Drive for Desktop installed and configured. (https://support.google.com/a/users/answer/13022292?hl=pt#drive_desktop_install)

1.5- Configured the GD for Desktop: download and install it, the configuration does not matter, what matters is that it creaties the a remote drive of your GD.

2- Configure the "Synced Folder (Google Drive or similar)" for the remote drive of your GD. (ex: H:/My Drive/Multi Savedata Backup)

3- Configure all folders of your choice.

4- Click on "Start Backup" to make the automatic backup of the configured folders directly into your GD.

5- Click on "Restore Backup" to automatic download the files from your GD, make sure to have all the configured folders correctly.


## ================= FOR DEVS =================
Requirements:

1- Winrar or 7zip installed. Google Drive for Desktop installed and configured. (https://support.google.com/a/users/answer/13022292?hl=pt#drive_desktop_install)

2- For testing
``python app.py``

3- For compiling
``pyinstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." --name="Multi Savedata Backup" app.py``

4- Copy the "locales" folder into the "dist" folder.

5- Run
dist/app.exe

6- Leave my signature alone? Please?

## Special thanks to:
* My friend Luck for giving me the idea.
* Rendricks for generating the Icon.
