terraform {
  backend "s3" {
    bucket = "superdev-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
