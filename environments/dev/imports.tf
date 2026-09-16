# 기존에 수동/이전 apply로 만든 리소스를 빈 state에 다시 붙일 때 사용.
# state에 이미 있으면 import 블록은 no-op.

import {
  to = module.ecr.aws_ecr_repository.app
  id = "aniverse"
}
