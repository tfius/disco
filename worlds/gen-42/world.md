Your world is a one-dimensional cellular automaton with 2 states and radius 2, on finite cyclic tapes and bounded windows. Each cell's next state is given by this rule table, indexed by the neighborhood read as a base-2 number (leftmost cell most significant):

[0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1]

This rule was generated at random from seed 42; nothing about it exists in any literature — every law is undiscovered. Implement the rule once as a tool, validate it against the table, then discover: backgrounds and invariants, cycle structure on small widths, particles and their collisions, statistical behavior of random tapes. Claims must be exact, seeded, and checked by running the automaton.
