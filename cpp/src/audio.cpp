#include "audio.h"
#include "ctr.h"
#include <fstream>
#include <iostream>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

void record_audio(std::string fname) {
  // ":1" refers to the microphone device on macOS (depends on system).
  std::string c = "ffmpeg -y -f avfoundation -i \":1\" " + fname + " &> /dev/null";

  // Simulate a button.
  std::cout << "Press <enter> to start recording. ";
  std::cin.ignore();

  // Execute the command.
  std::cout << "Recording audio (press <q> to stop)." << std::endl;
  system(c.c_str());

  return;
}

void encrypt_audio(BigInt& k, u64 t, std::string ptfname, std::string ctfname) {
  // Grab length of unencrypted audio file.
  struct stat statbuf;
  stat(ptfname.c_str(), &statbuf);

  // Create container for unencrypted audio.
  u8 *pt = new u8[statbuf.st_size]();
  CHECK(pt, "Failed to allocate memory for unencrypted data.");

  // Create container for encrypted audio.
  u8 *ct = new u8[statbuf.st_size]();
  CHECK(ct, "Failed to allocate memory for encrypted data.");

  // Open file stream for unencrypted audio.
  std::ifstream ptaudio(ptfname, std::ios::binary);
  CHECK(ptaudio, "Failed to open audio file.");

  // Open file stream for encrypted audio.
  std::ofstream ctaudio(ctfname, std::ios::binary | std::ios::trunc);
  CHECK(ctaudio, "Failed to open encrypted audio file.");

  // Format key.
  std::vector<u8> key = BigInt::to_bytes(k);

  // Read in unencrypted audio, encrypt, write out encrypted audio.
  // TODO: Nonce should be changed to ToD.
  ptaudio.read((char *)pt, statbuf.st_size);
  ctr_encrypt(t, key.data(), pt, ct, statbuf.st_size);
  ctaudio.write((char *)ct, statbuf.st_size);

  // Clean up.
  ptaudio.close();
  ctaudio.close();
  delete[] pt;
  delete[] ct;
  return;
}

void decrypt_audio(BigInt& k, u64 t, std::string ctfname, std::string pftname) {
  // Grab length of encrypted audio file.
  struct stat statbuf;
  stat(ctfname.c_str(), &statbuf);

  // Create container for encrypted audio.
  u8 *ct = new u8[statbuf.st_size]();
  CHECK(ct, "Failed to allocate memory for encrypted data.");

  // Create container for decrypted audio.
  u8 *pt = new u8[statbuf.st_size]();
  CHECK(pt, "Failed to allocate memory for decrypted data.");

  // Open file stream for encrypted audio.
  std::ifstream ctaudio(ctfname, std::ios::binary);
  CHECK(ctaudio, "Failed to open encrypted audio file.");

  // Open file stream for decrypted audio.
  std::ofstream ptaudio(pftname, std::ios::binary | std::ios::trunc);
  CHECK(ptaudio, "Failed to open decrypted audio file.");

  // Format key.
  std::vector<u8> key = BigInt::to_bytes(k);

  // Read encrypted audio, decrypt, write out decrypted audio.
  // TODO: Nonce should be changed to ToD.
  ctaudio.read((char *)ct, statbuf.st_size);
  ctr_decrypt(t, key.data(), ct, pt, statbuf.st_size);
  ptaudio.write((char *)pt, statbuf.st_size);

  // Clean up.
  ctaudio.close();
  ptaudio.close();
  delete[] ct;
  delete[] pt;
  return;
}

void play_audio(std::string fname) {
  // Format command to ffplay, volume can be changed.
  std::string c = "ffplay -nodisp -autoexit " + fname + " &> /dev/null";

  // Execute the command.
  std::cout << "Playing audio (will automatically stop)." << std::endl;
  system(c.c_str());

  return;
}
