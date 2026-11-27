# Agent handoff template

## Assignment

- Agent and task/phase
- Authorized feature branch, PR base and exact common base SHA
- Writable files/directories and expected deliverables
- Master Specification sections, requirements, ADRs and accepted change requests
- Supported versions and fixture links
- Review owner and acceptance checks

## Manual Skill handoff

Provide these repository-relative paths to the agent and ask the agent to report which files were actually read. Include `AGENTS.md` and `MASTER_TZ.md` from the same commit.

- `.agents/skills/requirements-engineer/SKILL.md`
- `.agents/skills/software-architect/SKILL.md`
- `.agents/skills/data-architecture-engineer/SKILL.md`
- `.agents/skills/qa-test-engineer/SKILL.md`
- `.agents/skills/python-desktop-developer/SKILL.md`
- `.agents/skills/code-reviewer/SKILL.md`
- `.agents/skills/gis-geospatial-engineer/SKILL.md`
- `.agents/skills/scientific-computing-engineer/SKILL.md`
- `.agents/skills/geomorphology-structural-geology-expert/SKILL.md`
- `.agents/skills/ui-ux-designer/SKILL.md`
- `.agents/skills/release-engineer/SKILL.md`

## Return for integration

- PR link, head SHA and exact base SHA
- Implemented behavior and every changed file
- Test commands, environment, actual results, CI evidence and unverified checks
- Dependency requests with license, platform, size and packaging impact
- Contract or requirements conflicts, version impact and review status
- Remaining work, risks and handoff to affected owners

[Ownership](WORKSTREAM_OWNERSHIP.md) · [Contract change process](CONTRACT_CHANGE_PROCESS.md)
