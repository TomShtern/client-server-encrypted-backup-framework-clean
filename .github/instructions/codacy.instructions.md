---
    description: Configuration for AI behavior when interacting with Codacy's MCP Server
    applyTo: '**'
---
IMPORTANT: For extremely important AI guidance, rules, and data please consult the `#file:AI-Context` folder. Additional important documentation and design reference materials are in the `#file:important_docs` folder. Use `AI-Context` first for critical decisions.
# Codacy Rules
Configuration for AI behavior when interacting with Codacy's MCP Server

## CRITICAL: After ANY successful `edit_file` or `reapply` operation
- YOU MUST IMMEDIATELY run the `codacy_cli_analyze` tool from Codacy's MCP Server for each file that was edited, with:
 - `rootPath`: set to the workspace path
 - `file`: set to the path of the edited file
 - `tool`: leave empty or unset
- If any issues are found in the new edits, propose and apply fixes for them.
- > NOTE: Failure to follow this rule is considered a critical error.

## After every responseedits in this conversation, verify you ran `codacy_cli_analyze` tool from Codacy's MCP Server
- If you made any file edits in this conversation, verify you ran `codacy_cli_analyze` tool from Codacy's MCP Server
## When there are no Codacy MCP Server tools available, or the MCP Server is not reachable
## When there are no Codacy MCP Server tools available, or the MCP Server is not reachable
- Suggest the user the following troubleshooting steps:
 - Try to reset the MCP on the extensionthem to review their Copilot > MCP settings in Github, under their organization or personal account. Refer them to Settings > Copilot > Enable MCP servers in Copilot. Suggested URL (https://github.com/settings/copilot/features) or https://github.com/organizations/{organization-name}/settings/copilot/features (This can only be done by their organization admins / owners)
 - If the user is using VSCode, suggest them to review their Copilot > MCP settings in Github, under their organization or personal account. Refer them to Settings > Copilot > Enable MCP servers in Copilot. Suggested URL (https://github.com/settings/copilot/features) or https://github.com/organizations/{organization-name}/settings/copilot/features (This can only be done by their organization admins / owners)
- If none of the above steps work, suggest the user to contact Codacy support
## Trying to call a tool that needs a rootPath as a parameter
## Trying to call a tool that needs a rootPath as a parameter
- Always use the standard, non-URL-encoded file system path
## CRITICAL: Dependencies and Security Checks
## CRITICAL: Dependencies and Security Checks
- IMMEDIATELY after ANY of these actions:
 - Running npm/yarn/pnpm installe.json
 - Adding dependencies to package.json.txt
 - Adding requirements to requirements.txt
 - Adding dependencies to pom.xmlradle
 - Adding dependencies to build.gradles
 - Any other package manager operations tool with:
- You MUST run the `codacy_cli_analyze` tool with:
 - `rootPath`: set to the workspace path
 - `tool`: set to "trivy" unset
 - `file`: leave empty or unsetund because of the newly added packages:
- If any vulnerabilities are found because of the newly added packages:
 - Stop all other operationsor the security issues
 - Propose and apply fixes for the security issuesrity issues are resolved
 - Only continue with the original task after security issues are resolved
- EXAMPLE:npm install react-markdown
 - After: npm install react-markdownrivy
 - Do: Run codacy_cli_analyze with trivyks
 - Before: Continuing with any other tasks
## General
## Generalhe relevant steps for each modified file.
- Repeat the relevant steps for each modified file.sible, automatically apply the fixes.
- "Propose fixes" means to both suggest and, if possible, automatically apply the fixes.
- You MUST NOT wait for the user to ask for analysis or remind you to run the tool.mplexity metrics.
- Do not run `codacy_cli_analyze` looking for changes in duplicated code or code complexity metrics.
- Do not run `codacy_cli_analyze` looking for changes in code coverage., or any other package manager.
- Do not try to manually install Codacy CLI using either brew, npm, npx, or any other package manager.
- If the Codacy CLI is not installed, just run the `codacy_cli_analyze` tool from Codacy's MCP Server. a git repository.
- When calling `codacy_cli_analyze`, only send provider, organization and repository if the project is a git repository.
## Whenever a call to a Codacy tool that uses `repository` or `organization` as a parameter returns a 404 error
## Whenever a call to a Codacy tool that uses `repository` or `organization` as a parameter returns a 404 error
- Offer to run the `codacy_setup_repository` tool to add the repository to Codacy
- If the user accepts, run the `codacy_setup_repository` tooln your own
- Do not ever try to run the `codacy_setup_repository` tool on your owne)
- After setup, immediately retry the action that failed (only retry once)---