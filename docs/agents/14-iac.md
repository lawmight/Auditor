# Agent 14: Terraform and AWS CDK

## Scope

Inventory IaC packages and commands.

## Method

LOC for terraform/ and aws_cdk/. Confirm Click commands terraform and cdk. Note HCL extractor.

## Evidence

- `docs/evidence/14_terraform_loc.tsv`
- `docs/evidence/14_aws_cdk_loc.tsv`
- `theauditor/commands/terraform.py`
- `theauditor/commands/cdk.py`
- `theauditor/ast_extractors/hcl_impl.py`

## Findings

Terraform package ~675 LOC (3 files) including graph construction into graphs.db. AWS CDK package ~230 LOC (2 files). HCL extractor sits under ast_extractors. Commands `terraform` and `cdk` are registered.

Compared to indexer/rules, IaC is a thin vertical. Capability claims in marketing docs overstate depth relative to LOC, but the seams are real and wired.

## Verdict

`VERIFIED`
