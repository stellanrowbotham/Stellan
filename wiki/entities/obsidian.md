---
type: entity
kind: tool
title: Obsidian
aliases: ["Obsidian.md"]
tags: [tool, pkm, markdown]
created: 2026-10-01
updated: 2026-10-02
sources: [src-karpathy-llm-wiki, src-qmd-readme]
---

# Obsidian
Markdown note-taking app used as the browsing front end ("the IDE") for an [[llm-wiki]].

## Summary
In the LLM Wiki workflow, the agent writes the files and the human reads them in Obsidian. The human follows links, checks the graph view, and reads updated pages as they change ([[src-karpathy-llm-wiki]]). This wiki uses `[[wikilinks]]` and YAML frontmatter so that it opens directly as an Obsidian vault.

## Key facts
- **Graph view** is the best way to see the shape of the wiki: hubs, clusters, and orphans. ([[src-karpathy-llm-wiki]])
- **Obsidian Web Clipper** is a browser extension that turns web articles into markdown, a fast way to get sources into `raw/`. ([[src-karpathy-llm-wiki]])
- **Attachment download:** set Settings → Files and links → Attachment folder path to `raw/assets/`, then bind "Download attachments for current file" to a hotkey (e.g. Ctrl+Shift+D). ([[src-karpathy-llm-wiki]])
- **Marp plugin:** markdown slide decks generated from wiki content. ([[src-karpathy-llm-wiki]])
- **Dataview plugin:** queries over page frontmatter, such as tags, dates, and source counts. ([[src-karpathy-llm-wiki]])

## Connections
- [[llm-wiki]]: the pattern it serves
- [[andrej-karpathy]]: uses it this way
- [[qmd]]: complementary. Obsidian is for humans browsing; qmd is for agents searching. The qmd README never mentions Obsidian. Its clickable result links target code editors such as VS Code, Cursor, Zed, and Sublime ([[src-qmd-readme]]).
