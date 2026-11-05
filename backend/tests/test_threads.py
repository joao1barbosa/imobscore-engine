"""Teste das threads do OpenBLAS: uma só, porque o motor usa matrizes pequenas."""

import numpy
import threadpoolctl


def test_openblas_usa_uma_thread_so() -> None:
    numpy.zeros((2, 2))
    libraries = [
        info for info in threadpoolctl.threadpool_info() if info["internal_api"] == "openblas"
    ]

    assert libraries, "o OpenBLAS do numpy não apareceu na lista do threadpoolctl"
    assert all(info["num_threads"] == 1 for info in libraries)
