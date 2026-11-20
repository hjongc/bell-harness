# notes-design: tagging for notes

Status: agreed

## Decisions
- D1: Notes stay plain text files, one per note -- why: users edit them with any editor -- by: user -- paths: README.md
- D2: A note may carry tags on a first line starting with `tags:` -- why: tags need no extra index file -- by: user

## Design
`notes tag <name>` lists notes whose first line has that tag. Tags are lowercase words separated by commas.
