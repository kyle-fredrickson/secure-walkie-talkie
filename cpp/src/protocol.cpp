#include "audio.h"
#include "ctr.h"
#include "protocol.h"
#include "rsa.h"
#include "sha3.h"
#include "util.h"
#include <iostream>
#include <iomanip>

JSON protocol::create_request(const BigInt& alice_rsa_d, const BigInt&
    alice_rsa_n, const BigInt& bob_rsa_e, const BigInt& bob_rsa_n, const BigInt&
    dh_g, const BigInt& dh_p, BigInt& tod, BigInt& alice_dh_pri) {
  // Step 1: Choose a random 256-bit number.
  BigInt key = BigInt::rand_n_bits(256, ms_since_epoch());

  // Step 2: Computer ToD since UNIX epoch in milliseconds.
  tod = BigInt::from_uint64(ms_since_epoch());

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
  alice_dh_pri = BigInt::rand_n_bits(4096, ms_since_epoch());
  BigInt alice_dh_pub = dh_g.powm(alice_dh_pri, dh_p);

  // Step 8: Package alice_dh_pub and hash_sess_key into JSON.
  JSON agree = {
    { "hash_sess_key", hash_sess_key.str_in_base(10) },
    { "diffie_pub_k", alice_dh_pub.str_in_base(10) }
  };

  // Step 9: Hash the bytes of agree, then convert hash to BigInt.
  std::string agree_str = agree.dump();
  std::vector<u8> bytes_agree(agree_str.begin(), agree_str.end());
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
  std::string payload_str = payload.dump();
  std::vector<u8> dec_payload(payload_str.begin(), payload_str.end());
  std::vector<u8> enc_payload(dec_payload.size());
  std::vector<u8> bytes_key = BigInt::to_bytes(key);
  ctr_encrypt(BigInt::to_uint64(tod), bytes_key.data(), dec_payload.data(),
    enc_payload.data(), dec_payload.size());

  // Step 13: Base64 encode enc_payload and encrypted sess_key.
  BigInt enc_payload_num = BigInt::from_bytes(enc_payload);
  std::string enc_payload_str = BigInt::to_base64(enc_payload_num);
  std::string enc_sess_key = BigInt::to_base64(enc_sess_key_num);

  // Step 14: Package enc_payload_str and enc_sess_key into JSON.
  JSON dhke = {
    { "payload", enc_payload_str },
    { "sess_key", enc_sess_key }
  };

  return dhke;
}

bool protocol::verify_request(const JSON& request, const BigInt& bob_rsa_d,
    const BigInt& bob_rsa_n, const JSON& bob_contacts, BigInt& tod, BigInt&
    alice_dh_pub, BigInt& alice_rsa_e, BigInt& alice_rsa_n)
{
  // Step 1: Unpack sess_key and payload request, both of which are base64 encoded.
  BigInt enc_sess_key_num = BigInt::from_base64(request["sess_key"].get<std::string>());
  BigInt enc_payload_num = BigInt::from_base64(request["payload"].get<std::string>());

  // Step 2: Decrypt the sess_key, which was encrypted with Bob's public RSA key.
  BigInt sess_key_num = RSA::decrypt(enc_sess_key_num, bob_rsa_d, bob_rsa_n);

  // Step 3: Unpack key and ToD after converting sess_key_num back into JSON.
  JSON sess_key = JSON::parse(BigInt::to_string(sess_key_num));
  BigInt key = BigInt(sess_key["key"].get<std::string>());
  tod = BigInt(sess_key["tod"].get<std::string>());

  // Step 4: Convert sess_key_num to bytes, hash it, then convert hash to BigInt.
  std::vector<u8> bytes_sess_key = BigInt::to_bytes(sess_key_num);
  std::vector<u8> digest_sess_key;
  SHA3::absorb(bytes_sess_key);
  SHA3::squeeze(digest_sess_key);
  BigInt hash_sess_key = BigInt::from_bytes(digest_sess_key);

  // Step 5: Decrypt payload using SIMON counter mode using ToD (the nonce) and the key.
  std::vector<u8> enc_payload = BigInt::to_bytes(enc_payload_num);
  std::vector<u8> dec_payload(enc_payload.size());
  std::vector<u8> bytes_key = BigInt::to_bytes(key);
  ctr_decrypt(BigInt::to_uint64(tod), bytes_key.data(), enc_payload.data(),
    dec_payload.data(), enc_payload.size());

  // Step 6: Reconstruct decrypted payload back into JSON.
  JSON payload = JSON::parse(std::string(dec_payload.begin(), dec_payload.end()));

  // Step 7: Unpack the payload which has Alice's signature and agreement data.
  JSON agree = payload["agreement_data"].get<JSON>();
  BigInt alice_hash_sess_key = BigInt(agree["hash_sess_key"].get<std::string>());
  alice_dh_pub = BigInt(agree["diffie_pub_k"].get<std::string>());
  BigInt alice_signature = BigInt(payload["signature"].get<std::string>());

  // Step 8: Verify computed and received hash_sess_key match.
  if (hash_sess_key != alice_hash_sess_key) {
    return false;
  }

  // Step 9: Hash the bytes of agree, then convert hash to BigInt.
  std::string agree_str = agree.dump();
  std::vector<u8> bytes_agree(agree_str.begin(), agree_str.end());
  std::vector<u8> digest_agree;
  SHA3::absorb(bytes_agree);
  SHA3::squeeze(digest_agree);
  BigInt hash_agree = BigInt::from_bytes(digest_agree);

  // Step 10: Check if Alice is one of Bob's contacts through the signature.
  bool verified = false;

  for (auto& contact : bob_contacts) {
    alice_rsa_e = BigInt(contact["rsa_e"].get<std::string>());
    alice_rsa_n = BigInt(contact["rsa_n"].get<std::string>());
    BigInt signature = RSA::verify(alice_signature, alice_rsa_e, alice_rsa_n);

    if (hash_agree == signature) {
      verified = true;
      break;
    }
  }

  return verified;
}

JSON protocol::create_response(const BigInt& bob_rsa_d, const BigInt& bob_rsa_n,
    const BigInt& alice_rsa_e, const BigInt& alice_rsa_n, const BigInt&
    alice_dh_pub, const BigInt& dh_g, const BigInt& dh_p, const BigInt& tod,
    BigInt& k1, BigInt& k2) {
  // Step 1: Choose a random 256-bit number.
  BigInt key = BigInt::rand_n_bits(256, ms_since_epoch());

  // Step 2: Package the key into JSON.
  JSON sess_key = {
    { "key", key.str_in_base(10) }
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
  std::string enc_sess_key = BigInt::to_base64(enc_sess_key_num);

  // Step 13: Package enc_payload_str and enc_sess_key into JSON.
  JSON dhke = {
    { "payload", enc_payload_str },
    { "sess_key", enc_sess_key }
  };

  // Step 14: Compute the shared Diffie-Hellman key.
  BigInt dh_shared = alice_dh_pub.powm(bob_dh_pri, dh_p);

  // Step 15: Compute the first hash key, k1.
  std::vector<u8> digest_k1;
  std::vector<u8> bytes_k1 = BigInt::to_bytes(dh_shared);
  bytes_k1.insert(bytes_k1.begin(), static_cast<u8>(0x01));
  SHA3::absorb(bytes_k1);
  SHA3::squeeze(digest_k1);
  k1 = BigInt::from_bytes(digest_k1);

  // Step 16: Computer the second hash key, k2.
  std::vector<u8> digest_k2;
  std::vector<u8> bytes_k2 = BigInt::to_bytes(dh_shared);
  bytes_k2.insert(bytes_k2.begin(), static_cast<u8>(0x02));
  SHA3::absorb(bytes_k2);
  SHA3::squeeze(digest_k2);
  k2 = BigInt::from_bytes(digest_k2);

  return dhke;
}

bool protocol::verify_response(const JSON& response, const BigInt& alice_rsa_d,
    const BigInt& alice_rsa_n, const BigInt& bob_rsa_e, const BigInt& bob_rsa_n,
    const BigInt& dh_p, const BigInt& alice_dh_pri, const BigInt& tod, BigInt&
    k1, BigInt& k2)
{
  // Step 1: Unpack sess_key and payload request, both of which are base64 encoded.
  BigInt enc_sess_key_num = BigInt::from_base64(response["sess_key"].get<std::string>());
  BigInt enc_payload_num = BigInt::from_base64(response["payload"].get<std::string>());

  // Step 2: Decrypt the sess_key, which was encrypted with Alice's public RSA key.
  BigInt sess_key_num = RSA::decrypt(enc_sess_key_num, alice_rsa_d, alice_rsa_n);

  // Step 3: Unpack key and ToD after converting sess_key_num back into JSON.
  JSON sess_key = JSON::parse(BigInt::to_string(sess_key_num));
  BigInt key = BigInt(sess_key["key"].get<std::string>());

  // Step 4: Convert sess_key_num to bytes, hash it, then convert hash to BigInt.
  std::vector<u8> bytes_sess_key = BigInt::to_bytes(sess_key_num);
  std::vector<u8> digest_sess_key;
  SHA3::absorb(bytes_sess_key);
  SHA3::squeeze(digest_sess_key);
  BigInt hash_sess_key = BigInt::from_bytes(digest_sess_key);

  // Step 5: Decrypt payload using SIMON counter mode using ToD (the nonce) and the key.
  std::vector<u8> enc_payload = BigInt::to_bytes(enc_payload_num);
  std::vector<u8> dec_payload(enc_payload.size());
  std::vector<u8> bytes_key = BigInt::to_bytes(key);
  ctr_decrypt(BigInt::to_uint64(tod), bytes_key.data(), enc_payload.data(),
    dec_payload.data(), enc_payload.size());

  // Step 6: Reconstruct decrypted payload back into JSON.
  JSON payload = JSON::parse(std::string(dec_payload.begin(), dec_payload.end()));

  // Step 7: Unpack the payload which has Bob's signature and agreement data.
  JSON agree = payload["agreement_data"].get<JSON>();
  BigInt bob_hash_sess_key = BigInt(agree["hash_sess_key"].get<std::string>());
  BigInt bob_dh_pub = BigInt(agree["diffie_pub_k"].get<std::string>());
  BigInt bob_signature = BigInt(payload["signature"].get<std::string>());

  // Step 8: Verify computed and received hash_sess_key match.
  if (hash_sess_key != bob_hash_sess_key) {
    return false;
  }

  // Step 9: Hash the bytes of agree, then convert hash to BigInt.
  std::string agree_str = agree.dump();
  std::vector<u8> bytes_agree(agree_str.begin(), agree_str.end());
  std::vector<u8> digest_agree;
  SHA3::absorb(bytes_agree);
  SHA3::squeeze(digest_agree);
  BigInt hash_agree = BigInt::from_bytes(digest_agree);

  // Step 10:
  BigInt signature = RSA::verify(bob_signature, bob_rsa_e, bob_rsa_n);

  // Step 10: Compute Alice's shared Diffie-Hellman key.
  BigInt dh_shared = bob_dh_pub.powm(alice_dh_pri, dh_p);

  // Step 11: Compute the first hash key, k1.
  std::vector<u8> digest_k1;
  std::vector<u8> bytes_k1 = BigInt::to_bytes(dh_shared);
  bytes_k1.insert(bytes_k1.begin(), static_cast<u8>(0x01));
  SHA3::absorb(bytes_k1);
  SHA3::squeeze(digest_k1);
  k1 = BigInt::from_bytes(digest_k1);

  // Step 12: Compute the second hash key, k2.
  std::vector<u8> digest_k2;
  std::vector<u8> bytes_k2 = BigInt::to_bytes(dh_shared);
  bytes_k2.insert(bytes_k2.begin(), static_cast<u8>(0x02));
  SHA3::absorb(bytes_k2);
  SHA3::squeeze(digest_k2);
  k2 = BigInt::from_bytes(digest_k2);

  return true;
}
