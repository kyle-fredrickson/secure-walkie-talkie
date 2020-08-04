#include "bigint.h"
#include "client.h"
#include "protocol.h"
#include "rsa.h"
#include "util.h"
#include <cassert>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <string>
#include <unistd.h>

#define OPTIONS   "hvl:t:i:p:"

void print_usage(char *program) {
  std::cerr <<
    "SYNOPSIS\n"
    "   Record and send encrypted audio.\n"
    "   Audio is received and decrypted by the listener program.\n"
    "\n"
    "USAGE\n";
  std::cerr <<  "   " << program << " [-hv] [-t team] [-i ip] [-p port]\n"
    "\n"
    "OPTIONS\n"
    "   -h        Display program help and usage\n"
    "   -v        Display verbose program output\n"
    "   -i ip     Specify IP to send audio to (default: localhost)\n"
    "   -p port   Specify port to send audio to (default: 8123)";
  std::cerr << std::endl;
  return;
}

int main(int argc, char **argv) {
  int opt = 0;
  int port = 8123;
  std::string ip = "localhost";
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
    case 'i':
      ip = optarg;
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

  // The following is required to create the request:
  //  - Alice's private RSA key (RSA d, RSA n)
  //  - Bob's public RSA key (RSA e, RSA n)
  //  - Diffie-Hellman prime and generator (DH p, DH, g)
  BigInt alice_rsa_d = BigInt(alice["rsa_d"].get<std::string>());
  BigInt alice_rsa_n = BigInt(alice["rsa_n"].get<std::string>());
  BigInt bob_rsa_e = BigInt(bob["rsa_e"].get<std::string>());
  BigInt bob_rsa_n = BigInt(bob["rsa_n"].get<std::string>());
  BigInt dh_p = BigInt(alice["dh_p"].get<std::string>());
  BigInt dh_g = BigInt(alice["dh_g"].get<std::string>());

  JSON contacts = alice["contacts"].get<JSON>();
  for (auto& contact : contacts) {
    std::cout << std::setw(2) << contact << std::endl;
  }

  // Create the request.
  JSON request = protocol::create_request(alice_rsa_d, alice_rsa_n, bob_rsa_e,
      bob_rsa_n, dh_p, dh_g);

  // Attempt communication with server.
  try {
    TCPClient client(ip, port);
    LOG("Connected to: " << ip << " on port: " << port);

    // Send the request.
    client.send_request(request);
    LOG("Sent request:\n" << std::setw(2) << request);
  } catch (TCPSocketException& err) {
    std::cerr << "Client error: " << err.what() << std::endl;
  }

  // Database::init();

//   BigInt da = BigInt::rand_n_bits(4096, ms_since_epoch());

//   BigInt tod = BigInt::from_uint64(ms_since_epoch());

//   Being alice("alice", rsa_p, rsa_q, rsa_e, dh_p, dh_g, da);

//   BigInt sa = BigInt::rand_n_bits(256, ms_since_epoch());
//   BigInt Da = alice.dh_pk;

//   JSON m1a = {
//     { "key", sa.str_in_base(10) },
//     { "tod", tod.str_in_base(10) }
//   };

//   BigInt m1a_bigint = BigInt::from_string(m1a.dump());

//   Being other;
//   CHECK(Database::search(team, other), "Error: bad team.");
//   LOG("Sending to: " << other.name);

//   BigInt ses1 = alice.encrypt(other, m1a_bigint);

//   std::vector<u8> m1a_data = BigInt::to_bytes(m1a_bigint);
//   std::vector<u8> hm1a_data;

//   SHA3::absorb(m1a_data);
//   SHA3::squeeze(hm1a_data);

//   BigInt hm1a = BigInt::from_bytes(hm1a_data);

//   JSON m1b {
//     { "hash_sess_key", hm1a.str_in_base(10) },
//     { "diffie_pub_k", Da.str_in_base(10) }
//   };

//   BigInt m1b_bigint = BigInt::from_string(m1b.dump());

//   std::vector<u8> m1b_data = BigInt::to_bytes(m1b_bigint);
//   std::vector<u8> hm1b_data;

//   SHA3::absorb(m1b_data);
//   SHA3::squeeze(hm1b_data);

//   BigInt hm1b = BigInt::from_bytes(hm1b_data);

//   BigInt sig1 = alice.sign(hm1b);

//   JSON something = {
//     { "agreement_data", m1b },
//     { "signature", sig1.str_in_base(10) }
//   };

//   BigInt something_bigint = BigInt::from_string(something.dump());

//   std::vector<u8> pt = BigInt::to_bytes(something_bigint);
//   std::vector<u8> ct(pt.size());
//   std::vector<u8> key_sa= BigInt::to_bytes(sa);

//   ctr_encrypt(BigInt::to_uint64(tod), key_sa.data(), pt.data(), ct.data(), pt.size());

//   BigInt m1c = BigInt::from_bytes(ct);

//   JSON m1 = {
//     { "payload", BigInt::to_base64(m1c) },
//     { "sess_key", BigInt::to_base64(ses1) }
//   };

//   // Initialize the TCP client.
//   try {
//     TCPClient client(ip, port);
//     LOG("Connected to: " << ip << " on port: " << port);

//     // Send packet 1.
//     client.send_request(m1);
//     LOG("Sent packet 1 to: " << other.name);

//     // Receive packet 2.
//     JSON m2;
//     client.recv_response(m2);
//     LOG("Received packet 2 from: " << other.name);

//     BigInt m2c = BigInt::from_base64(m2["payload"].get<std::string>());
//     BigInt ses2 = BigInt::from_base64(m2["sess_key"].get<std::string>());

//     BigInt m2a_bigint = alice.decrypt(ses2);

//     JSON m2a = JSON::parse(BigInt::to_string(m2a_bigint));

//     BigInt sb = BigInt(m2a["key"].get<std::string>().c_str());

//     std::vector<u8> ct2 = BigInt::to_bytes(m2c);
//     std::vector<u8> pt2(ct2.size());
//     std::vector<u8> key_sb = BigInt::to_bytes(sb);

//     ctr_decrypt(BigInt::to_uint64(tod), key_sb.data(), ct2.data(), pt2.data(), ct2.size());

//     BigInt something2_bigint = BigInt::from_bytes(pt2);

//     JSON something2 = JSON::parse(BigInt::to_string(something2_bigint));

//     JSON m2b = something2["agreement_data"].get<JSON>();
//     BigInt sig2 = BigInt(something2["signature"].get<std::string>().c_str());

//     BigInt m2b_bigint = BigInt::from_string(m2b.dump());

//     std::vector<u8> m2b_data = BigInt::to_bytes(m2b_bigint);
//     std::vector<u8> hm2b_data;

//     SHA3::absorb(m2b_data);
//     SHA3::squeeze(hm2b_data);

//     BigInt hm2b = BigInt::from_bytes(hm2b_data);

//     CHECK(alice.verify(other, sig2) == hm2b, "Error: bad signature.");

//     BigInt h = BigInt(m2b["hash_sess_key"].get<std::string>().c_str());
//     BigInt Db = BigInt(m2b["diffie_pub_k"].get<std::string>().c_str());

//     std::vector<u8> m2a_data = BigInt::to_bytes(m2a_bigint);
//     std::vector<u8> hm2a_data;

//     SHA3::absorb(m2a_data);
//     SHA3::squeeze(hm2a_data);

//     BigInt hm2a = BigInt::from_bytes(hm2a_data);

//     CHECK(h == hm2a, "Error: bad tag.");

//     BigInt Dab = Db.powm(da, dh_p);

//     std::vector<u8> Dab1_hash;
//     std::vector<u8> Dab1_data = BigInt::to_bytes(Dab);
//     Dab1_data.insert(Dab1_data.begin(), static_cast<u8>(0x01));

//     SHA3::absorb(Dab1_data);
//     SHA3::squeeze(Dab1_hash);

//     std::vector<u8> Dab2_hash;
//     std::vector<u8> Dab2_data = BigInt::to_bytes(Dab);
//     Dab2_data.insert(Dab2_data.begin(), static_cast<u8>(0x02));

//     SHA3::absorb(Dab2_data);
//     SHA3::squeeze(Dab2_hash);

//     BigInt k1 = BigInt::from_bytes(Dab1_hash);
//     BigInt k2 = BigInt::from_bytes(Dab2_hash);

//     if (!gui) {
//       record_audio("audio_client.wav");
//     }

//     encrypt_audio(k1, BigInt::to_uint64(tod), "audio_client.wav", "audio_client.encrypted");

//     struct stat statbuf;
//     stat("audio_client.encrypted", &statbuf);

//     std::ifstream audiofile("audio_client.encrypted", std::ios::binary);
//     CHECK(audiofile, "Failed to open audio file.");

//     std::vector<u8> audio(statbuf.st_size);
//     audiofile.read((char *)audio.data(), statbuf.st_size);

//     std::vector<u8> tag_hash;
//     std::vector<u8> tag_data = BigInt::to_bytes(k2);
//     tag_data.insert(tag_data.end(), audio.begin(), audio.end());

//     SHA3::absorb(tag_data);
//     SHA3::squeeze(tag_hash);

//     BigInt tag = BigInt::from_bytes(tag_hash);

//     JSON m3 = {
//       { "tag", BigInt::to_base64(tag) }
//     };

//     client.send_hmac(m3);
//     LOG("Sent packet 3 to: " << other.name);

//     client.send_audio("audio_client.encrypted");
//     LOG("Sent audio to: " << other.name);

//     remove("audio_client.encrypted");
//     remove("audio_client.wav");
//   } catch (TCPSocketException& err) {
//     std::cerr << "Client error: " << err.what() << std::endl;
//   }

  return 0;
}
