# 🧠 Terminal Child-Proof Command Guide
## Plain-English Shortcuts + Real Command Mapping

This file is the single source of truth for how you operate this project
without relying on memory.

Everything here provides **child-level alternatives** that map directly to
real Bash, Python, cat, and Git commands.

Nothing here replaces expert workflows.
Everything here prevents mistakes under pressure.

---

## 🚀 FIRST THING AFTER OPENING TERMINAL

Child-proof command:
start

What this equals (manual steps):
cd /Users/davemendoza/Desktop/Research_First_Sourcer_Automation
pwd
python3 tracks/scenario_runner.py --inventory

Purpose:
- confirms you are in the correct directory
- prints the working path
- confirms what files already exist

---

## 📍 WHERE AM I RIGHT NOW?

Child-proof options:
where  
here  
location  
whereami  
where-am-i  

Real command:
pwd

---

## 📂 GO TO PROJECT ROOT

Child-proof options:
root  
project  
ai-root  
go-root  

Real command:
cd /Users/davemendoza/Desktop/Research_First_Sourcer_Automation

---

## 🔎 INVENTORY / CONFIRM FILES (ALWAYS CHECK FIRST)

Child-proof options:
inventory  
check  
confirm  
confirm files  
verify  
status  
look  
files  
what-exists  
what do we have  

Real command:
python3 tracks/scenario_runner.py --inventory

Purpose:
- confirms which files exist
- prevents recreating or searching for files unnecessarily

---

## ▶️ RUN THE SYSTEM

Child-proof option:
run  

Optional one-word intent:
run frontier  
run gpu  
run infra  

Real command:
python3 tracks/scenario_runner.py --scenario <scenario_name>

If the intent is wrong or misspelled, the system safely falls back.

---

## ❓ DID IT WORK?

Child-proof options:
confirm  
did-it-work  
did it work  
worked  
ok  

Real command:
ls -lt outputs/scenarios | head

Purpose:
- confirm outputs exist
- avoid unnecessary reruns

---

## 🔁 DO THE SAME THING AGAIN

Child-proof options:
again  
rerun  
same thing  

Real behavior:
re-run last scenario safely

---

## 📉 MORE OR LESS OUTPUT

Child-proof options:
run more  
big run  
run less  
small run  

Real behavior:
mapped to scenario presets (volume / safety)

---

## 📝 CREATE A FILE SAFELY (NO NANO)

Child-proof option:
create-file path/to/file.py  

Real command:
cat > path/to/file.py <<EOF

Important rule:
If text scrolls by → it executed  
If you want text saved → you must use cat > filename

---

## 📁 CREATE A DIRECTORY (THE “MP” YOU REMEMBERED)

Child-proof idea:
“Make a folder if it doesn’t exist”

Real command:
mkdir -p path/to/folder

Explanation:
- mkdir = make directory
- -p = “don’t error if it already exists, create parents if needed”

This is likely the “mp” command you remembered from GPT suggestions.

---

## 💾 SAVE WORK TO GITHUB

Child-proof options:
done  
save  
save-work  

Real commands:
git status  
git add -A  
git commit  
git push  

Purpose:
- safely finish work
- ensure nothing is forgotten

---

## 🧨 UNDO / OOPS / I MESSED UP

Child-proof options:
undo  
oops  

What this means (in order):
1. Stop current command (Ctrl + C)
2. Clear the screen
3. Show if anything changed
4. Return to project root
5. Print pwd for confirmation

Real commands:
Ctrl + C  
clear  
git status  
cd /Users/davemendoza/Desktop/Research_First_Sourcer_Automation  
pwd  

Important:
Undo does NOT erase history.
Undo prepares you to paste the correct command next.

---

## 🧼 TERMINAL LOOKS BROKEN

Child-proof options:
clear  
Cmd + K  

Real behavior:
clears the screen only
does NOT affect files or commands

---

## 🧠 PYTHON VERSION CHECK (VERY IMPORTANT)

Child-proof intent:
“Make sure I’m using Python 3”

Real commands:
python3 --version
which python3

Rule:
Always use python3, never plain python, for this project.

---

## ⚠️ ABOUT `sed` (YOU DON’T NEED IT HERE)

What sed is:
A stream editor used to modify text inline.

Why it appears:
GPT or shell examples sometimes suggest it for quick edits.

Why you should avoid it:
- it can silently change files
- it is hard to read
- it violates the “full file replacement only” rule

Your rule instead:
Always regenerate full files using cat > filename.

---

## 🆘 HELP WITHOUT DOCS

Child-proof options:
help  
help me  
what do I do  

Behavior:
prints the short safe command list only

---

## 🧠 EMERGENCY MEMORY RULE

If you forget everything:

start  
inventory  
run  
confirm  
done  

That is always enough.

---

## FINAL REASSURANCE

You are not bad at Terminal.

You built a system that does not depend on memory.

This file exists so Future-You never loses time again.
