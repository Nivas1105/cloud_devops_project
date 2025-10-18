🚀 Terraform + Atlantis Setup on AWS EC2 (GitHub Actions CI/CD)

This documents the full process of setting up Atlantis to automatically manage and apply Terraform changes through GitHub pull requests.
It covers AWS EC2 deployment, SSH/permission setup, GitHub Actions automation, and solutions to common issues faced during integration.

🧩 Overview
What We Built

Infrastructure as Code (IaC): Managed AWS resources using Terraform.

Automation: Integrated Atlantis for PR-based Terraform plan & apply.

CI/CD: Used GitHub Actions to deploy Atlantis and manage Terraform workflow.

Security: Managed SSH keys, IAM roles, and GitHub secrets securely.

## 🏗️ Architecture

```text
GitHub Repo
   │
   ├── PR opened → Atlantis runs terraform plan
   │
   ├── Maintainer approves → Atlantis applies changes on EC2
   │
   └── EC2 Instance hosts Atlantis + Terraform backend (S3 + DynamoDB)
```

⚙️ Step-by-Step Setup
1. 🖥️ EC2 Instance Setup

Launch an Amazon Linux 2 / Ubuntu EC2 instance.

Allow inbound rules in Security Group:

Port 22 → SSH

Port 4141 → Atlantis Webhook endpoint

Connect via SSH:

ssh -i "key.pem" ec2-user@<EC2_PUBLIC_IP>


🧩 1. Container Setup for Atlantis

Atlantis was deployed on an Amazon EC2 instance inside a Docker container to handle pull-request-based Terraform automation.

docker run -d \
  --name atlantis \
  -p 4141:4141 \
  -v /home/ec2-user/repos:/repos \
  -v /home/ec2-user/.aws:/root/.aws \
  runatlantis/atlantis server \
  --repo-whitelist="github.com/Nivas1105/*" \
  --gh-user="github-bot-username" \
  --gh-token="$GITHUB_TOKEN" \
  --atlantis-url="http://<ec2-public-ip>:4141" \
  --port=4141

⚙️ 2. Configuring GitHub → Atlantis Webhook

Atlantis needs to listen to GitHub events (PR opened, merged, etc.).

Problem: Webhook failed because EC2’s security group didn’t allow inbound traffic on port 4141.

Solution:

Updated EC2 security group inbound rules to allow:

Port 4141 (HTTP for Atlantis)

Port 22 (SSH access)

Verified public access via:
http://<ec2-public-ip>:4141

Result: GitHub successfully sent webhook events to Atlantis.

🔐 3. AWS Backend Configuration Issue

Error faced:

Error: Failed to get existing workspaces: operation error S3: ListObjectsV2, 
requested bucket from "us-east-1", actual location "ap-south-1"


Root cause:
Terraform backend in main.tf was configured with a bucket created in ap-south-1, but Atlantis (running on EC2) tried to use the default us-east-1 region.

Fix:

terraform {
  backend "s3" {
    bucket         = "my-terraform-state-nivas"
    key            = "env:/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
  }
}


Result:
Atlantis could now access the S3 bucket and DynamoDB lock table correctly.

🧱 4. Permission Denied: GitHub SSH Key

Error:

git@github.com: Permission denied (publickey).


Cause: Atlantis container didn’t have a GitHub SSH key configured.

Resolution:

Generated SSH key inside EC2:

ssh-keygen -t rsa -b 4096 -C "atlantis-ec2"


Copied the public key (~/.ssh/id_rsa.pub) to GitHub →
Repository → Settings → Deploy keys → Add deploy key → Allow write access

Verified connection:

ssh -T git@github.com


Result: Atlantis container gained access to clone and push Terraform changes to the repo.

🪣 5. S3 & DynamoDB IAM Policy Setup

Issue:
Terraform couldn’t lock or write state files because of insufficient permissions.

Fix:
Attached a custom IAM Role to the EC2 instance with these permissions:

{
  "Effect": "Allow",
  "Action": [
    "s3:*",
    "dynamodb:*"
  ],
  "Resource": "*"
}


Result:
Atlantis gained full access to manage Terraform state backend safely.

🧠 6. atlantis.yaml and repo.yaml Configuration

Created .atlantis.yaml to define project workflow:

version: 3
projects:
  - dir: terraform
    workflow: default
    autoplan:
      when_modified: ["*.tf", "*.tfvars"]
      enabled: true


Result:
Every pull request automatically triggers terraform plan, and approvals trigger terraform apply directly on EC2.

✅ Final Outcome

✅ Atlantis container deployed successfully on EC2

✅ Integrated securely with GitHub webhooks

✅ Terraform state managed in S3 + DynamoDB backend

✅ Automated plan & apply triggered on pull requests

🧭 Verification

To test:

Open a PR in GitHub that modifies .tf files.

Observe Atlantis posting terraform plan results directly in the PR comments.

Approve the PR → Atlantis performs terraform apply.

4. 🔐 Configure SSH for GitHub Access

Generate SSH key:

ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f ~/.ssh/ec2_key


Add the public key to your GitHub repo:

Go to GitHub → Settings → Deploy Keys → Add Key

Paste content of:

cat ~/.ssh/ec2_key.pub


Enable Allow write access

Test connection:

ssh -T git@github.com

5. ⚙️ Atlantis Configuration

Create /etc/atlantis/config.yaml:

repos:
  - id: /.*/
    apply_requirements: [approved, mergeable]
    workflow: default

server:
  port: 4141
  data-dir: /var/lib/atlantis
  allow-repo-config: true
  gh-user: atlantis-bot
  gh-token: <GITHUB_PERSONAL_ACCESS_TOKEN>
  gh-webhook-secret: <WEBHOOK_SECRET>
  repo-allowlist: github.com/your-username/your-repo

6. 🧱 Run Atlantis Server
sudo nohup atlantis server \
  --config=/etc/atlantis/config.yaml \
  --port=4141 \
  --allow-repo-config \
  --repo-allowlist="github.com/your-username/your-repo" \
  --gh-user="atlantis-bot" \
  --gh-token="<GITHUB_TOKEN>" \
  --gh-webhook-secret="<WEBHOOK_SECRET>" \
  > atlantis.log 2>&1 &


To stop Atlantis later:

pkill -f atlantis

7. 🌐 GitHub Webhook Setup

Go to your GitHub repo → Settings → Webhooks → Add webhook:

Payload URL: http://<EC2_PUBLIC_IP>:4141/events

Content type: application/json

Secret: same as <WEBHOOK_SECRET> in config

Select events: Pull requests, Issue comments, Push
