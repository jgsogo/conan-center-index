import os
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from jinja2 import Template


class AndroidNDK(ConanFile):
    name = "android-ndk"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.android.com/ndk/index.html"
    description = "The Android NDK is a toolset that lets you implement parts of your app in"\
                  " native code, using languages such as C and C++"
    topics = ("NDK", "android", "toolchain", "compiler")
    license = "Apache-2.0"
    settings = "os", "arch"
    exports_sources = ["cmake-wrapper"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.arch != 'x86_64':
            raise ConanInvalidConfiguration("No binaries available for other than 'x86_64' architectures")

    def build(self):
        tarballs = self.conan_data["sources"][self.version]
        tools.get(**tarballs[str(self.settings.os)])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy("cmake-wrapper", dst="bin")
        self.copy(pattern="*", dst="bin", src=self._source_subfolder, keep_path=True, symlinks=True)
        self.copy(pattern="*NOTICE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*NOTICE.toolchain", dst="licenses", src=self._source_subfolder)
        self._fix_permissions()

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _fix_permissions(self):
        if os.name != 'posix':
            return
        for root, _, files in os.walk(self.package_folder):
            for filename in files:
                filename = os.path.join(root, filename)
                with open(filename, 'rb') as f:
                    sig = f.read(4)
                    if type(sig) is str:
                        sig = [ord(s) for s in sig]
                    else:
                        sig = [s for s in sig]
                    if len(sig) > 2 and sig[0] == 0x23 and sig[1] == 0x21:
                        self.output.info('chmod on script file: "%s"' % filename)
                        self._chmod_plus_x(filename)
                    elif sig == [0x7F, 0x45, 0x4C, 0x46]:
                        self.output.info('chmod on ELF file: "%s"' % filename)
                        self._chmod_plus_x(filename)
                    elif sig == [0xCA, 0xFE, 0xBA, 0xBE] or \
                         sig == [0xBE, 0xBA, 0xFE, 0xCA] or \
                         sig == [0xFE, 0xED, 0xFA, 0xCF] or \
                         sig == [0xCF, 0xFA, 0xED, 0xFE] or \
                         sig == [0xFE, 0xEF, 0xFA, 0xCE] or \
                         sig == [0xCE, 0xFA, 0xED, 0xFE]:
                        self.output.info('chmod on Mach-O file: "%s"' % filename)
                        self._chmod_plus_x(filename)

    def package_info(self):
        # ndk-build: https://developer.android.com/ndk/guides/ndk-build
        self.env_info.PATH.append(os.path.join(self.package_folder, 'bin'))

        # cmake: https://developer.android.com/ndk/guides/cmake#command-line
        if hasattr(self, 'settings_target'):
            self.env_info.CONAN_CMAKE_PROGRAM = os.path.join(self.package_folder, "bin", "cmake-wrapper")
            self.env_info.CMAKE_TOOLCHAIN_FILE = os.path.join(self.package_folder, "bin", "build", "cmake", "android.toolchain.cmake")
            self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(self.package_folder, "bin", "build", "cmake", "android.toolchain.cmake")
            self.env_info.ANDROID_PLATFORM = str(self.settings_target.os.api_level)

        # Other build-systems: https://developer.android.com/ndk/guides/other_build_systems
        # Translate settings_target to triplet
        if hasattr(self, 'settings_target'):
            host_tag = {'Windows': 'windows-x86_64', 'Linux': 'linux-x86_64', 'Macos': 'darwin-x86_64'}.get(str(self.settings.os))
            minSdkVersion = self.settings_target.os.api_level
            
            def _clang_triplet(arch):
                arch = {'armv7': 'armv7a',
                        'armv8': 'aarch64',
                        'x86': 'i686',
                        'x86_64': 'x86_64'}.get(str(arch))
                abi = 'androideabi' if arch == 'armv7' else 'android'
                return '%s-linux-%s' % (arch, abi)

            triplet = _clang_triplet(str(self.settings_target.arch))
            self.env_info.TARGET = triplet

            base_path = os.path.join(self.package_folder, "bin", "toolchains", "llvm", "prebuilt", host_tag, "bin")
            self.env_info.CC = os.path.join(base_path, "{}{}-clang".format(triplet, minSdkVersion))
            self.env_info.CXX = os.path.join(base_path, "{}{}-clang++".format(triplet, minSdkVersion))
            #self.env_info.ADDR2LINE = os.path.join(base_path, "{}-addr2line".format(triplet))
            self.env_info.AR = os.path.join(base_path, "{}-ar".format(triplet))
            self.env_info.AS = os.path.join(base_path, "{}-as".format(triplet))
            #self.env_info.ELFEDIT = os.path.join(base_path, "{}-elfedit".format(triplet))
            self.env_info.LD = os.path.join(base_path, "{}-ld".format(triplet))
            #self.env_info.NM = os.path.join(base_path, "{}-nm".format(triplet))
            #self.env_info.OBJCOPY = os.path.join(base_path, "{}-objcopy".format(triplet))
            #self.env_info.OBJDUMP = os.path.join(base_path, "{}-objdump".format(triplet))
            self.env_info.RANLIB = os.path.join(base_path, "{}-ranlib".format(triplet))
            #self.env_info.READELF = os.path.join(base_path, "{}-readelf".format(triplet))
            self.env_info.STRIP = os.path.join(base_path, "{}-strip".format(triplet))

