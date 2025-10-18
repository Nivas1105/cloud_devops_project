terraform {
  backend "s3" {
    bucket         = "my-terraform-state-nivas"
    key            = "envs/dev/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }
}

provider "random" {}

resource "random_pet" "name" {
  length = 3
}
