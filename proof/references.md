# References

Ledger keys resolved here; `verify/check_proof.py` fails any `cite` whose key
is not an anchor below.

- **[KHTS]** Juris Hartmanis and Richard E. Stearns. *On the Computational
  Complexity of Algorithms.* IRE–USNC-SJIT '65, 1965. Deterministic time
  hierarchy theorem. Also presented in standard textbooks (Sipser Thm 9.3;
  Arora–Barak Thm 3.3).
- **[SIPSER]** Michael Sipser. *Introduction to the Theory of Computation*,
  3rd ed., Cengage, 2013. Universal simulation overhead (Thm 8.1: O(T·log T)
  / quadratic single-tape overhead), s-m-n / enumeration theorems, hierarchy
  proof conventions.
- **[COOK]** Stephen A. Cook. *The Complexity of Theorem-Proving Procedures.*
  STOC '71, 1971. SAT is NP-complete; P = NP iff an NP-complete problem lies
  in P.
- **[LEVIN]** Leonid A. Levin. *Universal Search Problems.* (Tr. Math.
  Notes 10, 1973.) Independent NP-completeness formulation.
- **[GAREYJOHNSON]** Michael R. Garey and David S. Johnson. *Computers and
  Intractability*, W. H. Freeman, 1979. NP-completeness catalogue; the
  pigeonhole (PHP) CNF family used in `data/` is a classic example family
  from this literature.
- **[SEARLE]** Michael J. Searle. *P = NP Compared to Its Relativizing and
  Non-Relativizing Proofs.* Theoretical Computer Science 2, 1976. Sparse
  sets, Mahaney-style caveat on succinct halting sets. (Mahaney's theorem:
  Paul R. Mahaney. *Sparse Sets for Language Families.* ICALP 1982.)
- **[BGS]** Theodore Baker, Juris Hartmanis and Richard E. Stearns. *On the
  Complexity of Computation Machines.* SIAM J. Comput. 7(4), 1978. Oracle A
  with P^A ≠ NP^A.
- **[AA]** Oracle separation in the other direction: the Baker–Gill–Solovay
  conference version (IEEE FOCS '75, "On the Relative Complexity of NP")
  constructs an oracle B with P^B = NP^B; and Charles Bennett and John Gill,
  *Relative to a Random Oracle A, P^A ≠ NP^A with Probability 1*, SIAM J.
  Comput. 10(1), 1981.
- **[RR]** Joshua A. Razborov and Steven Rudich. *Natural Proofs.* JCSS 55
  (1), 1997. Natural proofs barrier against circuit lower bounds.
- **[WIGd]** Avi Wigderson. *The "S" Barriers.* In Gödel '02, Lecture Notes
  in Logic 21, ASL, 2003 (with Fortnow–Rogozin: arithmetization relativizes
  to algebraic extensions and cannot separate P from NP alone).
- **[ARV]** Sanjeev Arora and Boaz Barak. *Computational Complexity: A Modern
  Approach*, Cambridge UP, 2009, Ch. 8: the arithmetization technique and
  IP = PSPACE (after Lund–Fortnow–Karloff–Nisan, JACM 1992, and Shamir,
  SICOMP 1992).
