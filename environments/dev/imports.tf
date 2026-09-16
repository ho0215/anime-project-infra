# 기존에 수동/이전 apply로 만든 리소스를 빈 state에 다시 붙일 때 사용.
# state에 이미 있으면 import 블록은 no-op.

import {
  to = module.ecr.aws_ecr_repository.app
  id = "aniverse"
}

# cp1에서 수동 create-access-entry 한 iac-admin (kubectl 권한)
import {
  to = module.eks.aws_eks_access_entry.admins["arn:aws:iam::679583587966:user/iac-admin"]
  id = "aniverse-eks:arn:aws:iam::679583587966:user/iac-admin"
}

import {
  to = module.eks.aws_eks_access_policy_association.admins["arn:aws:iam::679583587966:user/iac-admin"]
  id = "aniverse-eks#arn:aws:iam::679583587966:user/iac-admin#arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
}
