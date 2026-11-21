#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import sys; assert sys.version_info >= (3, 10), "É necessário Python 3.10 ou superior"; print("Ambiente pronto. Esta versão usa apenas a biblioteca padrão do Python.")'
