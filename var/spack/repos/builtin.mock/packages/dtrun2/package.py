# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Dtrun2(Package):
    """Simple package which acts as a run dependency"""

    homepage = "http://www.example.com"
    url = "http://www.example.com/dtrun2-1.0.tar.gz"

    version('1.0', '0123456789abcdef0123456789abcdef')
