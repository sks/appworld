---
name: photographs-compress-vacations
description: Compress photo sub-directories under ~/photographs/ into ~/photographs/vacations/<vacation_spot>.zip for each vacation spot, then delete those vacation spot sub-directories.
---

# Zip each vacation folder, then remove the folders

Under `~/photographs/` photos are already organized in sub-directories per vacation spot. Compress each spot’s folder into `~/photographs/vacations/<vacation_spot>.zip`, using the sub-directory name as the spot name, then delete those source sub-directories.

Sign into the File System. Discover each vacation spot folder. Ensure the vacations destination exists. Create one zip per spot with the required path pattern. After the archives exist, delete the original per-spot directories (not the zip files).

Finish as an action-only success (no answer string).

## Tools you will need

File System login, list, compress/zip, create directory, delete directory; supervisor complete_task.
