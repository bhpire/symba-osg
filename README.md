# PIRE-symba-osg

An example workflow for running PIRE-symba on the Open Science Grid

## Environment

This version depends on the Webdav support in Pegasus, which was just
added. Therefore, you need to ensure a Pegasus 5.0.0dev build is in 
your path. For example:

    export PATH=~rynge/users/ck/pegasus-5.0.0dev/bin:$PATH

You also need to provide your credentials in
`~/.pegasus/credentials.conf`. Add:

    [data.cyverse.org]
    username =
    password =

Also ensure the file is only readable by the current user by running:

    chmod 600 ~/.pegasus/credentials.conf

## Inputs

The example does a simple webdav walk to find inputs.

## Outputs

Outputs are automatically staged back to Cyverse. The location is
configured in `sites.xml.template` under the `cyverse` entry.
Please change those locations to where you have write access.

## Workflow structure

The structure is defined in `workflow-generator.py`. 
The API is documented at
(https://pegasus.isi.edu/documentation/python/)

## Submitting

To generate a new workflow, run:

    ./generate-new-run

Note that when Pegasus plans a workflow, a work directory is
created and presented in the output. This directory is the handle to
the workflow instance and used by Pegasus command line tools. Some
useful tools to know about:

   * `pegasus-status -v [wfdir]`
        Provides status on a currently running workflow.
        ([more](https://pegasus.isi.edu/documentation/cli-pegasus-status.php))
   * `pegasus-analyzer [wfdir]`
        Provides debugging clues why a workflow failed. Run this after
        a workflow has failed.
        ([more](https://pegasus.isi.edu/documentation/cli-pegasus-analyzer.php))
   * `pegasus-statistics [wfdir]`
        Provides statistics, such as walltimes, on a workflow after it
        has completed.
        ([more](https://pegasus.isi.edu/documentation/cli-pegasus-statistics.php))
   * `pegasus-remove [wfdir]`
        Removes a workflow from the system.
        ([more](https://pegasus.isi.edu/documentation/cli-pegasus-remove.php))




