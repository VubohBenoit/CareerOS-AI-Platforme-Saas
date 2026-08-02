variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-1"
}

variable "allowed_ssh_cidrs" {
  description = "CIDR blocks allowed for SSH"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "db_name" {
  description = "Database name"
  default     = "careerosdb"
}

variable "db_username" {
  description = "Database username"
  default     = "careerosadmin"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  sensitive   = true
}

variable "key_pair_name" {
  description = "EC2 key pair name"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository URL"
  default     = "https://github.com/VubohBenoit/CareerOS-AI-Platforme-Saas.git"
}
