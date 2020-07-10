import os
from conans import ConanFile, tools


class AndroidNDK(ConanFile):
    name = "android-ndk"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.android.com/ndk/index.html"
    description = "The Android NDK is a toolset that lets you implement parts of your app in"
                  " native code, using languages such as C and C++"
    topics = ("NDK", "android", "toolchain", "compiler")
    license = "Apache-2.0"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
