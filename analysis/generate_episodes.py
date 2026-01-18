#!/usr/bin/env python3
"""
Generate Obsidian episode notes from analysis
"""

episodes = {
    336: {
        "guest": "Ben Shapiro",
        "title": "Politics, Extremism, Free Speech & Hate",
        "role": "Political commentator, lawyer",
        "domains": ["politics", "philosophy", "media"],
        "topics": ["free-speech", "extremism", "media-bias", "evil", "tribalism"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["politics/right", "domain/politics", "theme/truth"],
        "summary": "Conservative commentator Ben Shapiro discusses the nature of evil, political tribalism, free speech vs censorship, and media bias. Key focus on Hitler, antisemitism, and democratic fragility.",
        "quotes": [
            "Jumping from individual to group is the core mechanism of bigotry",
        ]
    },
    389: {
        "guest": "Benjamin Netanyahu",
        "title": "Israel, Palestine, Power, Corruption & Peace",
        "role": "Prime Minister of Israel",
        "domains": ["geopolitics", "governance", "middle-east"],
        "topics": ["israel-palestine", "judicial-reform", "iran-threat", "democracy"],
        "clusters": ["6-Power-Governance", "1-Existential-Risk"],
        "tags": ["politics/right", "region/israel-palestine", "guest-type/politician"],
        "summary": "Israeli PM Netanyahu on existential threats, judicial reform, Abraham Accords, and Israeli democracy.",
        "quotes": [
            "If somebody threatens to annihilate us, take them seriously and act to prevent it early on",
        ]
    },
    393: {
        "guest": "Andrew Huberman",
        "title": "Relationships, Drama, Betrayal, Sex & Love",
        "role": "Neuroscientist, Stanford",
        "domains": ["neuroscience", "psychology", "relationships"],
        "topics": ["relationships", "exercise", "jungian-shadow", "betrayal"],
        "clusters": ["7-Consciousness-Meaning", "5-Technology"],
        "tags": ["domain/neuroscience", "guest-type/scientist"],
        "summary": "Neuroscientist Andrew Huberman on relationship dynamics, exercise physiology, Jungian shadow integration, and human connection.",
        "quotes": []
    },
    410: {
        "guest": "Ben Shapiro & Destiny",
        "title": "Political Debate - Politics, Jan 6, Israel, Ukraine & Wokeism",
        "role": "Political commentators (Conservative & Liberal)",
        "domains": ["politics", "philosophy"],
        "topics": ["liberalism-vs-conservatism", "trump-vs-biden", "israel-palestine", "ukraine"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["politics/debate", "region/ukraine-russia", "region/israel-palestine"],
        "summary": "First major debate format: Ben Shapiro (conservative) vs Destiny (liberal) on core political differences.",
        "quotes": []
    },
    413: {
        "guest": "Bill Ackman",
        "title": "Investing, Financial Battles, Harvard, DEI & Free Speech",
        "role": "Activist investor, hedge fund manager",
        "domains": ["finance", "investing", "institutional-reform"],
        "topics": ["value-investing", "harvard", "dei", "free-speech"],
        "clusters": ["6-Power-Governance", "8-Methodology"],
        "tags": ["domain/finance", "guest-type/entrepreneur"],
        "summary": "Activist investor Bill Ackman on value investing, Harvard presidency controversy, DEI debates, and institutional accountability.",
        "quotes": [
            "Price is what you pay, value is what you get",
        ]
    },
    420: {
        "guest": "Annie Jacobsen",
        "title": "Nuclear War & National Security",
        "role": "Investigative journalist",
        "domains": ["nuclear-weapons", "national-security"],
        "topics": ["nuclear-war", "mad", "launch-on-warning", "deterrence"],
        "clusters": ["1-Existential-Risk", "6-Power-Governance"],
        "tags": ["theme/existential-risk", "domain/national-security"],
        "summary": "Investigative journalist Annie Jacobsen on nuclear war scenarios, 6-minute decision windows, and MAD doctrine.",
        "quotes": []
    },
    421: {
        "guest": "Dana White",
        "title": "UFC, Fighting, Khabib, Conor, Tyson & Ali",
        "role": "UFC President",
        "domains": ["combat-sports", "business"],
        "topics": ["ufc", "mma", "business-building"],
        "clusters": ["6-Power-Governance", "7-Consciousness-Meaning"],
        "tags": ["domain/sports", "guest-type/entrepreneur"],
        "summary": "UFC President Dana White on building combat sports empire, greatest fighters, and the business of MMA.",
        "quotes": []
    },
    424: {
        "guest": "Bassem Youssef",
        "title": "Israel-Palestine, Gaza, Hamas, Middle East & Satire",
        "role": "Comedian, 'Jon Stewart of Middle East'",
        "domains": ["political-satire", "middle-east"],
        "topics": ["israel-palestine", "october-7", "two-state-solution", "satire"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["region/israel-palestine", "domain/media", "guest-type/commentator"],
        "summary": "Egyptian satirist Bassem Youssef on Israel-Palestine conflict, October 7, media narratives, and comedy as resistance.",
        "quotes": []
    },
    425: {
        "guest": "Andrew Callaghan",
        "title": "Channel 5, Gonzo Journalism, QAnon & Politics",
        "role": "Gonzo journalist, Channel 5 host",
        "domains": ["journalism", "subcultures"],
        "topics": ["gonzo-journalism", "january-6", "qanon", "fringe-movements"],
        "clusters": ["4-Truth-Knowledge", "6-Power-Governance"],
        "tags": ["domain/media", "guest-type/commentator"],
        "summary": "Gonzo journalist Andrew Callaghan on documenting American fringe movements, January 6, and giving voice to margins.",
        "quotes": []
    },
    426: {
        "guest": "Edward Gibson",
        "title": "Human Language, Psycholinguistics, Syntax & LLMs",
        "role": "MIT Psycholinguistics Professor",
        "domains": ["linguistics", "cognitive-science"],
        "topics": ["language-universals", "chomsky-critique", "llms", "sapir-whorf"],
        "clusters": ["2-Intelligence-Foundations", "4-Truth-Knowledge"],
        "tags": ["domain/linguistics", "guest-type/scientist"],
        "summary": "MIT linguist Edward Gibson on language universals, Chomsky critique, and what LLMs reveal about syntax.",
        "quotes": []
    },
    430: {
        "guest": "Charan Ranganath",
        "title": "Human Memory, Imagination, Deja Vu & False Memories",
        "role": "UC Davis psychologist & neuroscientist",
        "domains": ["memory-science", "neuroscience"],
        "topics": ["false-memories", "forgetting", "memory-hacks", "time-perception"],
        "clusters": ["2-Intelligence-Foundations", "4-Truth-Knowledge"],
        "tags": ["domain/neuroscience", "guest-type/scientist"],
        "summary": "Memory researcher Charan Ranganath on false memories, why we forget, memory hacks, and the unreliability of recollection.",
        "quotes": []
    },
    434: {
        "guest": "Aravind Srinivas",
        "title": "Perplexity CEO on Future of AI, Search & the Internet",
        "role": "Perplexity CEO",
        "domains": ["ai", "search", "information-retrieval"],
        "topics": ["rag", "perplexity", "search-innovation", "citations"],
        "clusters": ["5-Technology", "2-Intelligence-Foundations"],
        "tags": ["domain/ai", "ai/capabilities", "guest-type/entrepreneur"],
        "summary": "Perplexity CEO Aravind Srinivas on RAG architecture, citation-based answers, and the future of search.",
        "quotes": []
    },
    435: {
        "guest": "Andrew Huberman",
        "title": "Focus, Controversy, Politics & Relationships",
        "role": "Neuroscientist, Stanford",
        "domains": ["neuroscience", "productivity"],
        "topics": ["focus", "supplements", "psychedelics", "controversy"],
        "clusters": ["5-Technology", "7-Consciousness-Meaning"],
        "tags": ["domain/neuroscience", "guest-type/scientist"],
        "summary": "Andrew Huberman's return: deep focus protocols, cannabis controversy, supplements, and navigating public criticism.",
        "quotes": []
    },
    439: {
        "guest": "Craig Jones",
        "title": "Jiu Jitsu, $2 Million Prize, CJI, ADCC & Ukraine",
        "role": "Elite Brazilian Jiu-Jitsu competitor",
        "domains": ["combat-sports", "jiu-jitsu"],
        "topics": ["cji-tournament", "adcc-reform", "sports-business"],
        "clusters": ["6-Power-Governance", "7-Consciousness-Meaning"],
        "tags": ["domain/sports"],
        "summary": "Elite grappler Craig Jones on challenging ADCC, $2M prize pool, and reforming jiu-jitsu institutions.",
        "quotes": []
    },
    441: {
        "guest": "Cenk Uygur",
        "title": "Trump vs Harris, Progressive Politics & Capitalism",
        "role": "The Young Turks founder, progressive commentator",
        "domains": ["progressive-politics", "media"],
        "topics": ["progressivism", "corruption", "money-in-politics", "communism-critique"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["politics/left", "domain/politics", "guest-type/commentator"],
        "summary": "Progressive commentator Cenk Uygur on political corruption, money in politics, and fixing democratic systems.",
        "quotes": [
            "Communism makes no sense at all, totally opposed to human nature",
        ]
    },
    442: {
        "guest": "Donald Trump",
        "title": "Presidential Interview - Politics, Ukraine, China & Division",
        "role": "45th/47th President of the United States",
        "domains": ["politics", "governance"],
        "topics": ["presidential-power", "ukraine", "2020-election", "media-warfare"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["politics/right", "guest-type/politician"],
        "summary": "Rare long-form interview with Donald Trump on Ukraine, China, 2020 election, and media narratives.",
        "quotes": []
    },
    446: {
        "guest": "Ed Barnhart",
        "title": "Ancient Civilizations - Maya, Aztec, Inca & Lost Cities",
        "role": "Archaeologist",
        "domains": ["archaeology", "ancient-civilizations"],
        "topics": ["maya", "aztec", "inca", "lost-civilizations", "psychedelics"],
        "clusters": ["3-Ancient-Civilizations", "7-Consciousness-Meaning"],
        "tags": ["domain/archaeology", "guest-type/scientist"],
        "summary": "Archaeologist Ed Barnhart on pre-Columbian Americas, lost civilizations, psychedelics, and religious origins.",
        "quotes": []
    },
    447: {
        "guest": "Cursor Team",
        "title": "Future of Programming with AI",
        "role": "Cursor AI coding tool founders",
        "domains": ["ai", "programming", "software-development"],
        "topics": ["ai-coding", "cursor-tab", "rag-for-code", "agents"],
        "clusters": ["5-Technology", "2-Intelligence-Foundations"],
        "tags": ["domain/ai", "ai/programming", "guest-type/entrepreneur"],
        "summary": "Cursor team on AI-assisted programming, code completion, RAG for codebases, and the future of development.",
        "quotes": []
    },
    450: {
        "guest": "Bernie Sanders",
        "title": "Progressive Politics, Healthcare & Corruption",
        "role": "U.S. Senator, two-time presidential candidate",
        "domains": ["progressive-politics", "economic-justice"],
        "topics": ["medicare-for-all", "corruption", "capitalism-critique", "hope"],
        "clusters": ["6-Power-Governance", "7-Consciousness-Meaning"],
        "tags": ["politics/left", "guest-type/politician"],
        "summary": "Senator Bernie Sanders on healthcare, political corruption, capitalism critique, and fighting for economic justice.",
        "quotes": []
    },
    452: {
        "guest": "Dario Amodei",
        "title": "Anthropic CEO on AI Safety & Claude",
        "role": "CEO of Anthropic",
        "domains": ["ai", "ai-safety"],
        "topics": ["scaling-laws", "constitutional-ai", "asl-levels", "cbrn-risks"],
        "clusters": ["1-Existential-Risk", "2-Intelligence-Foundations", "5-Technology"],
        "tags": ["domain/ai", "ai/safety", "theme/existential-risk"],
        "summary": "Anthropic CEO Dario Amodei on AI safety levels, Constitutional AI, scaling laws, and machines of loving grace.",
        "quotes": [
            "AI increases the amount of power in the world. And if you concentrate that power and abuse that power, it can do immeasurable damage",
        ]
    },
    455: {
        "guest": "Adam Frank",
        "title": "Alien Civilizations & Search for Extraterrestrial Life",
        "role": "Astrophysicist, University of Rochester",
        "domains": ["astrobiology", "cosmology", "seti"],
        "topics": ["fermi-paradox", "great-filter", "exoplanets", "drake-equation"],
        "clusters": ["1-Existential-Risk", "2-Intelligence-Foundations"],
        "tags": ["domain/physics", "domain/astrobiology", "theme/existential-risk"],
        "summary": "Astrophysicist Adam Frank on the Fermi Paradox, Great Filter, exoplanets, and search for alien civilizations.",
        "quotes": []
    },
    459: {
        "guest": "Dylan Patel & Nathan Lambert",
        "title": "DeepSeek - AI, China, Hardware & Geopolitics",
        "role": "SemiAnalysis & AI researcher",
        "domains": ["ai", "semiconductors", "geopolitics"],
        "topics": ["deepseek", "china-ai", "export-controls", "agi-timeline"],
        "clusters": ["5-Technology", "6-Power-Governance", "1-Existential-Risk"],
        "tags": ["domain/ai", "region/china-us", "ai/geopolitics"],
        "summary": "Analysis of DeepSeek's breakthrough: $6M training, China's AI capabilities, export controls, and US-China tech race.",
        "quotes": []
    },
    463: {
        "guest": "Douglas Murray",
        "title": "Putin, Zelenskyy, Trump, Israel, Netanyahu & Gaza",
        "role": "Author, political commentator",
        "domains": ["geopolitics", "war"],
        "topics": ["ukraine", "israel-palestine", "putin", "zelenskyy"],
        "clusters": ["6-Power-Governance", "1-Existential-Risk"],
        "tags": ["politics/right", "region/ukraine-russia", "region/israel-palestine"],
        "summary": "Author Douglas Murray on Ukraine war, Israel-Gaza conflict, Putin analysis, and Western civilization defense.",
        "quotes": []
    },
    464: {
        "guest": "Dave Smith",
        "title": "Israel, Ukraine, Epstein, Mossad & Conspiracies",
        "role": "Comedian, libertarian political commentator",
        "domains": ["libertarianism", "foreign-policy"],
        "topics": ["libertarianism", "israel-palestine", "ukraine", "conspiracy-theories"],
        "clusters": ["6-Power-Governance", "4-Truth-Knowledge"],
        "tags": ["politics/libertarian", "guest-type/commentator"],
        "summary": "Libertarian Dave Smith on anti-war politics, Israel-Palestine critique, Ukraine, and conspiracy skepticism.",
        "quotes": []
    },
    474: {
        "guest": "DHH (David Heinemeier Hansson)",
        "title": "Rails, AI, Programming & Productivity",
        "role": "Creator of Ruby on Rails, Basecamp co-founder",
        "domains": ["programming", "software-development"],
        "topics": ["ruby-on-rails", "programming-philosophy", "ai-skepticism"],
        "clusters": ["8-Methodology", "5-Technology"],
        "tags": ["domain/programming", "guest-type/entrepreneur"],
        "summary": "Rails creator DHH on programming philosophy, developer happiness, AI in coding, and owning your own servers.",
        "quotes": []
    },
    479: {
        "guest": "Dave Plummer",
        "title": "Programming, Autism & Old-School Microsoft",
        "role": "Former Microsoft engineer, YouTube creator",
        "domains": ["software-engineering", "microsoft-history"],
        "topics": ["task-manager", "windows", "autism", "debugging"],
        "clusters": ["8-Methodology", "5-Technology", "7-Consciousness-Meaning"],
        "tags": ["domain/programming", "guest-type/entrepreneur"],
        "summary": "Ex-Microsoft engineer Dave Plummer on creating Task Manager, Windows development, autism in tech, and debugging.",
        "quotes": []
    },
    480: {
        "guest": "Dave Hone",
        "title": "T-Rex, Dinosaurs, Extinction & Evolution",
        "role": "Paleontologist, Queen Mary University of London",
        "domains": ["paleontology", "evolution"],
        "topics": ["t-rex", "dinosaur-extinction", "evolution", "jurassic-park"],
        "clusters": ["3-Ancient-Civilizations", "4-Truth-Knowledge", "1-Existential-Risk"],
        "tags": ["domain/paleontology", "guest-type/scientist"],
        "summary": "Paleontologist Dave Hone on T-Rex, dinosaur extinction, evolution, deep time, and what Jurassic Park got wrong.",
        "quotes": []
    },
    484: {
        "guest": "Dan Houser",
        "title": "GTA, Red Dead Redemption, Rockstar & Gaming",
        "role": "Co-founder Rockstar Games, writer/producer of GTA & RDR",
        "domains": ["video-games", "creative-direction"],
        "topics": ["gta", "red-dead-redemption", "game-design", "ai-in-games"],
        "clusters": ["5-Technology", "7-Consciousness-Meaning"],
        "tags": ["domain/gaming", "guest-type/entrepreneur"],
        "summary": "Rockstar's Dan Houser on creating GTA and Red Dead Redemption, storytelling, game design, and AI's creative limits.",
        "quotes": []
    },
    485: {
        "guest": "David Kirtley",
        "title": "Nuclear Fusion, Plasma Physics & Future of Energy",
        "role": "CEO Helion Energy, nuclear engineer",
        "domains": ["nuclear-fusion", "energy"],
        "topics": ["fusion-energy", "plasma-physics", "kardashev-scale", "gpu-energy"],
        "clusters": ["5-Technology", "1-Existential-Risk"],
        "tags": ["domain/physics", "domain/energy", "guest-type/entrepreneur"],
        "summary": "Helion CEO David Kirtley on nuclear fusion breakthrough, 2028 timeline, energy for AI clusters, and Kardashev scale.",
        "quotes": []
    },
    488: {
        "guest": "Joel David Hamkins",
        "title": "Infinity, Set Theory, Paradoxes & Mathematical Multiverse",
        "role": "Mathematician, Philosopher of Mathematics",
        "domains": ["mathematics", "philosophy", "logic"],
        "topics": ["infinity", "set-theory", "godels-theorems", "p-vs-np", "paradoxes"],
        "clusters": ["2-Intelligence-Foundations", "4-Truth-Knowledge", "7-Consciousness-Meaning"],
        "tags": ["domain/mathematics", "domain/philosophy", "guest-type/scientist"],
        "summary": "Mathematician Joel David Hamkins on infinity, Gödel's incompleteness, set theory paradoxes, and limits of formal systems.",
        "quotes": [
            "The smallest uninteresting number is a super interesting property to have",
            "For any set whatsoever, the power set of that set is a strictly larger set",
        ]
    },
}

template = """---
episode: {episode}
title: "{title}"
guest: {guest}
guest_role: {role}
date: 2024
domains: {domains}
primary_topics: {topics}
clusters: {clusters}
tags: {tags}
---

# Episode {episode}: {guest} - {short_title}

## Overview

{summary}

---

## Key Topics

(Main discussion points organized by theme)

---

## Notable Quotes

{quotes_section}

---

## Connections to Other Episodes

(Links to related episodes and concepts)

---

## Cluster Mappings

{cluster_mappings}

---

## Further Exploration

**Related Episodes:**
(List related episodes)

**Related Concepts:**
(List key concepts from this episode)

---

*Back to: [[Episodes/MOC-All-Episodes|All Episodes]] | [[README|Vault Home]]*
"""

import os

vault_dir = "/sessions/awesome-wizardly-wozniak/mnt/analysis/obsidian-vault/Episodes"

for ep_num, data in episodes.items():
    # Skip if already created
    if ep_num in [488, 475]:
        continue

    filename = f"Episode-{ep_num}-{data['guest'].replace(' ', '-').replace('&', 'and')}.md"
    filepath = os.path.join(vault_dir, filename)

    quotes_section = "\n".join([f"> \"{q}\"" for q in data['quotes']]) if data['quotes'] else "(Notable quotes to be added)"

    cluster_list = "\n".join([f"- **[[{c}/MOC-{c.split('-', 1)[1]}|{c.split('-', 1)[1]}]]**" for c in data['clusters']])

    content = template.format(
        episode=ep_num,
        title=data['title'],
        guest=data['guest'],
        role=data['role'],
        domains=str(data['domains']),
        topics=str(data['topics']),
        clusters=str(data['clusters']),
        tags=str(data['tags']),
        short_title=data['title'].split(',')[0][:50],
        summary=data['summary'],
        quotes_section=quotes_section,
        cluster_mappings=cluster_list
    )

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"Created {filename}")

print(f"\nGenerated {len(episodes) - 2} episode notes!")
