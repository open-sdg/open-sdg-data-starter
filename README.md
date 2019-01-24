# Open SDG - Data - Armenia

This is the data repository for the Armenian implementation of Open SDG.

## Adding new indicators

A helper script is available to add new indicators. To use it, execute the script
with Python from the root of the repository. Here is an example:

`py scripts/batch/add_indicator 1.2.z "Title of indicator"`

This will create a new "1.2.z" indicator called "Title of indicator".

> This script requires the `pyyaml` package. Here is the command to install
> this package:
>
> `py -m pip install pyyaml`

Note that this only creates template files. You will still need to customize
these files as needed, and then add/commit/push them with Git.

Finally, the next step is to perform the same steps in the other repository (if
you have not already).