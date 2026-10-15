# Clinical foundation

[Polski](README.pl.md)

> **Status: pending clinical review.** No speech-language therapist (logopeda or neurologopeda) has reviewed this document, the exercise design, or any exercise item yet (backlog H1). Until someone qualified signs them off, treat everything here as a plan, not as clinical guidance.

This app is for practice between sessions with a speech-language therapist. It supports therapy and does not replace it, and it makes no medical or efficacy claims (principle C6 in [`loop/PROMPT.md`](../../loop/PROMPT.md)).

## What the evidence says, in short

- **Speech and language therapy helps.** A Cochrane review of 57 trials (Brady et al., 2016) found that speech and language therapy benefits functional communication compared with no therapy. The benefits of higher-intensity therapy were confounded by more people dropping out.
- **Computer practice helps with the words practised, not with conversation.** In the Big CACTUS trial (Palmer et al., 2019; 278 people with long-term aphasia after stroke), six months of self-managed computerised word-finding practice at home, with words chosen for each person, improved finding those words. It did not improve conversation or quality of life.

So this app must:

- let people practise **their own words**: words and photos chosen with a patient, carer or therapist (principle C2; not built yet, backlog P2-2);
- never claim that practising here improves conversation.

## The exercise types

Each type the app knows, what it does today, and what it should be based on.

### Word naming (`word_naming`)

- **Today:** the app shows a short description, for example "A small pet that purrs and says meow", and the person types the word. The items are in English only for now. There are no pictures yet (H2), so the description stands in for one. The prompt never contains the answer (C4, checked by `backend/tests/test_content.py`).
- **Basis:** naming practice for word-finding difficulty (anomia), with help given in steps:
  - **Cueing hierarchy:** when a word doesn't come, give cues one at a time, from least to most help (Linebaugh, Shisler & Lehner, 2005). Planned as backlog P2-3: meaning cue, then first sound or letter, then the whole word to repeat.
  - **Semantic Feature Analysis (SFA):** talking through the features of the item, such as its group, use, place and properties, to help retrieve its name (Boyle & Coelho, 1995: a single-case study).
  - **Phonological Components Analysis (PCA):** the same idea with the word's sounds, for example its first sound and how many syllables it has (Leonard, Rochon & Laird, 2008).
- **Gaps:** there are no cues yet, and no pictures. The items are placeholders.

### Sentence completion (`sentence_completion`)

- **Today:** a sentence with a gap ("The sky is ___") and four words to choose from.
- **Basis:** none of the established approaches in this document is a fill-the-gap task with choices. A closer model for sentence-level work is **Verb Network Strengthening Treatment (VNeST)**, which practises retrieving content words in sentences around a verb: who does it, and to what (Edmonds, Nadeau & Kiran, 2009). Whether to redesign this type along those lines is a question for clinical review.
- **Gaps:** the basis of the current task is [citation needed].

### Pronunciation (`pronunciation`)

- **Today:** a word or phrase to say ("Say: Hello"), which the person records. The browser's speech recognition judges the answer, if the person agrees to it.
- **Basis:** repetition of words and phrases is a common therapy task [citation needed].
- **Gaps:** speech recognition is unreliable for aphasic speech, so it must never be the only judge; the person should be able to rate themselves, or a therapist should review the recording (principle C5; backlog P2-7).

### Image recognition (`image_recognition`)

- **Today:** not offered. There are no pictures (H2), so the type has no exercises.
- **Basis:** a planned word–picture matching task (auditory or reading comprehension) [citation needed].

### Planned: script training

Practising short, personally relevant conversational scripts until they come easily (Youmans, Holland, Muñoz & Bourgeois, 2005: two people with non-fluent aphasia). In that study, both participants mastered their scripts. How far this carries over to other speech is less clear [citation needed]. Not in the app yet.

## The content model

Backlog P2-2 replaces the exercise items in the code with versioned content files. Each item should record:

- its language;
- its type and target word or phrase;
- the prompt;
- the cues, in order;
- any picture or recording, with its source and licence (`frontend/assets/CREDITS.md`);
- the features that make it easier or harder;
- its review status: "pending clinical review" until a named reviewer approves it, with the date.

## How content gets reviewed

1. New or changed items are marked "pending clinical review" (principle C7).
2. A qualified speech-language therapist reviews them in both languages (backlog H1). Polish items must be written in natural Polish, not translated word for word.
3. Only then are they marked approved, with the reviewer and the date. The automated loop that maintains this project never marks anything approved.

## References

Checked on 2026-10-15 against publisher and repository records. The full texts weren't read; what this document says about each study is limited to what those records state. Authors' initials are given only where the records showed them.

- Boyle & Coelho (1995). Application of semantic feature analysis as a treatment for aphasic dysnomia. *American Journal of Speech-Language Pathology, 4*(4), 94–98. https://doi.org/10.1044/1058-0360.0404.94
- Brady, M. C., Kelly, H., Godwin, J., Enderby, P., & Campbell, P. (2016). Speech and language therapy for aphasia following stroke. *Cochrane Database of Systematic Reviews*, 2016(6), CD000425. https://doi.org/10.1002/14651858.CD000425.pub4
- Edmonds, Nadeau & Kiran (2009). Effect of Verb Network Strengthening Treatment (VNeST) on lexical retrieval of content words in sentences in persons with aphasia. *Aphasiology, 23*(3), 402–424. https://doi.org/10.1080/02687030802291339
- Leonard, C., Rochon, E., & Laird, L. (2008). Treating naming impairments in aphasia: Findings from a phonological components analysis treatment. *Aphasiology, 22*(9), 923–947. (DOI not checked.)
- Linebaugh, C. W., Shisler, R., & Lehner, L. (2005). Cueing hierarchies and word retrieval: A therapy program. *Aphasiology, 19*(1), 77–92. (DOI not checked.)
- Palmer, R., et al. (2019). Self-managed, computerised speech and language therapy for patients with chronic aphasia post-stroke compared with usual care or attention control (Big CACTUS): a multicentre, single-blinded, randomised controlled trial. *The Lancet Neurology, 18*(9), 821–833. https://doi.org/10.1016/S1474-4422(19)30192-9
- Youmans, Holland, Muñoz & Bourgeois (2005). Script training and automaticity in two individuals with aphasia. *Aphasiology, 19*(3–5), 435–450. https://doi.org/10.1080/02687030444000877
