#include "bigint.h"
#include "protocol.h"
#include "server.h"
#include "util.h"
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <string>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#define OPTIONS   "hvt:l:p:"

void print_usage(char *program) {
  std::cerr <<
    "SYNOPSIS\n"
    "   Receive and play decrypted audio.\n"
    "   Audio is encrypted and sent by the talker program.\n"
    "\n"
    "USAGE\n";
  std::cerr <<  "   " << program << " [-hv] [-p port]\n"
    "\n"
    "OPTIONS\n"
    "   -h        Display program help and usage\n"
    "   -v        Display verbose program output\n"
    "   -p port   Specify port to send audio to (default: 8123)";
  std::cerr << std::endl;
  return;
}

int main(int argc, char **argv) {
  int opt = 0;
  int port = 8123;
  std::string talker_file = "config/Eugene.json";
  std::string listener_file = "config/Eunice.json";

  while ((opt = getopt(argc, argv, OPTIONS)) != -1) {
    switch (opt) {
    case 'h':
      print_usage(argv[0]);
      return 0;
    case 'v':
      verbose = true;
      break;
    case 'l':
      listener_file = optarg;
      break;
    case 't':
      talker_file = optarg;
      break;
    case 'p':
      port = std::stoi(std::string(optarg));
      break;
    default:
      print_usage(argv[0]);
      return 1;
    }
  }

  // Open up filestreams for talker and listener credentials.
  std::ifstream talker(talker_file);
  std::ifstream listener(listener_file);

  // Give Alice the talker credentials.
  JSON alice;
  talker >> alice;

  // Give Bob the listener credentials.
  JSON bob;
  listener >> bob;

  // The following is required to create the response:
  //  - Bob's private RSA key (RSA d, RSA n)
  //  - Alice's public RSA key (RSA e, RSA n)
  //  - Diffie-Hellman prime and generator (DH p, DH, g)
  //  - Bob's contacts.
  BigInt bob_rsa_d = BigInt(bob["rsa_d"].get<std::string>());
  BigInt bob_rsa_n = BigInt(bob["rsa_n"].get<std::string>());
  BigInt alice_rsa_e = BigInt(alice["rsa_e"].get<std::string>());
  BigInt alice_rsa_n = BigInt(alice["rsa_n"].get<std::string>());
  BigInt dh_p = BigInt(bob["dh_p"].get<std::string>());
  BigInt dh_g = BigInt(bob["dh_g"].get<std::string>());
  JSON bob_contacts = bob["contacts"].get<JSON>();

  // Attempt communication with client.
  try {
    TCPServer server(port);
    LOG("Server started on port: " << port);

    // Receive request.
    JSON request;
    server.recv_request(request);
    LOG("Received request:\n" << std::setw(2) << request);

    // Verify the request, pass back retained data by reference.
    JSON retained;

    if (!protocol::verify_request(request, bob_rsa_d, bob_rsa_n, bob_contacts, retained)) {
      std::cerr << "Error: invalid request" << std::endl;
      return 1;
    }

    LOG("Request verified.");

    // BigInt m1c = BigInt::from_base64(m1["payload"].get<std::string>());
    // BigInt ses1 = BigInt::from_base64(m1["sess_key"].get<std::string>());

    // BigInt m1a_bigint = bob.decrypt(ses1);

    // JSON m1a = JSON::parse(BigInt::to_string(m1a_bigint));

    // BigInt sa = BigInt(m1a["key"].get<std::string>().c_str());
    // u64 tod = BigInt::to_uint64(BigInt(m1a["tod"].get<std::string>().c_str()));

    // std::vector<u8> ct2 = BigInt::to_bytes(m1c);
    // std::vector<u8> pt2(ct2.size());
    // std::vector<u8> key_sa = BigInt::to_bytes(sa);

    // ctr_decrypt(tod, key_sa.data(), ct2.data(), pt2.data(), ct2.size());

    // BigInt something2_bigint = BigInt::from_bytes(pt2);
    // JSON something2 = JSON::parse(BigInt::to_string(something2_bigint));

    // JSON m1b = something2["agreement_data"].get<JSON>();
    // BigInt sig1 = BigInt(something2["signature"].get<std::string>().c_str());

    // BigInt m1b_bigint = BigInt::from_string(m1b.dump());

    // std::vector<u8> m1b_data = BigInt::to_bytes(m1b_bigint);
    // std::vector<u8> hm1b_data;

    // SHA3::absorb(m1b_data);
    // SHA3::squeeze(hm1b_data);

    // BigInt hm1b = BigInt::from_bytes(hm1b_data);

    // bool verified = false;
    // Being other;

    // for (const auto& being : beings) {
    //   if (bob.verify(being, sig1) == hm1b) {
    //     other = Being(being.name, being.rsa_n, being.rsa_e);
    //     verified = true;
    //     break;
    //   }
    // }

    // CHECK(verified, "Error: unknown being.");

    // BigInt h = BigInt(m1b["hash_sess_key"].get<std::string>().c_str());
    // BigInt Da = BigInt(m1b["diffie_pub_k"].get<std::string>().c_str());

    // std::vector<u8> m1a_data = BigInt::to_bytes(m1a_bigint);
    // std::vector<u8> hm1a_data;

    // SHA3::absorb(m1a_data);
    // SHA3::squeeze(hm1a_data);

    // BigInt hm1a = BigInt::from_bytes(hm1a_data);

    // CHECK(h == hm1a, "Error: bad packet.");

    // JSON m2a = {
    //   { "key", BigInt::to_base64(sb) }
    // };

    // BigInt m2a_bigint = BigInt::from_string(m2a.dump());

    // BigInt ses2 = bob.encrypt(other, m2a_bigint);

    // std::vector<u8> m2a_data = BigInt::to_bytes(m2a_bigint);
    // std::vector<u8> hm2a_data;

    // SHA3::absorb(m2a_data);
    // SHA3::squeeze(hm2a_data);

    // BigInt hm2a = BigInt::from_bytes(hm2a_data);

    // JSON m2b = {
    //   { "hash_sess_key", hm2a.str_in_base(10) },
    //   { "diffie_pub_k", Db.str_in_base(10) }
    // };

    // BigInt m2b_bigint = BigInt::from_string(m2b.dump());

    // std::vector<u8> m2b_data = BigInt::to_bytes(m2b_bigint);
    // std::vector<u8> hm2b_data;

    // SHA3::absorb(m2b_data);
    // SHA3::squeeze(hm2b_data);

    // BigInt hm2b = BigInt::from_bytes(hm2b_data);

    // BigInt sig2 = bob.sign(hm2b);

    // JSON m2c_json = {
    //   { "agreement_data", m2b },
    //   { "signature", sig2.str_in_base(10) }
    // };

    // BigInt m2c_bigint = BigInt::from_string(m2c_json.dump());

    // std::vector<u8> pt1 = BigInt::to_bytes(m2c_bigint);
    // std::vector<u8> ct1(pt1.size());
    // std::vector<u8> key_sb = BigInt::to_bytes(sb);

    // ctr_encrypt(tod, key_sb.data(), pt1.data(), ct1.data(), pt1.size());

    // BigInt m2c = BigInt::from_bytes(ct1);

    // JSON m2 = {
    //   { "payload", BigInt::to_base64(m2c) },
    //   { "sess_key", BigInt::to_base64(ses2) }
    // };

    // server.send_response(m2);
    // LOG("Sent packet 2 to: " << other.name);

    // BigInt Dab = Da.powm(db, dh_p);
    // std::vector<u8> Dab1_hash;
    // std::vector<u8> Dab1_data = BigInt::to_bytes(Dab);
    // Dab1_data.insert(Dab1_data.begin(), static_cast<u8>(0x01));

    // SHA3::absorb(Dab1_data);
    // SHA3::squeeze(Dab1_hash);

    // std::vector<u8> Dab2_hash;
    // std::vector<u8> Dab2_data = BigInt::to_bytes(Dab);
    // Dab2_data.insert(Dab2_data.begin(), static_cast<u8>(0x02));

    // SHA3::absorb(Dab2_data);
    // SHA3::squeeze(Dab2_hash);

    // BigInt k1 = BigInt::from_bytes(Dab1_hash);
    // BigInt k2 = BigInt::from_bytes(Dab2_hash);

    // JSON m3;
    // server.recv_hmac(m3);
    // LOG("Received packet 3 from: " << other.name);

    // BigInt m3_tag = BigInt::from_base64(m3["tag"].get<std::string>());

    // server.recv_audio("audio_server.encrypted");
    // LOG("Received audio from: " << other.name);

    // struct stat statbuf;
    // stat("audio_server.encrypted", &statbuf);

    // std::ifstream audiofile("audio_server.encrypted", std::ios::binary);
    // CHECK(audiofile, "Failed to open audio file.");

    // std::vector<u8> audio(statbuf.st_size);
    // audiofile.read((char *)audio.data(), statbuf.st_size);

    // std::vector<u8> tag_hash;
    // std::vector<u8> tag_data = BigInt::to_bytes(k2);
    // tag_data.insert(tag_data.end(), audio.begin(), audio.end());

    // SHA3::absorb(tag_data);
    // SHA3::squeeze(tag_hash);

    // BigInt tag = BigInt::from_bytes(tag_hash);

    // CHECK(tag == m3_tag, "Error: bad tag.");

    // decrypt_audio(k1, tod, "audio_server.encrypted", "audio_server.wav");

    // play_audio("audio_server.wav");

    // remove("audio_server.encrypted");
    // remove("audio_server.wav");
  } catch (TCPSocketException& err) {
    std::cerr << "Server error: " << err.what() << std::endl;
  }

  return 0;
}
