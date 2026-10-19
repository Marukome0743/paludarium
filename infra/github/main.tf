resource "github_repository" "this" {
  name        = var.repository_name
  description = var.repository_description
  visibility  = var.repository_visibility
  topics      = var.repository_topics

  has_issues      = true
  has_discussions = false
  has_projects    = true
  has_wiki        = true

  allow_merge_commit     = false
  allow_squash_merge     = true
  allow_rebase_merge     = false
  allow_auto_merge       = true
  delete_branch_on_merge = true

  web_commit_signoff_required = true

  archived = false

  lifecycle {
    prevent_destroy = true
  }
}

# The repository and GitHub's default labels existed before this module: the
# first apply adopts them from an empty state instead of creating them.
import {
  to = github_repository.this
  id = var.repository_name
}

resource "github_repository_vulnerability_alerts" "this" {
  repository = github_repository.this.name
}

locals {
  # The pull-request gates of ci.yml (team.md, Testing Posture) and the
  # commit-format check. Keep each context equal to the job's check name.
  required_checks = [
    "check / Commitlint",
    "lint",
    "dependencies",
    "unit tests (ubuntu-latest)",
    "unit tests (macos-latest)",
    "unit tests (windows-latest)",
    "differential tests (x86-64 Linux)",
    "line coverage >= 80%",
    "production wasm (shared Rust heap, nested Workers)",
    "U10 fixed guests and fresh native differential / native-first",
    "U10 fixed guests and fresh native differential / fixture-metadata-oracle",
    "U10 fixed guests and fresh native differential / differential",
    "u11-programs / build-oracle",
    "u11-programs / differential (ubuntu-latest, node)",
    "u11-programs / differential (ubuntu-latest, chromium)",
    "u11-programs / differential (ubuntu-latest, firefox)",
    "u11-programs / differential (macos-latest, safari)",
    "u11-fuzz / fuzz (load_elf)",
    "u11-fuzz / fuzz (syscall_args)",
    "u11-fuzz / fuzz (vfs_paths)",
    "u11-fuzz / fuzz (kernel_futex_u5)",
    "u11-fuzz / fuzz (kernel_threads_u5)",
    "u11-fuzz / fuzz (kernel_events_u6)",
    "u11-fuzz / fuzz (kernel_sockets_u6)",
  ]
}

resource "github_repository_ruleset" "main" {
  name        = "main"
  repository  = github_repository.this.name
  target      = "branch"
  enforcement = "active"

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  bypass_actors {
    actor_id    = 5
    actor_type  = "RepositoryRole"
    bypass_mode = "always"
  }

  rules {
    deletion                = true
    non_fast_forward        = true
    required_linear_history = true
    required_signatures     = true

    pull_request {
      required_approving_review_count   = 0
      dismiss_stale_reviews_on_push     = true
      require_code_owner_review         = false
      require_last_push_approval        = false
      required_review_thread_resolution = true
    }

    required_status_checks {
      strict_required_status_checks_policy = false

      dynamic "required_check" {
        for_each = local.required_checks

        content {
          context        = required_check.value
          integration_id = 15368
        }
      }
    }
  }
}

locals {
  labels = {
    "bug"              = { color = "d73a4a", description = "Something isn't working" }
    "documentation"    = { color = "0075ca", description = "Improvements or additions to documentation" }
    "duplicate"        = { color = "cfd3d7", description = "This issue or pull request already exists" }
    "enhancement"      = { color = "a2eeef", description = "New feature or request" }
    "good first issue" = { color = "7057ff", description = "Good for newcomers" }
    "help wanted"      = { color = "008672", description = "Extra attention is needed" }
    "invalid"          = { color = "e4e669", description = "This doesn't seem right" }
    "question"         = { color = "d876e3", description = "Further information is requested" }
    "wontfix"          = { color = "ffffff", description = "This will not be worked on" }

    "type: bug"      = { color = "d73a4a", description = "Something isn't working" }
    "type: feature"  = { color = "a2eeef", description = "New feature or capability" }
    "type: docs"     = { color = "0075ca", description = "Documentation improvements" }
    "type: refactor" = { color = "cfd3d7", description = "Code refactoring without behavior change" }
    "type: test"     = { color = "bfdadc", description = "Test additions or improvements" }
    "type: chore"    = { color = "fef2c0", description = "Maintenance tasks" }

    # Applied by .github/labeler.yml.
    "ci"           = { color = "ededed", description = "CI and GitHub Actions" }
    "infra"        = { color = "1d76db", description = "Infrastructure as Code under infra/" }
    "dependencies" = { color = "0366d6", description = "Pull requests that update a dependency file" }
    "emulator"     = { color = "5319e7", description = "Emulator crates and fuzz targets" }
    "wasm"         = { color = "6f42c1", description = "WebAssembly runtime, JIT and npm package" }
    "tests"        = { color = "bfdadc", description = "Tests and verification" }
    "tooling"      = { color = "fef2c0", description = "Development and release tooling" }
    "records"      = { color = "c2e0c6", description = "AI-DLC records under aidlc/" }

    "status: triage"        = { color = "e99695", description = "Needs initial triage" }
    "status: blocked"       = { color = "000000", description = "Blocked by something" }
    "status: in-progress"   = { color = "0052cc", description = "Currently being worked on" }
    "status: apply-failure" = { color = "b60205", description = "Auto-filed when Terraform Apply fails on main; auto-closed on recovery" }
  }

  # GitHub's default labels, created with the repository.
  existing_labels = toset([
    "bug", "documentation", "duplicate", "enhancement", "good first issue",
    "help wanted", "invalid", "question", "wontfix",
  ])
}

resource "github_issue_label" "labels" {
  for_each = local.labels

  repository  = github_repository.this.name
  name        = each.key
  color       = each.value.color
  description = each.value.description
}

import {
  for_each = local.existing_labels
  to       = github_issue_label.labels[each.key]
  id       = "${var.repository_name}:${each.key}"
}
