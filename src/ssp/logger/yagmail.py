#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import yagmail

from ssp.utils.config_manager import ConfigManager

from time import sleep

class YagMail():
    
    @staticmethod
    def email_notifier_ini(subject, contents, config_dir=None, attachments=None):
        """
        Sends mail notification using the default ini file location `CONFIG_DIR_PATH+"/yagmail.ini"`
        :param subject:
        :param contents:
        :param config_dir
        :param attachments:
        :return:
        """
        if config_dir is None:
            return

        config = ConfigManager(config_dir+"/yagmail.ini")
    
        from_address = config.get_item("default", "from_address")
        to_address = config.get_item("default", "to_address")
        to_address = [x.strip() for x in to_address.split(',')]
        from_email_password = config.get_item("default", "from_email_password")
    
        yag = yagmail.SMTP(from_address, from_email_password)
        yag.send(to=to_address, subject=subject, contents=contents, attachments=attachments)
    
        sleep(3) #wait for 3 seconds to make sure the SMPT server sends the mail

    @staticmethod
    def email_notifier_mannual(from_address, to_address, from_email_password, subject, contents, attachments=None):
        """
        Sends mail notification  based on given email details along with password
        :param from_address:
        :param to_address:
        :param from_email_password:
        :param subject:
        :param contents:
        :param attachments:
        :return:
        """
        yag = yagmail.SMTP(from_address, from_email_password)
        yag.send(to=to_address, subject=subject, contents=contents, attachments=attachments)

        sleep(3) #wait for 3 seconds to make sure the SMPT server sends the mail

