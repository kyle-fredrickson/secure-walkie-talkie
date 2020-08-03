#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#include "bigint.h"

namespace protocol {
  JSON request(const BigInt& alice_rsa_d, const BigInt& alice_rsa_n, const
      BigInt& bob_rsa_e, const BigInt& bob_rsa_n, const BigInt& dh_g, const
      BigInt& dh_p);

  JSON response(const BigInt& bob_rsa_d, const BigInt& bob_rsa_n,
    const BigInt& alice_rsa_e, const BigInt& alice_rsa_n, const BigInt& dh_g, const
    BigInt& dh_p, const BigInt& tod);
}

#endif
