"""API do ImobScore."""

import os

# O OpenBLAS abre uma thread por núcleo, o que só atrapalha nas matrizes
# pequenas do motor e quase dobra o tempo de resposta.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
