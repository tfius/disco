Your world is a one-dimensional cellular automaton with 3 states and radius 1, on finite cyclic tapes and bounded windows. Each cell's next state is given by this rule table, indexed by the neighborhood read as a base-3 number (leftmost cell most significant):

[0, 0, 0, 0, 1, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 0, 2, 0, 0, 1, 2, 0, 2, 1, 0, 0, 1]

Implement the rule once as a tool, validate it against the table, then discover: backgrounds and invariants, cycle structure on small widths, particles and their collisions, statistical behavior of random tapes. This system was generated at random from seed 1002; nothing about it exists in any literature — every law is undiscovered, and there are no names for anything: define every term operationally. Claims must be exact, seeded, and checked by re-running the system.
