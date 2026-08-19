/* monad_identity.h — the three faces of language in one binary.
 *
 * DESIGN PRINCIPLE: this file records WHERE information is, not WHAT it is.
 * Every heavy value (the context code, the prime address) is RECOMPUTABLE from
 * the sparse positions stored here plus the parameters in the header. That is
 * what makes the file discardable: once the algorithm is trusted, the .bin is
 * a cache of positions, not a store of content, and can be regenerated or
 * thrown away without loss.
 *
 * Nothing here is a float. Every field is an exact integer, an offset, or a
 * count, because the whole point is that the arithmetic is reproducible.
 *
 * THE THREE FACES
 *   FACE 1  LETTERS    spelling, muscle memory      primes <= 313, Fermat bands
 *   FACE 2  WORDS      composites, ORDER MATTERS    positional (Horner) codes
 *   FACE 3  PATHWAYS   ideas, order does NOT        multiplicative (prime products)
 *
 * The faces are not merged into one scalar. They are three algebras and a
 * single number would have to pick one and destroy the others. What joins them
 * is that FACE 1 DETERMINES THE STRUT and the strut SELECTS FACE 3's BOX KITE.
 */

#ifndef MONAD_IDENTITY_H
#define MONAD_IDENTITY_H

#include <stdint.h>

#define MI_MAGIC        0x4D4F4E4944454E54ULL   /* "MONIDENT" */
#define MI_VERSION      1
#define MI_LETTER_CAP   313      /* admits exactly F_0..F_3 — four generations */
#define MI_N_GEN        4        /* ranking, factors, GROUPING, division       */
#define MI_ALPHABET     26
#define MI_NO_PARENT    0xFFFFFFFFu

/* ── section directory ───────────────────────────────────────────────── */
typedef struct {
    uint64_t offset;      /* byte offset from start of file */
    uint64_t length;      /* byte length                    */
    uint64_t count;       /* element count (0 if a raw blob) */
} mi_section_t;

/* ── header: self-describing, so the file can be regenerated ─────────── */
typedef struct {
    uint64_t magic;                    /* MI_MAGIC                          */
    uint32_t version;                  /* MI_VERSION                        */
    uint32_t header_bytes;             /* sizeof(mi_header_t)               */

    /* FACE 1 parameters — everything needed to rebuild the letter ladder */
    uint32_t letter_cap;               /* 313                               */
    uint32_t n_generations;            /* 4                                 */
    uint32_t fermat[MI_N_GEN];         /* 3, 5, 17, 257                     */
    uint8_t  freq_order[MI_ALPHABET];  /* letters in frequency order, ASCII  */
    uint32_t letter_prime[MI_ALPHABET];/* the prime each letter maps to      */
    uint8_t  letter_gen[MI_ALPHABET];  /* its Fermat band, 0..3              */

    /* FACE 2 parameters */
    uint32_t spell_base;               /* 27 = alphabet + 1 offset           */

    /* FACE 3 parameters */
    uint32_t context_prime_lo;         /* first prime > letter_cap (73)      */
    uint32_t n_channels;               /* how many context channels are live */

    /* sections */
    mi_section_t s_strings;            /* surface forms, NUL-separated       */
    mi_section_t s_entries;            /* mi_entry_t[]                       */
    mi_section_t s_lineage;            /* uint8 generation sequences         */
    mi_section_t s_channels;           /* mi_chan_t[] sparse context vectors  */
    mi_section_t s_phon;               /* phoneme/morpheme blob              */
    mi_section_t s_edges;              /* mi_edge_t[] the 15-relation graph  */

    uint64_t     built_unix;           /* when                               */
    uint64_t     corpus_fingerprint;   /* what it was built from             */
    uint64_t     checksum;             /* FNV-1a over everything after header*/
} mi_header_t;

/* ── FACE 3: one sparse channel, index + exponent ────────────────────── */
typedef struct {
    uint32_t channel;   /* index into CONTEXT_PRIMES                        */
    uint8_t  exponent;  /* magnitude. 1 = squarefree, the unit-cube corner  */
    uint8_t  _pad[3];
} mi_chan_t;

/* ── the 15 relations: an EDGE, not a place ──────────────────────────── */
typedef struct {
    uint32_t from;        /* entry index                                    */
    uint32_t to;          /* entry index                                    */
    uint8_t  xor_class;   /* 1..15 — WHICH KIND of relation this is         */
    uint8_t  kind;        /* 0 hypernym, 1 mero, 2 similar, 3 antonym, ...  */
    uint16_t weight;      /* fixed-point x1000; charge, not truth           */
} mi_edge_t;

/* ── one word, all three faces ───────────────────────────────────────── */
typedef struct {
    /* ── identity ─────────────────────────────────────────────────────  */
    uint32_t index;            /* its own position; never moves            */
    uint32_t surface_off;      /* into s_strings                           */
    uint16_t surface_len;
    uint8_t  n_letters;        /* tier-1 content length                    */
    uint8_t  n_delims;         /* tier-0 aperture length (NOT in the maths) */

    /* ── FACE 1/2: LETTERS -> WORDS. positional, order matters. ───────  */
    uint64_t spell;            /* Horner base-27. BIJECTIVE — this IS the
                                * word. Unspell recovers it exactly; the
                                * hash is one-way only if you discard this. */
    uint32_t lineage_off;      /* into s_lineage: the ORDERED generation
                                * sequence, one byte per letter            */
    uint8_t  gen_hist[MI_N_GEN];/* letters per generation. the unordered
                                * summary — lineage is the ordered form.   */
    uint8_t  strut;            /* OR of the generation bits, 0..15         */
    uint8_t  box_kite;         /* strut & 7 when the division bit is set,
                                * else 0 = below the box-kite tier         */
    uint8_t  n_syllables;
    uint8_t  stress_pos;       /* where an INFIX would land (metrical, not
                                * semantic — the abso-FUCKING-lutely rule) */

    /* ── phoneme / morpheme face ──────────────────────────────────────  */
    uint32_t phon_off;         /* into s_phon: IPA, NUL-terminated         */
    uint16_t phon_len;
    uint16_t n_morphemes;
    uint32_t morph_off;        /* into s_phon: morpheme cuts               */
    uint8_t  prefix_len;
    uint8_t  suffix_len;
    uint8_t  pos_mask;         /* bit per POS: n,v,a,r,s                   */
    uint8_t  role;             /* 0 CONCEPT, 1 POINTER, 2 MODIFIER         */

    /* ── FACE 3: PATHWAYS. multiplicative, order does NOT matter. ─────  */
    uint32_t chan_off;         /* into s_channels                          */
    uint32_t chan_len;         /* how many channels are lit                */
    uint16_t code_digits;      /* size of prod p_c^e_c — RECOMPUTABLE      */
    uint16_t addr_digits;      /* size of next_prime(code)                 */
    uint32_t delta;            /* addr - code. the CLARIFIER. small.       */
    uint64_t addr_fp;          /* FNV-1a of the decimal address. a CHECK,
                                * not the address: the address is recomputed
                                * from chan[], which is the whole point.   */

    /* ── the dependency tree: 16 nodes, 15 edges, one root ────────────  */
    uint32_t parent;           /* MI_NO_PARENT = root (owns no edge)       */
    uint8_t  edge_class;       /* 1..15, the XOR relation to the parent    */
    uint8_t  depth;            /* distance to root = descent cost          */
    uint16_t n_children;       /* fan-out. writing FANS, reading CONVERGES */

    /* ── weights live OUTSIDE the chain; they never touch identity ────  */
    uint16_t charge;           /* what has been USED. slow tau.  x1000     */
    uint16_t intent;           /* what is WANTED now. fast tau.  x1000     */
    uint32_t _reserved;
} mi_entry_t;

#endif /* MONAD_IDENTITY_H */
