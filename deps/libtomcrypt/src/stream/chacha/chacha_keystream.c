/* LibTomCrypt, modular cryptographic library -- Tom St Denis */
/* SPDX-License-Identifier: Unlicense */

/* The implementation is based on:
 * chacha-ref.c version 20080118
 * Public domain from D. J. Bernstein
 */

#include "tomcrypt_private.h"

#ifdef LTC_CHACHA

/**
  Generate a stream of random bytes via ChaCha
  @param st      The ChaCha20 state
  @param out     [out] The output buffer
  @param outlen  The output length
  @return CRYPT_OK on success
 */
int chacha_keystream(chacha_state *st, unsigned char *out, unsigned long outlen)
{
   if (outlen == 0) return CRYPT_OK; /* nothing to do */
   LTC_ARGCHK(out != NULL);
   XMEMSET(out, 0, outlen);
   return chacha_crypt(st, out, outlen, out);
}

#endif
