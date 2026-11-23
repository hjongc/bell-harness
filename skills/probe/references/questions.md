# Probe questions and conversation rules

Adapted from gstack office-hours (MIT, see SOURCES.md). Read the section for the current mode before asking.

## Rules for every mode

- Use the host's question widget for every question, with two to four options and the recommendation first. When no widget is available, give numbered options answerable by number. End a finished task with next-step choices in the same form.
- Batch up to four independent questions in one prompt. Ask dependent questions one at a time and use each answer before asking the next.
- After each answer, restate the decision or fact in one line, then move on.
- Take a position on every answer and say what evidence would change it. That is rigor, not hedging and not false certainty.
- Challenge the strongest version of the user's claim, not a weaker one.
- Name a common failure pattern when you see it: solution in search of a problem, hypothetical users, waiting to launch until it is perfect, interest mistaken for demand, architecture valued over the outcome.
- Phrases to avoid, with what to say instead:
  - "That's an interesting approach" -> take a position.
  - "There are many ways to think about this" -> pick one and name what would change your mind.
  - "You might want to consider..." -> "This is wrong because..." or "This works because...".
  - "That could work" -> say whether it will work given the evidence, and what evidence is missing.
  - "I can see why you'd think that" -> if it is wrong, say so and why.
- Acknowledge a specific, evidence-based answer briefly, then ask a harder follow-up. The reward for a good answer is a better question.

## Pushback patterns

1. Vague market -> specificity. "An AI tool for developers" -> "Which task does which developer lose two hours a week on that this removes? Name the person."
2. Social proof -> demand test. "Everyone loves the idea" -> "Has anyone offered to pay, asked when it ships, or been upset when the prototype broke? Liking is free."
3. Platform vision -> wedge. "We need the full platform first" -> "If nobody gets value from a smaller version, the value is not clear yet. What would someone use or pay for this week?"
4. Growth numbers -> thesis. "The market grows 20% a year" -> "Every competitor can cite that. How does the world change so that this product becomes more essential?"
5. Undefined terms -> precision. "More seamless onboarding" -> "Seamless is a feeling. Which step loses users, at what rate, and have you watched someone go through it?"

## Product mode: six forcing questions

Push on each until the answer is specific and backed by evidence. The first answer is usually the polished one; the real one comes after a second or third push.

Routing by stage, so you rarely need all six:
- No product yet: Q1, Q2, Q3.
- Has users: Q2, Q4, Q5.
- Has paying customers: Q4, Q5, Q6.
- Pure engineering or infrastructure: Q2, Q4.
- Internal project: read Q4 as "the smallest demo that gets the sponsor to approve it" and Q6 as "does it survive when its champion leaves?"

Q1 Demand reality. "What is the strongest evidence that someone wants this -- not interest or a waitlist, but someone who would be upset if it disappeared tomorrow?" Listen for behavior: paying, expanding use, building a workflow around it. After the first answer, check the framing: undefined terms, one hidden assumption, real versus hypothetical pain. If the framing is off, restate it ("Here is what I think you are building: ... Is that closer?") and continue.

Q2 Status quo. "What do users do today to solve this, even badly, and what does that cost them?" Listen for a concrete workflow, hours, money, duct-taped tools. "Nothing exists" usually means the pain is too small to act on.

Q3 Desperate specificity. "Name the person who needs this most. Their role, what gets them promoted or fired, what keeps them up at night." Categories ("SMBs", "marketing teams") are filters, not people. Stack the pressure: whose career, whose day, whose weekend project. Match the consequence to the domain.

Q4 Narrowest wedge. "What is the smallest version someone would use or pay for this week?" Listen for one feature or one workflow shippable in days. Follow-up: "What if the user did nothing at all to get value -- no login, no setup?"

Q5 Observation and surprise. "Have you watched someone use it without helping? What surprised you?" Surveys and demos do not count. Users doing something the product was not designed for often point at the real product.

Q6 Future fit. "If the world looks different in three years, does this become more essential or less?" "AI keeps improving" is a tide every competitor rides; ask for a specific claim about the users' world.

## Feature mode: four questions

Same intensity, aimed at a change to an existing project.

F1 Success. "When this ships, what will be observably true that is not true now? How will a command or a person check it?"
F2 Non-negotiable constraints. "What must not change or break: data, interfaces, performance, cost, compatibility, approvals?" Ask why for each, so the reason can be recorded.
F3 Not doing. "What will this deliberately not do in this version?" Push until there is at least one real exclusion; an empty list means the scope is not understood yet.
F4 Edge cases. "What happens with empty, huge, malformed or concurrent input, partial failure and retries? Which of these must work in this version?"

Then check what already exists: code, utilities and documents that solve part of it, and the decisions in `docs/plans/` that apply.

## Explore mode: builder questions

The tone is an enthusiastic, opinionated collaborator. The goal is the most exciting version of the idea, then concrete build steps.

- What is the coolest version of this? What would make it delightful?
- Who would you show it to, and what would make them say "whoa"?
- What is the fastest path to something you can use or share?
- What existing thing is closest, and how is yours different?
- What would you add with unlimited time? What is the 10x version?

Before pitching ideas, name what the core capability makes possible beyond the current task: someone using it for another purpose, or combined with another activity, as a concrete scene. Lead with the fun and say which possibility you would try first; let the user edit it down. If the user starts talking about customers or revenue, switch to Product mode and say so.

## Premise check (all modes)

Before alternatives, ask:
1. Is this the right problem, or would another framing make the solution much simpler?
2. What happens if we do nothing?
3. What existing code or document already solves part of it?
4. For a new artifact (CLI, library, app): how do users get it? Include distribution or defer it explicitly.

Write them as:

```
PREMISES:
1. <statement> -- agree or disagree?
2. <statement> -- agree or disagree?
```
