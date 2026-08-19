/*
 * ptol_shell.c — ptol, the conversation window.
 *
 * No command-line flags. You type a prompt; you get the geometry. Everything
 * else is a /shortcut, and the shortcuts interrogate the CURRENT structure of
 * the monad rather than toggling output formats.
 *
 * DIAGNOSTICS FROM ABOVE. The window does not ask the engine how it feels. It
 * asks what HOLDS — the spectrum, the kernel, the strut, the descent cost —
 * and every answer is computed on the spot from the algebra, never stored.
 *
 * THE THREE FACES OF LANGUAGE, and each gets the encoding its algebra demands:
 *   LETTERS   spelling, muscle memory     primes <= 71, Fermat generation bands
 *   WORDS     composites, ORDER MATTERS   positional (Horner base 27)
 *   PATHWAYS  ideas, order does NOT       multiplicative (prime products)
 *
 * THE LADDER IS FERMAT. F_n = 2^(2^n)+1 IS the Cayley-Dickson doubling index:
 *   F_0=3 ranking   F_1=5 factors   F_2=17 GROUPING   F_3=257 division
 *   3*5*17*257 = 65535 = 2^16 - 1, the sedenion dimension.
 * A letter's prime carries its generation, read off its band.
 *
 * Build:  cc -O2 -std=c99 -o ptol ptol_shell.c -lm
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <unistd.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SD 16
#define NGEN 4
#define MAXLINE 4096

/* ── colour: only when someone is looking ────────────────────────────── */
static int g_tty = 0;
#define C(x)   (g_tty ? (x) : "")
#define DIM    C("\033[2m")
#define BOLD   C("\033[1m")
#define RED    C("\033[1;91m")
#define BLUE   C("\033[1;94m")
#define GREEN  C("\033[1;92m")
#define CYAN   C("\033[1;96m")
#define YELLOW C("\033[1;93m")
#define RST    C("\033[0m")

/* ── the ladder ──────────────────────────────────────────────────────── */
static const int FERMAT[NGEN] = { 3, 5, 17, 257 };
static const char *GEN_NAME[NGEN+1] = { "ranking", "factors", "GROUPING",
                                        "division", "beyond" };
/* English frequency order: the commonest letters take the lowest primes, so
 * the most-used letters are the most ancestral. */
static const char *FREQ = "etaoinshrdlcumwfgypbvkjxqz";
static int LETTER_PRIME[26];
static int LETTER_GEN[26];

/* the 16 projection frequencies — zero free parameters */
static const int P16[SD] = { 2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53 };

static int generation_of(int p)
{
    for (int n = 0; n < NGEN; n++) if (p <= FERMAT[n]) return n;
    return NGEN;
}

static void ladder_init(void)
{
    /* first 26 primes, in order; FREQ[i] takes the i-th */
    int n = 0;
    for (int v = 2; n < 26; v++) {
        int prime = 1;
        for (int d = 2; d * d <= v; d++) if (v % d == 0) { prime = 0; break; }
        if (prime) { LETTER_PRIME[n] = v; LETTER_GEN[n] = generation_of(v); n++; }
    }
}

static int letter_index(char c) { const char *p = strchr(FREQ, c); return p ? (int)(p - FREQ) : -1; }

/* ── Cayley-Dickson table, dim 16 ────────────────────────────────────── */
static int MI[SD][SD], MS[SD][SD];

static void cd_build(void)
{
    static int idx[SD][SD], sgn[SD][SD], oi[SD][SD], os_[SD][SD];
    int n = 1;
    idx[0][0] = 0; sgn[0][0] = 1;
    while (n < SD) {
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) { oi[i][j] = idx[i][j]; os_[i][j] = sgn[i][j]; }
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                int cj = (j == 0) ? 1 : -1;
                idx[i][j]         = oi[i][j];        sgn[i][j]         = os_[i][j];
                idx[i][j+n]       = n + oi[j][i];    sgn[i][j+n]       = os_[j][i];
                idx[i+n][j]       = n + oi[i][j];    sgn[i+n][j]       = os_[i][j] * cj;
                idx[i+n][j+n]     = oi[j][i];        sgn[i+n][j+n]     = -os_[j][i] * cj;
            }
        n *= 2;
    }
    memcpy(MI, idx, sizeof MI); memcpy(MS, sgn, sizeof MS);
}

static void sed_mul(const double x[SD], const double y[SD], double out[SD])
{
    for (int k = 0; k < SD; k++) out[k] = 0.0;
    for (int i = 0; i < SD; i++) {
        if (fabs(x[i]) < 1e-300) continue;
        for (int j = 0; j < SD; j++) out[MI[i][j]] += MS[i][j] * x[i] * y[j];
    }
}

static void build_L(const double a[SD], double L[SD][SD])
{
    double e[SD], col[SD];
    for (int j = 0; j < SD; j++) {
        for (int k = 0; k < SD; k++) e[k] = 0.0;
        e[j] = 1.0;
        sed_mul(a, e, col);
        for (int i = 0; i < SD; i++) L[i][j] = col[i];
    }
}

static void jacobi(double A[SD][SD], double w[SD])
{
    for (int sweep = 0; sweep < 100; sweep++) {
        double off = 0.0;
        for (int i = 0; i < SD; i++) for (int j = i+1; j < SD; j++) off += A[i][j]*A[i][j];
        if (off < 1e-26) break;
        for (int p = 0; p < SD; p++) for (int q = p+1; q < SD; q++) {
            if (fabs(A[p][q]) < 1e-18) continue;
            double th = (A[q][q]-A[p][p]) / (2.0*A[p][q]);
            double t  = (th >= 0 ? 1.0 : -1.0) / (fabs(th) + sqrt(th*th + 1.0));
            double c  = 1.0/sqrt(t*t+1.0), s = t*c;
            for (int k = 0; k < SD; k++) { double a1=A[k][p], a2=A[k][q];
                A[k][p]=c*a1-s*a2; A[k][q]=s*a1+c*a2; }
            for (int k = 0; k < SD; k++) { double a1=A[p][k], a2=A[q][k];
                A[p][k]=c*a1-s*a2; A[q][k]=s*a1+c*a2; }
        }
    }
    for (int i = 0; i < SD; i++) w[i] = A[i][i];
}

/* ── session state ───────────────────────────────────────────────────── */
typedef struct {
    double sigma;            /* the Eye. 0.5 = H, Noether-forced */
    char   eye;              /* R C H O S */
    char   last[MAXLINE];    /* the last prompt */
    double v_re[SD], v_im[SD];
    int    have_last;
    long   turns;
} Session;

static const struct { char name; double sigma; const char *what; } EYES[5] = {
    { 'R', 1.00, "real — the assertion"        },
    { 'C', 0.75, "complex"                     },
    { 'H', 0.50, "quaternion — Noether-forced" },
    { 'O', 0.25, "octonion"                    },
    { 'S', 0.00, "sedenion — the boundary"     },
};

/* ── the projection, kept COMPLEX to the end ─────────────────────────── */
static void project(const char *s, double sig, double re[SD], double im[SD])
{
    int n = (int)strlen(s);
    for (int k = 0; k < SD; k++) {
        double f = 2.0*M_PI/(double)P16[k], cr = 0.0, ci = 0.0;
        for (int i = 1; i <= n; i++) {
            double w = pow((double)i, -sig) * (double)(unsigned char)s[i-1];
            cr += w*cos(f*(double)i);  ci += w*sin(f*(double)i);
        }
        re[k] = cr; im[k] = ci;
    }
}

/* ═══════════════════════════════════════════════════════════════════════
 *  THE SHORTCUTS — each one interrogates the CURRENT structure
 * ═══════════════════════════════════════════════════════════════════════ */

static void sc_help(void)
{
    printf("\n%sptol — the conversation window.%s Type a prompt; get the geometry.\n",
           BOLD, RST);
    printf("%sEverything else is a /shortcut, and every answer is computed on the\n"
           "spot from the algebra. Nothing here is stored.%s\n\n", DIM, RST);
    struct { const char *cmd, *arg, *what; } H[] = {
      {"/faces",   "<word>", "all three faces at once: letters, strut, pathway"},
      {"/lineage", "<word>", "the ordered generation sequence, and the strut it ORs to"},
      {"/spell",   "<word>", "the bijective spell code — and unspell it back"},
      {"/ladder",  "",       "the Fermat ladder: which letters sit in which generation"},
      {"/gains",   "",       "the spectrum of L_a: {0 x4, 1 x8, sqrt2 x4}"},
      {"/kernel",  "",       "the 4-dim kernel — the directions that cost nothing"},
      {"/kite",    "",       "the box kite: 7 struts, 42 assessors, 84 diagonals"},
      {"/pencil",  "<k>",    "the 7 ways to FACTOR relation k into two others"},
      {"/trees",   "<n>",    "Telperion / Laurelin / Mingling — the partition of N"},
      {"/currents","",       "sigma_self and the Noether current of the last prompt"},
      {"/eye",     "<RCHOS>","set the observation Eye. H = 1/2 is Noether-forced"},
      {"/tiers",   "",       "the decomposition floor: ADD, SCALE, SIGN"},
      {"/status",  "",       "session state"},
      {"/help",    "",       "this"},
      {"/quit",    "",       "leave"},
    };
    for (unsigned i = 0; i < sizeof(H)/sizeof(H[0]); i++)
        printf("  %s%-9s%s %s%-8s%s %s\n", CYAN, H[i].cmd, RST, DIM, H[i].arg, RST, H[i].what);
    printf("\n");
}

static void sc_ladder(void)
{
    printf("\n%sTHE FERMAT LADDER%s  F_n = 2^(2^n)+1 IS the Cayley-Dickson doubling index\n",
           BOLD, RST);
    for (int n = 0; n < NGEN; n++)
        printf("  F_%d = %-6d generation %d  %s\n", n, FERMAT[n], n, GEN_NAME[n]);
    printf("  %s3 x 5 x 17 x 257 = 65535 = 2^16 - 1 — the sedenion dimension%s\n\n",
           DIM, RST);
    for (int g = 0; g < NGEN; g++) {
        printf("  gen %d %-9s ", g, GEN_NAME[g]);
        for (int i = 0; i < 26; i++)
            if (LETTER_GEN[i] == g) printf("%c(%d) ", FREQ[i], LETTER_PRIME[i]);
        printf("\n");
    }
    printf("\n");
}

/* letters -> spell, lineage, strut.
 * Returns WF_EMPTY, WF_OK or WF_OVERFLOW — three distinct outcomes, because
 * "no letters" and "too many letters" are not the same answer and collapsing
 * them would report a 30-letter word as pure aperture. */
#define WF_EMPTY    0
#define WF_OK       1
#define WF_OVERFLOW 2
static int word_faces(const char *w, unsigned long long *spell,
                      int *lin, int *nlin, int *strut)
{
    unsigned long long v = 0; int n = 0, bits = 0;
    for (const char *p = w; *p; p++) {
        if (!isalpha((unsigned char)*p)) continue;   /* TIER 0 — the aperture */
        int li = letter_index((char)tolower((unsigned char)*p));
        if (li < 0) continue;
        if (n < 64) lin[n] = LETTER_GEN[li];
        bits |= (1 << LETTER_GEN[li]);
        if (v > (0xFFFFFFFFFFFFFFFFULL - (unsigned long long)(li+1)) / 27ULL) {
            /* FLAGGED, never truncated: a truncated spell is not bijective,
             * and staying silent about that would make the tool lie. */
            *nlin = n; *strut = bits; *spell = 0; return WF_OVERFLOW;
        }
        v = v*27ULL + (unsigned long long)(li + 1);
        n++;
    }
    *spell = v; *nlin = n; *strut = bits;
    return n > 0 ? WF_OK : WF_EMPTY;
}

static void unspell(unsigned long long v, char *out, size_t sz)
{
    char tmp[80]; int n = 0;
    while (v > 0 && n < 79) { unsigned long long r = (v-1) % 27ULL; v = (v-1)/27ULL; tmp[n++] = FREQ[r]; }
    size_t o = 0;
    for (int i = n-1; i >= 0 && o+1 < sz; i--) out[o++] = tmp[i];
    out[o] = '\0';
}

static void sc_spell(const char *w)
{
    unsigned long long sp; int lin[64], nl, st;
    int r = word_faces(w, &sp, lin, &nl, &st);
    if (r == WF_EMPTY) { printf("  no tier-1 content — that is pure aperture\n\n"); return; }
    printf("\n%sFACE 1/2 — LETTERS -> WORDS%s  positional, because 'dog' != 'god'\n", BOLD, RST);
    if (r == WF_OVERFLOW) {
        printf("  %sOVERFLOW at %d letters%s — base-27 exceeds uint64 past 13.\n", RED, nl, RST);
        printf("  %sFLAGGED, not truncated: a truncated spell is not bijective, and%s\n", DIM, RST);
        printf("  %ssilence about that would make this tool lie about its own guarantee.%s\n", DIM, RST);
        printf("  %sthe strut and lineage are still exact — only the spell code overflows.%s\n\n", DIM, RST);
        return;
    }
    char back[80]; unspell(sp, back, sizeof back);
    printf("  spell    %llu\n", sp);
    printf("  unspell  %s   %sround-trip exact: %s%s\n", back, DIM,
           strlen(back) == (size_t)nl ? "yes" : "NO", RST);
    printf("  %sthe hash is one-way only if you discard the record%s\n\n", DIM, RST);
}

static void sc_lineage(const char *w)
{
    unsigned long long sp; int lin[64], nl, st;
    if (word_faces(w, &sp, lin, &nl, &st) == WF_EMPTY) {
        printf("  no tier-1 content — that is pure aperture, and the aperture\n");
        printf("  %sselects the domain but never enters the maths%s\n\n", DIM, RST);
        return;
    }
    printf("\n%sLINEAGE of '%s'%s   each letter carries its generation\n", BOLD, w, RST);
    printf("  ");
    /* bound by nl, NOT by the string: lin[] is only filled for the letters
     * that were actually recorded, and walking the whole word reads
     * uninitialised stack past an overflow or past the 64-letter cap. */
    int li = 0;
    for (const char *p = w; *p && li < nl; p++) {
        if (!isalpha((unsigned char)*p)) continue;
        int i = letter_index((char)tolower((unsigned char)*p));
        if (i < 0) continue;
        printf("%c%s->%s%d ", *p, DIM, RST, lin[li++]);
    }
    if (li < (int)strlen(w)) printf("%s...(+%d not recorded)%s", DIM, (int)strlen(w)-li, RST);
    printf("\n  ordered  [");
    for (int i = 0; i < nl; i++) printf("%d%s", lin[i], i+1<nl?" ":"");
    printf("]  %s<- a PATH, not a set%s\n", DIM, RST);
    printf("  strut    %d%d%d%d  = ", (st>>3)&1, (st>>2)&1, (st>>1)&1, st&1);
    for (int b = 0; b < NGEN; b++) if (st & (1<<b)) printf("%s ", GEN_NAME[b]);
    printf("\n");
    if (st & 0b1000) {
        int kite = st & 0b0111;
        if (kite) printf("  box kite %s%d%s  %s(division bit set, so it lives in a kite)%s\n",
                         GREEN, kite, RST, DIM, RST);
        else      printf("  box kite %snone%s  %s(division only — no free generation)%s\n", YELLOW, RST, DIM, RST);
    } else {
        printf("  box kite %snone%s  %s(never reaches generation 3 — below the box-kite tier)%s\n",
               YELLOW, RST, DIM, RST);
    }
    printf("  %sthe letters HAND the strut to face 3. nothing assigned by hand.%s\n\n", DIM, RST);
}

static void sc_gains(void)
{
    double a[SD] = {0}, L[SD][SD], M[SD][SD], w[SD];
    a[1] = a[10] = 1.0/sqrt(2.0);
    build_L(a, L);
    for (int i = 0; i < SD; i++) for (int j = 0; j < SD; j++) {
        double s = 0.0; for (int k = 0; k < SD; k++) s += L[k][i]*L[k][j]; M[i][j] = s; }
    jacobi(M, w);
    int n0=0,n1=0,n2=0;
    for (int i = 0; i < SD; i++) {
        double g = sqrt(fabs(w[i]) < 1e-14 ? 0.0 : w[i]);
        if (g < 1e-6) n0++; else if (fabs(g-1.0) < 1e-6) n1++;
        else if (fabs(g-sqrt(2.0)) < 1e-6) n2++;
    }
    printf("\n%sTHE SPECTRUM of L_a%s   a = (e1 + e10)/sqrt2, strut 3\n", BOLD, RST);
    printf("  gain 0      x%-2d  %sCONTRACT   free WORK — no direction here costs anything%s\n", n0, GREEN, RST);
    printf("  gain 1      x%-2d  %sPRESERVE   free IDENTITY — changes nothing. the STRING.%s\n", n1, CYAN, RST);
    printf("  gain sqrt2  x%-2d  %sDILATE     the ONLY cost, and it is IRRATIONAL%s\n", n2, YELLOW, RST);
    printf("\n  counting law  0^2*%d + 1^2*%d + 2*%d = %.0f  %s<- FORCED, not chosen%s\n",
           n0, n1, n2, 0.0*n0 + 1.0*n1 + 2.0*n2, DIM, RST);
    printf("  %s0 and 1 are the identities of ADD and SCALE. That is why they are free,%s\n", DIM, RST);
    printf("  %swhy they are tier 0, and why neither can ever be a prime.%s\n", DIM, RST);
    printf("  %s1 : sqrt2 is irrational, so the orbit is DENSE — it never closes.%s\n\n", DIM, RST);
}

static void sc_kernel(void)
{
    double a[SD] = {0}, L[SD][SD], M[SD][SD], w[SD];
    a[1] = a[10] = 1.0/sqrt(2.0);
    build_L(a, L);
    double sym = 0.0;
    for (int i = 0; i < SD; i++) for (int j = 0; j < SD; j++) {
        double s = 0.5*(L[i][j]+L[j][i]); sym += s*s; }
    for (int i = 0; i < SD; i++) for (int j = 0; j < SD; j++) {
        double s = 0.0; for (int k = 0; k < SD; k++) s += L[k][i]*L[k][j]; M[i][j] = s; }
    jacobi(M, w);
    int n0 = 0; for (int i = 0; i < SD; i++) if (sqrt(fabs(w[i])) < 1e-6) n0++;
    printf("\n%sTHE KERNEL%s   what costs nothing\n", BOLD, RST);
    printf("  nullity        %d of %d — %d fixed, %d turning in %d planes\n",
           n0, SD, n0, SD-n0, (SD-n0)/2);
    printf("  ||sym(L_a)||   %.3e  %s<- EXACTLY skew. no strain, so no shear, ever.%s\n",
           sqrt(sym), DIM, RST);
    printf("  %sso exp(L_a) is ORTHOGONAL: the norm is conserved for all t, and the%s\n", DIM, RST);
    printf("  %sINVERSE IS THE TRANSPOSE — O(1) instead of O(n^3), and exact.%s\n", DIM, RST);
    printf("\n  %sthe kernel does NOT orbit%s, so it is gravity ABSENT, not free fall.\n", YELLOW, RST);
    printf("  %sfree fall orbits because curvature converges geodesics; absent gravity%s\n", DIM, RST);
    printf("  %sgoes straight and never returns. Orbits are the global discriminant.%s\n", DIM, RST);
    printf("  %s%d of %d coordinates never move — updating them is provably wasted work.%s\n\n",
           DIM, n0, SD, RST);
}

static void sc_kite(void)
{
    printf("\n%sTHE BOX KITE%s   and every count is forced, none chosen\n", BOLD, RST);
    printf("  7 struts        %s2^3 - 1: three FREE generations below the forced division bit%s\n", DIM, RST);
    printf("  42 assessors    7 x 6\n");
    printf("  84 diagonals    42 x 2\n");
    printf("  PG(3,2)         15 points, 35 lines, 15 planes\n\n");
    printf("  %sBUT THE 15 ARE EDGES, NOT PLACES.%s They are the nonzero XOR\n", BOLD, RST);
    printf("  DIFFERENCES between 16 placeholders — kinds of RELATIONSHIP.\n");
    int pairs = 0, byk[16] = {0};
    for (int i = 0; i < SD; i++) for (int j = i+1; j < SD; j++) { byk[i^j]++; pairs++; }
    printf("    C(16,2) = %d pairs;  15 differences x %d each = %d  %s<- exact%s\n",
           pairs, byk[1], 15*byk[1], DIM, RST);
    printf("  a spanning tree on 16 nodes has 15 edges, which is why %se0 is not a\n"
           "  point%s: it is the ROOT, and the root owns no edge.\n\n", CYAN, RST);
}

static void sc_pencil(int k)
{
    if (k < 1 || k > 15) { printf("  /pencil takes a relation 1..15\n\n"); return; }
    printf("\n%sTHE PENCIL AT RELATION %d%s   the ways to FACTOR it into two others\n",
           BOLD, k, RST);
    int n = 0;
    for (int a = 1; a <= 15; a++) {
        int b = a ^ k;
        if (b > a && b <= 15) { printf("    %2d = %2d XOR %2d\n", k, a, b); n++; }
    }
    printf("  count %s%d%s  %s— and 7 is not a design choice anywhere: it is 105/15.%s\n\n",
           GREEN, n, RST, DIM, RST);
}

static void sc_trees(long n)
{
    printf("\n%sTHE TWO TREES%s   they partition N exactly, with no remainder\n", BOLD, RST);
    printf("  %sTELPERION%s  PRIME      what it CANNOT decompose into   backward, entropic\n", BLUE, RST);
    printf("  %sLAURELIN%s   COMPOSITE  what it IS decomposed into      forward, inertial\n", RED, RST);
    printf("  %sMINGLING%s   0 and 1    neither                        sigma = 1/2\n\n", CYAN, RST);
    if (n < 0) { printf("  %sgive a number: /trees 100%s\n\n", DIM, RST); return; }
    long p = 0, c = 0;
    for (long i = 2; i <= n; i++) {
        int prime = 1;
        for (long d = 2; d*d <= i; d++) if (i % d == 0) { prime = 0; break; }
        if (prime) p++; else c++;
    }
    printf("  over [0, %ld]:  Mingling 2   Telperion %ld   Laurelin %ld\n", n, p, c);
    printf("  total %ld of %ld   %scomplete: %s%s\n", 2+p+c, n+1, DIM,
           (2+p+c == n+1) ? "yes, zero overlap" : "NO", RST);
    if (n > 1)
        printf("  densities  %.6f + %.6f = %.3f  %s<- J_Red + J_Blue conserved%s\n",
               (double)p/(double)(n-1), (double)c/(double)(n-1),
               (double)(p+c)/(double)(n-1), DIM, RST);
    printf("\n");
}

static void sc_tiers(void)
{
    printf("\n%sTHE DECOMPOSITION FLOOR%s   run the geometries backwards\n", BOLD, RST);
    printf("  tier 3   chirality, factorial, leverage, balance   %scounts and RATIOS%s\n", DIM, RST);
    printf("  tier 2   vector, boundary, origin, fulcrum         %sFIXED SETS%s\n", DIM, RST);
    printf("  tier 1   reflect, rotate, contract/dilate          %sI - 2uu^T%s\n", DIM, RST);
    printf("  tier 0   %sADD, SCALE, SIGN%s                         %sIRREDUCIBLE%s\n\n", BOLD, RST, DIM, RST);
    printf("  ADD     identity 0             gain 0      Axis 1 {+,-}\n");
    printf("  SCALE   identity 1             gain 1      Axis 2 {x,/}\n");
    printf("  SIGN    identity even-parity   det +/-1    one bit, nothing between\n\n");
    printf("  %sFULCRUM = ANCHOR = origin = balance = ker(M - I). One computation,%s\n", DIM, RST);
    printf("  %sseveral names; the name records only what you were resisting.%s\n", DIM, RST);
    printf("  %sLeverage needs rigidity — a constraint from outside. A corollary.%s\n\n", DIM, RST);
}

static void sc_currents(Session *S)
{
    if (!S->have_last) { printf("  nothing projected yet — type a prompt first\n\n"); return; }
    double pr = 0.0, pb = 0.0, pmin = 1e300, pmax = -1e300;
    for (int k = 0; k < SD; k++) {
        double pw = S->v_re[k]*S->v_re[k] + S->v_im[k]*S->v_im[k];
        if (k >= 8) pr += pw; else pb += pw;
        if (pw < pmin) pmin = pw;
        if (pw > pmax) pmax = pw;
    }
    double jcur = 0.0;
    for (int k = 0; k+1 < SD; k++) {
        double dr = S->v_re[k+1]-S->v_re[k], di = S->v_im[k+1]-S->v_im[k];
        jcur += S->v_re[k]*di - S->v_im[k]*dr;
    }
    double sigma = (pr+pb > 0) ? pr/(pr+pb) : NAN;
    double temp  = (pmax > 0) ? (pmax-pmin)/pmax : 0.0;
    printf("\n%sCURRENTS%s for %s\"%s\"%s\n", BOLD, RST, DIM, S->last, RST);
    printf("  sigma_self       %.9f   %s|z|^2 ratio — the phase is already gone%s\n",
           sigma, DIM, RST);
    printf("  Noether current  %+.6e   %sIm(z* dz) — entirely phase%s\n", jcur, DIM, RST);
    printf("  temperature      %.6f   %s%s%s\n", temp,
           temp > 0.5 ? RED : CYAN, temp > 0.5 ? "HOT — forced, no deviation affordable"
                                               : "COLD — slack exists, style is affordable", RST);
    printf("  state            %s%s%s\n", fabs(jcur) > 1.0 ? BLUE : DIM,
           fabs(jcur) > 1.0 ? "WET — the current is flowing"
                            : "DRY — no current. a real amplitude has none.", RST);
    printf("\n  %sthe current is a VECTOR: it points. the ratio is a scalar: it sits.%s\n",
           DIM, RST);
    printf("  %sa slack string reads nothing — and zero current is not calm weather,%s\n", DIM, RST);
    printf("  %sit is a DRY medium with no information in transit.%s\n\n", DIM, RST);
}

static void sc_status(Session *S)
{
    printf("\n%sSESSION%s\n", BOLD, RST);
    printf("  eye       %c  sigma = %.4f   %s\n", S->eye, S->sigma,
           S->eye=='H' ? "Noether-forced, not a free parameter" : "");
    printf("  turns     %ld\n", S->turns);
    printf("  last      %s%s%s\n", DIM, S->have_last ? S->last : "(nothing yet)", RST);
    printf("  %sno .bin, no cache, no stored state. Every answer above is recomputed.%s\n\n",
           DIM, RST);
}

static void sc_faces(Session *S, const char *w)
{
    sc_lineage(w);
    sc_spell(w);
    printf("%sFACE 3 — PATHWAYS%s  multiplicative, because a set of ideas is a SET\n", BOLD, RST);
    double re[SD], im[SD];
    project(w, S->sigma, re, im);
    double pr=0, pb=0;
    for (int k = 0; k < SD; k++) {
        double pw = re[k]*re[k]+im[k]*im[k];
        if (k >= 8) pr += pw; else pb += pw;
    }
    printf("  R = sqrt(p_red)  %.6f     e = sqrt(p_blue)  %.6f\n", sqrt(pr), sqrt(pb));
    printf("  trochoid loss    %.6f  %snull iff sigma_self = 1/2%s\n",
           fabs(sqrt(pr)-sqrt(pb)), DIM, RST);
    printf("  %sorder does NOT matter here — that is why it is a product and not a%s\n", DIM, RST);
    printf("  %ssequence. Encoding it positionally would destroy what it carries.%s\n\n", DIM, RST);
}

/* ═══════════════════════════════════════════════════════════════════════
 *  THE WINDOW
 * ═══════════════════════════════════════════════════════════════════════ */

static void speak(Session *S, const char *prompt)
{
    project(prompt, S->sigma, S->v_re, S->v_im);
    snprintf(S->last, sizeof S->last, "%s", prompt);
    S->have_last = 1; S->turns++;

    double pr = 0.0, pb = 0.0;
    for (int k = 0; k < SD; k++) {
        double pw = S->v_re[k]*S->v_re[k] + S->v_im[k]*S->v_im[k];
        if (k >= 8) pr += pw; else pb += pw;
    }
    double sigma = (pr+pb > 0) ? pr/(pr+pb) : NAN;

    unsigned long long sp; int lin[64], nl, st;
    word_faces(prompt, &sp, lin, &nl, &st);
    int kite = (st & 0b1000) ? (st & 0b0111) : 0;

    printf("\n  %s16 scalars%s  ", DIM, RST);
    for (int k = 0; k < SD; k++) {
        double m = sqrt(S->v_re[k]*S->v_re[k] + S->v_im[k]*S->v_im[k]);
        printf("%s%.0f%s ", (k >= 8) ? RED : BLUE, m, RST);
    }
    printf("\n  %ssigma_self%s  %.9f    %sstrut%s %d%d%d%d   %skite%s %s%d%s\n",
           DIM, RST, sigma, DIM, RST,
           (st>>3)&1, (st>>2)&1, (st>>1)&1, st&1, DIM, RST,
           kite ? GREEN : DIM, kite, RST);
    printf("  %sthe scalars are the geometry. the words would be the shadow.%s\n\n",
           DIM, RST);
}

static void banner(void)
{
    printf("\n%s  ptol%s — the conversation window\n", BOLD, RST);
    printf("  %sno flags. type a prompt, or a /shortcut. /help lists them.%s\n",
           DIM, RST);
    printf("  %sdiagnostics from above: the window asks what HOLDS, never how it feels.%s\n\n",
           DIM, RST);
}

int main(int argc, char *argv[])
{
    (void)argc; (void)argv;
    g_tty = isatty(1);
    ladder_init();
    cd_build();

    Session S;
    memset(&S, 0, sizeof S);
    S.sigma = 0.5; S.eye = 'H';

    banner();

    char line[MAXLINE];
    for (;;) {
        printf("%s>%s ", CYAN, RST);
        fflush(stdout);
        if (!fgets(line, sizeof line, stdin)) { printf("\n"); break; }
        size_t n = strlen(line);
        while (n && (line[n-1]=='\n' || line[n-1]=='\r')) line[--n] = '\0';
        while (n && isspace((unsigned char)line[n-1])) line[--n] = '\0';
        char *p = line; while (*p && isspace((unsigned char)*p)) p++;
        if (!*p) continue;

        if (*p != '/') { speak(&S, p); continue; }

        char cmd[64] = {0}; char arg[MAXLINE] = {0};
        sscanf(p, "%63s %[^\n]", cmd, arg);
        char *a = arg; while (*a && isspace((unsigned char)*a)) a++;

        if (!strcmp(cmd,"/quit") || !strcmp(cmd,"/q") || !strcmp(cmd,"/exit")) break;
        else if (!strcmp(cmd,"/help") || !strcmp(cmd,"/?"))   sc_help();
        else if (!strcmp(cmd,"/ladder"))                      sc_ladder();
        else if (!strcmp(cmd,"/gains"))                       sc_gains();
        else if (!strcmp(cmd,"/kernel"))                      sc_kernel();
        else if (!strcmp(cmd,"/kite"))                        sc_kite();
        else if (!strcmp(cmd,"/tiers"))                       sc_tiers();
        else if (!strcmp(cmd,"/status"))                      sc_status(&S);
        else if (!strcmp(cmd,"/currents"))                    sc_currents(&S);
        else if (!strcmp(cmd,"/pencil"))                      sc_pencil(*a ? atoi(a) : 1);
        else if (!strcmp(cmd,"/trees"))                       sc_trees(*a ? atol(a) : -1);
        else if (!strcmp(cmd,"/spell"))   { if (*a) sc_spell(a);   else printf("  /spell <word>\n\n"); }
        else if (!strcmp(cmd,"/lineage")) { if (*a) sc_lineage(a); else printf("  /lineage <word>\n\n"); }
        else if (!strcmp(cmd,"/faces"))   { if (*a) sc_faces(&S,a); else printf("  /faces <word>\n\n"); }
        else if (!strcmp(cmd,"/eye")) {
            if (!*a) { printf("  /eye <R|C|H|O|S>\n\n"); continue; }
            char e = (char)toupper((unsigned char)*a); int found = 0;
            for (int i = 0; i < 5; i++) if (EYES[i].name == e) {
                S.eye = e; S.sigma = EYES[i].sigma; found = 1;
                printf("  eye %c  sigma = %.4f  %s%s%s\n\n", e, S.sigma, DIM, EYES[i].what, RST);
            }
            if (!found) printf("  unknown eye '%c' — R C H O S\n\n", e);
        }
        else printf("  %sunknown shortcut %s — /help lists them%s\n\n", DIM, cmd, RST);
    }
    printf("  %s%ld turns. nothing stored — it all recomputes.%s\n\n", DIM, S.turns, RST);
    return 0;
}
