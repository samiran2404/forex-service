import raven
from raven import Client
from raven.transport.http import HTTPTransport
import logging
import os
from configparser import ConfigParser
from config import constants
import boto3


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Cfg(object, metaclass=Singleton):
    def get_parameter(self, name, decrypt=False):
        if self.stage == constants.LOCAL:
            return name
        return boto3.client('ssm', region_name='ap-southeast-1').get_parameters(Names=[name], WithDecryption=decrypt)[
            "Parameters"][0]["Value"]

    def __init__(self, stage):
        self.stage = stage
        configp = ConfigParser()
        sentry_errors_log = logging.getLogger("sentry.errors")
        logging.getLogger().setLevel(logging.INFO)
        sentry_errors_log.addHandler(logging.StreamHandler())
        configp.read("config/" + stage + ".ini")
        self.Config = configp.get
        self.project_name = self.Config("project", "name")
        release = ""
        try:
            file_obj = open("release.commit", "r")
            release = file_obj.read()
        except IOError:
            try:
                release = raven.fetch_git_sha(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
            except:
                pass
        if self.stage != constants.LOCAL:
            self.Logger = Client(
                dsn=self.Config("sentry", "dsn"),
                environment=stage,
                release=release.strip(),
                repos={
                    'raven': {
                        'name': 'finaxar/%s/' % self.project_name,
                    }
                },
                transport=HTTPTransport)
        else:
            self.Logger = sentry_errors_log

        self.dynamo_client = boto3.client("dynamodb")
        self.table_name = self.Config("dynamodb", "table_name")
        self.rate_url = self.get_parameter(self.Config("api", "url"), decrypt=True)
        self.app_id = self.get_parameter(self.Config("api", "app_id"), decrypt=True)

