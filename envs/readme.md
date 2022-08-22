## Collection of the environments

Here is root for the all app environments. where stored all preconfigured environments of the application.
So here you can have several env files, like env for the local development, env for the azure deploy, etc. 
But not, that this directory is under git ignore, so no additional (except this readme and `example.env`) 
should not push to the repository, if you do not have strong reason to do this.

To create own env file, please copy&paste `example.env`, rename it by schema `{env_name}.env` 
where `{env_name}` is the name of the yor env. 


**Example env file [listed here](example.env)**


### Example Env file information:

* `SET_ME_PLEASE` should be adjusted to your env
* Empty variables is variables, which have default values, which calculated in runtime
* Regular variables - default values, vich can be overrited in the custom env
* file split be section, like
  ```shell
  ###########################
  ## Section name here 
  ###########################
  ```
