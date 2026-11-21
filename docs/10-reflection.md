# Task 10 — AI reflection

I used **Claude (Opus 5.5) in the claude.ai chat app** as my main assistant. It received the assignment
PDF, my GitHub repository and screenshots of my terminal. Because it cannot push to GitHub, it worked in
its own sandbox copy and sent every change as a patch file that I applied myself. It did not load
AGENTS.md automatically; the rules were in the conversation. For the read-only risk review I used a
**separate, fresh Claude chat** that only saw a ZIP of the repository.

The most useful suggestion was COR-4: the independent reviewer predicted that exporting on Windows
would write `\r\r\n` and crash on non-Latin letters. On my laptop the Kazakh letter "ә" really
crashed with `UnicodeEncodeError` and left a 0-byte file. The same reviewer also noticed that our
Task 1 evidence wrongly called the environment "fresh". A weak suggestion was AGT-2's claim that
tests could be deleted while still meeting AC5 — the criterion text forbids deleting tests, so I
marked it unsupported. The main assistant also made small mistakes (wrong diff sizes, a cut-off
check, lint warnings in its own tests) that only re-running the commands revealed.

I personally re-ran the tests on Windows after every stage (6, 16, then 27 passed), reproduced COR-4,
read the Task 7 diff on a review branch before merging it, and ran the tests on the tagged commit.
Tests changed decisions: the R5 test passed on Linux even before the fix, which showed that only my
Windows run was real evidence.

AGENTS.md helped: the assistant used the correct test command, worked on a branch and never ran
`reset`. But its rules are only text. Next I would add CI, pin dependencies, fix R4 and R6, and
test the instructions with an agent that loads AGENTS.md automatically.
