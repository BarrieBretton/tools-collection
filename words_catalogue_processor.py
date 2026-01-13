import os
import sys
import json

def split_consecutive_numbers(lst):
    sorted_lst = sorted(lst)
    result = []
    sublist = []
    for i, num in enumerate(sorted_lst):
        if i == 0 or num != sorted_lst[i - 1] + 1:
            sublist = [num]
            result.append(sublist)
        else:
            sublist.append(num)
    return result

def parse_unorganised_section(unorg):
    result = {'catalogue': {}}

    unorg = '\n'.join(unorg).strip()
    has_stray_notes = not unorg.startswith('-')
    unorg = [i for i in unorg.split('- ') if i]
    unorg = [i.splitlines() for i in unorg]

    if has_stray_notes:
        result['notes'] = unorg[0]
        del unorg[0]
    
    for i in unorg:
        wm = i[0].split(':')
        meaning = None
        notes = None
        if len(wm) == 1:
            word = wm[0]
        if len(wm) == 2:
            word, meaning = i[0].split(':')
            meaning = meaning.strip()

        notes = [x.strip() for x in i[1:]]
        word = word.strip()

        result['catalogue'].update({word: [meaning, notes]})

    return result

def fread(path):
    with open(path, 'r') as fp:
        r = fp.read()
    return r

def parse(path):
    global sec, subs, sub_lines, sub_ranges, r, u, content

    content = fread(path).strip()

    # Remove extraneous/unrequired spaces between words
    r = ' '.join([i for i in content.split(' ') if i])

    # Divide/Split mass of words into paragraphs
    r = [i.strip() for i in r.split('>>') if i.strip()]

    doc = {'unorganised': None, 'sections': {}}
    u = content.strip().startswith('>>')

    for x, s in enumerate(r):
        sec = [i.strip() for i in s.splitlines()
               if (i.strip() and set(i) != {'-'})]
        sec_title = sec[0].strip().title()

        if sec_title in doc:
            raise KeyError(f"Duplicate Key: {sec_title}")
        
        if not u and x == 0:
            print(u, x)
            doc['unorganised'] = parse_unorganised_section(sec)
            continue

        doc['sections'].update({sec_title: {"unorganised": {},
                                            "subsections": {}}})

        subs = [(ind, i) for ind, i in enumerate(sec[1:]) if i.startswith(('> '))]
        notes = [(ind, i) for ind, i in enumerate(sec[1:]) if not i.startswith(('> ', '-'))]
        word_meanings = [(ind, i) for ind, i in enumerate(sec[1:]) if i.startswith('-') and not i.startswith('> ')]

        sub_lines = [sec.index(i) for i in [x[1] for x in subs]]+[len(sec)]
        sub_count = len(sub_lines)

        note_lines = [sec.index(i) for i in [x[1] for x in notes]]
        # note_count = len(note_lines)

        # sub_ranges = [[j for j in range(sub_lines[i]+1, sub_lines[i+1]) if j not in note_lines] for i in range(sub_count-1)]
        sub_ranges = [[j for j in range(sub_lines[i]+1, sub_lines[i+1])] for i in range(sub_count-1)]
        sub_titles = [i.lstrip('>').strip() for i in [x[1] for x in subs]]

        note_ranges = split_consecutive_numbers(note_lines)
        note_starts = [x[0] for x in note_ranges]
        note_prestarts = [x[0]-1 for x in note_ranges]

        for sub_title, sub_range in zip(sub_titles, sub_ranges):
            sub_section = {}
            if sub_section.get(sub_title):
                raise KeyError(f"Duplicate Subsection: {sub_title}")
            sub_section = {}

            for i in sub_range:
                if i not in note_lines:
                    wm = sec[i].lstrip('-').strip().split(':')
                    word = wm[0].strip()
                    meaning = [i, None]
                    if len(wm) == 2:
                        meaning = [i, wm[1].strip()]

                    note = None
                    if i in note_prestarts:
                        note = [sec[i] for i in note_ranges[note_prestarts.index(i)]]
                    meaning.append(note)
                    sub_section.update({word: meaning})
            doc['sections'][sec_title]['subsections'][sub_title] = sub_section

        doc['sections'][sec_title]['unorganised'] = parse_unorganised_section(sec[1: sub_lines[0]])

    return doc

def operate(entitity='section_title'):
    entities = [
        'sec_title',
        'sub_title',
        '',
        ''
    ]


def enhanced_content(doc, write=False, fpath=None):
    # check if all words have meaning
    # check if all words are present in std eng dict
    # possible to blacklist sections from these checks

    unorg, secs = doc.values()

    for u in doc[unorg]:
        pass

    for sec in doc[secs]:
        pass

    if write:
        if fpath:
            pass
        else:
            raise Exception("No file mentioned to write to")

def main():
    global p
    p = parse(path)
    print(json.dumps(p, indent=2))

"""
Relative note postions MUST NOT CHANGE
'>>' marks the start of a new section
Sections must be arranged in alpha order w/ exception of slangs and other
Name of section usually follows right after
Make easy changing name of (sub)section/words
Make movement of misplaced words to another (sub)section
Make all words start with a Capital Letter
Make it easy to find and work with words without meanings
Make it easy to add meanings to the word lacking them
Add a small line of hyphens e.g. '------' of fixed length which is either
    greater than the length of largest sec heading
    unless it is more than a threshold, in which case, just clip the remaining length
Make synonymous words occur together separated by slashes in the same bullet point in alphabetic order
Sort all bullets in alphabetic order of the entire string
Make it easy to find new words and add to secs or subsecs from the internet with meaning
    but suggest must ask user's permission before being added to main doc
Make analysis of number of total (sub)sections/words/words without considering synonyms
    words/subsections within a (sub)section(s)
Export to xlsx format with colour coding and proper formatting
Mark Explicit words as "Word (E)"
Mark Archaic words as "Word (A)" and list them separately in same (sub)sec in sorted order
    Mark (NA) for North American Words and (I) for informal words
    Multiple markings can be space separated within 1 pair of parentheses but in sorted order
    E.g. "Word (E I NA)"
Check and optionally remove all words which are not actually words
Convert all words of doc to American English
"""

if __name__ == "__main__":
    testpaths = ["/media/vivojay/DATA/Vivo Jay/test.txt", "/media/vivojay/DATA/Vivo Jay/words.txt"]
    path = testpaths[int(sys.argv[1])-1]
    main()


