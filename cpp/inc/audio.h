#ifndef __AUDIO_H__
#define __AUDIO_H__

#include "bigint.h"
#include "util.h"
#include <string>

void record_audio(std::string fname);

void encrypt_audio(BigInt& k, u64 t, std::string ptname, std::string ctname);

void decrypt_audio(BigInt& k, u64 t, std::string ptname, std::string ctname);

void play_audio(std::string fname);

#endif
