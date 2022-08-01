import docker
import os
import re
import string
import tarfile
import threading

from sonja.config import logger
from sonja.credential_helper import build_credential_helper
from sonja.ssh import decode
from io import BytesIO, FileIO
from queue import Empty, SimpleQueue


docker_image_pattern = ("(([a-z0-9-]+\\.[a-z0-9\\.-]+(:[0-9]+)?/)?"
                        "[a-z0-9\\.-/]+)[:@]([a-z0-9\\.-]+)$")
build_package_dir_name = "conan_build_package"
build_output_dir_name = "conan_output"


class BuildFailed(Exception):
    pass


def create_build_tar(script_template_name: str, parameters: dict):

    def add_content(tar_archive, file_name, text_data, is_script = False):
        tar_info = tarfile.TarInfo("{0}/{1}".format(build_package_dir_name, file_name))
        content = BytesIO(bytes(text_data, "utf-8"))
        tar_info.size = len(content.getbuffer())
        if is_script:
            tar_info.mode = 0o555
        tar_archive.addfile(tar_info, content)

    setup_file_path = os.path.join(os.path.dirname(__file__), script_template_name)
    with open(setup_file_path) as setup_template_file:
        template = string.Template(setup_template_file.read())
    script = template.substitute(parameters)

    credential_helper = build_credential_helper(parameters["git_credentials"])

    # place into archive
    f = BytesIO()
    tar = tarfile.open(mode="w", fileobj=f, dereference=True)
    script_name = script_template_name[:-3]
    add_content(tar, script_name, script)
    add_content(tar, "credential_helper.sh", credential_helper, is_script=True)
    add_content(tar, "id_rsa", decode(parameters["ssh_key"]))
    add_content(tar, "known_hosts", decode(parameters["known_hosts"]))
    tar.close()
    f.seek(0)

    # with open("build.tar", "wb") as dump:
    #     dump.write(f.read())
    # f.seek(0)

    return f


def extract_output_tar(data: FileIO):
    f = BytesIO()
    for chunk in data:
        f.write(chunk)
    f.seek(0)
    tar = tarfile.open(fileobj=f)
    output_files = ["create", "info", "lock"]
    result = dict()
    for output_file in output_files:
        try:
            result[output_file] = tar.extractfile("{0}/{1}.json".format(build_output_dir_name, output_file)).read()
        except KeyError:
            pass

    return result


class Builder(object):
    def __init__(self, build_os, image):
        try:
            self.__client = docker.from_env()
        except docker.errors.DockerException as e:
            raise BuildFailed(f"Failed to instantiate docker client: '{e}")

        self.__image = image
        self.__build_os = build_os
        self.__container = None
        self.__container_logs = None
        self.__cancel_lock = threading.Lock()
        self.__cancelled = False
        self.__logs = SimpleQueue()
        self.build_output = dict()

    def __enter__(self):
        return self

    @property
    def __script_template(self):
        if self.__build_os == "Linux":
            return "build.sh.in"
        else:
            return "build.ps1.in"

    @property
    def __build_package_dir(self):
        if self.__build_os == "Linux":
            return "/{0}".format(build_package_dir_name)
        else:
            return "C:\\{0}".format(build_package_dir_name)

    @property
    def __escaped_build_package_dir(self):
        if self.__build_os == "Linux":
            return "/{0}".format(build_package_dir_name)
        else:
            return "C:\\\\{0}".format(build_package_dir_name)

    @property
    def __root_dir(self):
        if self.__build_os == "Linux":
            return "/"
        else:
            return "C:\\"

    @property
    def __build_output_dir(self):
        if self.__build_os == "Linux":
            return "/tmp/{0}".format(build_output_dir_name)
        else:
            return "C:\\{0}".format(build_output_dir_name)

    @property
    def __build_command(self):
        if self.__build_os == "Linux":
            return "sh {0}/build.sh".format(self.__build_package_dir)
        else:
            return 'cmd /s /c "powershell -File {0}\\build.ps1"'.format(self.__build_package_dir)

    def pull(self, parameters):
        m = re.match(docker_image_pattern, self.__image)
        if not m:
            raise BuildFailed(f"The image '{self.__image}' is not a valid docker image name")
        tag = m.group(4)
        repository = m.group(1)
        server = m.group(2).strip("/") if m.group(2) else ""
        if tag == "local":
            logger.info("Do not pull local image '%s'", self.__image)
            return

        auth_config = None
        credentials = next((c for c in parameters['docker_credentials'] if c["server"] == server), None)
        if credentials is not None:
            auth_config = {
                "username": credentials['username'],
                "password": credentials['password']
            }

        logger.info("Pull docker image '%s'", self.__image)
        try:
            self.__client.images.pull(repository=repository, tag=tag, auth_config=auth_config)
        except docker.errors.APIError as e:
            raise BuildFailed(f"Failed to pull docker container '{self.__image}': {e}")

    def setup(self, parameters):
        logger.info("Setup docker container")

        try:
            self.__container = self.__client.containers.create(image=self.__image,
                                                               command=self.__build_command)
            logger.info("Created docker container '%s'", self.__container.short_id)
        except docker.errors.APIError as e:
            raise BuildFailed(f"Failed to create docker container from image '{self.__image}': {e}")

        config_url = "{0} --type=git".format(parameters["conan_config_url"])
        config_branch = "--args \"-b {0}\"".format(parameters["conan_config_branch"])\
            if parameters["conan_config_branch"] else ""
        config_path = "-sf {0}".format(parameters["conan_config_path"])\
            if parameters["conan_config_path"] else ""
        user_channel = "{0}/{1}".format(parameters["sonja_user"], parameters["channel"]) \
            if parameters["sonja_user"] else ""
        version_user_channel = "{0}@{1}".format(parameters["version"], user_channel) \
            if parameters["version"] or user_channel else ""
        lock_file_version_arg = "--version {0}".format(parameters["version"]) if parameters["version"] else ""
        lock_file_user_arg = "--user {0} --channel {1}".format(parameters["sonja_user"], parameters["channel"]) \
            if parameters["sonja_user"] else ""

        patched_parameters = {
            **parameters,
            "conan_config_args": " ".join([config_url, config_branch, config_path]),
            "build_package_dir": self.__build_package_dir,
            "escaped_build_package_dir": self.__escaped_build_package_dir,
            "build_output_dir": self.__build_output_dir,
            "create_reference": version_user_channel,
            "info_reference": user_channel,
            "lock_args": " ".join([lock_file_version_arg, lock_file_user_arg])
        }
        build_tar = create_build_tar(self.__script_template, patched_parameters)

        try:
            self.__container.put_archive(self.__root_dir, data=build_tar)
            logger.info("Copied build files to container '%s'", self.__container.short_id)
        except docker.errors.APIError as e:
            raise BuildFailed("Failed to copy build files to container '{0}': {1}"\
                              .format(self.__container.short_id, e))

    def run(self):
        with self.__cancel_lock:
            if self.__cancelled:
                logger.info("Build was cancelled")
                return
            logger.info("Start build in container '{0}'" \
                        .format(self.__container.short_id))
            try:
                self.__container.start()
                self.__container_logs = self.__container.logs(stream=True, follow=True)
            except docker.errors.APIError as e:
                raise BuildFailed(f"Failed to start container: {e}")

        for byte_data in self.__container_logs:
            line = byte_data.decode("utf-8", errors="replace").strip('\n\r')
            self.__logs.put(line)
        with self.__cancel_lock:
            self.__container_logs = None
            if self.__cancelled:
                logger.info("Build was cancelled")
                return

        result = self.__container.wait()

        try:
            data, _ = self.__container.get_archive(self.__build_output_dir)
            self.build_output = extract_output_tar(data)
        except docker.errors.APIError as e:
            raise BuildFailed(f"Failed to obtain build output from container '{self.__container.short_id}': e")

        status_code = result.get("StatusCode")
        if status_code:
            raise BuildFailed(f"Build in container '{self.__container.short_id}' returned status code '{status_code}'")

    def cancel(self):
        with self.__cancel_lock:
            logger.info("Cancel build")
            self.__cancelled = True
            if self.__container_logs:
                logger.info("Close logs")
                self.__container_logs.close()

    def __exit__(self, type, value, traceback):
        if not self.__container:
            return

        try:
            logger.info("Stop docker container '%s'", self.__container.short_id)
            self.__container.stop()
        except docker.errors.APIError:
            pass

        try: 
            logger.info("Remove docker container '%s'", self.__container.short_id)
            self.__container.remove()
        except docker.errors.APIError:
            pass

    def get_log_lines(self):
        try:
            while True:
                yield self.__logs.get_nowait()
        except Empty:
            pass
