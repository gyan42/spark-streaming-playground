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

