#include "audio.h"
#include "ctr.h"
#include "protocol.h"
#include "rsa.h"
#include "sha3.h"
#include "util.h"

JSON protocol::request(const BigInt& alice_rsa_d, const BigInt& alice_rsa_n,
    const BigInt& bob_rsa_e, const BigInt& bob_rsa_n, const BigInt& dh_g, const
    BigInt& dh_p) {
  // Step 1: Choose a random 256-bit number.
  BigInt key = BigInt::rand_n_bits(256, ms_since_epoch());

  // Step 2: Computer ToD since UNIX epoch in milliseconds.
  BigInt tod = BigInt::from_uint64(ms_since_epoch());

  // Step 3: Package the key and time of day into JSON.
  JSON sess_key = {
    { "key", key.str_in_base(10) },
    { "tod", tod.str_in_base(10) }
  };

  // Step 4: Convert sess_key into a BigInt.
  BigInt sess_key_num = BigInt::from_string(sess_key.dump());

  // Step 5: Encrypt sess_key_num using Bob's RSA public n and e.
  BigInt enc_sess_key_num = RSA::encrypt(sess_key_num, bob_rsa_e, bob_rsa_n);

  // Step 6: Convert sess_key to bytes, hash it, then convert hash to BigInt.
  std::vector<u8> bytes_sess_key = BigInt::to_bytes(sess_key_num);
  std::vector<u8> digest_sess_key;
  SHA3::absorb(bytes_sess_key);
  SHA3::squeeze(digest_sess_key);
  BigInt hash_sess_key = BigInt::from_bytes(digest_sess_key);

  // Step 7: Setup Diffie-Hellman private and public keys.
  BigInt alice_dh_pri = BigInt::rand_n_bits(4096, ms_since_epoch());
  BigInt alice_dh_pub = dh_g.powm(alice_dh_pri, dh_p);

  // Step 8: Package alice_dh_pub and hash_sess_key into JSON.
  JSON agree = {
    { "hash_sess_key", hash_sess_key.str_in_base(10) },
    { "diffie_pub_k", alice_dh_pub.str_in_base(10) }
  };

  // Step 9: Hash the bytes of agree, then convert hash to BigInt.
  std::vector<u8> bytes_agree(agree.dump().begin(), agree.dump().end());
  std::vector<u8> digest_agree;
  SHA3::absorb(bytes_agree);
  SHA3::squeeze(digest_agree);
  BigInt hash_agree = BigInt::from_bytes(digest_agree);

  // Step 10: Sign hash_agree with Alice's private RSA key.
  BigInt signature = RSA::sign(hash_agree, alice_rsa_d, alice_rsa_n);

  // Step 11: Package agreement data and signature into package JSON.
  JSON payload = {
    { "agreement_data", agree },
    { "signature", signature.str_in_base(10) }
  };

  // Step 12: Encrypt payload with SIMON counter mode using ToD (the nonce) and the key.
  std::vector<u8> dec_payload(payload.dump().begin(), payload.dump().end());
  std::vector<u8> enc_payload(dec_payload.size());
  std::vector<u8> bytes_key = BigInt::to_bytes(key);
  ctr_encrypt(BigInt::to_uint64(tod), bytes_key.data(), dec_payload.data(),
    enc_payload.data(), dec_payload.size());

  // Step 13: Base64 encode enc_payload and sess_key.
  BigInt enc_payload_num = BigInt::from_bytes(enc_payload);
  std::string enc_payload_str = BigInt::to_base64(enc_payload_num);
  std::string enc_sess_key = BigInt::to_base64(sess_key_num);

  // Step 14: Package enc_payload_str and enc_sess_key into JSON.
  JSON dhke = {
    { "payload", enc_payload_str },
    { "sess_key", enc_sess_key }
  };

  return dhke;
}

JSON protocol::response(const BigInt& bob_rsa_d, const BigInt& bob_rsa_n,
    const BigInt& alice_rsa_e, const BigInt& alice_rsa_n, const BigInt& dh_g, const
    BigInt& dh_p, const BigInt& tod) {
  // Step 1: Choose a random 256-bit number.
  BigInt key = BigInt::rand_n_bits(256, ms_since_epoch());

  // Step 2: Package the key and time of day into JSON.
  JSON sess_key = {
    { "key", key.str_in_base(10) },
    { "tod", tod.str_in_base(10) }
  };

  // Step 3: Convert sess_key into a BigInt.
  BigInt sess_key_num = BigInt::from_string(sess_key.dump());

  // Step 4: Encrypt sess_key_num using Alice's RSA public n and e.
  BigInt enc_sess_key_num = RSA::encrypt(sess_key_num, alice_rsa_e, alice_rsa_n);

  // Step 5: Convert sess_key to bytes, hash it, then convert hash to BigInt.
  std::vector<u8> bytes_sess_key = BigInt::to_bytes(sess_key_num);
  std::vector<u8> digest_sess_key;
  SHA3::absorb(bytes_sess_key);
  SHA3::squeeze(digest_sess_key);
  BigInt hash_sess_key = BigInt::from_bytes(digest_sess_key);

  // Step 6: Setup Diffie-Hellman private and public keys.
  BigInt bob_dh_pri = BigInt::rand_n_bits(4096, ms_since_epoch());
  BigInt bob_dh_pub = dh_g.powm(bob_dh_pri, dh_p);

  // Step 7: Package bob_dh_pub and hash_sess_key into JSON.
  JSON agree = {
    { "hash_sess_key", hash_sess_key.str_in_base(10) },
    { "diffie_pub_k", bob_dh_pub.str_in_base(10) }
  };

  // Step 8: Hash the bytes of agree, then convert hash to BigInt.
  std::vector<u8> bytes_agree(agree.dump().begin(), agree.dump().end());
  std::vector<u8> digest_agree;
  SHA3::absorb(bytes_agree);
  SHA3::squeeze(digest_agree);
  BigInt hash_agree = BigInt::from_bytes(digest_agree);

  // Step 9: Sign hash_agree with Alice's private RSA key.
  BigInt signature = RSA::sign(hash_agree, bob_rsa_d, bob_rsa_n);

  // Step 10: Package agreement data and signature into package JSON.
  JSON payload = {
    { "agreement_data", agree },
    { "signature", signature.str_in_base(10) }
  };

  // Step 11: Encrypt payload with SIMON counter mode using ToD (the nonce) and the key.
  std::vector<u8> dec_payload(payload.dump().begin(), payload.dump().end());
  std::vector<u8> enc_payload(dec_payload.size());
  std::vector<u8> bytes_key = BigInt::to_bytes(key);
  ctr_encrypt(BigInt::to_uint64(tod), bytes_key.data(), dec_payload.data(),
    enc_payload.data(), dec_payload.size());

  // Step 12: Base64 encode enc_payload and sess_key.
  BigInt enc_payload_num = BigInt::from_bytes(enc_payload);
  std::string enc_payload_str = BigInt::to_base64(enc_payload_num);
  std::string enc_sess_key = BigInt::to_base64(sess_key_num);

  // Step 13: Package enc_payload_str and enc_sess_key into JSON.
  JSON dhke = {
    { "payload", enc_payload_str },
    { "sess_key", enc_sess_key }
  };

  return dhke;
}
