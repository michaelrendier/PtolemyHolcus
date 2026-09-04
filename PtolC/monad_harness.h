/* monad_harness.h — the seam ptol.c crosses to drive the Python tabbed
 * curses UI (PtolemyDesktop/ptolemy_console.py).
 *
 * Two inputs, unchanged from the PtolemyDesktop skeleton this is grown from:
 *   1. FRAMES  — newline-delimited JSON over a socketpair. `ptol -w` forks the
 *      console onto the tty (curses draws there) and keeps this end: it reads
 *      `say` / `cmd` / `mode` / `ping` / `quit` frames and answers `chat`.
 *   2. SUPPORT TEXT — the support harness never binds to C. It leaves
 *      regularly-structured lines in the Chat buffer; mh_parse_support_line()
 *      reads them back, Ptolemy's judgement lines included.
 *
 * Frame dispatch (mh_recv / mh_send_chat / mh_send_raw) is now real. The
 * monad.h ingest hooks (mh_ingest_support) are still TODO against the core.
 */
#ifndef MONAD_HARNESS_H
#define MONAD_HARNESS_H

#include <stddef.h>

/* the core, from monad.h — forward-declared so this header stands alone */
struct Monad_;

/* ── frame kinds ──────────────────────────────────────────────────────────── */
typedef enum {
    MH_F_ATTACH = 0,   /* handshake / status request                          */
    MH_F_STATUS,       /* status reply                                        */
    MH_F_TOOL,         /* a tool-request:  {name, args}                       */
    MH_F_ENGINE,       /* an engine call:  {engine, fn, args}                 */
    MH_F_RENDER,       /* a render request                                    */
    MH_F_RADIO,        /* a passive line for the Chat Tab                     */
    MH_F_RESULT,       /* a reply to TOOL / ENGINE / RENDER                   */
    MH_F_ERROR
} mh_frame_kind;

/* ── support-line kinds (parsed from the Chat buffer) ─────────────────────── */
typedef enum {
    MH_S_UNKNOWN = 0,
    MH_S_FACE_POST,        /* « <face> » [<intrusion>] <text>                  */
    MH_S_PTOLEMY_JUDGEMENT /* « Ptolemy » judgement [<face>/<intrusion>]: ...  */
} mh_support_kind;

typedef struct {
    mh_support_kind kind;
    char face[32];
    char intrusion[32];
    char decision[16];     /* HOLD|THROTTLE|HARDEN|ESCALATE|DEFER, judgement only */
    char text[512];        /* the reason (judgement) or the post body (face)   */
} mh_support_line;

/* Parse one line from the Chat buffer. Returns kind; fills `out`. */
mh_support_kind mh_parse_support_line(const char *line, mh_support_line *out);

/* Fold an ingested support line into the core. TODO: wire to monad.h. */
int mh_ingest_support(struct Monad_ *m, const mh_support_line *sl);

/* ── the frame link ──────────────────────────────────────────────────────── */
#define MH_FRAME_MAX 65536

typedef struct {
    char   t[24];              /* frame type: say|cmd|mode|ping|attach|quit    */
    char   text[MH_FRAME_MAX]; /* say/cmd body                                 */
    char   mode[16];           /* mode frames: "sentence" | "paragraph"        */
    long   id;                 /* correlation id, -1 if none                   */
} mh_frame;

typedef struct mh_harness mh_harness;

mh_harness *mh_open(int in_fd, int out_fd);   /* socketpair end (in==out ok)   */
void        mh_close(mh_harness *h);

/* Block for the next frame (timeout_ms < 0 = forever). Returns 1 = got one,
 * 0 = timed out, -1 = EOF / peer gone / hard error. */
int mh_recv(mh_harness *h, mh_frame *out, int timeout_ms);

/* Answer a say/cmd frame. `primes` is a pre-formatted "2 3 5 ..." string (may
 * be NULL/empty); sigma/gamma go out as numbers; `mode` echoes the current
 * construction mode. Returns 0 on success, -1 on write error. */
int mh_send_chat(mh_harness *h, long id, const char *text,
                 double sigma, double gamma,
                 const char *primes, const char *mode);

/* Write a raw pre-built JSON object line (no trailing newline needed). */
int mh_send_raw(mh_harness *h, const char *json_line);

/* one frame + drain chat — still TODO (frame side is done via mh_recv). */
int mh_pump(mh_harness *h, int timeout_ms);

#endif /* MONAD_HARNESS_H */
