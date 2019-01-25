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

## Github user validation

Pull-requests to change data or metadata will fail testing if the Github user
is not on a pre-determined list. The list is in the `scripts/validate` folder.
Users can be set as `administrator` so that they can submit pull-requests for
any file. The syntax for this is:

```
my-github-username: administrator
```

Alternatively, they can be given access to a list of specific indicators. The
syntax for this is:

```
my-github-username:
  indicators:
    - 1-1-1
    - 1-1-2
```

The indicators can include wildcards to give access to an entire goal or target:

```
my-github-username:
  indicators:
    - 1-1-*
    - 2-*-*
```

## Production deployments

To start a production deployment, merge the `develop` branch into `master`. You
can do this in Github.com by creating a new pull-request. The steps are:

1. Click "New pull request"
2. Set "base: master" and "compare: develop"
3. Click "Create pull request"
