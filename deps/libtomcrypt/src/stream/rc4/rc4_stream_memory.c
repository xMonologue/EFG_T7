/* LibTomCrypt, modular cryptographic library -- Tom St Denis */
/* SPDX-License-Identifier: Unlicense */

#include "tomcrypt_private.h"

#ifdef LTC_RC4_STREAM

/**
   Encrypt (or decrypt) bytes of ciphertext (or plaintext) with RC4
   @param key     The key
   @param keylen  The key length
   @param datain  The plaintext (or ciphertext)
   @param datalen The length of the input and output (octets)
   @param dataout [out] The ciphertext (or plaintext)
   @return CRYPT_OK if successful
*/
int rc4_stream_memory(const unsigned char *key,    unsigned long keylen,
                      const unsigned char *datain, unsigned long datalen,
                      unsigned char *dataout)
{
   rc4_state st;
   int err;

   if ((err = rc4_stream_setup(&st, key, keylen)) != CRYPT_OK) goto WIPE_KEY;
   err = rc4_stream_crypt(&st, datain, datalen, dataout);
WIPE_KEY:
   rc4_stream_done(&st);
   return err;
}

#endif /* LTC_RC4_STREAM */
