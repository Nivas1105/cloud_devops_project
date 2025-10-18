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
