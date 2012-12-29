#!/usr/bin/env python3

# Reference: P-systems with one membrane and symport/antiport rules of five
# symbols are computationally complete, A. Alhazov, R. Freund.

"""echo $state | ./psy.py [-v] [-l] program

Input:
    A program file contains a list of rules, and comments (lines starting with
    a '#'). Rules are whitespace-separated words, in which only the symbols a-e
    (outgoing) and A-E (incoming) are meaningful.  There must be at least one
    outgoing symbol.

Semantics:
    The program reads on stdin a string, from which the symbols a-e are
    extracted and used as the initial contents of the "cell".  The rest of the
    output is discarded.

    At each step the program finds a maximal multiset of rules such that the
    outgoing letters used in the rules are all present in the cell (with at
    least the required multiplicities).  These symbols are removed from the
    cell and replaced with the new symbols.

    The program stops when no rule is applicable anymore.  The amount of each
    symbol present in the cell is then printed (in decimal) on stdout.
"""

# We represent a state as a Counter of symbols, and a rule as a pair of Counter
# of (lowercase) symbols (outgoing, incoming).


from collections import Counter
Counter.__repr__ = lambda self: "".join(self.elements())


SYMBOLS = "abcde"


def run(rules, state, opts):
    if opts.detect_loops:
        previous_states = [state.copy()]
    while True:
        if opts.verbose:
            print(state)
        to_add = Counter()
        end = True
        for outgoing, incoming in rules:
            while True:
                if state - outgoing + outgoing == state:
                    state -= outgoing
                    to_add += incoming
                    end = False
                    if opts.verbose:
                        print(" ", outgoing, "->", incoming)
                else:
                    break
        state += to_add
        if opts.detect_loops:
            for prev in previous_states:
                if state - prev + prev == state:
                    raise Exception(
                        "Found increasing sequence: {}->{}".format(prev, state))
            previous_states.append(state.copy())
        if end:
            return state


def main(input_rules, input_state, opts):
    rules = [(Counter([symbol for symbol in word
                       if symbol in SYMBOLS]),
              Counter([symbol.lower() for symbol in word
                       if symbol in SYMBOLS.upper()]))
             for fname in input_rules
             for line in open(fname)
             if line and not line.startswith("#")
             for word in line.split()]
    for rule in rules:
        if not rule[0]:
            raise Exception("Rules without outgoing component are invalid.")
    state = Counter([symbol for symbol in input_state.read()
                     if symbol in SYMBOLS])
    print(run(rules, state, opts))


if __name__ == "__main__":
    import sys
    from optparse import OptionParser
    parser = OptionParser(__doc__)
    parser.add_option("-v", "--verbose", action="store_true",
                      help="show rules applied")
    parser.add_option("-l", "--detect-loops", action="store_true",
                      help="detect infinite increasing sequences (slow)")
    options, args = parser.parse_args()
    try:
        main(args, sys.stdin, options)
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
