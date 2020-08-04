#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#include "bigint.h"
#include "util.h"
#include <cstdbool>

namespace protocol {
  JSON create_request(const BigInt& alice_rsa_d, const BigInt& alice_rsa_n, const
      BigInt& bob_rsa_e, const BigInt& bob_rsa_n, const BigInt& dh_g, const
      BigInt& dh_p);

  bool verify_request(const JSON& request, const BigInt& bob_rsa_d, const
      BigInt& bob_rsa_n, const JSON& contacts, JSON& retained);

  JSON create_response(const BigInt& bob_rsa_d, const BigInt& bob_rsa_n,
      const BigInt& alice_rsa_e, const BigInt& alice_rsa_n, const BigInt& dh_g,
      const BigInt& dh_p, const BigInt& tod);
}

#endif
