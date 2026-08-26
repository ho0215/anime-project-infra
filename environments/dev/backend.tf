terraform {
  backend "s3" {
    bucket       = "aniverse-tfstate-younju"
    key          = "dev/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
