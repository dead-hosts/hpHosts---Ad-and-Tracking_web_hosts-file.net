#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Update Me !

This module has been written in order to be the main entry for every tests in a
directory which contain a list to test.

Also consider this script a clean script which have to be filled for every repository.

Author:
    @Funilrys, Nissar Chababy <contactTAfunilrysTODcom>

Contributors:
    Let's contribute !

    @GitHubUsername, Name, Email (optional)
"""
# pylint: disable=bad-continuation, too-many-lines

from json import decoder, dump, loads
from os import environ, getcwd, path, remove
from os import sep as directory_separator
from re import compile as comp
from re import escape
from re import sub as substrings
from subprocess import PIPE, Popen
from time import ctime, strftime

from requests import get

class Settings:  # pylint: disable=too-few-public-methods
    """
    This class will save all data that can be called from anywhere in the code.
    """

    # This variable will help us keep a track on info.json content.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    informations = {}

    # This variable should be initiated with the raw link to the hosts file or the
    # list we are going to test.
    #
    # Note: The variable name should not be changed.
    # Note: This variable is auto updated by Initiate()
    #
    # Example: "https://raw.githubusercontent.com/AdAway/adaway.github.io/master/hosts.txt"
    raw_link = ""

    # This variable should be initiated with the name of the list once downloaded.
    # Recommended formats:
    #  - GitHub Repository:
    #    - GitHubUsername@RepoName.list
    #  - GitHub organization:
    #    - GitHubOrganisationName@RepoName.list
    #  - Others:
    #    - websiteDomainName.com@listName.list
    #
    # Note: The variable name should not be changed.
    # Note: This variable is auto updated by Initiate()
    #
    # Example: "adaway.github.io@AdAway.list"
    list_name = ""

    # This variable will help us know where we are working into the filesystem.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    current_directory = getcwd() + directory_separator

    # This variable will help us know which file we are going to test.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    file_to_test = current_directory

    # This variable will help us know what how many days we have to wait until next test.
    #
    # Note: This variable is auto updated by Initiate()
    days_until_next_test = 0

    # This variable will help us know the date of the last test.
    #
    # Note: This variable is auto updated by Initiate()
    last_test = 0

    # This variable will help us manage the implementation of days_until_next_test and last_test.
    #
    # Note: This variable is auto updated by Initiate()
    currently_under_test = False

    # This variable will help us know where should the info.json file be located.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    repository_info = current_directory + "info.json"

    # This variable will help us know which version of PyFunceble we are going to use.
    #
    # Note: True = master | False = dev
    # Note: This variable is auto updated by Initiate()
    stable = False

    # This variable represent the PyFunceble infrastructure.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    PyFunceble = {
        ".PyFunceble_production.yaml": "https://raw.githubusercontent.com/funilrys/PyFunceble/dev/.PyFunceble_production.yaml"  # pylint: disable=line-too-long
    }

    PyFunceble_config = {
        "less": True,
        "plain_list_domain": True,
        "seconds_before_http_timeout": 6,
        "share_logs": True,
        "split": True,
        "travis_autosave_minutes": 10,
        "travis": True,
        "multiprocess": False,
        "maximal_processes": 10,
        "dns_server": ["1.1.1.1", "1.0.0.1"],
    }

    try:
        PyFunceble_config["travis_branch"] = environ["GIT_BRANCH"]
    except KeyError:
        PyFunceble_config["travis_branch"] = "master"

    # This variable is used to match [ci skip] from the git log.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    regex_travis = "[ci skip]"

    # This variable is used to set the default commit message when we commit
    # under Travic CI.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    commit_autosave_message = ""

    # This variable is used to set permanent_license_link.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    permanent_license_link = "https://raw.githubusercontent.com/dead-hosts/repository-structure/master/LICENSE"  # pylint: disable=line-too-long

    # This variable is used to set the permanant config links
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    permanent_config_link = "https://raw.githubusercontent.com/dead-hosts/repository-structure/master/.PyFunceble_cross_repositories_config.yaml"  # pylint: disable=line-too-long

    # This variable is used to set the arguments when executing PyFunceble.py
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    arguments = []

    # This variable is used to know if we need to delete INACTIVE and INVALID
    # domain from the original file.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    clean_original = False

    # This variable is used to set the location of the file for the list without
    # dead/inactive domains
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    clean_list_file = "clean.list"

    # This variable is used to know if we read a custom `config.yaml` or
    # download the latest from the repository structure.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    custom_pyfunceble_config = False

    # This variable is used to get the list of GitHub username to ping at the
    # end of a test.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    # Note: This variable is auto updated by Initiate()
    ping = []

    # This variable set the name of the administration file.
    #
    # Note: DO NOT TOUCH UNLESS YOU KNOW WHAT IT MEANS!
    administration_script = "admin.py"


class Initiate:
    """
    Initiate several actions.
    """

    def __init__(self):  # pylint: disable=too-many-branches
        self.travis()
        self.travis_permissions()

        self._fix_cross_repo_config()

        if not Settings.custom_pyfunceble_config and not path.isfile(
            Settings.permanent_config_link.split("/")[-1]
        ):
            Helpers.Download(Settings.permanent_config_link, ".PyFunceble.yaml").link()
        self.stucture()

    @classmethod
    def _fix_cross_repo_config(cls):
        """
        This method will fix the cross repositories configuration.
        """

        if not Settings.stable:
            to_download = Settings.PyFunceble[".PyFunceble_production.yaml"].replace(
                "master", "dev"
            )
        else:
            to_download = Settings.PyFunceble[".PyFunceble_production.yaml"].replace(
                "dev", "master"
            )

        destination = Settings.permanent_config_link.split("/")[-1]

        if path.isfile(destination):
            Helpers.Download(to_download, destination).link()

            destination_file = Helpers.File(destination)
            content = Helpers.Dict().from_yaml(destination_file.read())

            content.update(Settings.PyFunceble_config)

            Helpers.Dict(content).to_yaml(destination)
            Helpers.Dict(content).to_yaml(".PyFunceble.yaml")

    @classmethod
    def travis(cls):
        """
        Initiate Travis CI settings.
        """
        try:
            _ = environ["TRAVIS_BUILD_DIR"]
            Helpers.Command("git remote rm origin", False).execute()
            Helpers.Command(
                "git remote add origin https://"
                + "%s@github.com/%s.git"
                % (environ["GH_TOKEN"], environ["TRAVIS_REPO_SLUG"]),
                False,
            ).execute()
            Helpers.Command(
                'git config --global user.email "%s"' % (environ["GIT_EMAIL"]), False
            ).execute()
            Helpers.Command(
                'git config --global user.name "%s"' % (environ["GIT_NAME"]), False
            ).execute()
            Helpers.Command("git config --global push.default simple", False).execute()
            Helpers.Command("git checkout %s" % environ["GIT_BRANCH"], False).execute()

            return

        except KeyError:
            pass

    @classmethod
    def travis_permissions(cls):
        """
        Set permissions in order to avoid issues before commiting.
        """
        try:
            build_dir = environ["TRAVIS_BUILD_DIR"]
            commands = [
                "sudo chown -R travis:travis %s" % (build_dir),
                "sudo chgrp -R travis %s" % (build_dir),
                "sudo chmod -R g+rwX %s" % (build_dir),
                "sudo chmod 777 -Rf %s.git" % (build_dir + directory_separator),
                r"sudo find %s -type d -exec chmod g+x '{}' \;" % (build_dir),
            ]

            for command in commands:
                Helpers.Command(command, False).execute()

            if (
                Helpers.Command("git config core.sharedRepository", False).execute()
                == ""
            ):
                Helpers.Command(
                    "git config core.sharedRepository group", False
                ).execute()

            return

        except KeyError:
            pass

    @classmethod
    def set_info_settings(cls, index):
        """
        Set Settings.informations according to info.json.

        Arguments:
            index: A string, a valid index name.
        """

        try:
            getattr(Settings, index)
            if (
                index
                in [
                    "stable",
                    "currently_under_test",
                    "clean_original",
                    "custom_pyfunceble_config",
                ]
                and Settings.informations[index].isdigit()
            ):
                setattr(Settings, index, bool(int(Settings.informations[index])))
            elif (
                index in ["days_until_next_test", "last_test"]
                and Settings.informations[index].isdigit()
            ):
                setattr(Settings, index, int(Settings.informations[index]))
            else:
                setattr(Settings, index, Settings.informations[index])
        except AttributeError:
            raise Exception(
                '"%s" into %s in unknown.' % (index, Settings.repository_info)
            )

    @classmethod
    def install_right_pyfunceble(cls):
        """
        This method will install the right version of PyFunceble
        depending of the status of the `stable` index.
        """

        if Settings.stable:
            to_download = "PyFunceble"
        else:
            to_download = "PyFunceble-dev"

        Helpers.Command("pip3 install %s" % to_download, False).execute()

    def download_PyFunceble(self):  # pylint: disable=invalid-name
        """
        Download PyFunceble files if they are not present.
        """

        for file in Settings.PyFunceble:
            file_path = Settings.current_directory + file

            if not path.isfile(file_path) or not Settings.stable:
                download_link = Settings.PyFunceble[file].replace("master", "dev")
            else:
                download_link = Settings.PyFunceble[file].replace("dev", "master")

            if not Helpers.Download(download_link, file_path).link():
                raise Exception("Unable to download %s." % download_link)

            self.travis_permissions()

            Helpers.File(Settings.current_directory + "PyFunceble.py").delete()
            Helpers.File(Settings.current_directory + "tool.py").delete()

        self.install_right_pyfunceble()

    @classmethod
    def _format_domain(cls, extracted_domain):
        """
        Format the extracted domain before passing it to the system.

        Argument:
            - extracted_domain: str
                The extracted domain or line from the file.
        """

        if not extracted_domain.startswith("#"):

            if "#" in extracted_domain:
                extracted_domain = extracted_domain[
                    : extracted_domain.find("#")
                ].strip()

            if " " in extracted_domain or "\t" in extracted_domain:
                splited_line = extracted_domain.split()

                index = 1
                while index < len(splited_line):
                    if splited_line[index]:
                        break

                    index += 1

                return splited_line[index]

            return extracted_domain

        return ""

    def _extract_lines(self, file):
        """
        This method extract and format each line to get the domain.

        Argument:
            - file: str
                The file to read.
        """

        result = []

        for line in Helpers.File(file).to_list():
            if line and not line.startswith("#"):
                result.append(self._format_domain(line.strip()))

        return result

    def list_file(self):
        """
        Download Settings.raw_link.
        """

        regex_new_test = r"Launch\stest"

        if (
            not Settings.currently_under_test
            or Helpers.Regex(
                Helpers.Command("git log -1", False).execute(),
                regex_new_test,
                return_data=False,
            ).match()
        ):

            if Helpers.Download(Settings.raw_link, Settings.file_to_test).link():
                Helpers.Command("dos2unix " + Settings.file_to_test, False).execute()

                formated_content = self._extract_lines(Settings.file_to_test)

                Helpers.File(Settings.file_to_test).write(
                    "\n".join(formated_content), overwrite=True
                )
            elif not Settings.raw_link:
                print("\n")
            else:
                raise Exception(
                    "Unable to download the the file. Please check the link."
                )

            if path.isdir(Settings.current_directory + "output"):
                try:
                    Helpers.Command("PyFunceble --clean", False).execute()
                except KeyError:
                    pass
            else:
                try:
                    Helpers.Command("PyFunceble --directory-structure", False).execute()
                except KeyError:
                    pass

            self.travis_permissions()

            return True

        return False

    def stucture(self):
        """
        Read info.json and retranscript its data into the script.
        """

        if path.isfile(Settings.repository_info):
            content = Helpers.File(Settings.repository_info).read()
            Settings.informations = Helpers.Dict().from_json(content)

            to_ignore = ["raw_link", "name"]

            for index in Settings.informations:
                if Settings.informations[index] != "":
                    if index not in to_ignore[1:]:
                        self.set_info_settings(index)
                elif index in to_ignore:
                    continue

                else:
                    raise Exception(
                        'Please complete "%s" into %s'
                        % (index, Settings.repository_info)
                    )

            self.download_PyFunceble()

            Settings.file_to_test += Settings.list_name

            self.list_file()
        else:
            raise Exception(
                "Impossible to read %s" % Settings.current_directory + "info.json"
            )

    @classmethod
    def allow_test(cls):
        """
        Check if we allow a test.
        """

        if (
            not Settings.currently_under_test
            and Helpers.Regex(
                Helpers.Command("git log -1", False).execute(),
                r"Launch\stest",
                return_data=False,
            ).match()
        ):
            return True

        if Settings.days_until_next_test >= 1 and Settings.last_test != 0:
            retest_date = Settings.last_test + (
                24 * Settings.days_until_next_test * 3600
            )

            if int(strftime("%s")) >= retest_date or Settings.currently_under_test:
                return True

            return False

        return True

    @classmethod
    def _construct_arguments(cls):
        """
        Construct the arguments to pass to PyFunceble.
        """

        result = []

        result.append(
            "--cmd-before-end %s" % Settings.current_directory
            + Settings.administration_script
        )

        if Settings.arguments:
            result.extend(Settings.arguments)

        return " ".join(result)

    @classmethod
    def github_username_constructor(cls):
        """
        Create the list of user to ping.
        """

        result = []

        if Settings.ping:
            for username in Settings.ping:
                if username.startswith("@"):
                    result.append(username)
                else:
                    result.append("@%s" % username)

        return " ".join(result)

    def PyFunceble(self):  # pylint: disable=invalid-name
        """
        Install and run PyFunceble.
        """

        # pylint: disable=invalid-name
        PyFunceble_path = "PyFunceble"

        try:
            command_to_execute = (
                "export TRAVIS_BUILD_DIR=%s && " % environ["TRAVIS_BUILD_DIR"]
            )
            command_to_execute += "%s --version && " % PyFunceble_path

            usernames = self.github_username_constructor()

            if usernames:
                ping_message = " // cc %s" % usernames
            else:
                ping_message = ""

            command_to_execute += (
                "%s %s --commit-autosave-message '%s' --commit-results-message '%s' --travis-branch '%s' -f '%s'"  # pylint: disable=line-too-long
                % (
                    PyFunceble_path,
                    self._construct_arguments(),
                    "[Autosave] %s" % Settings.commit_autosave_message,
                    "[Results] %s %s"
                    % (Settings.commit_autosave_message, ping_message),
                    environ["GIT_BRANCH"],
                    Settings.file_to_test,
                )
            )
        except KeyError:
            command_to_execute = "%s %s -f %s" % (  # pylint: disable=line-too-long
                PyFunceble_path,
                self._construct_arguments(),
                Settings.file_to_test,
            )

        if self.allow_test():
            Helpers.Download(
                Settings.permanent_license_link, Settings.current_directory + "LICENSE"
            ).link()

            Settings.informations["currently_under_test"] = str(int(True))
            Settings.informations["last_test"] = strftime("%s")
            Settings.informations["days_until_next_test"] = str(0)

            Helpers.Dict(Settings.informations).to_json(Settings.repository_info)
            self.travis_permissions()

            try:
                Helpers.Command(command_to_execute, True).execute()
            except KeyError:
                pass
        else:
            print(
                "No need to test until %s."
                % ctime(
                    Settings.last_test + (24 * Settings.days_until_next_test * 3600)
                )
            )
            exit(0)


class Helpers:  # pylint: disable=too-few-public-methods
    """
    Well thanks to those helpers I wrote :)
    """

    class List:  # pylint: disable=too-few-public-methods
        """
        List manipulation.
        """

        def __init__(self, main_list=None):
            if main_list is None:
                self.main_list = []
            else:
                self.main_list = main_list

        def format(self):
            """
            Return a well formated list. Basicaly, it's sort a list and remove duplicate.
            """

            try:
                return sorted(list(set(self.main_list)), key=str.lower)

            except TypeError:
                return self.main_list

    class Dict:
        """
        Dictionary manipulations.

        Arguments:
            main_dictionnary: A dict, the main_dictionnary to pass to the whole class.
        """

        def __init__(self, main_dictionnary=None):

            if main_dictionnary is None:
                self.main_dictionnary = {}
            else:
                self.main_dictionnary = main_dictionnary

        def to_json(self, destination):
            """
            Save a dictionnary into a JSON file.

            Arguments:
                destination: A string, A path to a file where we're going to Write
                    the converted dict into a JSON format.
            """

            with open(destination, "w") as file:
                dump(
                    self.main_dictionnary,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                )

        def to_yaml(self, destination, flow_style=False):
            """
            Save a dictionnary into a YAML file.

            Arguments:
                - destination: A string, A path to a file which we are going to write.
                - flow_style: A bool, Tell us to follow or not the default flow style.
            """

            with open(destination, "w") as file:
                yaml_dump(
                    self.main_dictionnary,
                    file,
                    encoding="utf-8",
                    allow_unicode=True,
                    indent=4,
                    default_flow_style=flow_style,
                )

        @classmethod
        def from_json(cls, data):
            """
            Convert a JSON formated string into a dictionary.

            Arguments:
                data: A string, a JSON formeted string to convert to dict format.
            """

            try:
                return loads(data)

            except decoder.JSONDecodeError:
                return {}

        @classmethod
        def from_yaml(cls, yaml):
            """
            Conver a YAML formatted string into a dictionnary.

            Argument:
                yaml: A string, A YAML formatted string.
            """

            return yaml_load(yaml)

    class File:  # pylint: disable=too-few-public-methods
        """
        File treatment/manipulations.

        Arguments:
            file: A string, a path to the file to manipulate.
        """

        def __init__(self, file):
            self.file = file

        def read(self):
            """
            Read a given file path and return its content.
            """

            with open(self.file, "r", encoding="utf-8") as file:
                funilrys = file.read()

            return funilrys

        def to_list(self):
            """
            Read a file path and return each line as a list element.
            """

            result = []

            for read in open(self.file):
                result.append(read.rstrip("\n").strip())

            return result

        def write(self, data_to_write, overwrite=False):
            """
            Write or append data into the given file path.

            Argument:
                - data_to_write: str
                    The data to write.
            """

            if data_to_write is not None and isinstance(data_to_write, str):
                if overwrite or not path.isfile(self.file):
                    with open(self.file, "w", encoding="utf-8") as file:
                        file.write(data_to_write)
                else:
                    with open(self.file, "a", encoding="utf-8") as file:
                        file.write(data_to_write)

        def delete(self):
            """
            Delete a given file path.
            """

            try:
                remove(self.file)
            except OSError:
                pass

    class Download:  # pylint: disable=too-few-public-methods
        """
        This class will initiate a download of the desired link.

        Arguments:
            link_to_download: A string, the link to the file we are going to download.
            destination: A string, the destination of the downloaded data.
        """

        def __init__(self, link_to_download, destination):
            self.link_to_download = link_to_download
            self.destination = destination

        def link(self):
            """
            This method initiate the download.
            """

            req = get(self.link_to_download)

            if req.status_code == 200:
                Helpers.File(self.destination).write(req.text, overwrite=True)

                del req

                return True

            return False

    class Command:
        """
        Shell command execution.

        Arguments:
            command: A string, the command to execute.
            allow_stdout: A bool, If true stdout is always printed otherwise stdout
                is passed to PIPE.
        """

        def __init__(self, command, allow_stdout=True):
            self.decode_type = "utf-8"
            self.command = command
            self.stdout = allow_stdout

        def decode_output(self, to_decode):
            """Decode the output of a shell command in order to be readable.

            Arguments:
                to_decode: byte(s), Output of a command to decode.
            """
            if to_decode is not None:
                return str(to_decode, self.decode_type)

            return False

        def execute(self):
            """Execute the given command."""

            if not self.stdout:
                process = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=True)
            else:
                process = Popen(self.command, stderr=PIPE, shell=True)

            (output, error) = process.communicate()

            if process.returncode != 0:
                decoded = self.decode_output(error)

                if not decoded:
                    return "Unkown error. for %s" % (self.command)

                if self.stdout:
                    print(decoded)
                    exit(1)
                else:
                    return decoded

            return self.decode_output(output)

    class Regex:  # pylint: disable=too-few-public-methods

        """A simple implementation ot the python.re package

        Arguments:
            - data: str
                The data to regex check.
            - regex: str
                The regex to match.
            - group: int
                The group to return
            - rematch: bool
                True: return the matched groups into a formated list.
                    (implementation of Bash ${BASH_REMATCH})
            - replace_with: str
                The value to replace the matched regex with.
            - occurences: int
                The number of occurence(s) to replace.
        """

        def __init__(self, data, regex, **args):
            # We initiate the needed variable in order to be usable all over
            # class
            self.data = data

            # We assign the default value of our optional arguments
            optional_arguments = {
                "escape": False,
                "group": 0,
                "occurences": 0,
                "rematch": False,
                "replace_with": None,
                "return_data": True,
            }

            # We initiate our optional_arguments in order to be usable all over the
            # class
            for (arg, default) in optional_arguments.items():
                setattr(self, arg, args.get(arg, default))

            if self.escape:  # pylint: disable=no-member
                self.regex = escape(regex)
            else:
                self.regex = regex

        def not_matching_list(self):
            """
            This method return a list of string which don't match the
            given regex.
            """

            pre_result = comp(self.regex)

            return list(
                filter(lambda element: not pre_result.search(str(element)), self.data)
            )

        def matching_list(self):
            """
            This method return a list of the string which match the given
            regex.
            """

            pre_result = comp(self.regex)

            return list(
                filter(lambda element: pre_result.search(str(element)), self.data)
            )

        def match(self):
            """
            Used to get exploitable result of re.search
            """

            # We initate this variable which gonna contain the returned data
            result = []

            # We compile the regex string
            to_match = comp(self.regex)

            # In case we have to use the implementation of ${BASH_REMATCH} we use
            # re.findall otherwise, we use re.search
            if self.rematch:  # pylint: disable=no-member
                pre_result = to_match.findall(self.data)
            else:
                pre_result = to_match.search(self.data)

            if self.return_data and pre_result:  # pylint: disable=no-member
                if self.rematch:  # pylint: disable=no-member
                    for data in pre_result:
                        if isinstance(data, tuple):
                            result.extend(list(data))
                        else:
                            result.append(data)

                    if self.group != 0:  # pylint: disable=no-member
                        return result[self.group]  # pylint: disable=no-member
                else:
                    result = pre_result.group(
                        self.group  # pylint: disable=no-member
                    ).strip()

                return result

            if not self.return_data and pre_result:  # pylint: disable=no-member
                return True

            return False

        def replace(self):
            """
            Used to replace a matched string with another.
            """

            if self.replace_with:  # pylint: disable=no-member
                return substrings(
                    self.regex,
                    self.replace_with,  # pylint: disable=no-member
                    self.data,
                    self.occurences,  # pylint: disable=no-member
                )

            return self.data


if __name__ == "__main__":
    try:
        from yaml import dump as yaml_dump
        from yaml import safe_load as yaml_load
    except ModuleNotFoundError:
        Helpers.Command("pip3 install pyyaml").execute()

        from yaml import dump as yaml_dump
        from yaml import safe_load as yaml_load

    Initiate().PyFunceble()
