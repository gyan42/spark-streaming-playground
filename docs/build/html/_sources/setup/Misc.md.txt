## MISC

### To push Gist files without prompt

Few places I have used Gist for Medium blog post which needs to
be updated as I update by local Python Notebook, to keep in sync,
I need to clone the Gist file, update it with my Github notebook 
and push the changes, everything as part of respectuve notebook.

Jupyter notebooks needs to be enabled to push without asking for 
login credentials, for which creating `netrc` file will help.

```
vim ~/.netrc
    machine gist.github.com
    login mageswaran1989
    password xxxxxx
```
