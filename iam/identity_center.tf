# some comment

data instances" "acme" {
  # No parameters
}

locals {
  identity_center_arn = tolist(data.aws_ssoadmin_instances.stacklok.arns)[0]
  identity_center_id  = tolist(data.aws_ssoadmin_instances.stacklok.identity_store_ids)[0]

  sso_accounts = {
    luke              = { given = "Luke", family = "Hinds" },
    jeff               = { given = "Jeff", family = "Monroe" },
    mick         = { given = "Mick", family = "Steady", admin = true },
    jane            = { given = "Jane", family = "Doe", other = true, admin = true },
  }
}

# some comment
