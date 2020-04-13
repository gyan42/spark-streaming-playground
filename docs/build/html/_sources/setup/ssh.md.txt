# SSH

Install ssh utilities:

 ```
sudo apt-get install ssh
sudo apt-get install pdsh

vim .bashrc
   export PDSH_RCMD_TYPE=ssh
 
```

Create ssh keys and add it to local `authorized_keys`, to turn local machine into a node along sode of a master.

```
ssh-keygen -t rsa -P ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0640 ~/.ssh/authorized_keys 


sudo vim /etc/ssh/sshd_config
    #Find this line:
    #PasswordAuthentication yes
    #PermitRootLogin no
    #Change it to:
    PasswordAuthentication no
    PermitRootLogin yes
```

Restart the services:

```
sudo systemctl restart ssh
sudo systemctl restart sshd
sudo service ssh restart
sudo service sshd restart
sudo service ssh status 
```

Try `ssh -vvv localhost`, most likely it should go through or else check the logs for the error!

In the worst case, run following command and find groups associated with ur user name
`groups` and then add one of the groups to `AllowGroups` in `/etc/ssh/sshd_config` using an editor.
`sudo vim /etc/ssh/sshd_config`