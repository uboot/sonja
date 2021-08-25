import docker
import os
import re
import string
import tarfile
import threading

from conanci.config import logger
from conanci.ssh import decode
from io import BytesIO, FileIO
from queue import Empty, SimpleQueue


docker_image_pattern = ("(([a-z0-9\\.-]+(:[0-9]+)?/)?"
                        "[a-z0-9\\.-/]+)[:@]([a-z0-9\\.-]+)$")
build_package_dir_name = "conan_build_package"
build_output_dir_name = "conan_output"


def create_build_tar(script_template_name: str, parameters: dict):

    def add_content(tar_archive, file_name, text_data):
        tar_info = tarfile.TarInfo("{0}/{1}".format(build_package_dir_name, file_name))
        content = BytesIO(bytes(text_data, "utf-8"))
        tar_info.size = len(content.getbuffer())
        tar_archive.addfile(tar_info, content)

    setup_file_path = os.path.join(os.path.dirname(__file__), script_template_name)
    with open(setup_file_path) as setup_template_file:
        template = string.Template(setup_template_file.read())
    script = template.substitute(parameters)

    # place into archive
    f = BytesIO()
    tar = tarfile.open(mode="w", fileobj=f, dereference=True)
    script_name = script_template_name[:-3]
    add_content(tar, script_name, script)
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
    for bytes in data:
        f.write(bytes)
    f.seek(0)
    tar = tarfile.open(fileobj=f)
    output_files = ["create", "info"]
    result = dict()
    for output_file in output_files:
        try:
            result[output_file] = tar.extractfile("{0}/{1}.json".format(build_output_dir_name, output_file)).read()
        except KeyError:
            pass

    return result


class Builder(object):
    def __init__(self, build_os, image):
        self.__client = docker.from_env()
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
    def script_template(self):
        if self.__build_os == "Linux":
            return "build.sh.in"
        else:
            return "build.ps1.in"

    @property
    def build_package_dir(self):
        if self.__build_os == "Linux":
            return "/{0}".format(build_package_dir_name)
        else:
            return "C:\\{0}".format(build_package_dir_name)

    @property
    def build_package_dir(self):
        if self.__build_os == "Linux":
            return "/{0}".format(build_package_dir_name)
        else:
            return "C:\\{0}".format(build_package_dir_name)

    @property
    def root_dir(self):
        if self.__build_os == "Linux":
            return "/"
        else:
            return "C:\\"

    @property
    def build_output_dir(self):
        if self.__build_os == "Linux":
            return "/tmp/{0}".format(build_output_dir_name)
        else:
            return "C:\\{0}".format(build_output_dir_name)

    @property
    def build_command(self):
        if self.__build_os == "Linux":
            return "sh {0}/build.sh".format(self.build_package_dir)
        else:
            return 'cmd /s /c "powershell -File {0}\\build.ps1"'.format(self.build_package_dir)

    def pull(self, parameters):
        m = re.match(docker_image_pattern, self.__image)
        if not m:
            raise Exception("The image '{0}' is not a valid "
                            "docker image name".format(self.__image))
        tag = m.group(4)
        repository = m.group(1)
        if tag == "local":
            logger.info("Do not pull local image '%s'", self.__image)
            return

        auth_config = None
        if parameters['docker_user']:
            auth_config = {
                "username": parameters['docker_user'],
                "password": parameters['docker_password']
            }

        logger.info("Pull docker image '%s'", self.__image)
        self.__client.images.pull(repository=repository, tag=tag, auth_config=auth_config)

    def setup(self, parameters):
        logger.info("Setup docker container")

        self.__container = self.__client.containers.create(image=self.__image,
                                                           command=self.build_command)
        logger.info("Created docker container '%s'", self.__container.short_id)

        config_url = "{0} --type=git".format(parameters["conan_config_url"])
        config_branch = "--args \"-b {0}\"".format(parameters["conan_config_branch"])\
            if parameters["conan_config_branch"] else ""
        config_path = "-sf {0}".format(parameters["conan_config_path"])\
            if parameters["conan_config_path"] else ""

        patched_parameters = {
            **parameters,
            "conan_config_args": " ".join([config_url, config_branch, config_path]),
            "build_package_dir": self.build_package_dir,
            "build_output_dir": self.build_output_dir
        }
        build_tar = create_build_tar(self.script_template, patched_parameters)
        result = self.__container.put_archive(self.root_dir, data=build_tar)
        if not result:
            raise Exception("Failed to copy build files to container '{0}'"\
                            .format(self.__container.short_id))
        logger.info("Copied build files to container '%s'", self.__container.short_id)

    def run(self):
        with self.__cancel_lock:
            if self.__cancelled:
                logger.info("Build was cancelled")
                return
            logger.info("Start build in container '{0}'" \
                        .format(self.__container.short_id))
            self.__container.start()
            self.__container_logs = self.__container.logs(stream=True, follow=True)
        for byte_data in self.__container_logs:
            line = byte_data.decode("utf-8").strip('\n\r')
            self.__logs.put(line)
        with self.__cancel_lock:
            self.__container_logs = None
            if self.__cancelled:
                logger.info("Build was cancelled")
                return

        result = self.__container.wait()

        try:
            data, _ = self.__container.get_archive(self.build_output_dir)
            self.build_output = extract_output_tar(data)
        except docker.errors.APIError:
            logger.error("Failed to obtain build output from container '%s'", self.__container.short_id)

        if result.get("StatusCode"):
            raise Exception("Build in container '{0}' failed with status '{1}'".format(
                            self.__container.short_id, result.get("StatusCode")))

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
